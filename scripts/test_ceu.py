"""Offline regression tests for the CEU terminal client; no real credentials used."""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock
from unittest.mock import patch
from urllib.error import HTTPError, URLError


ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "ceu.py"
if not MODULE.exists():
    MODULE = Path(__file__).with_name("ceu.py")
spec = importlib.util.spec_from_file_location("ceu", MODULE)
ceu = importlib.util.module_from_spec(spec)
sys.modules["ceu"] = ceu
spec.loader.exec_module(ceu)


class WorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.output = []

    def apply(self, files, answer=True, expected=None):
        return ceu.apply_files(self.root, files, lambda _: answer, self.output.append, expected)

    def test_creates_multiple_files_without_executing_them(self):
        result = self.apply([
            {"path": "src/hello.py", "content": "raise RuntimeError('not executed')\n"},
            {"path": "README.md", "content": "Generated example.\n"},
        ])
        self.assertEqual(result, ["src/hello.py", "README.md"])
        self.assertIn("RuntimeError", (self.root / "src/hello.py").read_text())

    def test_declining_overwrite_cancels_whole_batch(self):
        (self.root / "analysis.py").write_text("x = 1\n")
        result = self.apply([
            {"path": "new.py", "content": "x = 3\n"},
            {"path": "analysis.py", "content": "x = 2\n"},
        ], answer=False)
        self.assertEqual(result, [])
        self.assertFalse((self.root / "new.py").exists())
        self.assertEqual((self.root / "analysis.py").read_text(), "x = 1\n")

    def test_approved_replacement_keeps_backup(self):
        (self.root / "analysis.py").write_text("x = 1\n")
        self.apply([{"path": "analysis.py", "content": "x = 2\n"}])
        backups = list((self.root / ".ceu/backups").rglob("analysis.py"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(), "x = 1\n")
        self.assertEqual((self.root / "analysis.py").read_text(), "x = 2\n")
        self.assertTrue(any("-x = 1" in line for line in self.output))

    def test_editor_change_while_waiting_is_preserved(self):
        (self.root / "analysis.py").write_text("x = 99\n")
        with self.assertRaises(ceu.UserError):
            self.apply([{"path": "analysis.py", "content": "x = 2\n"}],
                       expected={"analysis.py": "x = 1\n"})
        self.assertEqual((self.root / "analysis.py").read_text(), "x = 99\n")

    def test_editor_change_during_confirmation_is_preserved(self):
        path = self.root / "analysis.py"
        path.write_text("x = 1\n")
        def confirm(_):
            path.write_text("x = 99\n")
            return True
        with self.assertRaises(ceu.UserError):
            ceu.apply_files(self.root, [{"path": "analysis.py", "content": "x = 2\n"}], confirm, self.output.append)
        self.assertEqual(path.read_text(), "x = 99\n")

    def test_unsafe_paths_are_rejected_before_any_write(self):
        for name in ("../escape.py", "/tmp/escape.py", "C:\\escape.py", ".env", ".ceu/config.json",
                     "nested/.secrets.md", "data/raw/data.csv", "credentials.json", "key.pem", "ceu.py",
                     "NUL.py", "hello\x1b.py"):
            with self.subTest(name=name), self.assertRaises(ceu.UserError):
                self.apply([{"path": "good.py", "content": "x = 1"}, {"path": name, "content": "x = 2"}])
            self.assertFalse((self.root / "good.py").exists())

    def test_duplicate_and_conflicting_paths_are_rejected(self):
        for names in (("a.py", "a.py"), ("a.py", "A.py"), ("a", "a/b.py")):
            with self.subTest(names=names), self.assertRaises(ceu.UserError):
                self.apply([{"path": name, "content": "x = 1"} for name in names])
        self.assertEqual(list(self.root.iterdir()), [])

    def test_symlink_cannot_escape_workspace(self):
        with tempfile.TemporaryDirectory() as outside:
            (self.root / "link").symlink_to(outside, target_is_directory=True)
            with self.assertRaises(ceu.UserError):
                self.apply([{"path": "link/out.py", "content": "x = 1"}])
            self.assertEqual(list(Path(outside).iterdir()), [])

    def test_invalid_python_does_not_write_any_files(self):
        with self.assertRaises(ceu.UserError):
            self.apply([{"path": "good.py", "content": "x = 1"}, {"path": "bad.py", "content": "def !"}])
        self.assertEqual(list(self.root.iterdir()), [])

    def test_read_context_only_reads_explicitly_shared_files(self):
        (self.root / "chosen.py").write_text("x = 1")
        (self.root / "unshared.py").write_text("x = 2")
        (self.root / ".env").write_text("DUMMY_SECRET=not-real")
        self.assertEqual(ceu.read_context(self.root, {"chosen.py"}), {"chosen.py": "x = 1"})
        with self.assertRaises(ceu.UserError):
            ceu.read_context(self.root, {".env"})

    def test_setup_round_trip_and_private_permissions(self):
        path = self.root / ".ceu/config.json"
        config = ceu.Config("dummy-id", "dummy-secret", "example-model")
        ceu.save_config(config, path)
        self.assertEqual(ceu.load_config(path), config)
        if os.name != "nt":
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
            self.assertEqual(path.parent.stat().st_mode & 0o777, 0o700)

    def test_symlink_config_is_rejected(self):
        (self.root / ".ceu").symlink_to(self.root, target_is_directory=True)
        with self.assertRaises(ceu.UserError):
            ceu.save_config(ceu.Config("dummy", "dummy"), self.root / ".ceu/config.json")


class ProtocolTests(unittest.TestCase):
    def client(self, response):
        opener = Mock()
        opener.open.return_value = io.BytesIO(json.dumps(response).encode())
        return ceu.CEUClient(ceu.Config("dummy-id", "dummy-secret", "test-model"), opener), opener

    def test_model_discovery_contract(self):
        client, opener = self.client({"data": [{"modelName": "test-model"}]})
        self.assertEqual(client.models(), ["test-model"])
        req = opener.open.call_args.args[0]
        self.assertEqual(req.full_url, ceu.API_URL + "/api/v1/llm/models")
        self.assertEqual(req.get_method(), "GET")
        self.assertEqual(dict((k.lower(), v) for k, v in req.header_items())["x-client-secret"], "dummy-secret")

    def test_chat_contract_and_secrets_not_in_model_context(self):
        answer = {"message": "Here is your file.", "files": [{"path": "a.py", "content": "x = 1"}]}
        client, opener = self.client({"data": {"content": json.dumps(answer), "finishReason": "stop"}})
        self.assertEqual(client.generate("Create a file", {}, []), answer)
        req = opener.open.call_args.args[0]
        body = json.loads(req.data)
        self.assertEqual(req.full_url, ceu.API_URL + "/api/v1/llm/chat")
        self.assertEqual(set(body), {"model", "messages"})
        self.assertEqual(body["messages"][0]["role"], "user")
        self.assertNotIn("dummy-secret", body["messages"][0]["content"])

    def test_http_errors_are_not_retried_and_do_not_echo_secrets(self):
        client, opener = self.client({})
        opener.open.side_effect = HTTPError(ceu.API_URL, 401, "dummy-secret", {}, None)
        with self.assertRaises(ceu.UserError) as caught:
            client.models()
        self.assertNotIn("dummy-secret", str(caught.exception))
        self.assertEqual(opener.open.call_count, 1)

    def test_redirects_are_refused(self):
        self.assertIsNone(ceu.NoRedirect().redirect_request(None, None, 302, "", {}, "https://other.invalid"))

    def test_secret_input_refuses_visible_fallback(self):
        import warnings
        def visible_fallback(_):
            warnings.warn("Cannot disable echo", ceu.getpass.GetPassWarning)
            return "must-not-be-read"
        with patch.object(ceu.getpass, "getpass", visible_fallback), self.assertRaises(ceu.UserError):
            ceu.read_secret("Secret: ")

    def test_non_ascii_credentials_are_rejected_before_http_encoding(self):
        with self.assertRaises(ceu.UserError):
            ceu.CEUClient(ceu.Config("dummy", "secret\u2603"))

    def test_invalid_truncated_and_unsuccessful_replies(self):
        for data in ({"content": "not JSON"}, {"content": "{}", "finishReason": "length"}, {"content": None}):
            client, _ = self.client({"data": data})
            with self.subTest(data=data), self.assertRaises(ceu.UserError):
                client.generate("hello", {}, [])
        client, _ = self.client({"success": False})
        with self.assertRaises(ceu.UserError):
            client.models()

    def test_schema_and_file_limits(self):
        for answer in ([], {"message": "x", "files": [{"path": "a.py", "content": 3}]},
                       {"message": "x", "files": [{"path": "a", "content": "x"}] * 13}):
            with self.subTest(answer=answer), self.assertRaises(ceu.UserError):
                ceu.parse_reply(json.dumps(answer))
        self.assertEqual(ceu.parse_reply('```json\n{"message":"hello","files":[]}\n```')["message"], "hello")

    def test_large_context_does_not_send_a_request(self):
        client, opener = self.client({})
        with self.assertRaises(ceu.UserError):
            client.generate("x" * ceu.MAX_CONTEXT, {}, [])
        opener.open.assert_not_called()

    def test_multiline_paste_is_one_prompt(self):
        from prompt_toolkit import PromptSession
        from prompt_toolkit.input import create_pipe_input
        from prompt_toolkit.output import DummyOutput
        with create_pipe_input() as pipe:
            session = PromptSession(input=pipe, output=DummyOutput())
            pipe.send_text("\x1b[200~First line\nSecond line\x1b[201~\r")
            self.assertEqual(session.prompt("You> "), "First line\nSecond line")

    def test_two_independent_sessions_do_not_share_context(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d).resolve()
            client, _ = self.client({})
            client.generate = Mock(return_value={"message": "Done", "files": [{"path": "a.py", "content": "x = 1"}]})
            inputs = iter(["create", "follow up", "/quit"])
            with contextlib.redirect_stdout(io.StringIO()):
                ceu.run_chat(client, root, lambda _: next(inputs))
            # Mock stores references; use copied context to check the second request.
            self.assertEqual(client.generate.call_args_list[1].args[1], {"a.py": "x = 1"})
            other, _ = self.client({})
            other.generate = Mock(return_value={"message": "Hello", "files": []})
            inputs = iter(["hello", "/quit"])
            with contextlib.redirect_stdout(io.StringIO()):
                ceu.run_chat(other, root, lambda _: next(inputs))
            self.assertEqual(other.generate.call_args.args[1], {})


if __name__ == "__main__":
    unittest.main()
