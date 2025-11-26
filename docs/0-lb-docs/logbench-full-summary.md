# LogBench: Automated Logging Generation Benchmark - Comprehensive Summary

## Executive Summary

LogBench is a benchmark for evaluating Large Language Models (LLMs) and other approaches in automated logging statement generation. Published in IEEE Transactions on Software Engineering (2024) by researchers from Tsinghua University, CUHK, and University of Ottawa, LogBench addresses the critical need for automated tools to assist developers in writing effective logging statements.

**Paper**: "Exploring the Effectiveness of LLMs in Automated Logging Generation: An Empirical Study" (arXiv:2307.05950)

---

## 1. Background and Motivation

### Why Logging Matters
Logging statements are imperative in modern software development. They serve critical roles in:
- **Reflecting developer intentions**: Documenting what the code is designed to do
- **Recording system behavior**: Capturing runtime states and execution flow
- **Guiding failure diagnosis**: Providing essential information for debugging and troubleshooting

### The Challenge
Despite their importance, logging statements are often:
- **Neglected** during development due to time constraints
- **Inconsistent** in quality and coverage across codebases
- **Difficult to write effectively** (requires understanding of system behavior, appropriate granularity, and clarity)

### The Solution
LogBench provides a standardized benchmark to evaluate automated approaches for generating three key logging statement ingredients:
1. **Logging Level**: Severity indicator (error, warn, info, debug, trace)
2. **Logging Variables**: Runtime information from system states
3. **Logging Text**: Natural language description of activities

---

## 2. Dataset Construction Methodology

### 2.1 Data Collection Process

#### Repository Selection Criteria
The dataset was built by mining open-source Java repositories from GitHub with rigorous quality standards:

| Criterion | Threshold | Purpose |
|-----------|-----------|---------|
| **Stars** | > 20 | Indicates higher level of community attention |
| **Commits** | > 100 | Suggests active maintenance and maturity |
| **Contributors** | ≥ 5 | Demonstrates collaborative development quality |
| **Logging Frameworks** | Log4j or SLF4J | Ensures consistent logging API usage |

**Result**: **3,089 repositories** meeting these criteria

#### Extraction Process

1. **Dependency Filtering**
   - Selected projects whose POM files include popular logging utility dependencies (Log4j, SLF4J)
   - These are the most widely-used logging frameworks in the Java ecosystem

2. **File Extraction**
   - Extracted Java files containing at least one logging statement
   - Identified using **regular expressions** matching specified syntax patterns (e.g., `log.info()`, `logger.debug()`)

3. **Random Sampling**
   - Randomly sampled files across various repositories
   - Ensures diversity and prevents over-representation of specific projects

4. **Archive Date**
   - All repositories archived in **July 2023**
   - Important for understanding potential data leakage with LLMs

### 2.2 Dataset Statistics

#### LogBench-O (Original Dataset)

| Metric | Count |
|--------|-------|
| **Java Files** | 2,430 files |
| **Methods** | 3,870 methods |
| **Logging Statements** | 6,849 statements |
| **Source Repositories** | 3,089 GitHub repositories |
| **Programming Language** | Java |
| **Logging APIs** | SLF4J and Log4j |

#### Context Length Analysis
- **98.6%** of Java files fall within 4,096-token limit
- **94.3%** of files within 2,048-token range
- Ensures compatibility with most current LLMs

---

## 3. LogBench-O: The Original Dataset

### 3.1 What It Contains

LogBench-O consists of real-world logging statements from high-quality GitHub repositories. Each logging statement has **three ingredients**:

#### Example Logging Statement
```java
log.warn("Failed to connect to host: {}", url)
```

**Components:**
1. **Logging Level**: `warn` - Indicates severity
2. **Logging Variable**: `url` - Captures runtime state
3. **Logging Text**: `"Failed to connect to host: {}"` - Describes the event

### 3.2 Input Format

For evaluation, the benchmark creates inputs by:
- Removing each logging statement from its original location
- Creating a `<Logging Point>` placeholder
- For code with **n** logging statements, creates **n-1** input instances

**Example Input:**
```java
public void handleEvent(Event event) {
    try {
        boolean minified = htmlLibraryManager.isMinifyEnabled();
        String path = (String) event.getProperty(SlingConstants.PROPERTY_PATH);
        log.                    // <-- Logging point to be filled
        ClientLibrary library = htmlLibraryManager.getLibraries().get(path);
        if (library != null) {
            for (LibraryType type : library.getTypes()) {
                String includePath = library.getIncludePath(type, minified);
                server.triggerReload(includePath);
            }
        }
    } catch (JSONException e) {
        log.info("Unable to send reload", e);
    }
}
```

**Expected Output:**
```java
log.info("Client Library at {} invalidated. Sending reload.", path);
```

### 3.3 Dataset Organization

In the repository, each sample consists of:
1. **`.java` file**: Code with logging statement removed (marked by incomplete `log.` statement)
2. **`_config.txt` file**: Contains the ground truth logging statement

**Example Files:**
- `acs-aem-tools_ClientLibraryListener_handleEvent.java` - Code with placeholder
- `acs-aem-tools_ClientLibraryListener_handleEvent_config.txt` - Ground truth

**File Naming Convention:**
```
{project}_{class}_{method}.java
{project}_{class}_{method}_config.txt
```

---

## 4. LogBench-T: The Transformed Dataset

### 4.1 Motivation

**Problem: Data Leakage**
- LLMs are trained on massive web-scraped datasets
- May have seen LogBench-O code during training
- Difficult to distinguish true inference from memorization

**Solution: Semantic-Preserving Code Transformation**
- Create syntactically different but semantically equivalent code
- Evaluate generalization capability on truly unseen code
- Fair assessment of model reasoning vs. memorization

### 4.2 Transformation Methodology

#### Transformation Philosophy
Unlike prior work that replaces meaningful identifiers with meaningless ones (e.g., `totalMemory` → `var0`), LogBench-T preserves:
- **Readability**: Keeps informative identifier names
- **Semantics**: Maintains identical code functionality
- **Debugging capability**: Code remains understandable

#### Implementation
- **4,074 lines** of Java code
- Uses **JavaParser** library for AST manipulation
- Works at Abstract Syntax Tree (AST) level for reliability

### 4.3 Eight Code Transformers

The transformation tool employs **8 carefully engineered, lightweight transformers**:

| # | Transformer | Description | Example Transformation |
|---|-------------|-------------|----------------------|
| 1 | **Condition-Dup** | Add logically neutral elements | `if (exp0)` → `if (exp0 || false)` |
| 2 | **Condition-Swap** | Swap symmetrical operands | `if (var0 != null)` → `if (null != var0)` |
| 3 | **Local Variable** | Extract constants to variables | `var0 = const0;` → `int var1 = const0; var0 = var1;` |
| 4 | **Assignment** | Separate declaration/assignment | `int var0 = var1;` → `int var0; var0 = var1;` |
| 5 | **Constant** | Replace with equivalent expressions | `int var0 = const0` → `int var0 = const0 + 0` |
| 6 | **For-While** | Convert for-loops to while-loops | `for (i = 0; i < n; i++)` → `while (i++ < n)` |
| 7 | **While-For** | Convert while-loops to for-loops | Inverse of above |
| 8 | **Parenthesis** | Add redundant parentheses | `var0 = arithExpr0` → `var0 = (arithExpr0)` |

### 4.4 Transformation Process

1. **Parse**: Convert source code to Abstract Syntax Tree (AST)
2. **Detect**: Checkers traverse AST top-down to identify transformation points
3. **Transform**: Apply transformers independently at identified points
4. **Chain**: Combine transformations: T = T₁ ∘ T₂ ∘ ... ∘ Tₙ
5. **Generate**: Convert transformed AST back to source code

### 4.5 Transformation Example

**Original Code (LogBench-O):**
```java
public void handleEvent(Event event) {
    try {
        boolean minified = htmlLibraryManager.isMinifyEnabled();
        String path = (String) event.getProperty(SlingConstants.PROPERTY_PATH);
        log.
        ClientLibrary library = htmlLibraryManager.getLibraries().get(path);
        if (library != null) {
            for (LibraryType type : library.getTypes()) {
                String includePath = library.getIncludePath(type, minified);
                server.triggerReload(includePath);
            }
        }
    } catch (JSONException e) {
        log.info("Unable to send reload", e);
    }
}
```

**Transformed Code (LogBench-T):**
```java
public void handleEvent(Event event) {
    try {
        boolean minified = (htmlLibraryManager.isMinifyEnabled());  // Added parentheses
        String path = ((String) event.getProperty(SlingConstants.PROPERTY_PATH));  // Added parentheses
        
        // Added logically neutral for-loop and while-loop wrappers
        for (int counter101 = 0; counter101 < (1 + 1 - 1); counter101++) {  // Constant transformation
            for (; true; ) {
                if (true) {
                    log.  // <-- Logging point
                }
                break;
            }
            break;
        }
        
        ClientLibrary library = (htmlLibraryManager.getLibraries().get(path));
        for (; true; ) {  // For-While transformation
            if (((null != library) || false) && true) {  // Condition-Swap + Condition-Dup
                for (LibraryType type : library.getTypes()) {
                    String includePath = (library.getIncludePath(type, minified));
                    for (int counter100 = 0; counter100 < (1 + 1 - 1); counter100++) {
                        if (true) {
                            server.triggerReload(includePath);
                        }
                        break;
                    }
                }
            }
            break;
        }
    } catch (JSONException e) {
        log.info("Unable to send reload", e);
    }
}
```

**Key Observations:**
- Semantically identical (produces same output)
- Syntactically very different (unlikely seen during LLM training)
- Maintains readability (no variable name obfuscation)
- Preserves debugging capability

### 4.6 Verification

**Soundness Verification:**
- Transformation rules proven effective in various code-related tasks
- **Unit tests** executed on sample projects
- Confirms transformations don't hurt functionality
- AST-level approach ensures semantic equivalence

### 4.7 Dataset Size

**LogBench-T Statistics:**
- **3,842 Java files** (comparable to LogBench-O's 3,857)
- Each file corresponds to a transformed version from LogBench-O
- Same ground truth logging statements as LogBench-O

---

## 5. Dataset Variants

LogBench offers multiple variants to support different evaluation settings:

### 5.1 Context-Level Variants

#### Method-Level (Standard)
- **Input**: Single method containing the logging point
- **Context**: Limited to method scope
- **Use Case**: Standard evaluation setting

#### File-Level (Extended Context)
- **Input**: Entire Java file with multiple methods
- **Context**: Access to class-level information, other methods, imports
- **Impact**: Significant performance improvement
  - **+2.7%** for logging level prediction
  - **+6.9%** for variable prediction
  - **+49.3%** for BLEU-4 score (text generation)
- **Why It Helps**: 
  - Access to functionality-similar methods
  - Variable definitions at class level
  - Intra-project logging style patterns

### 5.2 Comment Inclusion Variants

#### With Comments (Standard)
- Includes all developer-written comments
- Provides additional context about code functionality

#### Without Comments (Ablation Study)
- Removes all code comments
- Tests model's ability to infer from code alone
- **Impact**: Performance drops
  - **-0.8%** AOD (logging levels)
  - **-2.1%** F1 (variables)
  - **-2.2%** BLEU-4 and **-3.0%** ROUGE-L (text)
- **Insight**: Comments describe functionalities similar to logging practices

### 5.3 Dataset File Organization

```
LogBench-O/
├── LogBench-O_prefix_1point.zip (method-level, with comments)
├── LogBench-O_prefix_1point_file_level.zip (file-level, with comments)
└── LogBench-O_prefix_1point_wo_comments.zip (method-level, without comments)

LogBench-T/
├── LogBench-T_prefix_1point.zip (method-level, with comments)
└── LogBench-T_prefix_1point_file_level.zip (file-level, with comments)
```

**Total Dataset Variants**: 5 different configurations

---

## 6. Evaluation Methodology

### 6.1 Evaluation Metrics

LogBench uses **ingredient-specific metrics** for the three logging components:

#### (1) Logging Levels

**L-ACC (Level Accuracy):**
- Simple accuracy: Percentage of correctly predicted log levels
- Binary metric (correct or incorrect)

**AOD (Average Ordinal Distance):**
- Considers the ordered nature of logging levels
- Formula: `AOD = Σ(1 - Dis(aᵢ, sᵢ)/MaxDis(aᵢ)) / N`
- Accounts for severity hierarchy: `error → warn → info → debug → trace`
- Example: Distance(error, warn) = 1 < Distance(error, info) = 2
- **Why It Matters**: Confusing `error` with `warn` is less severe than confusing `error` with `trace`

#### (2) Logging Variables

**Precision:**
- Proportion of predicted variables that are correct
- Formula: `P = |Spd ∩ Sgt| / |Spd|`
- Measures accuracy of predictions

**Recall:**
- Proportion of actual variables that were predicted
- Formula: `R = |Spd ∩ Sgt| / |Sgt|`
- Measures completeness of predictions

**F1 Score:**
- Harmonic mean of precision and recall
- Formula: `F1 = 2 × P × R / (P + R)`
- Balances both metrics

**Key Finding**: Recall consistently lower than precision (models struggle to identify all relevant variables)

#### (3) Logging Texts

**Syntax-Based Metrics:**

**BLEU-K** (K ∈ {1, 2, 4}):
- Measures N-gram overlap between generated and actual logs
- BLEU-1: Unigram overlap
- BLEU-2: Bigram overlap  
- BLEU-4: 4-gram overlap (most strict)
- Higher scores = better match

**ROUGE-K** (K ∈ {1, 2, L}):
- Recall-oriented N-gram metrics
- ROUGE-L: Longest common subsequence
- Widely used in summarization tasks

**Semantic-Based Metrics:**

**Semantic Similarity:**
- Uses code embedding models (UniXcoder, OpenAI embedding)
- Calculates cosine similarity between embeddings
- Addresses limitation of token-based metrics
- Example: "initialize connection" vs. "start connection" (different tokens, similar meaning)

### 6.2 Models Evaluated

The paper evaluates **11 top-performing LLMs** across different categories:

#### Commercial API-Based LLMs:
1. **Davinci** (GPT-3)
2. **ChatGPT** (GPT-3.5/4)

#### Open-Source LLMs:
3. **LANCE** - Specialized for log statement generation (ICSE'22)
4. **InCoder** - Code infilling model (ICLR'23)
5. **Llama2** - Meta's foundation model
6. **StarCoder** - Hugging Face's code model
7. **CodeLlama** - Meta's code-specialized Llama2

#### Commercial Plugin-Based Tools:
8. **CodeGeex** - Tsinghua's code generation tool
9. **TabNine** - AI code completion
10. **GitHub Copilot** - OpenAI Codex-based assistant
11. **AWS CodeWhisperer** - Amazon's code assistant

#### Conventional (Non-LLM) Baselines:
12. **DeepLV** - Ordinal neural network for log levels (ICSE'21)
13. **WhichVar** - Variable selection model (TSE'21)
14. **LoGenText-Plus** - NMT-based text generation (TOSEM'23)

### 6.3 Performance Results

#### Best-Performing Model: **GitHub Copilot**

| Component | Metric | Score | Interpretation |
|-----------|--------|-------|----------------|
| **Logging Levels** | L-ACC | 74.3% | 3 out of 4 levels predicted correctly |
| **Logging Variables** | F1 | 71.2% | Good but not excellent variable identification |
| **Logging Texts** | BLEU-4 | 0.244 | Only 24.4% 4-gram overlap |
| **Logging Texts** | Semantic Similarity | 0.703 | 70.3% semantic match |

#### Key Findings:

1. **Level prediction is easiest**
   - 74.3% accuracy suggests models understand severity
   - Ordinal nature helps (5 ordered choices)

2. **Variable prediction is challenging**
   - Recall < Precision consistently
   - Models struggle to identify ALL relevant variables
   - Tendency to under-predict rather than over-predict

3. **Text generation is hardest**
   - BLEU-4 of 0.244 indicates significant room for improvement
   - Gap between syntax (BLEU) and semantics (0.703) suggests models capture meaning better than exact phrasing
   - Natural language generation in technical context is difficult

4. **LLMs outperform conventional methods**
   - Without fine-tuning, LLMs surpass specialized logging models
   - Transfer learning from general coding knowledge is effective

5. **Significant generalization gap (LogBench-O → LogBench-T)**
   - **8.2% - 16.2%** performance drop on transformed code
   - Indicates potential memorization rather than pure reasoning
   - Highlights importance of LogBench-T for fair evaluation

---

## 7. Key Insights and Research Findings

### 7.1 LLM Capabilities and Limitations

#### Strengths:
- ✅ Reasonable logging level prediction (74.3% accuracy)
- ✅ Outperform specialized conventional models without fine-tuning
- ✅ Capture semantic meaning better than exact token matching (70.3% semantic similarity vs 24.4% BLEU-4)
- ✅ Benefit significantly from broader context (file-level > method-level)

#### Weaknesses:
- ❌ Low BLEU scores (0.244) for text generation
- ❌ Struggle to identify all relevant variables (recall < precision)
- ❌ Significant performance degradation on unseen code transformations (8-16% drop)
- ❌ Inconsistent performance across different logging statement ingredients
- ❌ Limited ability to generate complete, high-quality logging statements

### 7.2 Impact of Context

#### File-Level Context Benefits:
- **+49.3%** improvement in BLEU-4 for logging text
- Access to:
  - Other methods in the same class
  - Class-level variable definitions
  - Consistent logging styles within the project
  - Import statements revealing libraries used

#### Comment Inclusion Benefits:
- **+2-3%** improvement across metrics
- Comments provide:
  - Functionality descriptions
  - Intent documentation
  - Natural language parallels to logging text

### 7.3 Prompt Engineering Insights

The paper explored optimal prompting strategies for LLMs:

#### Instruction Design:
- Conducted developer survey to identify effective instructions
- Top 5 instructions selected
- Clear, specific instructions improve performance

#### Demonstration Examples:
- Used BM25 retrieval to select relevant examples
- **Optimal range**: 5-7 demonstration examples
- Too few: Insufficient guidance
- Too many: Context length limitations, noise

### 7.4 Generalization vs. Memorization

**Critical Finding**: LogBench-T reveals significant generalization gaps

| Model Type | Avg. Performance Drop (LogBench-O → LogBench-T) |
|------------|-----------------------------------------------|
| LLMs | 8.2% - 16.2% |
| Conventional | Lower drops (less memorization) |

**Implications**:
- LLMs may partially memorize training data
- True reasoning capability is lower than LogBench-O suggests
- LogBench-T provides fairer evaluation
- Need for enhanced generalization techniques

---

## 8. Summary Table

| Aspect | Details |
|--------|---------|
| **Purpose** | Evaluate automated logging statement generation |
| **Dataset Size (LogBench-O)** | 6,849 statements, 3,870 methods, 2,430 files |
| **Source** | 3,089 GitHub repositories (Java) |
| **Quality Criteria** | 20+ stars, 100+ commits, 5+ contributors |
| **Logging Frameworks** | Log4j, SLF4J |
| **Transformations (LogBench-T)** | 8 semantic-preserving AST transformers |
| **Evaluation Metrics** | L-ACC, AOD (levels), P/R/F1 (variables), BLEU/ROUGE/Semantic (text) |
| **Models Evaluated** | 11 LLMs + 3 conventional baselines |
| **Best Performance** | 74.3% (levels), 71.2% F1 (variables), 0.244 BLEU-4 (text) |
| **Variants** | 5 configurations (O/T, method/file-level, ±comments) |
| **Key Finding** | Significant room for improvement, especially in text generation |
| **Publication** | IEEE TSE 2024 |
| **Dataset Release** | Open-source (GitHub) |

---

**Document Version**: 1.0  
**Last Updated**: 2024  
**Prepared for**: Naptha Better Onboarding Project  
**Based on**: LogBench paper (arXiv:2307.05950) and repository analysis
