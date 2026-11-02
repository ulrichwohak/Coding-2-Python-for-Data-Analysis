"""Offline regression tests for the CEU terminal client; no real credentials used."""

from __future__ import annotations

import contextlib
import ast
import importlib.util
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
import warnings
from unittest.mock import Mock
from unittest.mock import patch
from urllib.error import HTTPError, URLError


ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "ceu-ai.py"
if not MODULE.exists():
    MODULE = Path(__file__).with_name("ceu-ai.py")
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

    def test_automatic_batch_reports_created_updated_deleted_and_keeps_originals(self):
        (self.root / "update.py").write_text("x = 1\n")
        (self.root / "remove.py").write_text("old work\n")
        changed = ceu.apply_files(self.root, [
            {"path": "new.py", "content": "raise RuntimeError('not executed')\n"},
            {"path": "update.py", "content": "x = 2\n"},
        ], emit=self.output.append, delete_files=["remove.py"])
        self.assertEqual(changed, ["new.py", "update.py", "remove.py"])
        self.assertEqual((self.root / "update.py").read_text(), "x = 2\n")
        self.assertFalse((self.root / "remove.py").exists())
        self.assertEqual(self.output[:3], ["Created new.py", "Updated update.py", "Deleted remove.py"])
        self.assertFalse(any(line.startswith("---") for line in self.output))
        backups = list((self.root / ".ceu/backups").iterdir())
        self.assertEqual(len(backups), 1)
        self.assertEqual((backups[0] / "update.py").read_text(), "x = 1\n")
        self.assertEqual((backups[0] / "remove.py").read_text(), "old work\n")
        self.assertIn(str(backups[0].relative_to(self.root)), self.output[-1])

    def test_deletion_rejects_directories_missing_files_and_protected_paths_before_writes(self):
        (self.root / "folder").mkdir()
        for name in ("folder", "missing.py", "../outside.py", ".git/config", "harness.md",
                     "ceu-ai.py", "data/raw/hotels_course.csv", "ceu-api-credentials.txt"):
            with self.subTest(name=name), self.assertRaises(ceu.UserError):
                ceu.apply_files(self.root, [{"path": "new.py", "content": "x = 1"}],
                                emit=self.output.append, delete_files=[name])
            self.assertFalse((self.root / "new.py").exists())
            self.assertFalse((self.root / ".ceu").exists())
        self.assertTrue((self.root / "folder").is_dir())

    def test_deletion_rejects_symlinks_and_existing_datasets(self):
        (self.root / "data.csv").write_text("price\n80\n")
        with tempfile.TemporaryDirectory() as outside:
            target = Path(outside) / "notes.txt"
            target.write_text("Keep this")
            (self.root / "link.txt").symlink_to(target)
            for name in ("link.txt", "data.csv"):
                with self.subTest(name=name), self.assertRaises(ceu.UserError):
                    ceu.apply_files(self.root, [], delete_files=[name])
            self.assertEqual(target.read_text(), "Keep this")
        self.assertEqual((self.root / "data.csv").read_text(), "price\n80\n")

    def test_write_delete_conflict_is_rejected_before_any_change(self):
        path = self.root / "analysis.py"
        path.write_text("x = 1")
        with self.assertRaisesRegex(ceu.UserError, "same file twice"):
            ceu.apply_files(self.root, [{"path": "analysis.py", "content": "x = 2"}],
                            delete_files=["analysis.py"])
        self.assertEqual(path.read_text(), "x = 1")
        self.assertFalse((self.root / ".ceu").exists())

    def test_deletion_preserves_newer_editor_changes(self):
        path = self.root / "analysis.py"
        path.write_text("newer work")
        with self.assertRaisesRegex(ceu.UserError, "changed in your editor"):
            ceu.apply_files(self.root, [], expected={"analysis.py": "old work"}, delete_files=["analysis.py"])
        self.assertEqual(path.read_text(), "newer work")
        self.assertFalse((self.root / ".ceu").exists())

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
                     "nested/.secrets.md", "data/raw/data.csv", "credentials.json", "key.pem", "ceu-ai.py",
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

    def test_csv_context_is_a_read_only_summary_with_five_preview_rows(self):
        path = self.root / "data/raw/hotels.csv"
        path.parent.mkdir(parents=True)
        source = "city,price,distance_miles\n" + "Vienna,80,2.5\n" * 5 + "NOT_IN_PREVIEW,90,3.5\n"
        path.write_text(source)
        (self.root / "unshared.csv").write_text("private\nNEVER_SEND_THIS\n")
        context = ceu.read_context(self.root, {"data/raw/hotels.csv"})
        summary = json.loads(context["data/raw/hotels.csv"])
        self.assertEqual(summary["kind"], "read_only_csv_summary")
        self.assertEqual(summary["row_count"], 6)
        self.assertEqual([c["name"] for c in summary["columns"]], ["city", "price", "distance_miles"])
        self.assertEqual(summary["columns"][1]["dtype"], "int64")
        self.assertEqual(summary["columns"][2]["dtype"], "float64")
        self.assertEqual(len(summary["preview"]), 5)
        self.assertNotIn("NOT_IN_PREVIEW", context["data/raw/hotels.csv"])
        self.assertNotIn("NEVER_SEND_THIS", str(context))
        self.assertEqual(path.read_text(), source)

    def test_csv_types_use_all_rows_and_preview_handles_missing_values(self):
        path = self.root / "sample.csv"
        path.write_text("price,label\n80,a\n,b\n90,c\n100,d\n110,e\n120.5,f\n")
        summary = json.loads(ceu.read_context(self.root, {"sample.csv"})["sample.csv"])
        self.assertEqual(summary["columns"][0]["dtype"], "float64")
        self.assertIsNone(summary["preview"][1]["price"])
        self.assertEqual(summary["row_count"], 6)

    def test_csv_summary_supports_files_larger_than_text_context_limit(self):
        path = self.root / "sample.csv"
        path.write_text("price,description\n" + "100,Hotel room\n" * 20_000)
        self.assertGreater(path.stat().st_size, ceu.MAX_CONTEXT)
        context = ceu.read_context(self.root, {"sample.csv"})
        self.assertEqual(json.loads(context["sample.csv"])["row_count"], 20_000)
        self.assertLess(len(context["sample.csv"].encode()), ceu.MAX_CONTEXT)

    def test_csv_preview_truncates_long_text_and_keeps_headers(self):
        (self.root / "sample.csv").write_text("long_column_name\n" + "x" * 500 + "\n")
        summary = json.loads(ceu.read_context(self.root, {"sample.csv"})["sample.csv"])
        self.assertEqual(summary["columns"][0]["name"], "long_column_name")
        self.assertEqual(summary["preview"][0]["long_column_name"], "x" * ceu.CSV_PREVIEW_CHARS + "... [truncated]")

    def test_header_only_csv_is_valid(self):
        (self.root / "empty.csv").write_text("price,distance_miles\n")
        summary = json.loads(ceu.read_context(self.root, {"empty.csv"})["empty.csv"])
        self.assertEqual(summary["row_count"], 0)
        self.assertEqual(summary["preview"], [])

    def test_invalid_and_oversized_csv_fail_with_friendly_errors(self):
        path = self.root / "bad.csv"
        for content in (b"", b"a,b\n1,2\n3,4,5\n", b"a\n\xff\n"):
            with self.subTest(content=content):
                path.write_bytes(content)
                with self.assertRaisesRegex(ceu.UserError, "Cannot read"):
                    ceu.read_context(self.root, {"bad.csv"})
        path.write_text("value\n1\n")
        with patch.object(ceu, "MAX_CSV_BYTES", 1), self.assertRaisesRegex(ceu.UserError, "CSV limit"):
            ceu.read_context(self.root, {"bad.csv"})

    def test_csv_summary_obeys_total_context_limit(self):
        (self.root / "small.csv").write_text("value\n1\n")
        with patch.object(ceu, "MAX_CONTEXT", 100), self.assertRaisesRegex(ceu.UserError, "shared files are too large"):
            ceu.read_context(self.root, {"small.csv"})

    def test_csv_read_access_does_not_weaken_path_or_raw_write_protection(self):
        for name in ("../outside.csv", ".ceu/config.csv", "data/raw/notes.txt", "venv/data.csv", "secret.key"):
            with self.subTest(name=name), self.assertRaises(ceu.UserError):
                ceu.read_context(self.root, {name})
        with tempfile.TemporaryDirectory() as outside:
            (self.root / "linked.csv").symlink_to(Path(outside) / "data.csv")
            with self.assertRaises(ceu.UserError):
                ceu.read_context(self.root, {"linked.csv"})
        for name in ("data/raw/hotels.csv", "Data/Raw/hotels.csv"):
            with self.subTest(name=name), self.assertRaises(ceu.UserError):
                self.apply([{"path": "good.py", "content": "x = 1"}, {"path": name, "content": "a\n1\n"}])
        self.assertFalse((self.root / "good.py").exists())

    def test_existing_csv_outside_raw_cannot_be_overwritten(self):
        (self.root / "sample.csv").write_text("price\n80\n")
        expected = ceu.read_context(self.root, {"sample.csv"})
        with self.assertRaisesRegex(ceu.UserError, "read-only"):
            self.apply([{"path": "new.py", "content": "x = 1"},
                        {"path": "sample.csv", "content": "price\n999\n"}], expected=expected)
        self.assertEqual((self.root / "sample.csv").read_text(), "price\n80\n")
        self.assertFalse((self.root / "new.py").exists())

    def test_notebook_cell_ids_are_repaired_and_saved_without_warnings(self):
        import nbformat

        for minor in (4, 5):
            with self.subTest(minor=minor):
                notebook = {"nbformat": 4, "nbformat_minor": minor, "metadata": {}, "cells": [
                    {"cell_type": "markdown", "metadata": {}, "source": "A heading", "id": "keep-me"},
                    {"cell_type": "code", "metadata": {}, "source": "x = 1", "execution_count": None, "outputs": []},
                    {"cell_type": "raw", "metadata": {}, "source": "Some notes", "id": "keep-me"},
                ]}
                with warnings.catch_warnings(record=True) as caught:
                    warnings.simplefilter("always")
                    self.apply([{"path": f"notebook-{minor}.ipynb", "content": json.dumps(notebook)}])
                    saved = nbformat.read(self.root / f"notebook-{minor}.ipynb", as_version=4)
                    nbformat.validate(saved)
                self.assertEqual(caught, [])
                self.assertEqual(saved.nbformat_minor, 5)
                ids = [cell.id for cell in saved.cells]
                self.assertEqual(ids[0], "keep-me")
                self.assertEqual(len(set(ids)), 3)
                self.assertEqual([cell.source for cell in saved.cells], ["A heading", "x = 1", "Some notes"])
                self.assertIsNone(saved.cells[1].execution_count)
                self.assertEqual(saved.cells[1].outputs, [])

    def test_notebook_repair_does_not_accept_bad_code_or_stored_results(self):
        for changes in ({"source": "def !"}, {"execution_count": 1},
                        {"outputs": [{"output_type": "stream", "name": "stdout", "text": "fake result"}]}):
            cell = {"cell_type": "code", "metadata": {}, "source": "x = 1", "execution_count": None, "outputs": []}
            cell.update(changes)
            notebook = {"nbformat": 4, "nbformat_minor": 5, "metadata": {}, "cells": [cell]}
            with self.subTest(changes=changes), self.assertRaises(ceu.UserError):
                self.apply([{"path": "good.py", "content": "x = 1"},
                            {"path": "bad.ipynb", "content": json.dumps(notebook)}])
        self.assertFalse((self.root / "good.py").exists())
        self.assertFalse((self.root / "bad.ipynb").exists())

    def test_notebook_accepts_strings_and_lists_of_lines_without_changing_content(self):
        import nbformat

        sources = ["# Description\n\nA café example.\n", "x = 1\nprint(x)\n", "Unformatted\nnotes"]
        for as_list in (False, True):
            cells = []
            for kind, source in zip(("markdown", "code", "raw"), sources):
                cell = {"cell_type": kind, "metadata": {},
                        "source": source.splitlines(keepends=True) if as_list else source}
                if kind == "code":
                    cell.update(execution_count=None, outputs=[])
                cells.append(cell)
            notebook = {"nbformat": 4, "nbformat_minor": 5, "metadata": {}, "cells": cells}
            name = f"source-{as_list}.ipynb"
            with self.subTest(as_list=as_list), warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                self.apply([{"path": name, "content": json.dumps(notebook)}])
                saved = nbformat.read(self.root / name, as_version=4)
                nbformat.validate(saved)
            self.assertEqual(caught, [])
            self.assertEqual([cell.source for cell in saved.cells], sources)
            self.assertEqual(len({cell.id for cell in saved.cells}), 3)

    def test_invalid_source_lists_are_rejected_with_field_not_full_content(self):
        for source in (["SECRET_SENTINEL\n", 42], [None], [["nested"]]):
            notebook = {"nbformat": 4, "nbformat_minor": 5, "metadata": {}, "cells": [
                {"cell_type": "code", "id": "cell-1", "metadata": {}, "source": source,
                 "execution_count": None, "outputs": []}]}
            with self.subTest(source=source), self.assertRaises(ceu.InvalidSourceError) as caught:
                self.apply([{"path": "good.py", "content": "x = 1"},
                            {"path": "bad.ipynb", "content": json.dumps(notebook)}])
            self.assertIn("cells.0.source", str(caught.exception))
            self.assertNotIn("SECRET_SENTINEL", str(caught.exception))
        self.assertEqual(list(self.root.iterdir()), [])

    def test_notebook_syntax_error_identifies_cell_and_line_without_printing_code(self):
        notebook = {"nbformat": 4, "nbformat_minor": 5, "metadata": {}, "cells": [
            {"cell_type": "markdown", "id": "intro", "metadata": {}, "source": "Intro"},
            {"cell_type": "code", "id": "code", "metadata": {},
             "source": ["x = 1\n", "SECRET_SENTINEL =\n"], "execution_count": None, "outputs": []}]}
        with self.assertRaises(ceu.InvalidSourceError) as caught:
            ceu.validate_source("analysis.ipynb", json.dumps(notebook))
        message = str(caught.exception)
        self.assertIn("analysis.ipynb", message)
        self.assertIn("cell 2, line 2", message)
        self.assertIn("invalid Python syntax", message)
        self.assertNotIn("SECRET_SENTINEL", message)

    def test_notebook_json_and_version_errors_are_specific(self):
        for source, reason in (("{\ninvalid}", "JSON at line 2"),
                               ("[]", "JSON must be an object"),
                               ('{"nbformat": 4.5}', "nbformat must be the integer 4"),
                               ('{"nbformat": 4, "nbformat_minor": "5"}', "nbformat_minor")):
            with self.subTest(source=source), self.assertRaisesRegex(ceu.InvalidSourceError, reason):
                ceu.validate_source("analysis.ipynb", source)

    def test_structured_notebook_cells_are_packaged_without_changing_code(self):
        import nbformat

        source = "x = 1\nprint('first\\nsecond')\npath = r'C:\\new'\n"
        original = {"cells": [{"cell_type": "markdown", "source": "# Example"},
                              {"cell_type": "code", "source": source}]}
        reply = ceu.parse_reply(json.dumps({"message": "Ready", "files": [
            {"path": "analysis.ipynb", "content": original}]}))
        self.apply(reply["files"])
        saved = nbformat.read(self.root / "analysis.ipynb", as_version=4)
        nbformat.validate(saved)
        self.assertEqual(saved.cells[1].source, source)
        self.assertEqual(saved.metadata.kernelspec.name, "python3")
        self.assertEqual(saved.metadata.kernelspec.display_name, "Python 3 (ipykernel)")
        self.assertIsNone(saved.cells[1].execution_count)
        self.assertEqual(saved.cells[1].outputs, [])
        self.assertTrue(all(cell.id for cell in saved.cells))
        self.assertNotIn("nbformat", original)

    def test_structured_notebooks_still_reject_bad_code_and_stored_results(self):
        for changes in ({"source": "def !"}, {"execution_count": 1},
                        {"outputs": [{"output_type": "stream", "name": "stdout", "text": "invented"}]}):
            cell = {"cell_type": "code", "source": "x = 1"} | changes
            reply = ceu.parse_reply(json.dumps({"message": "Ready", "files": [
                {"path": "good.py", "content": "x = 1"},
                {"path": "bad.ipynb", "content": {"cells": [cell]}}]}))
            with self.subTest(changes=changes), self.assertRaises(ceu.InvalidSourceError):
                self.apply(reply["files"])
        self.assertEqual(list(self.root.iterdir()), [])

    def test_structured_content_is_only_allowed_for_notebooks_and_is_size_limited(self):
        for path, content in (("analysis.py", {"cells": []}), ("analysis.ipynb", []),
                              ("analysis.ipynb", None)):
            with self.subTest(path=path, content=content), self.assertRaises(ceu.UserError):
                ceu.parse_reply(json.dumps({"message": "Ready", "files": [{"path": path, "content": content}]}))
        with patch.object(ceu, "MAX_BYTES", 10), self.assertRaisesRegex(ceu.UserError, "too large"):
            ceu.parse_reply(json.dumps({"message": "Ready", "files": [
                {"path": "analysis.ipynb", "content": {"cells": []}}]}))

    def test_required_field_error_identifies_missing_field(self):
        content = ceu.notebook_content({"cells": [{"cell_type": "code"}]})
        with self.assertRaisesRegex(ceu.InvalidSourceError, "missing required fields: source"):
            ceu.validate_source("analysis.ipynb", content)

    def test_uppercase_extensions_do_not_bypass_source_validation(self):
        for name, content in (("bad.PY", "def !"), ("bad.IPYNB", "not JSON")):
            with self.subTest(name=name), self.assertRaises(ceu.InvalidSourceError):
                ceu.validate_source(name, content)

    def test_notebook_protocol_example_is_valid_json_with_real_source_line_breaks(self):
        example = next(line for line in ceu.INSTRUCTIONS.splitlines()
                       if line.startswith('{"message": "Notebook ready"'))
        reply = ceu.parse_reply(example)
        self.apply(reply["files"])
        notebook = json.loads((self.root / "example.ipynb").read_text())
        self.assertEqual("".join(notebook["cells"][1]["source"]), "x = 1\nprint(x)")

    def test_all_instruction_response_examples_match_the_actual_protocol(self):
        examples = [line for line in ceu.INSTRUCTIONS.splitlines() if line.startswith('{"message":')]
        self.assertEqual(len(examples), 4)
        reads = []
        writes = []
        for example in examples:
            raw = json.loads(example)
            self.assertIsInstance(raw["message"], str)
            self.assertIsInstance(raw["files"], list)
            reply = ceu.parse_reply(example)
            self.assertLessEqual(len(reply.get("read_files", [])), ceu.MAX_READ_FILES)
            reads.extend(reply.get("read_files", []))
            for file in reply["files"]:
                ceu.local_path(self.root, file["path"], writing=True)
                ceu.validate_source(file["path"], file["content"])
                writes.append(file["path"])
            for file in raw["files"]:
                if file["path"].endswith(".ipynb"):
                    self.assertIsInstance(file["content"], dict)
                    for cell in file["content"]["cells"]:
                        self.assertIsInstance(cell["source"], str)
                        self.assertNotIn("execution_count", cell)
                        self.assertNotIn("outputs", cell)
                else:
                    self.assertEqual(file["content"], "x = 1\nprint(x)")
        self.assertEqual(reads, ["data/raw/file.csv"])
        self.assertEqual(writes, ["analysis.py", "example.ipynb"])

    def test_setup_round_trip_and_private_permissions(self):
        path = self.root / ".ceu/config.json"
        config = ceu.Config("dummy-id", "dummy-secret")
        ceu.save_config(config, path)
        self.assertEqual(ceu.load_config(path), config)
        self.assertEqual(set(json.loads(path.read_text())), {"client_id", "secret"})
        if os.name != "nt":
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
            self.assertEqual(path.parent.stat().st_mode & 0o777, 0o700)

    def test_symlink_config_is_rejected(self):
        (self.root / ".ceu").symlink_to(self.root, target_is_directory=True)
        with self.assertRaises(ceu.UserError):
            ceu.save_config(ceu.Config("dummy", "dummy"), self.root / ".ceu/config.json")

    def test_legacy_model_choices_are_ignored_without_losing_credentials(self):
        path = self.root / "config.json"
        for model in ("GPT-5", "gpt-5-nano", "", None):
            with self.subTest(model=model):
                path.write_text(json.dumps({"client_id": "dummy-id", "secret": "dummy-secret", "model": model}))
                config = ceu.load_config(path)
                self.assertEqual(config, ceu.Config("dummy-id", "dummy-secret"))
                self.assertNotIn("model", vars(config))
                with patch.object(ceu.CEUClient, "models", return_value=[ceu.COURSE_MODEL]):
                    self.assertEqual(ceu.CEUClient(config).course_model(), ceu.COURSE_MODEL)


class ProjectTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()

    def file(self, name, content="example"):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        return path

    def client(self, replies):
        client = ceu.CEUClient(ceu.Config("dummy-id", "dummy-secret"))
        answers = iter(replies)
        def request(route, body=None):
            if route.endswith("/models"):
                return {"data": [{"modelName": ceu.COURSE_MODEL}]}
            answer = next(answers)
            return {"data": {"content": answer if isinstance(answer, str) else json.dumps(answer),
                             "finishReason": "stop"}}
        client.request = Mock(side_effect=request)
        return client

    def payloads(self, client):
        return [json.loads(call.args[1]["messages"][0]["content"][len(ceu.INSTRUCTIONS) + 1:])
                for call in client.request.call_args_list if call.args[0].endswith("/chat")]

    def test_tree_lists_supported_files_without_reading_them(self):
        self.file("README.md")
        self.file("modules/topic/analysis.ipynb")
        self.file("data/raw/hotels.csv")
        self.file("pyproject.toml")
        for name in (".ceu/config.json", ".git/config", ".venv/anything.py", "venv/anything.py",
                     "node_modules/package/index.js", "ceu-api-credentials.txt", "ClientSecret.txt",
                     "nested/PASSWORDS.csv", "fr-invitation-token.txt", "private/notes.md", "grades.csv",
                     "grading/students.csv", "final-exam.md", "AGENTS.md", "CLAUDE.md", "course repo.md",
                     "data/raw/notes.txt", "photo.png", "syllabus.docx"):
            self.file(name, "SENSITIVE_SENTINEL")
        with patch.object(Path, "read_text", side_effect=AssertionError("Tree must not read file contents")):
            project = ceu.project_snapshot(self.root, set())
        names = project["tree"]
        for name in ("README.md", "modules/", "modules/topic/", "modules/topic/analysis.ipynb",
                     "data/", "data/raw/", "data/raw/hotels.csv", "pyproject.toml"):
            self.assertIn(name, names)
        self.assertEqual(set(names), {"README.md", "modules/", "modules/topic/", "modules/topic/analysis.ipynb",
                                      "data/", "data/raw/", "data/raw/hotels.csv", "pyproject.toml", "nested/"})
        self.assertNotIn(str(self.root), json.dumps(project))
        self.assertFalse(project["truncated"])

    def test_tree_excludes_symlinks_and_is_bounded(self):
        with tempfile.TemporaryDirectory() as outside:
            target = Path(outside) / "outside.py"
            target.write_text("not in project")
            (self.root / "link.py").symlink_to(target)
            (self.root / "linked_folder").symlink_to(outside, target_is_directory=True)
            for i in range(5):
                self.file(f"file{i}.py")
            with patch.object(ceu, "MAX_PROJECT_ENTRIES", 3):
                project = ceu.project_snapshot(self.root, set())
        self.assertEqual(len(project["tree"]), 3)
        self.assertTrue(project["truncated"])
        self.assertFalse(any("link" in name for name in project["tree"]))

    def test_credential_names_are_blocked_even_for_explicit_reads_or_writes(self):
        for name in ("ceu-api-credentials.txt", "mySecret.md", "nested/api_key.csv", "ClientID.txt",
                     "fr-invitation-token.txt", "grades.csv", "AGENTS.md"):
            self.file(name, "SENSITIVE_SENTINEL")
            for writing in (False, True):
                with self.subTest(name=name, writing=writing), self.assertRaises(ceu.UserError):
                    ceu.local_path(self.root, name, writing=writing)

    def test_model_reads_real_columns_before_notebook_generation(self):
        self.file("data/raw/hotels.csv", "price,distance_miles,log_price\n80,2.5,4.38\n")
        self.file("README.md", "Notebooks are in modules/topic.")
        self.file("unrequested.py", "UNREQUESTED_CONTENT")
        self.file("modules/topic/README.md", "A module")
        notebook = {"nbformat": 4, "nbformat_minor": 5, "metadata": {}, "cells": [
            {"cell_type": "code", "metadata": {}, "source": ["x = 1\n", "raise RuntimeError('not executed')\n"],
             "execution_count": None, "outputs": []}]}
        final = {"message": "Notebook created", "files": [
            {"path": "modules/topic/new.ipynb", "content": json.dumps(notebook)}]}
        client = self.client([
            {"message": "Inspect data and layout", "read_files": ["data/raw/hotels.csv", "README.md"], "files": []},
            final,
        ])
        shared = set()
        log = []
        reply, context = ceu.generate_with_project(client, self.root, "Create the hotel notebook", shared, [], set(), log.append)
        payloads = self.payloads(client)
        self.assertEqual(len(payloads), 2)
        self.assertEqual(payloads[0]["shared_files"], {})
        self.assertIn("modules/topic/", payloads[0]["project"]["tree"])
        summary = json.loads(payloads[1]["shared_files"]["data/raw/hotels.csv"])
        self.assertIn("distance_miles", [column["name"] for column in summary["columns"]])
        self.assertEqual(shared, {"data/raw/hotels.csv", "README.md"})
        self.assertNotIn("UNREQUESTED_CONTENT", json.dumps(payloads))
        self.assertFalse((self.root / "modules/topic/new.ipynb").exists())
        saved = ceu.apply_files(self.root, reply["files"], lambda _: True, lambda _: None, expected=context)
        self.assertEqual(saved, ["modules/topic/new.ipynb"])
        self.assertTrue(json.loads((self.root / saved[0]).read_text())["cells"][0]["id"])
        self.assertTrue(any("CSV summary" in line for line in log))

    def test_blocked_or_outside_reads_return_errors_without_sending_contents(self):
        self.file("ceu-api-credentials.txt", "NEVER_SEND_CREDENTIALS")
        self.file("excluded.txt", "NEVER_SEND_EXCLUDED")
        reads = ["ceu-api-credentials.txt", "../outside.txt", "/etc/passwd", "excluded.txt"]
        client = self.client([{"message": "read", "read_files": reads, "files": []},
                              {"message": "The files are unavailable", "files": []}])
        _, context = ceu.generate_with_project(client, self.root, "Inspect", set(), [], {"excluded.txt"}, lambda _: None)
        payloads = self.payloads(client)
        self.assertEqual(context, {})
        self.assertEqual(len(payloads[1]["inspection"]["read_errors"]), 4)
        self.assertNotIn("NEVER_SEND", json.dumps(payloads))
        self.assertNotIn("excluded.txt", payloads[0]["project"]["tree"])

    def test_symlink_swap_after_listing_is_rejected(self):
        path = self.file("notes.txt", "original")
        with tempfile.TemporaryDirectory() as outside:
            target = Path(outside) / "outside.txt"
            target.write_text("OUTSIDE_CONTENT")
            client = self.client([])
            def generate(*args, **kwargs):
                if path.is_symlink():
                    return {"message": "Unavailable", "files": []}
                path.unlink()
                path.symlink_to(target)
                return {"message": "read", "read_files": ["notes.txt"], "files": []}
            client.generate = Mock(side_effect=generate)
            _, context = ceu.generate_with_project(client, self.root, "Read notes", set(), [], set(), lambda _: None)
        self.assertEqual(context, {})
        self.assertIn("Symbolic links", client.generate.call_args.kwargs["inspection"]["read_errors"][0]["error"])

    def test_innocently_named_file_with_saved_credentials_is_not_sent(self):
        self.file("notes.txt", 'The saved value is dummy-secret. Do not send it.')
        client = self.client([{"message": "read", "read_files": ["notes.txt"], "files": []},
                              {"message": "Cannot read that file", "files": []}])
        output = []
        _, context = ceu.generate_with_project(client, self.root, "Read notes", set(), [], set(), output.append)
        self.assertEqual(context, {})
        self.assertNotIn("dummy-secret", json.dumps(self.payloads(client)))
        self.assertNotIn("dummy-secret", str(output))
        self.assertIn("saved CEU credentials", self.payloads(client)[1]["inspection"]["read_errors"][0]["error"])

    def test_explicit_credential_content_is_blocked_before_any_api_request(self):
        for content in ("dummy-secret", 'dummy-id', 'text with a secret: ab"cd'):
            client = self.client([])
            if 'ab"cd' in content:
                client.config.secret = 'ab"cd'
                content = json.dumps({"secret": 'ab"cd'})
            with self.subTest(content=content), self.assertRaisesRegex(ceu.UserError, "saved CEU credentials"):
                client.generate("Explain", {"notes.txt": content}, [])
            client.request.assert_not_called()

    def test_unreadable_file_does_not_crash_the_inspection_loop(self):
        self.file("large.txt", "x" * (ceu.MAX_CONTEXT + 1))
        client = self.client([{"message": "read", "read_files": ["large.txt"], "files": []},
                              {"message": "Please provide a smaller file", "files": []}])
        reply, context = ceu.generate_with_project(client, self.root, "Inspect", set(), [], set(), lambda _: None)
        self.assertEqual(reply["files"], [])
        self.assertEqual(context, {})
        self.assertTrue(self.payloads(client)[1]["inspection"]["read_errors"])

    def test_repeated_reads_stop_at_the_model_call_limit(self):
        self.file("notes.txt", "Notes")
        read = {"message": "read", "read_files": ["notes.txt"], "files": []}
        client = self.client([read] * (ceu.MAX_READ_ROUNDS + 1))
        with self.assertRaisesRegex(ceu.UserError, "inspection limit"):
            ceu.generate_with_project(client, self.root, "Inspect", set(), [], set(), lambda _: None)
        payloads = self.payloads(client)
        self.assertEqual(len(payloads), 4)
        self.assertEqual([p["inspection"]["read_rounds_remaining"] for p in payloads], [3, 2, 1, 0])
        self.assertEqual(len(list(self.root.iterdir())), 1)

    def test_invalid_notebook_is_corrected_once_before_chat_saves_anything(self):
        self.file("data/raw/hotels.csv", "price,distance_miles\n80,2.5\n")
        name = "modules/topic/new.ipynb"
        notebook = {"nbformat": 4, "nbformat_minor": 5, "metadata": {}, "cells": [
            {"cell_type": "code", "metadata": {}, "source": ["raise RuntimeError('not executed')\n"],
             "execution_count": None, "outputs": []}]}
        invalid = {"message": "Created", "files": [{"path": name, "content": "not JSON"}]}
        corrected = {"message": "Corrected", "files": [{"path": name, "content": json.dumps(notebook)}]}
        client = self.client([
            {"message": "Inspect", "read_files": ["data/raw/hotels.csv"], "files": []},
            invalid, corrected,
        ])
        inputs = iter(["Create the hotel notebook", "/quit"])
        with contextlib.redirect_stdout(io.StringIO()) as output:
            ceu.run_chat(client, self.root, lambda _: next(inputs))
        payloads = self.payloads(client)
        self.assertEqual(len(payloads), 3)
        self.assertEqual({p["request"] for p in payloads}, {"Create the hotel notebook"})
        self.assertNotIn("source_correction", payloads[1]["inspection"])
        correction = payloads[2]["inspection"]["source_correction"]
        self.assertEqual(correction["previous_response"], invalid)
        self.assertIn("JSON at line 1", correction["error"])
        self.assertIn("data/raw/hotels.csv", payloads[2]["shared_files"])
        saved = json.loads((self.root / name).read_text())
        self.assertTrue(saved["cells"][0]["id"])
        self.assertEqual(saved["cells"][0]["outputs"], [])
        self.assertFalse((self.root / ".ceu").exists())
        self.assertIn("correct the source once", output.getvalue())

    def test_second_invalid_response_stops_without_saving_a_valid_sibling_file(self):
        invalid = {"message": "Done", "files": [{"path": "valid.py", "content": "x = 1\n"},
                                                 {"path": "bad.ipynb", "content": "not JSON"}]}
        client = self.client([invalid, invalid])
        with self.assertRaises(ceu.InvalidSourceError):
            ceu.generate_with_project(client, self.root, "Create", set(), [], set(), lambda _: None)
        self.assertEqual(len(self.payloads(client)), 2)
        self.assertEqual(list(self.root.iterdir()), [])

    def test_malformed_reply_is_corrected_before_editing_shared_notebook(self):
        name = "modules/topic/analysis.ipynb"
        old = ceu.notebook_content({"cells": [{"cell_type": "code", "source": "x = 1"}]})
        path = self.file(name, old)
        malformed = '{"message": "PRIVATE_REPLY_SENTINEL", "files": [}'
        corrected = {"message": "Updated", "files": [
            {"path": name, "content": {"cells": [{"cell_type": "code", "source": "x = 2"}]}}]}
        client = self.client([malformed, corrected])
        respond = client.request.side_effect
        def check_original(route, body=None):
            self.assertEqual(path.read_text(), old)
            self.assertFalse((self.root / ".ceu").exists())
            return respond(route, body)
        client.request.side_effect = check_original
        prompt = "Revise the model in modules/topic/analysis.ipynb"
        inputs = iter(["/add " + name, prompt, "/quit"])
        with contextlib.redirect_stdout(io.StringIO()) as output:
            ceu.run_chat(client, self.root, lambda _: next(inputs))
        payloads = self.payloads(client)
        self.assertEqual(len(payloads), 2)
        self.assertEqual([p["request"] for p in payloads], [prompt, prompt])
        self.assertEqual(payloads[1]["shared_files"][name], old)
        correction = payloads[1]["inspection"]["response_correction"]
        self.assertEqual(correction["previous_reply"], malformed)
        self.assertIn("line 1, column", correction["error"])
        self.assertIn("correct the reply format once", output.getvalue())
        self.assertNotIn("PRIVATE_REPLY_SENTINEL", output.getvalue())
        self.assertIn("x = 2", path.read_text())
        backups = list((self.root / ".ceu/backups").rglob("analysis.ipynb"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(), old)

    def test_second_malformed_reply_stops_without_saving_or_printing_response(self):
        client = self.client(["PRIVATE_REPLY_SENTINEL", "PRIVATE_REPLY_SENTINEL"])
        logs = []
        with self.assertRaisesRegex(ceu.UserError, "No further automatic correction") as caught:
            ceu.generate_with_project(client, self.root, "Create", set(), [], set(), logs.append)
        self.assertEqual(len(self.payloads(client)), 2)
        self.assertNotIn("PRIVATE_REPLY_SENTINEL", str(caught.exception) + str(logs))
        self.assertEqual(list(self.root.iterdir()), [])

    def test_reply_and_source_errors_share_one_correction_budget(self):
        bad_source = {"message": "Done", "files": [{"path": "bad.py", "content": "def !"}]}
        for replies in (["not JSON", bad_source], [bad_source, "not JSON"]):
            client = self.client(replies)
            with self.subTest(replies=replies), self.assertRaises(ceu.UserError):
                ceu.generate_with_project(client, self.root, "Create", set(), [], set(), lambda _: None)
            self.assertEqual(len(self.payloads(client)), 2)
        self.assertEqual(list(self.root.iterdir()), [])

    def test_format_correction_can_recover_a_read_request_then_finish_normally(self):
        self.file("notes.txt", "Class notes")
        client = self.client(["not JSON", {"message": "Read", "read_files": ["notes.txt"], "files": []},
                              {"message": "Done", "files": []}])
        reply, context = ceu.generate_with_project(client, self.root, "Explain notes", set(), [], set(), lambda _: None)
        payloads = self.payloads(client)
        self.assertEqual(len(payloads), 3)
        self.assertEqual(context, {"notes.txt": "Class notes"})
        self.assertNotIn("response_correction", payloads[2]["inspection"])
        self.assertEqual(reply["message"], "Done")

    def test_reply_correction_does_not_extend_four_call_limit(self):
        self.file("notes.txt", "Class notes")
        read = {"message": "Read", "read_files": ["notes.txt"], "files": []}
        for replies in ([read, read, read, "bad JSON"], [read, read, "bad JSON", "bad JSON"]):
            client = self.client(replies)
            with self.subTest(replies=replies), self.assertRaises(ceu.UserError):
                ceu.generate_with_project(client, self.root, "Explain", set(), [], set(), lambda _: None)
            self.assertEqual(len(self.payloads(client)), 4)

    def test_malformed_reply_containing_credentials_is_not_sent_for_correction(self):
        client = self.client(["bad JSON dummy-secret"])
        with self.assertRaisesRegex(ceu.UserError, "saved CEU credentials"):
            ceu.generate_with_project(client, self.root, "Create", set(), [], set(), lambda _: None)
        self.assertEqual(len(self.payloads(client)), 1)
        self.assertNotIn("dummy-secret", json.dumps(self.payloads(client)))

    def test_corrected_reply_still_cannot_write_unsafe_paths(self):
        client = self.client(["bad JSON", {"message": "Write", "files": [
            {"path": "../outside.py", "content": "x = 1"}]}])
        with self.assertRaisesRegex(ceu.UserError, "Invalid project file path"):
            ceu.generate_with_project(client, self.root, "Create", set(), [], set(), lambda _: None)
        self.assertEqual(list(self.root.iterdir()), [])

    def test_unsupported_action_is_not_retried_as_a_format_error(self):
        client = self.client([{"message": "Run", "files": [], "command": "something"}])
        with self.assertRaisesRegex(ceu.UserError, "unsupported action"):
            ceu.generate_with_project(client, self.root, "Create", set(), [], set(), lambda _: None)
        self.assertEqual(len(self.payloads(client)), 1)

    def test_chat_renames_automatically_reports_paths_and_removes_deleted_context(self):
        old = self.file("old.py", "x = 1\n")
        reply = {"message": "Renamed the file.", "files": [{"path": "new.py", "content": "x = 1\n"}],
                 "delete_files": ["old.py"]}
        client = self.client([reply, {"message": "Follow-up", "files": []}])
        inputs = iter(["/add old.py", "Rename old.py to new.py", "Explain", "/quit"])
        prompts = []
        def ask(prompt):
            prompts.append(prompt)
            return next(inputs)
        with contextlib.redirect_stdout(io.StringIO()) as output:
            ceu.run_chat(client, self.root, ask)
        self.assertTrue(all(prompt == "You> " for prompt in prompts))
        self.assertFalse(old.exists())
        self.assertEqual((self.root / "new.py").read_text(), "x = 1\n")
        self.assertIn("Created new.py", output.getvalue())
        self.assertIn("Deleted old.py", output.getvalue())
        self.assertIn("Originals saved in .ceu/backups/", output.getvalue())
        followup = self.payloads(client)[1]
        self.assertNotIn("old.py", followup["shared_files"])
        self.assertIn("new.py", followup["shared_files"])
        self.assertEqual(followup["conversation"][-1]["deleted_files"], ["old.py"])

    def test_source_correction_cannot_add_a_deletion(self):
        path = self.file("keep.py", "x = 1")
        client = self.client([
            {"message": "Write", "files": [{"path": "bad.py", "content": "def !"}]},
            {"message": "Correct", "files": [{"path": "bad.py", "content": "x = 1"}],
             "delete_files": ["keep.py"]},
        ])
        with self.assertRaisesRegex(ceu.UserError, "different destination"):
            ceu.generate_with_project(client, self.root, "Create", set(), [], set(), lambda _: None)
        self.assertEqual(path.read_text(), "x = 1")

    def test_source_correction_does_not_exceed_four_calls(self):
        self.file("notes.txt", "Notes")
        read = {"message": "Read", "read_files": ["notes.txt"], "files": []}
        invalid = {"message": "Done", "files": [{"path": "bad.py", "content": "def !"}]}
        for responses in ([read, read, read, invalid], [read, read, invalid, invalid]):
            client = self.client(responses)
            with self.subTest(responses=responses), self.assertRaises(ceu.InvalidSourceError):
                ceu.generate_with_project(client, self.root, "Create", set(), [], set(), lambda _: None)
            self.assertEqual(len(self.payloads(client)), 4)
            self.assertFalse((self.root / "bad.py").exists())

    def test_unsafe_destination_does_not_trigger_source_correction(self):
        reply = {"message": "Done", "files": [{"path": "bad.py", "content": "def !"},
                                               {"path": "../outside.py", "content": "x = 1"}]}
        client = self.client([reply])
        with self.assertRaises(ceu.UserError):
            ceu.generate_with_project(client, self.root, "Create", set(), [], set(), lambda _: None)
        self.assertEqual(len(self.payloads(client)), 1)
        self.assertEqual(list(self.root.iterdir()), [])

    def test_source_correction_cannot_read_more_files_or_change_destinations(self):
        invalid = {"message": "Done", "files": [{"path": "bad.py", "content": "def !"}]}
        for second in ({"message": "Read", "read_files": ["notes.txt"], "files": []},
                       {"message": "Write", "files": [{"path": "other.py", "content": "x = 1"}]}):
            client = self.client([invalid, second])
            with self.subTest(second=second), self.assertRaises(ceu.UserError):
                ceu.generate_with_project(client, self.root, "Create", set(), [], set(), lambda _: None)
            self.assertEqual(len(self.payloads(client)), 2)
        self.assertEqual(list(self.root.iterdir()), [])

    def test_rejected_response_with_credentials_is_not_sent_for_correction(self):
        invalid = {"message": "Done", "files": [{"path": "bad.py", "content": "dummy-secret ="}]}
        client = self.client([invalid])
        with self.assertRaisesRegex(ceu.UserError, "saved CEU credentials"):
            ceu.generate_with_project(client, self.root, "Create", set(), [], set(), lambda _: None)
        self.assertEqual(len(self.payloads(client)), 1)
        self.assertNotIn("dummy-secret", json.dumps(self.payloads(client)))

    def test_read_protocol_rejects_writes_shell_commands_and_bad_arguments(self):
        for response in (
            {"message": "run", "files": [], "command": "echo no"},
            {"message": "read", "read_files": "notes.txt", "files": []},
            {"message": "read", "read_files": [42], "files": []},
            {"message": "read", "read_files": ["notes.txt"] * 5, "files": []},
            {"message": "read and write", "read_files": ["notes.txt"],
             "files": [{"path": "new.py", "content": "x = 1"}]},
        ):
            with self.subTest(response=response), self.assertRaises(ceu.UserError):
                ceu.parse_reply(json.dumps(response))

    def test_drop_exclusions_survive_new_and_add_reenables_a_file(self):
        self.file("notes.txt", "Notes")
        self.file("data/raw/hotels.csv", "price\n80\n")
        client = self.client([{"message": "Done", "files": []}] * 3)
        inputs = iter(["/drop notes.txt", "/drop data", "/new", "first",
                       "/add notes.txt", "second", "/new", "third", "/quit"])
        with contextlib.redirect_stdout(io.StringIO()):
            ceu.run_chat(client, self.root, lambda _: next(inputs))
        first, second, third = self.payloads(client)
        self.assertNotIn("notes.txt", first["project"]["tree"])
        self.assertIn("notes.txt", second["project"]["tree"])
        self.assertEqual(second["shared_files"], {"notes.txt": "Notes"})
        self.assertEqual(third["shared_files"], {})
        for payload in (first, second, third):
            self.assertNotIn("data/", payload["project"]["tree"])
            self.assertNotIn("data/raw/hotels.csv", payload["shared_files"])

    def test_inspected_source_still_has_overwrite_and_concurrent_edit_protection(self):
        path = self.file("analysis.py", "x = 1\n")
        client = self.client([{"message": "read", "read_files": ["analysis.py"], "files": []},
                              {"message": "revise", "files": [{"path": "analysis.py", "content": "x = 2\n"}]}])
        reply, context = ceu.generate_with_project(client, self.root, "Revise", set(), [], set(), lambda _: None)
        self.assertEqual(ceu.apply_files(self.root, reply["files"], lambda _: False, lambda _: None, context), [])
        self.assertEqual(path.read_text(), "x = 1\n")
        path.write_text("x = 99\n")
        with self.assertRaisesRegex(ceu.UserError, "changed in your editor"):
            ceu.apply_files(self.root, reply["files"], lambda _: True, lambda _: None, context)

    def test_startup_refuses_to_scan_an_unrelated_working_folder(self):
        with patch.object(sys, "argv", ["ceu-ai.py"]), patch.object(sys.stdin, "isatty", return_value=True), \
                patch.object(Path, "cwd", return_value=self.root), patch.object(ceu, "load_config") as load, \
                patch.object(ceu, "run_chat") as chat, contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(ceu.main(), 1)
        load.assert_not_called()
        chat.assert_not_called()

    def test_course_catalogue_reads_only_approved_schemas_not_values_or_other_files(self):
        self.file("harness.md", "Keep each step in a separate cell.")
        self.file("data/raw/hotels_course.csv", "price,distance_miles,label\n80,2.5,ROW_VALUE_SENTINEL\n")
        self.file("data/raw/unapproved.csv", "UNAPPROVED_HEADER\nUNAPPROVED_ROW\n")
        self.file("modules/topic/reference.ipynb", "REFERENCE_SENTINEL")
        self.file("ceu-api-credentials.txt", "CREDENTIAL_SENTINEL")
        course = ceu.course_context(self.root, set())
        self.assertEqual(course["guide"]["status"], "available")
        self.assertEqual(course["guide"]["content"], "Keep each step in a separate cell.")
        self.assertEqual([item["path"] for item in course["datasets"]], list(ceu.COURSE_DATASETS))
        hotels = course["datasets"][0]
        self.assertEqual(hotels["status"], "available")
        self.assertEqual(hotels["row_count"], 1)
        self.assertEqual(hotels["columns"][1], {"name": "distance_miles", "dtype": "float64"})
        self.assertNotIn("preview", hotels)
        self.assertNotIn("SENTINEL", json.dumps(course))
        self.assertNotIn("UNAPPROVED", json.dumps(course))
        self.assertTrue(all(item["status"] == "missing" for item in course["datasets"][1:]))

    def test_course_catalogue_refreshes_columns_counts_and_types(self):
        path = self.file("data/raw/hotels_course.csv", "price\n80\n")
        before = ceu.course_context(self.root, set())["datasets"][0]
        path.write_text("price,new_distance\n80.5,2.5\n90.5,3.5\n")
        after = ceu.course_context(self.root, set())["datasets"][0]
        self.assertEqual(before["columns"], [{"name": "price", "dtype": "int64"}])
        self.assertEqual(after["columns"], [{"name": "price", "dtype": "float64"},
                                            {"name": "new_distance", "dtype": "float64"}])
        self.assertEqual(after["row_count"], 2)

    def test_course_context_respects_file_folder_and_guide_exclusions(self):
        self.file("harness.md", "GUIDE_SENTINEL")
        self.file("data/raw/hotels_course.csv", "HIDDEN_HEADER\n80\n")
        course = ceu.course_context(self.root, {"HARNESS.MD", "DATA/RAW/hotels_course.csv"})
        self.assertEqual(course["guide"], {"path": "harness.md", "status": "excluded"})
        self.assertNotIn("data/raw/hotels_course.csv", json.dumps(course))
        self.assertNotIn("HIDDEN_HEADER", json.dumps(course))
        self.assertEqual(ceu.course_context(self.root, {"data"})["datasets"], [])

    def test_course_catalogue_reports_unavailable_data_without_guessing(self):
        self.file("data/raw/hotels_course.csv", "")
        self.file("data/raw/share_health_course.csv", "price\n80\n")
        with tempfile.TemporaryDirectory() as outside:
            target = Path(outside) / "data.csv"
            target.write_text("OUTSIDE_HEADER\n99\n")
            (self.root / "data/raw/wms_course.csv").symlink_to(target)
            course = ceu.course_context(self.root, set())
        entries = {item["path"]: item for item in course["datasets"]}
        self.assertEqual(entries["data/raw/hotels_course.csv"]["status"], "unavailable")
        self.assertEqual(entries["data/raw/share_health_course.csv"]["status"], "available")
        self.assertEqual(entries["data/raw/airbnb_hackney_course.csv"]["status"], "missing")
        self.assertEqual(entries["data/raw/wms_course.csv"]["status"], "unavailable")
        self.assertNotIn("OUTSIDE_HEADER", json.dumps(course))
        with patch.object(ceu, "MAX_CSV_BYTES", 1):
            limited = ceu.course_context(self.root, set())["datasets"][1]
        self.assertEqual(limited["status"], "unavailable")
        self.assertIn("CSV limit", limited["reason"])

    def test_guide_is_bounded_utf8_and_not_a_symlink(self):
        self.assertEqual(ceu.course_context(self.root, set())["guide"]["status"], "missing")
        path = self.file("harness.md", "x" * (ceu.MAX_HARNESS_BYTES + 1))
        with self.assertRaisesRegex(ceu.UserError, "16 KB"):
            ceu.course_context(self.root, set())
        path.write_bytes(b"\xff")
        with self.assertRaisesRegex(ceu.UserError, "UTF-8"):
            ceu.course_context(self.root, set())
        path.unlink()
        with tempfile.TemporaryDirectory() as outside:
            target = Path(outside) / "guide.md"
            target.write_text("OUTSIDE_GUIDE")
            path.symlink_to(target)
            with self.assertRaisesRegex(ceu.UserError, "Symbolic links"):
                ceu.course_context(self.root, set())

    def test_guide_and_catalogue_accompany_inspection_and_source_correction(self):
        self.file("harness.md", "TEACHING_GUIDE")
        self.file("data/raw/hotels_course.csv", "price,distance_miles\n80,2.5\n")
        client = self.client([
            {"message": "Inspect", "read_files": ["data/raw/hotels_course.csv"], "files": []},
            {"message": "Write", "files": [{"path": "analysis.py", "content": "def !"}]},
            {"message": "Correct", "files": [{"path": "analysis.py", "content": "x = 1"}]},
        ])
        ceu.generate_with_project(client, self.root, "Create", {"harness.md"}, [], set(), lambda _: None)
        payloads = self.payloads(client)
        self.assertEqual(len(payloads), 3)
        for payload in payloads:
            self.assertEqual(payload["course"], payloads[0]["course"])
            self.assertEqual(payload["course"]["guide"]["content"], "TEACHING_GUIDE")
            self.assertEqual(payload["course"]["datasets"][0]["columns"][1]["name"], "distance_miles")
            self.assertNotIn("harness.md", payload["shared_files"])
        self.assertNotIn("preview", payloads[0]["course"]["datasets"][0])
        self.assertIn("preview", json.loads(payloads[1]["shared_files"]["data/raw/hotels_course.csv"]))

    def test_new_and_drop_keep_their_meaning_for_automatic_context(self):
        guide = self.file("harness.md", "ORIGINAL_GUIDE")
        dataset = self.file("data/raw/hotels_course.csv", "price\n80\n")
        client = self.client([{"message": "Done", "files": []}] * 4)
        inputs = iter(["first", "/new", "second", "/drop harness.md", "/drop data", "third",
                       "/add harness.md", "fourth", "/quit"])
        def ask(_):
            value = next(inputs)
            if value == "second":
                guide.write_text("REVISED_GUIDE")
                dataset.write_text("new_column\n1\n2\n")
            return value
        with contextlib.redirect_stdout(io.StringIO()):
            ceu.run_chat(client, self.root, ask)
        first, second, third, fourth = self.payloads(client)
        self.assertEqual(first["course"]["guide"]["content"], "ORIGINAL_GUIDE")
        self.assertEqual(second["course"]["guide"]["content"], "REVISED_GUIDE")
        self.assertEqual(second["course"]["datasets"][0]["columns"][0]["name"], "new_column")
        self.assertEqual(second["conversation"], [])
        self.assertEqual(third["course"]["guide"]["status"], "excluded")
        self.assertEqual(third["course"]["datasets"], [])
        self.assertEqual(fourth["course"]["guide"]["content"], "REVISED_GUIDE")
        self.assertEqual(fourth["course"]["datasets"], [])

    def test_context_preview_does_not_send_a_chat_request(self):
        self.file("harness.md", "Visible guide")
        self.file("data/raw/hotels_course.csv", "price\n987654\n")
        client = self.client([])
        inputs = iter(["/context", "/quit"])
        with contextlib.redirect_stdout(io.StringIO()) as output:
            ceu.run_chat(client, self.root, lambda _: next(inputs))
        self.assertEqual(self.payloads(client), [])
        self.assertIn("Visible guide", output.getvalue())
        self.assertNotIn("987654", output.getvalue())
        self.assertIn("Preview only", output.getvalue())

    def test_credentials_in_automatic_context_never_reach_the_api_or_preview(self):
        guide = self.file("harness.md", "dummy-secret")
        client = self.client([])
        with self.assertRaisesRegex(ceu.UserError, "saved CEU credentials"):
            ceu.generate_with_project(client, self.root, "Create", set(), [], set(), lambda _: None)
        client.request.assert_not_called()
        inputs = iter(["/context", "/quit"])
        with contextlib.redirect_stdout(io.StringIO()) as output:
            ceu.run_chat(client, self.root, lambda _: next(inputs))
        self.assertNotIn("dummy-secret", output.getvalue())
        guide.write_text("Safe guide")
        self.file("data/raw/hotels_course.csv", "dummy-secret\n1\n")
        client = self.client([])
        with self.assertRaisesRegex(ceu.UserError, "saved CEU credentials"):
            ceu.generate_with_project(client, self.root, "Create", set(), [], set(), lambda _: None)
        client.request.assert_not_called()

    def test_automatic_course_context_counts_towards_request_limit(self):
        self.file("harness.md", "A guide " * 100)
        client = self.client([])
        with patch.object(ceu, "MAX_CONTEXT", 50), self.assertRaisesRegex(ceu.UserError, "too large"):
            ceu.generate_with_project(client, self.root, "Create", set(), [], set(), lambda _: None)
        client.request.assert_not_called()

    def test_model_cannot_overwrite_guide_even_with_confirmation(self):
        path = self.file("harness.md", "Keep me")
        with self.assertRaises(ceu.UserError):
            ceu.apply_files(self.root, [{"path": "harness.md", "content": "Replace me"}], lambda _: True)
        self.assertEqual(path.read_text(), "Keep me")

    def test_model_can_request_existing_notebooks_and_builder_without_manual_sharing(self):
        names = ["modules/topic/reference.ipynb", "scripts/build_notebooks.py"]
        for name in names:
            self.file(name, "REFERENCE_CONTENT_SENTINEL")
        client = self.client([{"message": "Read", "read_files": names, "files": []},
                              {"message": "Compared", "files": []}])
        _, context = ceu.generate_with_project(client, self.root, "Compare the reference and its builder",
                                             set(), [], set(), lambda _: None)
        payloads = self.payloads(client)
        self.assertEqual(payloads[0]["shared_files"], {})
        self.assertNotIn("manual_share_only", payloads[0]["project"])
        self.assertEqual(payloads[1]["inspection"]["read_errors"], [])
        self.assertEqual(context, {name: "REFERENCE_CONTENT_SENTINEL" for name in names})
        self.assertEqual(payloads[1]["shared_files"], context)
        client = self.client([{"message": "Compare", "files": []}])
        inputs = iter(["/add " + names[0], "Compare my result", "/quit"])
        with contextlib.redirect_stdout(io.StringIO()):
            ceu.run_chat(client, self.root, lambda _: next(inputs))
        payload = self.payloads(client)[0]
        self.assertEqual(payload["shared_files"][names[0]], "REFERENCE_CONTENT_SENTINEL")
        self.assertNotIn(names[1], payload["shared_files"])

    def test_model_reads_then_edits_notebook_and_keeps_backup(self):
        name = "modules/topic/analysis.ipynb"
        old = ceu.notebook_content({"cells": [{"cell_type": "code", "source": "x = 1"}]})
        path = self.file(name, old)
        client = self.client([{"message": "Inspect notebook", "read_files": [str(path)], "files": []},
            {"message": "Updated", "files": [
            {"path": name, "content": {"cells": [{"cell_type": "code", "source": "x = 2"}]}}]},
            {"message": "Explanation without an unnecessary empty files field"}])
        prompt = f"I want to change the example in {path}. Set x to 2."
        inputs = iter([prompt, "Explain the change", "/quit"])
        with contextlib.redirect_stdout(io.StringIO()) as output:
            ceu.run_chat(client, self.root, lambda _: next(inputs))
        first, inspected, followup = self.payloads(client)
        self.assertNotIn(name, first["shared_files"])
        self.assertEqual(inspected["shared_files"][name], old)
        self.assertIn("x = 2", followup["shared_files"][name])
        self.assertIn("Reading " + name, output.getvalue())
        self.assertIn("Updated " + name, output.getvalue())
        self.assertNotIn("correct the reply", output.getvalue())
        backups = list((self.root / ".ceu/backups").rglob("analysis.ipynb"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(), old)

    def test_read_mechanism_has_no_prompt_position_or_wording_requirement(self):
        name = "modules/topic/my analysis.ipynb"
        path = self.file(name, "NOTEBOOK_SENTINEL")
        # These mocks test the app's read mechanism, not the model's language understanding.
        # Real-model probes cover whether it chooses the appropriate read action.
        for prompt in (f'Read "{name}". Explain it.',
                       f'First consider the analysis, then read "{name}" and explain it.',
                       f'Please explain the regression in "{name}".',
                       f'Use a quadratic model in "{path}".',
                       f'I have a question.\nThe notebook is `{name}`. What does it do?'):
            for requested in (name, str(path)):
                with self.subTest(prompt=prompt, requested=requested):
                    client = self.client([{"message": "Inspect", "read_files": [requested], "files": []},
                                          {"message": "Explained", "files": []}])
                    _, context = ceu.generate_with_project(client, self.root, prompt, set(), [], set(), lambda _: None)
                    self.assertEqual(context[name], "NOTEBOOK_SENTINEL")
                    self.assertEqual(self.payloads(client)[0]["shared_files"], {})
                    self.assertEqual(self.payloads(client)[1]["inspection"]["read_errors"], [])
                    self.assertEqual(self.payloads(client)[0]["request"], prompt)

    def test_prompt_text_is_never_parsed_into_automatic_file_reads(self):
        name = "reference.ipynb"
        self.file(name, "REFERENCE_CONTENT_SENTINEL")
        for prompt in (f"Read {name}", f"Do not read {name}",
                       f'Explain the instruction "Read {name}"', f'"Read {name}"'):
            with self.subTest(prompt=prompt):
                client = self.client([{"message": "Explanation", "files": []}])
                _, context = ceu.generate_with_project(client, self.root, prompt, set(), [], set(), lambda _: None)
                self.assertNotIn(name, context)
                self.assertNotIn("REFERENCE_CONTENT_SENTINEL", json.dumps(self.payloads(client)))

    def test_read_protections_apply_even_when_model_requests_the_path(self):
        self.file("analysis.ipynb", "NEVER_SHARE")
        self.file(".hidden.ipynb", "NEVER_SHARE")
        self.file("credentials.txt", "NEVER_SHARE")
        self.file("private/analysis.ipynb", "NEVER_SHARE")
        self.file("notes.txt", "dummy-secret")
        with tempfile.TemporaryDirectory() as outside:
            target = Path(outside) / "external.ipynb"
            target.write_text("NEVER_SHARE")
            (self.root / "link.ipynb").symlink_to(target)
            cases = [(str(target), set()), ("link.ipynb", set()), (".hidden.ipynb", set()),
                     ("credentials.txt", set()), ("private/analysis.ipynb", set()),
                     ("missing.ipynb", set()), ("../external.ipynb", set()),
                     (str(self.root / ".." / "external.ipynb"), set()),
                     ("analysis.ipynb", {"analysis.ipynb"}),
                     (str(self.root / "analysis.ipynb"), {"analysis.ipynb"}), ("notes.txt", set())]
            for name, excluded in cases:
                with self.subTest(name=name):
                    client = self.client([{"message": "Read", "read_files": [name], "files": []},
                                          {"message": "Cannot read that file", "files": []}])
                    _, context = ceu.generate_with_project(client, self.root, "Inspect this project",
                                                         set(), [], excluded, lambda _: None)
                    self.assertEqual(context, {})
                    payloads = self.payloads(client)
                    self.assertEqual(len(payloads[1]["inspection"]["read_errors"]), 1)
                    self.assertNotIn("NEVER_SHARE", json.dumps(payloads))
                    self.assertNotIn("dummy-secret", json.dumps(payloads))

    def test_model_csv_read_still_sends_only_summary_and_preview(self):
        name = "data/raw/hotels_course.csv"
        self.file(name, "price\n80\n90\n100\n110\n120\n987654321\n")
        client = self.client([{"message": "Inspect", "read_files": [name], "files": []},
                              {"message": "Explained"}])
        _, context = ceu.generate_with_project(client, self.root, f"Read {name}", set(), [], set(), lambda _: None)
        self.assertEqual(json.loads(context[name])["row_count"], 6)
        self.assertEqual(len(json.loads(context[name])["preview"]), 5)
        self.assertNotIn("987654321", json.dumps(self.payloads(client)))

    def test_unshared_existing_notebook_cannot_be_blindly_overwritten(self):
        name = "reference.ipynb"
        path = self.file(name, "Keep me")
        client = self.client([{"message": "Updated", "files": [
            {"path": name, "content": {"cells": [{"cell_type": "code", "source": "x = 2"}]}}]}])
        with self.assertRaisesRegex(ceu.UserError, "without reading it first"):
            ceu.generate_with_project(client, self.root, "Make the analysis quadratic", set(), [], set(), lambda _: None)
        self.assertEqual(path.read_text(), "Keep me")

    def test_add_and_drop_accept_absolute_paths_within_project(self):
        name = "analysis.ipynb"
        path = self.file(name, "NOTEBOOK_SENTINEL")
        client = self.client([{"message": "Shared"}, {"message": "Excluded"}])
        inputs = iter([f'/add "{path}"', "Explain", f'/drop "{path}"', "Explain", "/quit"])
        with contextlib.redirect_stdout(io.StringIO()):
            ceu.run_chat(client, self.root, lambda _: next(inputs))
        first, second = self.payloads(client)
        self.assertIn(name, first["shared_files"])
        self.assertNotIn(name, second["shared_files"])
        self.assertNotIn(name, second["project"]["tree"])

    def test_created_notebook_remains_context_without_manual_add(self):
        notebook = {"nbformat": 4, "nbformat_minor": 5, "metadata": {}, "cells": [
            {"cell_type": "code", "metadata": {}, "source": "x = 1", "execution_count": None, "outputs": []}]}
        name = "modules/topic/new.ipynb"
        client = self.client([{"message": "Created", "files": [{"path": name, "content": json.dumps(notebook)}]},
                              {"message": "Explain", "files": []}])
        inputs = iter(["Create a notebook", "Explain the notebook", "/quit"])
        with contextlib.redirect_stdout(io.StringIO()):
            ceu.run_chat(client, self.root, lambda _: next(inputs))
        payload = self.payloads(client)[1]
        self.assertIn(name, payload["shared_files"])

    def test_created_notebook_saved_outputs_are_refreshed_for_interpretation(self):
        name = "modules/topic/analysis.ipynb"
        notebook = {"cells": [{"cell_type": "code", "source": "print('example output')"}]}
        client = self.client([
            {"message": "Created", "files": [{"path": name, "content": notebook}]},
            {"message": "Interpretation of the saved text result", "files": []},
        ])
        inputs = iter(["Create a notebook", f"Interpret the saved output in {name}. Do not edit it.", "/quit"])
        saved = []
        def ask(_):
            prompt = next(inputs)
            if prompt.startswith("Interpret"):
                # Simulate VS Code saving execution results between chat requests.
                path = self.root / name
                executed = json.loads(path.read_text())
                executed["cells"][0]["execution_count"] = 1
                executed["cells"][0]["outputs"] = [{"output_type": "stream", "name": "stdout",
                                                   "text": "SAVED_RESULT_SENTINEL\n"}]
                saved.append(json.dumps(executed))
                path.write_text(saved[0])
            return prompt
        with contextlib.redirect_stdout(io.StringIO()):
            ceu.run_chat(client, self.root, ask)
        first, followup = self.payloads(client)
        self.assertNotIn(name, first["shared_files"])
        self.assertEqual(followup["shared_files"][name], saved[0])
        self.assertIn("SAVED_RESULT_SENTINEL", followup["shared_files"][name])
        self.assertEqual((self.root / name).read_text(), saved[0])
        self.assertFalse((self.root / ".ceu/backups").exists())

    def test_shipped_guide_and_allowlist_match_prepared_course_datasets(self):
        guide = (ROOT / "harness.md").read_text()
        source = ast.parse((ROOT / "scripts/fetch_data.py").read_text())
        outputs = {"data/raw/" + call.args[0].value for call in ast.walk(source)
                   if isinstance(call, ast.Call) and isinstance(call.func, ast.Name)
                   and call.func.id == "write_dataset"}
        self.assertEqual(set(ceu.COURSE_DATASETS), outputs)
        for name in ceu.COURSE_DATASETS:
            self.assertIn(Path(name).name, guide)
        for line in guide.splitlines():
            if line.startswith("| ") and "`modules/" in line:
                folder = line.split("`")[1]
                dataset = line.split("`")[3]
                self.assertTrue((ROOT / folder).is_dir())
                self.assertIn(dataset, (ROOT / folder / "README.md").read_text())


class ProtocolTests(unittest.TestCase):
    def test_renamed_app_preserves_credentials_location_and_self_protection(self):
        self.assertEqual(MODULE.name, "ceu-ai.py")
        self.assertEqual(ceu.CONFIG_PATH, MODULE.resolve().parent / ".ceu/config.json")
        self.assertIn(MODULE.name, ceu.PROTECTED_NAMES)

    def client(self, response, *, models=None):
        opener = Mock()
        if models is None:
            models = {"data": [{"modelName": ceu.COURSE_MODEL}]}
        def respond(request, **kwargs):
            result = models if request.full_url.endswith("/models") else response
            return io.BytesIO(json.dumps(result).encode())
        opener.open.side_effect = respond
        return ceu.CEUClient(ceu.Config("dummy-id", "dummy-secret"), opener), opener

    def test_model_discovery_contract(self):
        client, opener = self.client({}, models={"data": [{"modelName": "test-model"}]})
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
        self.assertEqual(body["model"], ceu.COURSE_MODEL)
        self.assertEqual(body["messages"][0]["role"], "user")
        self.assertNotIn("dummy-secret", body["messages"][0]["content"])

    def test_course_model_uses_exact_ceu_name_and_is_cached(self):
        answer = {"message": "Hello", "files": []}
        for name in ("gemini-3.1-flash-lite", "Gemini 3.1 Flash-Lite"):
            with self.subTest(name=name):
                client, opener = self.client(
                    {"data": {"content": json.dumps(answer)}},
                    models={"data": [{"modelName": "GPT-5"}, {"modelName": name}]},
                )
                self.assertEqual(client.course_model(), name)
                client.generate("Hello", {}, [])
                client.generate("Hello again", {}, [])
                requests = [call.args[0] for call in opener.open.call_args_list]
                self.assertEqual(sum(req.get_method() == "GET" for req in requests), 1)
                self.assertEqual([json.loads(req.data)["model"] for req in requests if req.data], [name, name])

    def test_unavailable_course_model_never_falls_back_or_sends_chat(self):
        for names in (["GPT-5 nano", "Gemini 3.5 Flash"], ["Gemini 3.1 Flash-Lite Preview"], []):
            with self.subTest(names=names):
                client, opener = self.client({}, models={"data": [{"modelName": n} for n in names]})
                with self.assertRaises(ceu.UserError):
                    client.generate("Hello", {}, [])
                self.assertEqual(opener.open.call_count, 1)
                self.assertEqual(opener.open.call_args.args[0].get_method(), "GET")

    def test_setup_asks_only_for_credentials(self):
        ask = Mock(return_value="dummy-id")
        secret_prompt = Mock(return_value="dummy-secret")
        with patch.object(ceu.CEUClient, "models", return_value=[ceu.COURSE_MODEL]), \
                patch.object(ceu, "save_config") as save, contextlib.redirect_stdout(io.StringIO()):
            client = ceu.setup(ask, secret_prompt)
        ask.assert_called_once_with("Client ID: ")
        secret_prompt.assert_called_once_with("Client secret: ")
        save.assert_called_once_with(ceu.Config("dummy-id", "dummy-secret"))
        self.assertEqual(client.course_model(), ceu.COURSE_MODEL)

    def test_unavailable_course_model_does_not_save_setup(self):
        with patch.object(ceu.CEUClient, "models", return_value=["GPT-5"]), \
                patch.object(ceu, "save_config") as save, contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaisesRegex(ceu.UserError, "No other model will be used"):
                ceu.setup(lambda _: "dummy-id", lambda _: "dummy-secret")
        save.assert_not_called()

    def test_model_command_cannot_change_model(self):
        client, opener = self.client({})
        client.generate = Mock()
        inputs = iter(["/help", "/model", "/quit"])
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            ceu.run_chat(client, ROOT, lambda _: next(inputs))
        self.assertNotIn("/model", output.getvalue())
        self.assertIn("Unknown command", output.getvalue())
        self.assertEqual(client.course_model(), ceu.COURSE_MODEL)
        self.assertEqual(opener.open.call_count, 1)
        client.generate.assert_not_called()

    def test_saved_credentials_start_chat_without_setup(self):
        config = ceu.Config("dummy-id", "dummy-secret")
        with patch.object(sys, "argv", ["ceu-ai.py"]), patch.object(sys.stdin, "isatty", return_value=True), \
                patch.object(ceu, "load_config", return_value=config), patch.object(ceu, "setup") as setup, \
                patch.object(ceu, "run_chat") as chat, patch("prompt_toolkit.PromptSession"):
            self.assertEqual(ceu.main(), 0)
        setup.assert_not_called()
        self.assertEqual(chat.call_args.args[0].config, config)

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
        client, _ = self.client({}, models={"success": False})
        with self.assertRaises(ceu.UserError):
            client.models()

    def test_schema_and_file_limits(self):
        for answer in ([], {"message": "x", "files": [{"path": "a.py", "content": 3}]},
                       {"message": "x", "files": [{"path": "a", "content": "x"}] * 13}):
            with self.subTest(answer=answer), self.assertRaises(ceu.UserError):
                ceu.parse_reply(json.dumps(answer))
        self.assertEqual(ceu.parse_reply('```json\n{"message":"hello","files":[]}\n```')["message"], "hello")

    def test_message_only_reply_is_safe_but_other_missing_fields_are_not_inferred(self):
        self.assertEqual(ceu.parse_reply('{"message": "Please share the notebook"}'),
                         {"message": "Please share the notebook", "files": []})
        for answer in ({"message": "x", "files": None}, {"message": None}, {"cells": []},
                       {"message": "x", "delete_files": ["old.py"]},
                       {"message": "x", "read_files": ["notes.txt"]},
                       {"message": "x", "content": "SOURCE_SENTINEL"}):
            with self.subTest(answer=answer), self.assertRaises(ceu.InvalidReplyError) as caught:
                ceu.parse_reply(json.dumps(answer))
            self.assertNotIn("SOURCE_SENTINEL", str(caught.exception))
            self.assertIn("message:", str(caught.exception))

    def test_deletion_protocol_rejects_bad_arguments_mixed_reads_and_oversized_batches(self):
        for answer in (
            {"message": "Delete", "files": [], "delete_files": "old.py"},
            {"message": "Delete", "files": [], "delete_files": [None]},
            {"message": "Delete", "files": [], "delete_files": [""]},
            {"message": "Read", "files": [], "delete_files": ["old.py"], "read_files": ["old.py"]},
            {"message": "Delete", "files": [], "delete_files": [f"old{i}.py" for i in range(13)]},
            {"message": "Change", "files": [{"path": "new.py", "content": "x = 1"}],
             "delete_files": [f"old{i}.py" for i in range(12)]},
        ):
            with self.subTest(answer=answer), self.assertRaises(ceu.UserError):
                ceu.parse_reply(json.dumps(answer))
        reply = {"message": "Delete", "files": [], "delete_files": ["old.py"]}
        self.assertEqual(ceu.parse_reply(json.dumps(reply)), reply)

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

    def test_add_csv_then_request_sends_summary_and_drop_and_new_remove_it(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d).resolve()
            path = root / "data/raw/hotels.csv"
            path.parent.mkdir(parents=True)
            path.write_text("price,distance_miles\n" + "80,2.5\n" * 5 + "999999,99\n")
            answer = {"message": "Here is the explanation.", "files": []}
            client, opener = self.client({"data": {"content": json.dumps(answer)}})
            def ask(prompt):
                value = next(inputs)
                if value == "follow up":
                    path.write_text("price,distance_miles\n90,1.5\n")
                return value
            inputs = iter(["/add data/raw/hotels.csv", "regress price", "follow up",
                           "/drop data/raw/hotels.csv", "after drop", "/add data/raw/hotels.csv",
                           "/new", "after new", "/quit"])
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                ceu.run_chat(client, root, ask)
            requests = [call.args[0] for call in opener.open.call_args_list if call.args[0].data]
            payloads = [json.loads(json.loads(req.data)["messages"][0]["content"][len(ceu.INSTRUCTIONS) + 1:])
                        for req in requests]
            first = json.loads(payloads[0]["shared_files"]["data/raw/hotels.csv"])
            self.assertEqual(first["row_count"], 6)
            self.assertNotIn("999999", requests[0].data.decode())
            updated = json.loads(payloads[1]["shared_files"]["data/raw/hotels.csv"])
            self.assertEqual(updated["row_count"], 1)
            self.assertEqual(payloads[2]["shared_files"], {})
            self.assertEqual(payloads[3]["shared_files"], {})
            self.assertEqual(payloads[3]["conversation"], [])
            self.assertIn("Only this summary and preview", output.getvalue())
            self.assertEqual(len(requests), 4)  # /add itself never sends a request.


if __name__ == "__main__":
    unittest.main()
