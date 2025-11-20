# SDK Ingredients vs Task Types

**Purpose**: Clarify the distinction between SDK Ingredients (evaluation criteria) and Task Types (problem scenarios) in SDK-Bench.

---

## Quick Summary

| Concept | What It Is | Purpose | Example |
|---------|-----------|---------|---------|
| **SDK Ingredients** | Components needed in solution | Evaluation criteria | "Does it have initialization?" |
| **Task Types** | Problem scenarios to solve | Test difficulty levels | "Insert middleware" vs "Build complete auth" |

**Ingredients** = **WHAT** to evaluate (vertical dimension)
**Task Types** = **HOW** complex is the challenge (horizontal dimension)

---

## SDK Ingredients = WHAT (Components of a solution)

These are the **building blocks** that make up any correct SDK integration. They're inspired by LogBench's three ingredients (level, variables, text) and represent what must be present in the final code.

**Think of them as evaluation criteria** - "Does the solution have all these components?"

### The Four SDK Ingredients

#### ✅ Ingredient 1: Initialization Location

**Where** to initialize the SDK in the codebase:
- Application entry point (`src/index.js`, `src/main.py`)
- Configuration/setup files
- Provider/wrapper components
- Environment-specific initialization

#### ✅ Ingredient 2: Configuration Values

**What** SDK configuration and credentials are needed:
- API keys and secrets
- Environment-specific settings
- Optional feature flags
- Client IDs, workspace IDs, etc.

#### ✅ Ingredient 3: Integration Points

**Where** to use SDK features in code:
- Middleware integration (auth checks)
- API endpoint handlers
- React hooks/components
- Background jobs/workers
- Event handlers

#### ✅ Ingredient 4: Error Handling

**How** to handle SDK-specific errors:
- Try-catch blocks
- Fallback behavior
- Error logging
- Retry logic

### Complete Example: All 4 Ingredients

```javascript
// Example: WorkOS SSO Integration
// All 4 ingredients must be present:

// ✅ Ingredient 1: Initialization Location
import { WorkOS } from '@workos-inc/node';
const workos = new WorkOS(process.env.WORKOS_API_KEY);  // <-- WHERE to init

// ✅ Ingredient 2: Configuration Values
// .env file:
// WORKOS_API_KEY=sk_test_xxx                             // <-- WHAT config
// WORKOS_CLIENT_ID=client_xxx

// ✅ Ingredient 3: Integration Points
app.get('/auth/sso', (req, res) => {
  const url = workos.sso.getAuthorizationURL({...});    // <-- WHERE to use SDK
});

app.get('/auth/callback', async (req, res) => {
  const profile = await workos.sso.getProfile(code);    // <-- Another use point
});

// ✅ Ingredient 4: Error Handling
try {
  await workos.sso.getProfile(code);
} catch (error) {                                        // <-- HOW to handle errors
  logger.error('SSO failed:', error);
  res.redirect('/login?error=sso_failed');
}
```

### Ingredient-Based Scoring

Each ingredient is scored separately in evaluation:
- Missing initialization? → Low **I-ACC** score (Initialization Correctness)
- Missing env vars? → Low **C-COMP** score (Configuration Completeness)
- Missing integration points? → Low **IPA** score (Integration Point Accuracy)
- Missing error handling? → Low **CQ** score (Code Quality)

---

## Task Types = HOW (Types of problems/scenarios)

These are the **different challenges** we present to agents. They represent different levels of complexity and integration scenarios.

**Think of them as test cases** - "What problem are we asking the agent to solve?"

### Task Type 1: SDK Initialization (Simplest)

**Problem**: "Add SDK to a project that has none"

**Complexity**: Basic
**Files Modified**: 1-2 (main file + package.json)
**Ingredients Involved**: Primarily #1 (initialization) + #2 (configuration)

```javascript
// INPUT: Bare project
import express from 'express';
const app = express();

app.listen(3000);

// EXPECTED OUTPUT: Just initialization
import express from 'express';
import { WorkOS } from '@workos-inc/node';

const app = express();
const workos = new WorkOS(process.env.WORKOS_API_KEY);

app.listen(3000);
```

**Success Criteria**:
- SDK imported correctly ✅
- Initialized in right location ✅
- Environment variables documented ✅

---

### Task Type 2: Middleware Integration (Intermediate)

**Problem**: "Add auth middleware to protect routes"

**Complexity**: Intermediate
**Files Modified**: 2-3 (main file, middleware file, config)
**Ingredients Involved**: #1 (init), #2 (config), #3 (integration points), #4 (error handling)

```javascript
// INPUT: App with routes but no auth
const app = express();

app.get('/api/protected', (req, res) => {
  res.json({ data: 'secret' });
});

// EXPECTED OUTPUT: Middleware + protected routes
import { ClerkExpressRequireAuth } from '@clerk/clerk-sdk-node';

const app = express();

// Middleware integration point
app.use('/api', ClerkExpressRequireAuth());

app.get('/api/protected', (req, res) => {
  const { userId } = req.auth;  // Now has auth context
  res.json({ data: 'secret', userId });
});

// Error handling for auth failures
app.use((err, req, res, next) => {
  if (err.name === 'UnauthorizedError') {
    res.status(401).json({ error: 'Unauthorized' });
  }
  next(err);
});
```

**Success Criteria**:
- SDK initialized ✅
- Middleware applied correctly ✅
- Protected routes updated ✅
- Auth context used ✅
- Error handling present ✅

---

### Task Type 3: Feature Flag Integration (Specific use case)

**Problem**: "Add feature flag to conditionally show UI"

**Complexity**: Intermediate
**Files Modified**: 1 (component file)
**Ingredients Involved**: #1 (SDK init elsewhere), #3 (integration point), #4 (fallback = error handling)

```javascript
// INPUT: Component with hardcoded behavior
export function Dashboard({ user }) {
  return <StandardDashboard user={user} />;
}

// EXPECTED OUTPUT: Feature flag check
import { useVariableValue } from '@devcycle/react-client-sdk';

export function Dashboard({ user }) {
  const showNewUI = useVariableValue('new-dashboard-ui', false);

  return showNewUI
    ? <NewDashboard user={user} />
    : <StandardDashboard user={user} />;
}
```

**Success Criteria**:
- Feature flag retrieved ✅
- Default value provided (error handling) ✅
- Conditional rendering correct ✅

---

### Task Type 4: Complete Integration (Most complex)

**Problem**: "Build complete auth system from scratch"

**Complexity**: Advanced
**Files Modified**: 5+ (main, routes, middleware, config, types)
**Ingredients Involved**: ALL FOUR ingredients, multiple times across multiple files

```javascript
// INPUT: Blank Express app
import express from 'express';
const app = express();

// EXPECTED OUTPUT: Complete auth system

// File 1: src/index.js
import express from 'express';
import { WorkOS } from '@workos-inc/node';
import authRoutes from './routes/auth.js';

const app = express();
const workos = new WorkOS(process.env.WORKOS_API_KEY);  // Ingredient 1

app.use('/auth', authRoutes(workos));                    // Ingredient 3
app.listen(3000);

// File 2: src/routes/auth.js
export default function authRoutes(workos) {
  const router = express.Router();

  router.get('/sso', async (req, res) => {               // Ingredient 3
    try {
      const url = workos.sso.getAuthorizationURL({
        clientId: process.env.WORKOS_CLIENT_ID,          // Ingredient 2
        redirectUri: process.env.REDIRECT_URI,
        provider: req.query.provider
      });
      res.redirect(url);
    } catch (error) {                                     // Ingredient 4
      logger.error('SSO init failed:', error);
      res.status(500).json({ error: 'SSO initialization failed' });
    }
  });

  router.get('/callback', async (req, res) => {          // Ingredient 3
    try {
      const { code } = req.query;
      const profile = await workos.sso.getProfile(code);

      // Create session
      req.session.userId = profile.id;
      res.redirect('/dashboard');
    } catch (error) {                                     // Ingredient 4
      logger.error('SSO callback failed:', error);
      res.redirect('/login?error=sso_failed');
    }
  });

  return router;
}

// File 3: .env.example
WORKOS_API_KEY=sk_test_xxx                               // Ingredient 2
WORKOS_CLIENT_ID=client_xxx
REDIRECT_URI=http://localhost:3000/auth/callback

// File 4: package.json
{
  "dependencies": {
    "@workos-inc/node": "^7.0.0"                         // Ingredient 1
  }
}
```

**Success Criteria**:
- SDK initialized ✅
- All environment variables configured ✅
- Multiple integration points (authorize, callback, logout) ✅
- Comprehensive error handling ✅
- Session management ✅
- Multi-file organization ✅

---

### Task Type 5: Migration (Real-world scenario)

**Problem**: "Update from SDK v6 to v7 with breaking changes"

**Complexity**: Intermediate
**Files Modified**: Multiple (wherever SDK is used)
**Ingredients Involved**: Modifying existing #1, #3, possibly #4

```javascript
// INPUT: Working code with old SDK (v6)
const workos = new WorkOS(apiKey);
const user = workos.sso.getUser(code);  // v6 API method

// EXPECTED OUTPUT: Updated code (v7)
const workos = new WorkOS(process.env.WORKOS_API_KEY);
const profile = await workos.sso.getProfile(code);  // v7 API - different method name

// Also handle new error types in v7
try {
  const profile = await workos.sso.getProfile(code);
} catch (error) {
  if (error.code === 'invalid_grant') {  // v7-specific error handling
    return res.redirect('/login?expired=true');
  }
  throw error;
}
```

**Success Criteria**:
- Old API calls replaced ✅
- New initialization pattern ✅
- Breaking changes addressed ✅
- New error types handled ✅
- Tests still pass ✅

---

## Analogy: Cooking Recipe

To make this more intuitive:

### Ingredients = The components you need

- Salt (initialization)
- Flour (configuration)
- Eggs (integration points)
- Butter (error handling)

### Task Types = Different dishes you can make

- **Task 1**: "Make simple dough" (just flour + water) → Easy
- **Task 2**: "Make cake batter" (flour + eggs + butter + sugar) → Medium
- **Task 3**: "Make cookies" (different ratio, different technique) → Medium
- **Task 4**: "Make 3-course meal" (use everything, multiple times) → Hard
- **Task 5**: "Convert cake recipe from cups to grams" (adaptation) → Medium

---

## Why This Distinction Matters for Evaluation

### Ingredients Allow Granular Scoring

```python
def evaluate_sdk_integration(solution, ground_truth):
    scores = {
        'initialization': check_ingredient_1(solution),      # 85%
        'configuration': check_ingredient_2(solution),       # 90%
        'integration_points': check_ingredient_3(solution),  # 60%
        'error_handling': check_ingredient_4(solution)       # 70%
    }

    overall = weighted_average(scores)
    return scores, overall
```

**Insight**: "Agent is good at initialization (85%) and configuration (90%) but struggles with finding all integration points (60%)"

**Action**: Focus improvement on integration point detection

---

### Task Types Allow Complexity Analysis

```python
results_by_task = {
    'initialization': {
        'samples': 100,
        'avg_score': 85%,        # Simple tasks: high success
        'std_dev': 8%
    },
    'middleware': {
        'samples': 100,
        'avg_score': 70%,        # Intermediate: moderate success
        'std_dev': 12%
    },
    'feature_flags': {
        'samples': 100,
        'avg_score': 75%,        # Specific: good success
        'std_dev': 10%
    },
    'complete_integration': {
        'samples': 100,
        'avg_score': 45%,        # Complex: struggling
        'std_dev': 15%
    },
    'migration': {
        'samples': 100,
        'avg_score': 55%,        # Real-world: challenging
        'std_dev': 18%
    }
}
```

**Insight**: "Agent handles simple tasks well (85%) but drops 40 percentage points on complete integration (45%)"

**Action**: Improve multi-file reasoning and project-level understanding

---

### Cross-Analysis: Ingredients × Task Types

```python
# Which ingredients fail on which task types?
analysis = {
    'initialization': {
        'task_1': 95%,  # Easy in simple tasks
        'task_2': 90%,
        'task_3': 85%,
        'task_4': 70%,  # Harder in complex tasks (multiple files)
        'task_5': 80%
    },
    'integration_points': {
        'task_1': 90%,  # Easy - single point
        'task_2': 75%,  # Medium - multiple points
        'task_3': 80%,  # Medium - single but specific
        'task_4': 45%,  # Hard - many points across files
        'task_5': 60%   # Medium - finding all old calls
    },
    'error_handling': {
        'task_1': 60%,  # Often skipped in simple tasks
        'task_2': 70%,
        'task_3': 75%,
        'task_4': 35%,  # Frequently incomplete in complex
        'task_5': 50%
    }
}
```

**Insight**: "Error handling (Ingredient 4) is consistently weak, especially in complex tasks (35% on Task 4)"

**Action**: Enhance error handling prompts and examples

---

## In LogBench Terms

### LogBench Structure

**Ingredients** (WHAT to generate):
1. Logging Level (error/warn/info/debug/trace)
2. Logging Variables (which runtime variables to include)
3. Logging Text (the descriptive message)

**Task**:
- Single task type: "Insert one logging statement at `<LOGGING_POINT>`"
- Evaluated on all 3 ingredients simultaneously

**Example**:
```java
// Input
public void processOrder(Order order) {
    // <LOGGING_POINT>
    orderService.process(order);
}

// Expected Output
LOG.info("Processing order {} for customer {}", order.id, order.customerId);
//   ^      ^                                     ^
//  Level   Text                                Variables
```

**Evaluation**:
- Level Accuracy: Is it `info`? ✅
- Variable Selection: Has `order.id` and `order.customerId`? ✅
- Text Quality: BLEU score vs ground truth ✅

---

### SDK-Bench Structure (Extended)

**Ingredients** (WHAT to integrate):
1. Initialization Location
2. Configuration Values
3. Integration Points
4. Error Handling

**Tasks** (COMPLEXITY levels):
1. Initialization only (simplest)
2. Middleware integration (medium)
3. Feature flag usage (specific)
4. Complete integration (complex)
5. Migration/update (real-world)

**Example** (Task Type 2 - Middleware):
```javascript
// Input: App without auth
app.get('/api/protected', handler);

// Expected Output: All 4 ingredients
import { Clerk } from '@clerk/clerk-sdk-node';           // Ingredient 1
const clerk = Clerk({ apiKey: process.env.CLERK_API });

app.use(ClerkExpressRequireAuth());                      // Ingredient 3
app.get('/api/protected', (req, res) => {
  try {                                                  // Ingredient 4
    const { userId } = req.auth;                         // Ingredient 3
    res.json({ userId });
  } catch (err) {
    res.status(401).json({ error: 'Unauthorized' });    // Ingredient 4
  }
});
```

**Evaluation**:
- I-ACC: Is SDK initialized? ✅
- C-COMP: Are env vars configured? ✅
- IPA: Are middleware and auth checks present? Partial (missing logout)
- CQ: Is error handling present? ✅

---

## Example Evaluation: All Dimensions

### Scenario: Agent attempts Task Type 4 (Complete Integration)

```javascript
// Agent's solution for "Build complete WorkOS auth system"

// ✅ File 1: src/index.js
import { WorkOS } from '@workos-inc/node';
const workos = new WorkOS(process.env.WORKOS_API_KEY);  // Ingredient 1: ✅

// ✅ File 2: .env.example
// WORKOS_API_KEY=sk_test_xxx                            // Ingredient 2: ✅

// ⚠️ File 3: src/routes/auth.js
app.get('/auth/sso', (req, res) => {
  const url = workos.sso.getAuthorizationURL({...});    // Ingredient 3: ⚠️ Partial
  res.redirect(url);
});
// Missing: /auth/callback endpoint
// Missing: /auth/logout endpoint

// ❌ No error handling anywhere                         // Ingredient 4: ❌
```

### Ingredient Scores:

| Ingredient | Score | Reason |
|------------|-------|--------|
| 1. Initialization | 100% | ✅ Perfect - correct import, location, syntax |
| 2. Configuration | 100% | ✅ Perfect - .env.example with all required keys |
| 3. Integration Points | 33% | ⚠️ Partial - has authorize (1/3), missing callback & logout (0/3) |
| 4. Error Handling | 0% | ❌ None - no try-catch blocks anywhere |

### Task Performance:

| Task Type | Expected Score | Agent Score | Delta |
|-----------|---------------|-------------|-------|
| Task 4 (Complete) | 100% | 58% | -42% |

**Calculation**:
```
Overall = (0.20 × 100) + (0.15 × 100) + (0.25 × 33) + (0.10 × 0) + (0.25 × 50) + (0.05 × 65)
        = 20 + 15 + 8.25 + 0 + 12.5 + 3.25
        = 59% (rounded to 58%)
```

### Insights:

**By Ingredient**:
- Strong at initialization and configuration (100% each)
- Weak at complete integration point coverage (33%)
- Missing error handling entirely (0%)

**By Task Type**:
- Would likely score 85%+ on Task 1 (just initialization)
- Scoring only 58% on Task 4 (complete integration)
- Gap = 27+ percentage points between simple and complex tasks

**Actionable Finding**:
"Agent successfully handles individual components but struggles with multi-step, multi-file integration. Needs improvement in:
1. Identifying all required integration points
2. Adding any error handling
3. Completing full user flows (authorize → callback → session)"

---

## Matrix View: Evaluation Framework

|  | Task 1 (Init) | Task 2 (Middleware) | Task 3 (Feature Flag) | Task 4 (Complete) | Task 5 (Migration) |
|---|---|---|---|---|---|
| **Ingredient 1: Initialization** | Primary focus | Required | Required | Required (multi-file) | Modified |
| **Ingredient 2: Configuration** | Primary focus | Required | Optional | Required (comprehensive) | Updated |
| **Ingredient 3: Integration** | Minimal | Primary focus | Primary focus | Extensive (3-5 points) | All existing points |
| **Ingredient 4: Error Handling** | Basic | Important | Medium | Critical | Updated patterns |

**Reading the matrix**:
- Task 1 focuses on Ingredients 1-2
- Task 2 adds focus on Ingredient 3
- Task 4 requires mastery of all 4 ingredients
- Task 5 tests ability to update all ingredients

---

## Summary Table

| Dimension | Ingredients | Task Types |
|-----------|-------------|------------|
| **What it represents** | Components of solution | Problem complexity |
| **Evaluation use** | Granular scoring | Difficulty analysis |
| **Number of types** | 4 fixed categories | 5 complexity levels |
| **Score per...** | Ingredient (0-100%) | Task type (avg across all) |
| **Example question** | "How good is error handling?" | "How well does it handle complex integrations?" |
| **Improvement focus** | "Fix weak ingredients" | "Address complexity gaps" |
| **Analogous to** | Recipe ingredients | Recipe difficulty |

---

## Practical Usage

### For Researchers:
```python
# Analyze by ingredient
for ingredient in ['init', 'config', 'integration', 'error_handling']:
    avg_score = scores_by_ingredient[ingredient].mean()
    print(f"{ingredient}: {avg_score}%")

# Analyze by task type
for task in ['init', 'middleware', 'feature_flag', 'complete', 'migration']:
    avg_score = scores_by_task[task].mean()
    print(f"{task}: {avg_score}%")

# Cross-analysis
print(f"Error handling on complex tasks: {scores[ingredient='error_handling'][task='complete'].mean()}%")
```

### For Developers:
- **Ingredients** = What to implement in your integration
- **Task Types** = Examples of different integration scenarios

### For Agents:
- **Ingredients** = Checklist of what to include
- **Task Types** = Understanding of problem scope

---

**Document Version**: 1.0
**Last Updated**: November 2024
**Related**: plan.md (full SDK-Bench plan)
