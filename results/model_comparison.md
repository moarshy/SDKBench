# SDK Bench Model Comparison

**Date:** November 24, 2024
**Framework:** Clerk Authentication SDK Integration
**Total Samples:** 50

## Executive Summary

| Model | Avg Score | Min | Max | Success Rate | Time | Speed |
|-------|-----------|-----|-----|--------------|------|-------|
| **GPT-5.1** 🏆 | **85.9%** | 81.8% | 99.0% | 49/50 | 72s | **2.6x** |
| Claude 4.5 | 83.5% | 73.3% | 99.0% | 50/50 | 189s | 1.0x |

## Detailed Comparison

### 🎯 Quality Metrics
- **GPT-5.1**: Higher average score (85.9% vs 83.5%)
- **GPT-5.1**: More consistent (min 81.8% vs 73.3%)
- **Both**: Achieved same maximum score (99.0%)

### ⚡ Performance Metrics
- **GPT-5.1**: 2.6x faster (72s vs 189s)
- **GPT-5.1**: ~1.4 seconds per sample
- **Claude 4.5**: ~3.8 seconds per sample

### 📊 Task Breakdown (5 Task Types)
| Task Type | Samples | Description |
|-----------|---------|-------------|
| Task 1: Init | 15 | Basic SDK initialization |
| Task 2: Middleware | 15 | Middleware configuration |
| Task 3: Hooks | 10 | React hooks integration |
| Task 4: Complete | 7 | Full implementation |
| Task 5: Migration | 3 | Legacy migration |

### 🔍 Key Observations

1. **GPT-5.1 Advantages:**
   - 2.4% higher average score
   - 2.6x faster execution
   - Better consistency (higher minimum score)

2. **Claude 4.5 Advantages:**
   - 100% success rate (vs 98% for GPT-5.1)
   - One less failed evaluation

3. **Technical Notes:**
   - GPT-5.1 requires  parameter (new API)
   - Both models work without model name validation
   - F-CORR metric disabled for both (requires Node.js runtime)

## Conclusion

**GPT-5.1 (gpt-5.1-2025-11-13)** demonstrates superior performance in both quality and speed for SDK integration tasks, with a 2.4% higher average score and 2.6x faster execution time.
