# SDK-Bench Notebooks

This directory contains interactive Jupyter notebooks for exploring and understanding the SDK-Bench evaluation pipeline.

## Available Notebooks

### 1. `sdkbench_step_by_step_evaluation.ipynb`

A comprehensive walkthrough of the SDK-Bench evaluation pipeline that demonstrates:

- **Prompt Construction**: See exactly how system and user prompts are built
- **LLM Integration**: Generate solutions using different models
- **Metric Evaluation**: Understand what each metric measures and how
- **Step-by-Step Analysis**: Walk through evaluation of a real sample task

## Getting Started

1. **Install Jupyter** (if not already installed):
   ```bash
   pip install jupyter notebook
   ```

2. **Launch Jupyter**:
   ```bash
   cd /Users/arshath/play/naptha/better-onboarding/SDKBench/notebooks
   jupyter notebook
   ```

3. **Open the notebook** and run cells sequentially

## Key Features of the Step-by-Step Notebook

### Sections Covered:

1. **Setup**: Import required modules and configure environment
2. **Load Sample**: Load a real SDK-Bench task with metadata
3. **Task Types**: Understand the 6 different task categories
4. **Prompt Building**: See the exact prompts sent to LLMs
5. **Solution Generation**: Either use existing solutions or generate new ones
6. **Metrics Explanation**: Detailed explanation of all 6 evaluation metrics:
   - **I-ACC** (Implementation Accuracy): 30% weight
   - **C-COMP** (Configuration Completeness): 20% weight
   - **IPA** (Integration Point Accuracy): 15% weight
   - **F-CORR** (Functional Correctness): 15% weight
   - **CQ** (Code Quality): 10% weight
   - **SEM-SIM** (Semantic Similarity): 10% weight
7. **Evaluation**: Run the evaluation and see detailed results
8. **Analysis**: Understand strengths, weaknesses, and improvement areas

### Configuration Options:

- **Sample Selection**: Change `SAMPLE_ID` to test different tasks
- **Model Selection**: Test different LLMs (Claude, GPT-4, etc.)
- **Generation Mode**: Use existing solutions or generate new ones

### Example Output:

The notebook shows:
- Raw prompts (system and user)
- Generated solution files
- Metric scores with explanations
- Common failure patterns
- Recommendations for improvement

## Requirements

- Python 3.8+
- All SDK-Bench dependencies installed
- (Optional) API keys for LLM providers if generating new solutions:
  - `ANTHROPIC_API_KEY` for Claude models
  - `OPENAI_API_KEY` for GPT models

## Tips

1. Start with existing solutions to understand the evaluation without needing API keys
2. The notebook uses `task1_init_001` by default - a simple initialization task
3. Each metric section explains what it measures and shows actual evaluation results
4. The weighted score calculation shows how the overall score is computed
5. Common issues section helps identify typical LLM mistakes

## Troubleshooting

If imports fail, ensure you're running from the notebooks directory and that SDK-Bench is properly installed:

```bash
cd /Users/arshath/play/naptha/better-onboarding/SDKBench
pip install -e .
```

## Next Steps

After running this notebook, you can:
1. Try different sample tasks to see various complexity levels
2. Generate new solutions with different models for comparison
3. Analyze patterns across multiple evaluations
4. Use insights to improve prompts or evaluation metrics