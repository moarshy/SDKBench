# Difference Between evaluate.py and llm_evaluate.py

## Overview

The scripts serve two distinct phases of the evaluation process:

| Aspect | **llm_evaluate.py** | **evaluate.py** |
|--------|---------------------|-----------------|
| **Purpose** | Generate solutions using LLMs | Score existing solutions |
| **Phase** | Solution Generation | Solution Evaluation |
| **Input** | Sample problems | Generated solutions |
| **Output** | Code files | Evaluation scores |
| **Uses LLM?** | Yes | No |
| **Cost** | Requires API credits | Free (local analysis) |

## Detailed Comparison

### llm_evaluate.py - Solution Generator

**What it does:**
- Takes SDK-Bench sample problems as input
- Sends prompts to LLMs (Claude, GPT-4, etc.)
- Receives generated code from the LLM
- Saves the generated files to disk

**Workflow:**
```
Sample Problem → LLM API → Generated Code Files
```

**Example Usage:**
```bash
# Generate solutions using Claude
python scripts/evaluation/llm_evaluate.py \
    --provider anthropic \
    --model claude-3-haiku-20240307 \
    --samples samples/ \
    --output results/llm_solutions/
```

**Key Functions:**
- Builds prompts from sample metadata
- Calls LLM APIs (Anthropic, OpenAI)
- Parses LLM responses
- Extracts and saves generated code files
- Tracks token usage and costs

**Output Structure:**
```
results/llm_solutions/
├── task1_init_001/
│   └── claude-3-haiku-20240307/
│       ├── middleware.ts
│       ├── app/layout.tsx
│       ├── package.json
│       └── llm_response.txt
```

### evaluate.py - Solution Scorer

**What it does:**
- Takes generated solutions as input
- Applies 6 evaluation metrics
- Produces numerical scores
- No LLM calls needed

**Workflow:**
```
Generated Code → Metrics Analysis → Evaluation Scores
```

**Example Usage:**
```bash
# Evaluate an existing solution
python scripts/evaluation/evaluate.py \
    results/llm_solutions/task1_init_001/claude-3-haiku \
    --metadata samples/task1_init_001/expected/metadata.json \
    --output results/
```

**Key Functions:**
- Loads solution files
- Runs each metric evaluator:
  - I-ACC: Check initialization patterns
  - C-COMP: Verify configuration completeness
  - IPA: Measure integration point accuracy
  - F-CORR: Test functional correctness
  - CQ: Assess code quality
  - SEM-SIM: Calculate semantic similarity
- Aggregates scores into final report

**Output Structure:**
```
results/
├── evaluation_task1_init_001_claude-3-haiku.json
└── evaluation_report.json
```

## Pipeline Flow

```mermaid
graph LR
    A[Sample Problem] --> B[llm_evaluate.py]
    B --> C[Generated Solution]
    C --> D[evaluate.py]
    D --> E[Scores & Report]
```

## When to Use Which

### Use llm_evaluate.py when:
- You want to test how well an LLM can solve SDK integration tasks
- You need to generate new solutions from scratch
- You're comparing different LLM models
- You have API credits and want fresh solutions

### Use evaluate.py when:
- You already have generated solutions to score
- You want to measure solution quality
- You need numerical metrics for comparison
- You're analyzing human-written code

## Complete Example Workflow

```bash
# Step 1: Generate solutions with LLM
python scripts/evaluation/llm_evaluate.py \
    --provider anthropic \
    --model claude-3-haiku-20240307 \
    --samples samples/task1_init_001 \
    --output results/llm_solutions/

# Step 2: Evaluate the generated solutions
python scripts/evaluation/evaluate.py \
    results/llm_solutions/task1_init_001/claude-3-haiku-20240307 \
    --metadata samples/task1_init_001/expected/metadata.json \
    --output results/ \
    --detailed

# Step 3: View results
cat results/evaluation_task1_init_001_claude-3-haiku-20240307.json
```

## Key Differences Summary

1. **Generation vs Evaluation**: llm_evaluate.py creates code, evaluate.py scores it
2. **API Usage**: llm_evaluate.py requires LLM API access, evaluate.py runs locally
3. **Input Type**: llm_evaluate.py needs problems, evaluate.py needs solutions
4. **Cost**: llm_evaluate.py costs money (API calls), evaluate.py is free
5. **Speed**: llm_evaluate.py is slower (API latency), evaluate.py is fast (local)
6. **Dependencies**: llm_evaluate.py needs API keys, evaluate.py needs only local code