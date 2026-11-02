# Session 1: Reconstructing a Regression Workflow

Use this worksheet after completing the human analysis in Lecture 12. Each student
develops their own prompt. Include only the steps completed in class; extend the prompt
with multiple regression after covering Lecture 13 in a later meeting.

## Initial prompt

> Analyze how Vienna hotel prices vary with distance. Write the Python
> code and explain the results.

Run this version first. Before looking at the answer, predict what it leaves unspecified.

## Develop your specification

Decide what the improved prompt must say about:

- the local dataset path and analysis sample;
- the outcome scale and predictor units;
- the sequence from graph to simple regression;
- robust uncertainty;
- fitted values, residuals, confidence intervals, and prediction intervals;
- transformations, only if completed in class;
- noncausal interpretation and reproducibility.

## Improved prompt scaffold

> We are analyzing `[QUESTION]` using the local file
> `data/raw/hotels_course.csv`. Use `[SAMPLE]`. First produce a numbered analysis plan,
> then complete Python code using pandas, seaborn, and statsmodels. The workflow must
> `[REQUIRED STEPS]`. Report `[REQUIRED OUTPUTS]`. Use the existing project environment,
> download nothing, and install nothing. State any choice not determined by this prompt.
> Interpret associations with their units and do not make causal claims.

## Audit the reconstruction

- Did it select the same sample and outcome scale?
- Did it reproduce the simple-regression specification?
- Did it avoid adding model steps that were not requested?
- If transformations were included, did it interpret their units correctly?
- Did it distinguish confidence and prediction intervals?
- Did it use residuals as evidence rather than label hotels automatically?
- Which terms differ from the language used during live coding?
