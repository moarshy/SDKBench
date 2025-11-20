# SDK-Bench: Benchmark for SDK Instrumentation and Integration

**Purpose**: Create a benchmark to evaluate whether AI agents and LLMs can correctly insert and use SDKs in codebases, inspired by LogBench's methodology.

**Context**: Companies like WorkOS, Clerk, DevCycle, and LanceDB require instrumentation/SDK integration in customer codebases. Currently, only logging benchmarks exist (LogBench, AL-Bench), but no benchmark exists for SDK instrumentation.

---

## Table of Contents

1. [Overview](#overview)
2. [Applying LogBench Methodology](#applying-logbench-methodology)
3. [Dataset Construction](#dataset-construction)
4. [Benchmark Task Types](#benchmark-task-types)
5. [Dataset Structure](#dataset-structure)
6. [Transformation Strategy](#transformation-strategy)
7. [Evaluation Metrics](#evaluation-metrics)
8. [Implementation Phases](#implementation-phases)
9. [Success Criteria](#success-criteria)

---

## Overview

### Problem Statement
Modern dev tools require developers to:
- Install SDK packages
- Initialize SDKs with proper configuration
- Integrate SDK calls at appropriate points in code
- Handle errors and edge cases
- Follow SDK-specific best practices

**Goal**: Create SDK-Bench to evaluate AI agents' ability to perform these instrumentation tasks correctly.

### Inspiration from LogBench

LogBench successfully created a benchmark for automated logging by:
1. Mining high-quality repositories (3,089 repos, 6,849 logging statements)
2. Extracting real-world examples with clear patterns
3. Creating two datasets: Original (LogBench-O) and Transformed (LogBench-T)
4. Using ingredient-specific evaluation metrics
5. Testing generalization with semantic-preserving transformations

**Adaptation**: Apply this methodology to SDK instrumentation, which is more complex (multi-file, project-level integration vs. single statement insertion).

---

## Applying LogBench Methodology

### Repository Selection Criteria

Following LogBench's quality thresholds:

| Criterion | Threshold | Purpose |
|-----------|-----------|---------|
| **Stars** | > 20 | Community validation |
| **Commits** | > 100 | Mature implementation |
| **Contributors** | ≥ 5 | Collaborative quality |
| **SDK Usage** | Successful integration | Real-world patterns |
| **Activity** | Active in last 2 years | Recent SDK versions |
| **Documentation** | README with setup | Clear integration examples |

### Target SDKs for Initial Benchmark

**Phase 1: Authentication & Authorization**
- WorkOS SDK (SSO, Directory Sync, User Management)
- Clerk SDK (Auth, User Management, Sessions)
- Auth0 SDK (Authentication, Authorization)

**Phase 2: Feature Management**
- DevCycle SDK (Feature flags, A/B testing)
- LaunchDarkly SDK (Feature flags)
- PostHog Feature Flags

**Phase 3: Data & Analytics**
- LanceDB SDK (Vector database)
- Mixpanel SDK (Analytics)
- Amplitude SDK (Product analytics)

**Selection Rationale**:
- Well-documented with clear patterns
- Popular in dev tool space (aligns with our target market)
- Different complexity levels
- Cross-language support (JavaScript, TypeScript, Python)

---

## Dataset Construction

### SDK Integration Components

Expanding LogBench's three ingredients (level, variables, text) to **four SDK ingredients**:

#### 1. Initialization Location
Where to initialize the SDK in the codebase:
- Application entry point (`src/index.js`, `src/main.py`)
- Configuration/setup files
- Provider/wrapper components
- Environment-specific initialization

#### 2. Configuration Values
SDK configuration and credentials:
- API keys and secrets
- Environment-specific settings
- Optional feature flags
- Client IDs, workspace IDs, etc.

#### 3. Integration Points
Where to use SDK features in code:
- Middleware integration (auth checks)
- API endpoint handlers
- React hooks/components
- Background jobs/workers
- Event handlers

#### 4. Error Handling
SDK-specific error management:
- Try-catch blocks
- Fallback behavior
- Error logging
- Retry logic

### Data Collection Process

#### Step 1: Repository Mining

```bash
# Example GitHub search queries
- "workos-inc/node" in:dependencies stars:>20
- "clerk" in:dependencies language:typescript stars:>20
- "devcycle-sdk" in:dependencies commits:>100
```

#### Step 2: Pattern Extraction

Use regex and AST parsing to identify:
```javascript
// Pattern matching examples
const patterns = {
  // Initialization patterns
  initialization: [
    /new WorkOS\([^)]+\)/,
    /Clerk\.initialize\([^)]+\)/,
    /DevCycle\.client\([^)]+\)/
  ],

  // Configuration patterns
  config: [
    /process\.env\.WORKOS_API_KEY/,
    /require\(['"]\.\/config['"]\)/,
    /\.env files/
  ],

  // Usage patterns
  usage: [
    /workos\.sso\./,
    /useAuth\(\)/,
    /getVariable\(['"][^'"]+['"]/
  ]
};
```

#### Step 3: Categorization

Organize by:
- SDK name and version
- Integration type (initialization, middleware, feature usage)
- Framework (Express, Next.js, Fastify, Flask, FastAPI)
- Language (JavaScript, TypeScript, Python)
- Difficulty (basic, intermediate, advanced)

#### Step 4: Ground Truth Creation

For each sample:
```json
{
  "sample_id": "workos_sso_express_001",
  "sdk": "WorkOS",
  "sdk_version": "7.x",
  "task_type": "sso_integration",
  "difficulty": "intermediate",
  "files_modified": ["src/index.js", "src/auth/workos.js", ".env"],
  "dependencies_added": ["@workos-inc/node@^7.0.0"],
  "ground_truth": {
    "initialization": "const workos = new WorkOS(process.env.WORKOS_API_KEY);",
    "configuration": {"WORKOS_API_KEY": "required", "WORKOS_CLIENT_ID": "required"},
    "integration_points": ["authorize endpoint", "callback handler"],
    "error_handling": ["OAuth errors", "API failures"]
  }
}
```

---

## Benchmark Task Types

### Task Type 1: SDK Initialization

**Objective**: Initialize SDK with proper configuration

**Input**:
```javascript
// src/index.js
import express from 'express';
const app = express();

// <SDK_INIT_POINT>

app.listen(3000);
```

**Expected Output**:
```javascript
import express from 'express';
import { WorkOS } from '@workos-inc/node';

const app = express();

const workos = new WorkOS(process.env.WORKOS_API_KEY);

app.listen(3000);
```

**Additional Files**:
- `.env.example` with required keys
- Updated `package.json`

### Task Type 2: Middleware Integration

**Objective**: Add SDK middleware for authentication/authorization

**Input**:
```javascript
// src/index.js
const app = express();

// <AUTH_MIDDLEWARE_POINT>

app.get('/api/protected', (req, res) => {
  res.json({ data: 'secret' });
});
```

**Expected Output**:
```javascript
import { ClerkExpressRequireAuth } from '@clerk/clerk-sdk-node';

const app = express();

app.use('/api', ClerkExpressRequireAuth());

app.get('/api/protected', (req, res) => {
  const { userId } = req.auth;
  res.json({ data: 'secret', userId });
});
```

### Task Type 3: Feature Flag Integration

**Objective**: Add feature flag checks with SDK

**Input**:
```javascript
// src/components/Dashboard.jsx
export function Dashboard({ user }) {
  // <FEATURE_FLAG_POINT>

  return <StandardDashboard user={user} />;
}
```

**Expected Output**:
```javascript
import { useVariableValue } from '@devcycle/react-client-sdk';

export function Dashboard({ user }) {
  const showNewUI = useVariableValue('new-dashboard-ui', false);

  return showNewUI ? <NewDashboard user={user} /> : <StandardDashboard user={user} />;
}
```

### Task Type 4: Complete SDK Integration

**Objective**: Full SDK setup from scratch

**Input**:
- Bare Express/Next.js/Flask application
- Requirements: "Add WorkOS SSO authentication"

**Expected Output**:
- SDK initialized
- Environment variables configured
- Auth routes created
- Middleware integrated
- Protected routes updated
- Error handling added

### Task Type 5: SDK Migration/Update

**Objective**: Migrate from SDK v6 to v7 (handling breaking changes)

**Input**: Code using old SDK version
**Output**: Code updated to new SDK version with API changes

---

## Dataset Structure

### SDK-Bench-O (Original Dataset)

```
SDK-Bench-O/
├── workos/
│   ├── initialization/
│   │   ├── express_basic/
│   │   │   ├── input/
│   │   │   │   ├── src/index.js          # Code without SDK
│   │   │   │   └── package.json
│   │   │   ├── output/
│   │   │   │   ├── src/index.js          # Code with SDK
│   │   │   │   ├── package.json          # Updated deps
│   │   │   │   └── .env.example          # Required env vars
│   │   │   └── metadata.json             # Task metadata
│   │   ├── nextjs_basic/
│   │   └── fastify_basic/
│   ├── sso_integration/
│   │   ├── express_sso/
│   │   ├── nextjs_sso/
│   │   └── directory_sync/
│   └── user_management/
├── clerk/
│   ├── initialization/
│   ├── middleware/
│   ├── react_hooks/
│   └── session_management/
├── devcycle/
│   ├── client_init/
│   ├── feature_flags/
│   ├── user_targeting/
│   └── react_integration/
└── lancedb/
    ├── connection/
    ├── table_operations/
    └── vector_search/
```

### Metadata Schema

```json
{
  "sample_id": "workos_sso_express_001",
  "sdk": {
    "name": "WorkOS",
    "version": "7.x",
    "package": "@workos-inc/node"
  },
  "task": {
    "type": "sso_integration",
    "difficulty": "intermediate",
    "description": "Integrate WorkOS SSO into Express app"
  },
  "context": {
    "language": "javascript",
    "framework": "express",
    "context_level": "multi_file",
    "files_count": 3
  },
  "requirements": {
    "dependencies_added": ["@workos-inc/node@^7.0.0"],
    "env_vars_required": ["WORKOS_API_KEY", "WORKOS_CLIENT_ID"],
    "files_modified": ["src/index.js", "src/auth/workos.js", ".env.example"],
    "must_have": [
      "WorkOS initialization",
      "SSO authorize endpoint",
      "Callback handler",
      "Session management"
    ],
    "must_not_have": [
      "Hardcoded API keys",
      "Missing error handling",
      "Synchronous API calls without await"
    ]
  },
  "evaluation": {
    "functional_test": "npm test",
    "metrics": ["initialization", "integration_points", "configuration", "error_handling"]
  }
}
```

---

## Transformation Strategy (SDK-Bench-T)

### Semantic-Preserving Transformations

Following LogBench's approach, create transformed versions that are functionally equivalent but syntactically different:

#### Transformation 1: Framework Variation
```javascript
// Original (Express)
app.use(clerkMiddleware());
app.get('/api/protected', requireAuth(), handler);

// Transformed (Fastify)
fastify.register(clerkPlugin);
fastify.get('/api/protected', { preHandler: requireAuth }, handler);

// Transformed (Next.js API Routes)
export default withAuth(handler);
```

#### Transformation 2: Language Variation
```javascript
// Original (JavaScript)
const workos = new WorkOS(process.env.WORKOS_API_KEY);

// Transformed (TypeScript)
import { WorkOS } from '@workos-inc/node';
const workos: WorkOS = new WorkOS(process.env.WORKOS_API_KEY!);

// Transformed (Python)
from workos import WorkOSClient
workos = WorkOSClient(api_key=os.environ['WORKOS_API_KEY'])
```

#### Transformation 3: Configuration Method
```javascript
// Original (Environment Variables)
const workos = new WorkOS(process.env.WORKOS_API_KEY);

// Transformed (Config File)
const config = require('./config');
const workos = new WorkOS(config.workos.apiKey);

// Transformed (Inline Object)
const workos = new WorkOS({
  apiKey: process.env.WORKOS_API_KEY,
  clientId: process.env.WORKOS_CLIENT_ID
});
```

#### Transformation 4: Import Style
```javascript
// Original (Named Import)
import { WorkOS } from '@workos-inc/node';

// Transformed (Default Import)
import WorkOS from '@workos-inc/node';

// Transformed (CommonJS)
const { WorkOS } = require('@workos-inc/node');

// Transformed (Dynamic Import)
const { WorkOS } = await import('@workos-inc/node');
```

#### Transformation 5: Async Pattern
```javascript
// Original (Async/Await)
const result = await workos.sso.getProfile(code);

// Transformed (Promise Chain)
workos.sso.getProfile(code).then(result => { ... });

// Transformed (Callback)
workos.sso.getProfile(code, (err, result) => { ... });
```

#### Transformation 6: Code Structure (Similar to LogBench)
```javascript
// Original
if (user) { doAuth(); }

// Transformed (Condition-Dup)
if (user && true) { doAuth(); }

// Transformed (Condition-Swap)
if (null !== user) { doAuth(); }

// Transformed (Extra Parentheses)
if ((user)) { (doAuth()); }
```

### Transformation Verification

Ensure transformed code:
1. ✅ Passes same test suite as original
2. ✅ Produces identical runtime behavior
3. ✅ Maintains type safety (TypeScript)
4. ✅ Follows language/framework conventions
5. ✅ Is syntactically valid

---

## Evaluation Metrics

### Metric 1: Initialization Correctness (I-ACC)

**Components**:
- ✅ Correct import statement (1 point)
- ✅ Correct initialization location (1 point)
- ✅ Required configuration present (1 point)
- ✅ Proper variable naming (0.5 points)
- ✅ No syntax errors (0.5 points)

**Score**: `I-ACC = (points_earned / 4.0) * 100%`

**Example**:
```javascript
// Perfect (100%): All components correct
import { WorkOS } from '@workos-inc/node';
const workos = new WorkOS(process.env.WORKOS_API_KEY);

// Partial (75%): Missing proper variable name
import { WorkOS } from '@workos-inc/node';
const w = new WorkOS(process.env.WORKOS_API_KEY);

// Poor (50%): Wrong location, missing config
import { WorkOS } from '@workos-inc/node';
const workos = new WorkOS(); // Inside a route handler
```

### Metric 2: Integration Point Accuracy (IPA)

**Precision**: Correct SDK calls / Total SDK calls inserted
**Recall**: Correct SDK calls / Required SDK calls
**F1 Score**: `2 * (Precision * Recall) / (Precision + Recall)`

**Example**:
```javascript
// Required SDK calls: 3 (authorize, callback, getUserProfile)
// Agent inserted: 4 calls
// Correct calls: 2 (authorize, callback)
// Incorrect: 1 (wrong method), 1 (unnecessary call)

Precision = 2/4 = 0.50 (50% of inserted calls are correct)
Recall = 2/3 = 0.67 (67% of required calls are present)
F1 = 2 * (0.50 * 0.67) / (0.50 + 0.67) = 0.57 (57%)
```

### Metric 3: Configuration Completeness (C-COMP)

**Weighted Score**:
- Required env vars present: 40%
- Optional env vars appropriate: 20%
- Config file structure: 20%
- No hardcoded secrets: 20%

**Score**: `C-COMP = weighted_sum * 100%`

### Metric 4: Functional Correctness (F-CORR)

**Automated Test Suite**:
```bash
# Run functional tests
npm test

# Test categories:
- Unit tests: SDK initialization works
- Integration tests: Full auth flow works
- E2E tests: User can authenticate successfully
```

**Score**: `F-CORR = (passing_tests / total_tests) * 100%`

### Metric 5: Code Quality (CQ)

**Components**:
- ✅ Syntax validity (runs without errors)
- ✅ Type safety (TypeScript: no `any`, proper types)
- ✅ Error handling (try-catch blocks present)
- ✅ Security (no hardcoded secrets, proper env var usage)
- ✅ Best practices (follows SDK documentation patterns)

**Score**: `CQ = (criteria_met / 5) * 100%`

### Metric 6: Semantic Similarity (SEM-SIM)

Use code embeddings to measure similarity:
```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('microsoft/codebert-base')

# Get embeddings
ground_truth_embedding = model.encode(ground_truth_code)
generated_embedding = model.encode(generated_code)

# Calculate cosine similarity
semantic_similarity = cosine_similarity(
    ground_truth_embedding,
    generated_embedding
)
```

**Score**: `SEM-SIM = cosine_similarity * 100%`

### Overall SDK-Bench Score

```
Overall = (0.20 * I-ACC) + (0.25 * IPA-F1) + (0.15 * C-COMP) +
          (0.25 * F-CORR) + (0.10 * CQ) + (0.05 * SEM-SIM)
```

**Weights Rationale**:
- Functional correctness most important (25%)
- Integration accuracy critical (25%)
- Initialization foundation (20%)
- Configuration security (15%)
- Code quality matters (10%)
- Semantic similarity bonus (5%)

---

## Implementation Phases

### Phase 1: Proof of Concept (4 weeks)

**Goal**: Validate concept with ONE SDK

**SDK Choice**: Clerk (Reasoning: excellent docs, clear patterns, multiple frameworks)

**Deliverables**:
1. **Week 1**: Data collection
   - Mine 50-100 repositories using Clerk
   - Extract 50 integration examples
   - Categorize by task type (init, middleware, hooks)

2. **Week 2**: Dataset creation
   - Create input/output pairs for 50 samples
   - Write metadata for each sample
   - Create 3 task types: initialization, middleware, React hooks

3. **Week 3**: Evaluation pipeline
   - Build automated test runner
   - Implement metrics calculation
   - Create validation scripts

4. **Week 4**: Baseline testing
   - Test Claude 3.5 Sonnet
   - Test GPT-4
   - Test GitHub Copilot
   - Analyze results, identify gaps

**Success Criteria**:
- 50 working samples with passing tests
- Metrics pipeline functional
- Baseline LLM performance measured
- Clear understanding of what "correct" means

### Phase 2: Expansion (4 weeks)

**Goal**: Add 2 more SDKs, create transformed dataset

**New SDKs**: WorkOS (auth), DevCycle (feature flags)

**Deliverables**:
1. **Week 5-6**: Multi-SDK dataset
   - 150 total samples (50 per SDK)
   - Consistent metadata format
   - Cross-framework coverage (Express, Next.js, Fastify)

2. **Week 7**: Transformation tool
   - Build AST-based transformer
   - Implement 6 transformation types
   - Generate SDK-Bench-T

3. **Week 8**: Validation & testing
   - Verify transformed code works
   - Run generalization tests
   - Measure performance drop on SDK-Bench-T

**Success Criteria**:
- 150 original + 150 transformed samples
- Transformation preserves semantics (100% test pass rate)
- Clear generalization gap identified (target: 10-20% drop)

### Phase 3: Scale & Refine (4 weeks)

**Goal**: Expand to 5+ SDKs, multiple languages

**New SDKs**: LanceDB, Mixpanel, Auth0

**Deliverables**:
1. **Week 9-10**: Dataset expansion
   - 500+ total samples
   - Add Python support
   - Add TypeScript variants

2. **Week 11**: Advanced metrics
   - Security analysis
   - Performance profiling
   - Best practices scoring

3. **Week 12**: Documentation & release
   - Complete documentation
   - Example notebooks
   - Public dataset release
   - Leaderboard setup

**Success Criteria**:
- 500+ samples across 6 SDKs
- Multi-language support (JavaScript, TypeScript, Python)
- Comprehensive evaluation suite
- Ready for public use

### Phase 4: Agent Testing & Iteration (Ongoing)

**Goal**: Test specialized agents, iterate based on results

**Agents to Test**:
- General-purpose: Claude, GPT-4, Gemini
- Code-specialized: GitHub Copilot, Cursor, Replit
- Custom agents: Naptha onboarding agent

**Deliverables**:
- Regular benchmark runs
- Leaderboard updates
- Performance analysis
- Dataset improvements based on findings

---

## Success Criteria

### Benchmark Quality Metrics

**Dataset Quality**:
- ✅ 500+ samples across 5+ SDKs
- ✅ 3+ task types per SDK
- ✅ 3+ frameworks per language
- ✅ 100% of samples have passing tests
- ✅ Clear, consistent metadata

**Evaluation Validity**:
- ✅ Metrics correlate with human judgment (>0.7 correlation)
- ✅ Automated tests catch incorrect integrations (>90% accuracy)
- ✅ Generalization gap measurable (SDK-Bench-T)
- ✅ Results reproducible

### Performance Targets (Initial)

**Expected LLM Performance**:
| Metric | Target (Good) | Stretch Goal |
|--------|--------------|--------------|
| Initialization (I-ACC) | 70% | 85% |
| Integration (IPA F1) | 60% | 75% |
| Configuration (C-COMP) | 75% | 90% |
| Functional (F-CORR) | 50% | 70% |
| Code Quality (CQ) | 65% | 80% |
| Overall Score | 60% | 75% |

**Generalization (SDK-Bench-T)**:
- Performance drop < 20% (compared to SDK-Bench-O)
- Some models may show larger drops (indicates memorization)

### Research Questions to Answer

1. **Can LLMs correctly initialize SDKs?**
   - Hypothesis: Yes, >70% accuracy (simpler than full integration)

2. **Can they integrate SDKs across multiple files?**
   - Hypothesis: Moderate success, 50-60% (multi-file is harder)

3. **Does providing SDK documentation help?**
   - Hypothesis: +20-30% improvement with docs in context

4. **How much does framework affect performance?**
   - Hypothesis: Express > Next.js > Fastify (based on training data prevalence)

5. **Is there a memorization vs. reasoning gap?**
   - Hypothesis: 10-20% drop on SDK-Bench-T (transformed code)

6. **Which SDKs are easier to integrate?**
   - Hypothesis: Clerk > DevCycle > WorkOS > LanceDB (by complexity)

---

## Next Steps

### Immediate Actions (Week 1)

1. **Validate with stakeholders**
   - Review this plan
   - Agree on Phase 1 scope
   - Confirm SDK choice (Clerk)

2. **Set up infrastructure**
   - GitHub repo for SDK-Bench
   - Data storage (samples, metadata)
   - Evaluation pipeline skeleton

3. **Start data collection**
   - Mine Clerk repositories
   - Extract first 10 samples manually
   - Validate metadata schema

4. **Build evaluation basics**
   - Simple test runner
   - Basic metrics calculation
   - Manual validation workflow

### Questions to Resolve

1. **Licensing**: Can we redistribute code samples? (Similar to LogBench)
2. **SDK versions**: Focus on latest, or include multiple versions?
3. **Language priority**: JavaScript first, or multi-language from start?
4. **Public vs Private**: Release dataset publicly or keep internal?
5. **Collaboration**: Partner with SDK companies for validation?

---

## References

### LogBench Paper
- **Title**: "Exploring the Effectiveness of LLMs in Automated Logging Generation: An Empirical Study"
- **Authors**: Li et al., IEEE TSE 2024
- **ArXiv**: https://arxiv.org/abs/2307.05950
- **Key Insights Applied**:
  - High-quality repository selection (20+ stars, 100+ commits)
  - Dual dataset (original + transformed for generalization)
  - Ingredient-specific metrics (levels, variables, text)
  - Semantic-preserving transformations
  - Automated evaluation pipeline

### Target SDKs Documentation
- **WorkOS**: https://workos.com/docs
- **Clerk**: https://clerk.com/docs
- **DevCycle**: https://docs.devcycle.com
- **LanceDB**: https://lancedb.github.io/lancedb/
- **Mixpanel**: https://developer.mixpanel.com
- **Auth0**: https://auth0.com/docs

### Related Benchmarks
- **LogBench**: Logging statement generation
- **AL-Bench**: Automatic logging benchmark
- **HumanEval**: Code generation (algorithmic)
- **MBPP**: Programming problems
- **CodeXGLUE**: Code intelligence tasks

---

**Document Version**: 1.0
**Last Updated**: November 2024
**Status**: Proposal / Planning
**Next Review**: After Phase 1 completion
