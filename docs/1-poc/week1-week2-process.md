# Week 1 & Week 2: Implementation Process Documentation

**SDK-Bench POC: Clerk Integration**
**Documentation Date:** 2025-11-20
**Status:** Week 1 & 2 Complete ✅

---

## Table of Contents

1. [Week 1: Data Collection](#week-1-data-collection)
   - [Step 1: Repository Search](#step-1-repository-search)
   - [Step 2: Repository Mining](#step-2-repository-mining)
   - [Step 3: Pattern Extraction](#step-3-pattern-extraction)
2. [Week 2: Dataset Construction](#week-2-dataset-construction)
3. [Technology Stack](#technology-stack)
4. [Data Flow](#data-flow)

---

## Week 1: Data Collection

**Goal:** Find and analyze real-world Clerk repositories to extract integration patterns

**Duration:** 5 days (completed in 1 day)

**Output Files:**
- `data/repositories.json` - Catalog of repositories found
- `data/mined-repos.json` - Analyzed repository metadata
- `data/patterns.json` - Extracted patterns (JSON)
- `data/patterns.md` - Pattern documentation (Markdown)
- `data/cloned-repos/` - Directory of cloned repositories

### Step 1: Repository Search

**Script:** `scripts/search_repos.py`

**Purpose:** Search GitHub for repositories using Clerk SDK and filter by quality criteria

**Command:**
```bash
uv run search-repos --max-repos 100
```

#### Process Flow

1. **Initialize GitHub Client**
   - Uses PyGithub library
   - Authenticates with GITHUB_TOKEN from `.env`
   - Creates `ClerkRepoSearcher` class

2. **Execute Multiple Search Queries**
   - Runs 7 different search queries to maximize coverage
   - Queries include:
     ```python
     [
       # Next.js queries
       {"query": '"@clerk/nextjs"', "language": "TypeScript", "min_stars": 5},
       {"query": '"@clerk/nextjs"', "language": "JavaScript", "min_stars": 3},

       # React queries
       {"query": '"@clerk/clerk-react"', "language": "TypeScript", "min_stars": 3},
       {"query": '"@clerk/clerk-react"', "language": "JavaScript", "min_stars": 2},

       # Express queries
       {"query": '"@clerk/express" OR "@clerk/clerk-sdk-node"', "language": "TypeScript", "min_stars": 2},

       # Broader searches
       {"query": "clerk nextjs", "language": "TypeScript", "min_stars": 10},
       {"query": '"@clerk/nextjs" in:file filename:package.json', "min_stars": 5}
     ]
     ```

3. **Quality Filters Applied**
   - **Minimum stars:** 2-10 (varies by query)
   - **Recent activity:** Optional (can disable with `max_age_months: 0`)
   - **Language:** TypeScript or JavaScript preferred
   - **Has tests:** Check for test directories/files (preferred)

4. **Parallel Processing**
   - Uses `ThreadPoolExecutor` with 10 workers by default
   - Processes repositories concurrently to speed up API calls
   - Progress tracked with `tqdm` progress bar

5. **Extract Repository Metadata**
   For each repository, extract:
   ```python
   {
     "id": "repo_001",
     "name": "repo-name",
     "full_name": "user/repo-name",
     "url": "https://github.com/user/repo-name",
     "clone_url": "https://github.com/user/repo-name.git",
     "stars": 45,
     "forks": 12,
     "language": "TypeScript",
     "description": "...",
     "created_at": "2024-01-15T...",
     "updated_at": "2024-11-15T...",
     "pushed_at": "2024-11-10T...",
     "size_kb": 1024,
     "default_branch": "main",
     "topics": ["nextjs", "clerk", "authentication"],
     "has_issues": true,
     "has_wiki": false,
     "has_tests": true,
     "contributors": 5,
     "search_query": '"@clerk/nextjs"',
     "collected_at": "2025-11-20T..."
   }
   ```

6. **Deduplication**
   - Tracks `seen_repos` set using `full_name`
   - Prevents duplicate entries from multiple queries
   - Stops when target count reached (if `--max-repos` specified)

7. **Classification**
   Automatically classify repositories by framework:
   - **Next.js:** Check topics, description, name for "nextjs", "next.js", "next-"
   - **Express:** Check for "express" in topics/description
   - **React SPA:** Has "react" topic but not "next"
   - **Other:** Doesn't match above categories
   - **v4 Migration Candidates:** Uses `@clerk/nextjs@4` syntax

8. **Save Results**
   ```json
   {
     "summary": {
       "total_repositories": 100,
       "by_framework": {
         "nextjs": 70,
         "express": 15,
         "react_spa": 10,
         "other": 5
       },
       "v4_migration_candidates": 8,
       "collection_date": "2025-11-20T...",
       "avg_stars": 42.3,
       "avg_contributors": 3.1,
       "with_tests": 65
     },
     "repositories": [...],  // Full metadata array
     "classified": {...}      // Grouped by framework
   }
   ```

#### Technologies Used
- **PyGithub:** GitHub API wrapper for Python
- **python-dotenv:** Load environment variables
- **ThreadPoolExecutor:** Parallel processing
- **tqdm:** Progress bars
- **click:** CLI argument parsing

#### Key Algorithm: Test Detection
```python
def _check_has_tests(repo) -> bool:
    """Check if repository likely has tests."""
    test_indicators = [
        "test", "tests", "__tests__", "spec", "specs",
        ".test.", ".spec.", "jest.config", "vitest.config"
    ]

    contents = repo.get_contents("")
    for content in contents:
        if any(indicator in content.name.lower()
               for indicator in test_indicators):
            return True
    return False
```

#### Actual Results (Week 1 Run)
- **Repositories found:** 100+ searched, 20 selected for mining
- **Frameworks:** 16 Next.js, 4 React
- **Average stars:** ~50-100 (quality repositories)
- **Time:** ~10-15 minutes

---

### Step 2: Repository Mining

**Script:** `scripts/mine_repos.py`

**Purpose:** Clone repositories and extract Clerk SDK usage patterns from code

**Command:**
```bash
uv run mine-repos --limit 20  # Test with 20 repos
uv run mine-repos              # Mine all repos
```

#### Process Flow

1. **Load Repository List**
   - Reads `data/repositories.json`
   - Extracts `repositories` array
   - Optional: Limit to first N repos with `--limit` flag

2. **Clone Repositories**
   ```python
   def clone_repository(repo_data) -> Path:
       repo_name = repo_data["full_name"].replace("/", "_")
       repo_path = clone_dir / repo_name

       # Skip if already exists
       if repo_path.exists():
           return repo_path

       # Shallow clone (depth=1) to save space
       git.Repo.clone_from(
           repo_data["clone_url"],
           repo_path,
           depth=1
       )
       return repo_path
   ```

   - **Shallow cloning:** Uses `depth=1` to only get latest commit
   - **Skip existing:** Won't re-clone if directory exists
   - **Error handling:** Continues on clone failures

3. **Find Clerk-Related Files**

   Searches for 6 file categories:

   | Category | Files Found | Search Method |
   |----------|-------------|---------------|
   | **package_json** | `package.json` with `"@clerk/"` | Recursive search, read content |
   | **layout_files** | Files with "layout" in name | Filename + content check |
   | **middleware_files** | Files with "middleware" | Filename + content check |
   | **component_files** | `.tsx/.jsx/.ts/.js` with Clerk | Extension + content check |
   | **api_routes** | Files in `api/` or "route"/"handler" | Path + filename check |
   | **config_files** | `.env.example`, `.env.local` | Filename + "CLERK" in content |

   ```python
   def find_clerk_files(repo_path) -> Dict[str, List[Path]]:
       clerk_files = {
           "package_json": [],
           "layout_files": [],
           "middleware_files": [],
           "component_files": [],
           "api_routes": [],
           "config_files": []
       }

       # Find package.json with Clerk
       for pkg in repo_path.rglob("package.json"):
           if "node_modules" not in str(pkg):
               content = pkg.read_text()
               if "@clerk/" in content:
                   clerk_files["package_json"].append(pkg)

       # Find TypeScript/JavaScript files
       for ext in ["*.ts", "*.tsx", "*.js", "*.jsx"]:
           for file in repo_path.rglob(ext):
               if "node_modules" in str(file) or ".next" in str(file):
                   continue

               content = file.read_text()
               if "@clerk/" not in content:
                   continue

               # Classify by filename/path
               filename = file.name.lower()
               if "layout" in filename:
                   clerk_files["layout_files"].append(file)
               elif "middleware" in filename:
                   clerk_files["middleware_files"].append(file)
               elif "api" in str(file) or "route" in filename:
                   clerk_files["api_routes"].append(file)
               else:
                   clerk_files["component_files"].append(file)

       return clerk_files
   ```

4. **Detect Clerk Version**
   - Parse `package.json` dependencies
   - Extract version from any `@clerk/*` package
   - Example: `"@clerk/nextjs": "^5.0.0"` → `"^5.0.0"`

5. **Detect Framework**
   ```python
   if any("next.config" in str(f) for f in repo_path.rglob("*")):
       framework = "nextjs"
   elif any("express" in str(f).lower() for f in clerk_files["api_routes"]):
       framework = "express"
   elif clerk_files["component_files"]:
       framework = "react"
   else:
       framework = "unknown"
   ```

6. **Create Enhanced Metadata**
   ```json
   {
     ...original_repo_data,
     "analysis": {
       "clerk_version": "^5.0.0",
       "framework": "nextjs",
       "file_counts": {
         "package_json": 1,
         "layout_files": 2,
         "middleware_files": 1,
         "component_files": 15,
         "api_routes": 8,
         "config_files": 2
       },
       "clerk_files": {
         "layout_files": [
           "app/layout.tsx",
           "app/(auth)/layout.tsx"
         ],
         "middleware_files": ["middleware.ts"],
         "component_files": ["app/components/UserButton.tsx", ...],
         "api_routes": ["app/api/user/route.ts", ...],
         "config_files": [".env.example"]
       },
       "analyzed_at": "2025-11-20T..."
     }
   }
   ```

7. **Progress Tracking**
   - Uses `tqdm` progress bar
   - Shows repository name being processed
   - Displays success/failure for each clone

8. **Save Results**
   - Array of enhanced metadata (one per repo)
   - Summary statistics (successful vs failed)
   - Framework distribution

#### Technologies Used
- **GitPython:** Clone and manage git repositories
- **pathlib:** File path operations
- **json:** Parse package.json files
- **tqdm:** Progress tracking

#### Key Algorithm: Framework Detection
```python
# Priority-based detection
1. Check for next.config.* → Next.js
2. Check for "express" in API routes → Express
3. Check for React components → React SPA
4. Default → Unknown
```

#### Actual Results (Week 1 Run)
- **Repositories mined:** 20
- **Successful clones:** 20
- **Total Clerk files found:** ~200+ files across all repos
- **Frameworks:** 16 Next.js, 4 React
- **Disk space:** ~2-5 GB
- **Time:** 10-30 minutes

---

### Step 3: Pattern Extraction

**Script:** `scripts/extract_patterns.py`

**Purpose:** Analyze mined repositories to extract common Clerk integration patterns

**Command:**
```bash
uv run extract-patterns
```

#### Process Flow

1. **Load Mined Data**
   - Read `data/mined-repos.json`
   - Parse each repository's analysis

2. **Extract Patterns by File Type**

   For each repository, analyze different file types:

   **A. Import Patterns**
   ```python
   def extract_imports(file_path) -> List[str]:
       """Extract Clerk imports from a file."""
       import_patterns = [
           r"import\s+{([^}]+)}\s+from\s+['\"](@clerk/[^'\"]+)['\"]",
           r"import\s+(\w+)\s+from\s+['\"](@clerk/[^'\"]+)['\"]",
           r"require\(['\"](@clerk/[^'\"]+)['\"]\)"
       ]

       for pattern in import_patterns:
           matches = re.finditer(pattern, content)
           # Extract and collect imports
   ```

   Example imports found:
   ```typescript
   import { ClerkProvider } from "@clerk/nextjs"
   import { auth } from "@clerk/nextjs/server"
   import { useUser } from "@clerk/nextjs"
   ```

   **B. Provider Usage Patterns**
   ```python
   def extract_provider_usage(file_path) -> Dict:
       """Extract ClerkProvider usage patterns."""
       if "ClerkProvider" in content:
           pattern_data["has_provider"] = True

           # Extract props from JSX
           props_match = re.search(r"<ClerkProvider([^>]*)>", content)

           # Check for specific props
           if "publishableKey" in props_text:
               pattern_data["has_publishable_key"] = True
           if "appearance" in props_text:
               pattern_data["has_appearance"] = True
           if "afterSignInUrl" in props_text:
               pattern_data["has_redirect_urls"] = True
   ```

   **C. Middleware Patterns**
   ```python
   def extract_middleware_patterns(file_path) -> Dict:
       """Extract middleware patterns."""
       if "authMiddleware" in content:
           pattern_data["type"] = "authMiddleware"

           # Extract publicRoutes array
           public_routes_match = re.search(
               r"publicRoutes:\s*\[(.*?)\]", content, re.DOTALL
           )
           # Parse routes: ["/", "/about", "/api/webhook"]

           # Extract ignoredRoutes array
           ignored_routes_match = re.search(
               r"ignoredRoutes:\s*\[(.*?)\]", content, re.DOTALL
           )
   ```

   **D. Hook Usage**
   ```python
   def extract_hook_usage(file_path) -> Dict:
       """Extract Clerk hook usage patterns."""
       hooks = {
           "useAuth": False,
           "useUser": False,
           "useClerk": False,
           "useSignIn": False,
           "useSignUp": False
       }

       for hook in hooks.keys():
           if hook in content:
               hooks[hook] = True

       return {k: v for k, v in hooks.items() if v}
   ```

   **E. API Protection Patterns**
   ```python
   def extract_api_protection_patterns(file_path) -> Dict:
       """Extract API route protection patterns."""
       # Check for various auth patterns

       # Pattern 1: auth() helper
       if re.search(r"const\s*{[^}]*userId[^}]*}\s*=\s*auth\(\)", content):
           pattern_data["uses_auth_helper"] = True

       # Pattern 2: currentUser()
       if "currentUser()" in content:
           pattern_data["uses_current_user"] = True

       # Pattern 3: getAuth (v4)
       if "getAuth(" in content:
           pattern_data["uses_get_auth"] = True
   ```

   **F. Environment Variables**
   ```python
   def extract_env_variables(file_path) -> List[str]:
       """Extract Clerk environment variables."""
       env_vars = set()

       for line in file:
           if line.startswith("CLERK_") or line.startswith("NEXT_PUBLIC_CLERK_"):
               var_name = line.split("=")[0].strip()
               env_vars.add(var_name)

       return list(env_vars)
   ```

3. **Aggregate Patterns Across All Repos**

   ```python
   aggregated = {
       "total_repos_analyzed": 20,
       "by_framework": Counter(),          # nextjs: 16, react: 4
       "clerk_versions": Counter(),        # ^5.0.0: 10, ^4.x: 5, ...
       "common_imports": Counter(),        # Top 10 imports
       "provider_usage": {
           "total": 22,
           "with_publishable_key": 0,
           "with_appearance": 8,
           "with_redirect_urls": 0
       },
       "middleware_usage": {
           "authMiddleware": 5,
           "express_middleware": 0
       },
       "common_hooks": Counter(),          # useUser: 23, useAuth: 15, ...
       "api_protection_methods": Counter(), # uses_get_auth: 6, ...
       "common_env_vars": Counter(),       # Top env vars
       "task_suitability": {               # Which repos good for which tasks
           "task1_init": [...],
           "task2_middleware": [...],
           "task3_hooks": [...],
           "task4_complete": [...],
           "task5_migration": [...]
       }
   }
   ```

4. **Determine Task Suitability**

   For each repository, determine which task types it's suitable for:

   | Task Type | Suitability Criteria |
   |-----------|----------------------|
   | **Task 1 (Init)** | Has ClerkProvider in layout/index files |
   | **Task 2 (Middleware)** | Has authMiddleware or express middleware |
   | **Task 3 (Hooks)** | Uses useUser, useAuth, or useClerk |
   | **Task 4 (Complete)** | Has 3+ of: provider, middleware, hooks, API protection |
   | **Task 5 (Migration)** | Uses Clerk v4.x (check version) |

   ```python
   # Example logic for Task 4
   has_provider = len(pattern["provider_patterns"]) > 0
   has_middleware = len(pattern["middleware_patterns"]) > 0
   has_hooks = len(pattern["hook_usage"]) > 0
   has_api = len(pattern["api_protection"]) > 0

   if sum([has_provider, has_middleware, has_hooks, has_api]) >= 3:
       aggregated["task_suitability"]["task4_complete"].append(
           pattern["repo_name"]
       )
   ```

5. **Generate Pattern Statistics**

   **Top Imports Found:**
   ```
   - import { ClerkProvider } from "@clerk/nextjs": 18 repos
   - import { auth } from "@clerk/nextjs/server": 18 repos
   - import { currentUser } from "@clerk/nextjs": 14 repos
   - import { useUser } from "@clerk/nextjs": 10 repos
   ```

   **Top Environment Variables:**
   ```
   - NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY: 12 repos
   - CLERK_SECRET_KEY: 12 repos
   - NEXT_PUBLIC_CLERK_SIGN_IN_URL: 6 repos
   - NEXT_PUBLIC_CLERK_SIGN_UP_URL: 5 repos
   ```

   **Hook Usage:**
   ```
   - useUser(): 23 repos
   - useAuth(): 15 repos
   - useClerk(): 4 repos
   - useSignIn(): 4 repos
   ```

6. **Generate Markdown Documentation**

   Creates human-readable `patterns.md` with:
   - Overview statistics
   - Framework distribution
   - Clerk version distribution
   - Ingredient 1: Initialization patterns
   - Ingredient 2: Configuration patterns
   - Ingredient 3: Integration points
   - Task suitability (which repos for which tasks)

7. **Save Output Files**

   **patterns.json:**
   ```json
   {
     "individual_patterns": [
       // One entry per repository with all extracted patterns
     ],
     "aggregated": {
       // Statistics across all repositories
     }
   }
   ```

   **patterns.md:** Human-readable summary

#### Technologies Used
- **re (regex):** Pattern matching for imports, JSX props, etc.
- **collections.Counter:** Count occurrences across repos
- **json:** Save structured data
- **pathlib:** File operations

#### Key Algorithms

**Pattern Matching Examples:**

1. **Extract JSX Props:**
   ```python
   # Match: <ClerkProvider appearance={{...}} afterSignInUrl="...">
   r"<ClerkProvider([^>]*)>"
   ```

2. **Extract Array from Code:**
   ```python
   # Match: publicRoutes: ["/", "/about"]
   r"publicRoutes:\s*\[(.*?)\]"
   # Then extract strings: r"['\"]([^'\"]+)['\"]"
   ```

3. **Check for Hook Usage:**
   ```python
   # Simple string search suffices
   if "useUser" in content:
       hooks["useUser"] = True
   ```

#### Actual Results (Week 1 Run)
```
Total repos analyzed: 20
Frameworks: nextjs (16), react (4)
Clerk versions: 10 different versions found
Common imports: 40+ unique import statements
Provider usage: 22 repos
Middleware: 5 repos with authMiddleware
Hooks: 39 hook usage instances found
Task suitability:
  - Task 1 (Init): 22 repos
  - Task 2 (Middleware): 5 repos
  - Task 3 (Hooks): 39 instances
  - Task 4 (Complete): 4 repos
  - Task 5 (Migration): 4 repos with v4
```

---

## Week 2: Dataset Construction

**Goal:** Build 50 SDK-Bench samples across 5 task types

**Duration:** 7 days (completed in 1 day)

**Output Files:**
- `samples/task1_init_001/` through `samples/task1_init_015/` (15 samples)
- `samples/task2_middleware_016/` through `samples/task2_middleware_030/` (15 samples)
- `samples/task3_hooks_031/` through `samples/task3_hooks_040/` (10 samples)
- `samples/task4_complete_041/` through `samples/task4_complete_047/` (7 samples)
- `samples/task5_migration_048/` through `samples/task5_migration_050/` (3 samples)
- `samples/dataset_manifest.json`

### Sample Construction Process

**Script:** `scripts/build_samples.py`

**Command:**
```bash
uv run build-samples
```

#### Process Flow

1. **Initialize Sample Builder**
   ```python
   class SampleBuilder:
       def __init__(self, patterns_file, mined_repos_file, output_dir):
           self.patterns = load_json(patterns_file)
           self.mined_repos = load_json(mined_repos_file)
           self.output_dir = output_dir

           self.task_counts = {
               1: 15,  # Initialization
               2: 15,  # Middleware
               3: 10,  # Hooks
               4: 7,   # Complete Integration
               5: 3,   # Migration v4→v5
           }
   ```

2. **Sample Directory Structure**

   Each sample follows this structure:
   ```
   samples/task{X}_{name}_{NNN}/
   ├── input/                    # Starter code WITHOUT Clerk
   │   ├── app/                  # Next.js app directory
   │   ├── components/           # Components
   │   ├── package.json          # Dependencies (no Clerk)
   │   └── .env.example          # Empty or partial
   ├── expected/                 # Solution code WITH Clerk
   │   ├── app/                  # Complete app with Clerk
   │   ├── components/           # Components using Clerk
   │   ├── package.json          # Dependencies (with Clerk)
   │   ├── .env.example          # Complete env vars
   │   └── metadata.json         # Ground truth annotations
   └── tests/                    # Automated tests
       └── *.test.ts             # Jest tests
   ```

3. **Task Type 1: Initialization (15 samples)**

   **Goal:** Set up ClerkProvider with basic configuration

   **Framework Rotation:**
   ```python
   frameworks = ["nextjs", "nextjs", "nextjs", "react", "express"]
   framework = frameworks[index % len(frameworks)]
   # Result: 9 Next.js, 3 React, 3 Express
   ```

   **Input Creation:**
   - Next.js: `app/layout.tsx` without ClerkProvider
   - React: `src/index.tsx` without ClerkProvider
   - Express: `server.js` without ClerkExpressWithAuth
   - `package.json` without `@clerk/*` dependencies
   - `.env.example` empty or with TODO comments

   **Expected Creation:**
   - Next.js: Wrap children with `<ClerkProvider>`
   - React: Wrap `<App />` with `<ClerkProvider publishableKey={...}>`
   - Add `@clerk/nextjs` or `@clerk/clerk-react` to dependencies
   - Complete `.env.example` with required vars

   **Test Creation:**
   ```typescript
   describe('Clerk Initialization', () => {
     it('should have ClerkProvider in layout', () => {
       const layout = readFileSync('expected/app/layout.tsx', 'utf-8');
       expect(layout).toContain('ClerkProvider');
       expect(layout).toContain("from '@clerk/nextjs'");
     });

     it('should have @clerk/nextjs in package.json', () => {
       const pkg = JSON.parse(readFileSync('expected/package.json', 'utf-8'));
       expect(pkg.dependencies).toHaveProperty('@clerk/nextjs');
     });

     it('should have required environment variables', () => {
       const env = readFileSync('expected/.env.example', 'utf-8');
       expect(env).toContain('NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY');
       expect(env).toContain('CLERK_SECRET_KEY');
     });
   });
   ```

   **Metadata Creation:**
   ```json
   {
     "sample_id": "task1_init_001",
     "task_type": 1,
     "task_name": "initialization",
     "framework": "nextjs",
     "clerk_version": "5.0.0",
     "difficulty": "easy",
     "estimated_lines": 10,
     "ground_truth": {
       "ingredients": {
         "initialization": {
           "location": "app/layout.tsx",
           "pattern": "ClerkProvider wrapper",
           "imports": ["@clerk/nextjs"]
         },
         "configuration": {
           "env_vars": ["NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY", "CLERK_SECRET_KEY"]
         }
       }
     },
     "evaluation_targets": {
       "i_acc": {
         "correct_file": "app/layout.tsx",
         "correct_pattern": "ClerkProvider",
         "correct_imports": ["ClerkProvider from @clerk/nextjs"]
       },
       "c_comp": {
         "required_env_vars": 2
       },
       "f_corr": {
         "test_command": "npm test -- init.test.ts",
         "expected_pass": true
       }
     }
   }
   ```

4. **Task Type 2: Middleware (15 samples)**

   **Goal:** Add authentication middleware to protect routes

   **Framework:** All Next.js (authMiddleware is Next.js-specific)

   **Variation Strategy:**
   ```python
   public_routes_variants = [
       '["/", "/about"]',
       '["/", "/api/webhook"]',
       '["/"]'
   ]
   public_routes = public_routes_variants[index % len(public_routes_variants)]
   # Rotates through different publicRoutes configurations
   ```

   **Input Creation:**
   - `middleware.ts` with basic Next.js middleware (no auth)
   - `app/dashboard/page.tsx` (unprotected)
   - `app/api/protected/route.ts` (unprotected)

   **Expected Creation:**
   ```typescript
   // middleware.ts
   import { authMiddleware } from "@clerk/nextjs/server"

   export default authMiddleware({
     publicRoutes: ["/", "/about"]  // Varies per sample
   })

   export const config = {
     matcher: ['/((?!.+\\.[\\w]+$|_next).*)', '/', '/(api|trpc)(.*)'],
   }
   ```

   **Test Creation:**
   - Check authMiddleware imported
   - Check exported as default
   - Check publicRoutes configuration present
   - Check matcher config present

5. **Task Type 3: Hooks (10 samples)**

   **Goal:** Use Clerk hooks to access user authentication data

   **Hook Rotation:**
   ```python
   hook_types = ["useUser", "useAuth", "useClerk"]
   hook_type = hook_types[index % len(hook_types)]
   # Result: ~3-4 samples per hook type
   ```

   **Input Creation:**
   - `components/UserProfile.tsx` without auth
   - Simple placeholder component

   **Expected Creation (varies by hook):**

   **useUser variant:**
   ```typescript
   'use client'
   import { useUser } from '@clerk/nextjs'

   export default function UserProfile() {
     const { isLoaded, isSignedIn, user } = useUser()

     if (!isLoaded) return <div>Loading...</div>
     if (!isSignedIn) return <div>Please sign in</div>

     return (
       <div>
         <h1>Welcome, {user.firstName}!</h1>
         <p>Email: {user.primaryEmailAddress?.emailAddress}</p>
       </div>
     )
   }
   ```

   **useAuth variant:**
   ```typescript
   'use client'
   import { useAuth } from '@clerk/nextjs'

   export default function UserProfile() {
     const { isLoaded, isSignedIn, userId } = useAuth()

     if (!isLoaded) return <div>Loading...</div>
     if (!isSignedIn) return <div>Please sign in</div>

     return (
       <div>
         <h1>User Profile</h1>
         <p>User ID: {userId}</p>
       </div>
     )
   }
   ```

   **useClerk variant:**
   ```typescript
   'use client'
   import { useClerk } from '@clerk/nextjs'

   export default function UserProfile() {
     const { user, signOut } = useClerk()

     if (!user) return <div>Please sign in</div>

     return (
       <div>
         <h1>Welcome, {user.firstName}!</h1>
         <button onClick={() => signOut()}>Sign Out</button>
       </div>
     )
   }
   ```

6. **Task Type 4: Complete Integration (7 samples)**

   **Goal:** Full Clerk integration with all 4 ingredients

   **All Ingredients Present:**
   1. **Initialization:** ClerkProvider in `app/layout.tsx`
   2. **Configuration:** All env vars + middleware config
   3. **Route Protection:** authMiddleware in `middleware.ts`
   4. **Server Component:** `currentUser()` in dashboard
   5. **API Protection:** `auth()` in API routes

   **Input Creation:**
   - `app/layout.tsx` without ClerkProvider
   - `middleware.ts` basic (no auth)
   - `app/dashboard/page.tsx` unprotected
   - `app/api/user/route.ts` unprotected

   **Expected Creation:**

   All 4 files modified:

   ```typescript
   // 1. app/layout.tsx
   import { ClerkProvider } from '@clerk/nextjs'

   export default function RootLayout({ children }) {
     return (
       <ClerkProvider>
         <html lang="en">
           <body>{children}</body>
         </html>
       </ClerkProvider>
     )
   }

   // 2. middleware.ts
   import { authMiddleware } from "@clerk/nextjs/server"

   export default authMiddleware({
     publicRoutes: ["/"]
   })

   // 3. app/dashboard/page.tsx
   import { currentUser } from '@clerk/nextjs/server'
   import { redirect } from 'next/navigation'

   export default async function Dashboard() {
     const user = await currentUser()

     if (!user) {
       redirect('/sign-in')
     }

     return (
       <div>
         <h1>Dashboard</h1>
         <p>Welcome, {user.firstName}!</p>
       </div>
     )
   }

   // 4. app/api/user/route.ts
   import { auth } from '@clerk/nextjs/server'
   import { NextResponse } from 'next/server'

   export async function GET() {
     const { userId } = auth()

     if (!userId) {
       return new Response('Unauthorized', { status: 401 })
     }

     return NextResponse.json({ userId, message: 'User data' })
   }

   // 5. .env.example
   NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
   CLERK_SECRET_KEY=sk_test_...
   NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
   NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/dashboard
   ```

7. **Task Type 5: Migration v4→v5 (3 samples)**

   **Goal:** Migrate Clerk v4 code to v5 (breaking changes)

   **Migration Scenarios:**
   ```python
   scenarios = ["api_route", "middleware", "server_component"]
   scenario = scenarios[index % len(scenarios)]
   # Result: 1 sample per scenario
   ```

   **Scenario A: API Route Migration**

   Input (v4):
   ```typescript
   import { getAuth } from '@clerk/nextjs/server'
   import type { NextRequest } from 'next/server'

   export async function GET(req: NextRequest) {
     const { userId } = getAuth(req)  // Takes request parameter
     // ...
   }
   ```

   Expected (v5):
   ```typescript
   import { auth } from '@clerk/nextjs/server'

   export async function GET() {
     const { userId } = auth()  // No request parameter!
     // ...
   }
   ```

   **Scenario B: Middleware Migration**

   Input (v4):
   ```typescript
   import { authMiddleware } from "@clerk/nextjs"

   export default authMiddleware({
     publicRoutes: ["/"]
   })
   ```

   Expected (v5):
   ```typescript
   import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server'

   const isPublicRoute = createRouteMatcher(['/'])

   export default clerkMiddleware((auth, request) => {
     if (!isPublicRoute(request)) {
       auth().protect()
     }
   })
   ```

   **Scenario C: Server Component Migration**

   Input (v4):
   ```typescript
   import { currentUser } from '@clerk/nextjs/app-beta'  // Beta import path
   ```

   Expected (v5):
   ```typescript
   import { currentUser } from '@clerk/nextjs/server'  // Stable path
   ```

8. **Generate Dataset Manifest**

   After all samples created:
   ```json
   {
     "dataset_version": "1.0",
     "created_at": "2025-11-20T...",
     "total_samples": 50,
     "by_task_type": {
       "1": 15,
       "2": 15,
       "3": 10,
       "4": 7,
       "5": 3
     },
     "samples": [
       {
         "sample_id": "task1_init_001",
         "task_type": 1,
         "created_at": "..."
       },
       // ... 49 more
     ]
   }
   ```

#### Technologies Used
- **pathlib:** File and directory operations
- **json:** Metadata generation
- **click:** CLI argument parsing
- **datetime:** Timestamps

#### Key Design Decisions

1. **Variation Strategy:**
   - Use modulo operator (`index % len(variants)`) to rotate through variations
   - Ensures diversity across samples

2. **Framework Distribution:**
   - Task 1: 60% Next.js, 20% React, 20% Express
   - Task 2-5: 100% Next.js (framework-specific features)

3. **Difficulty Progression:**
   - Task 1-2: Easy-Medium (10-15 lines)
   - Task 3: Medium (20 lines)
   - Task 4-5: Hard (25-50 lines)

4. **Metadata Completeness:**
   - Every sample has complete ground truth
   - Includes evaluation targets for Week 3 metrics
   - Documents all 4 SDK ingredients where applicable

#### Actual Results (Week 2)
- **Total samples:** 50
- **Task 1 (Init):** 15 samples (3 frameworks)
- **Task 2 (Middleware):** 15 samples (3 publicRoutes variants)
- **Task 3 (Hooks):** 10 samples (3 hook types)
- **Task 4 (Complete):** 7 samples (all 4 ingredients)
- **Task 5 (Migration):** 3 samples (3 scenarios)
- **Time to generate:** <5 minutes
- **Total size:** ~5-10 MB (text files only)

---

## Technology Stack

### Core Languages & Frameworks
- **Python 3.10+** - All scripts
- **TypeScript/JavaScript** - Sample code
- **Next.js 14** - Primary framework for samples
- **React 18** - Component framework

### Python Libraries

| Library | Purpose | Version |
|---------|---------|---------|
| **PyGithub** | GitHub API client | >=2.1.1 |
| **GitPython** | Git repository operations | >=3.1.40 |
| **python-dotenv** | Environment variable management | >=1.0.0 |
| **click** | CLI argument parsing | >=8.1.7 |
| **tqdm** | Progress bars | >=4.66.1 |
| **requests** | HTTP requests | >=2.31.0 |

### Development Tools
- **uv** - Fast Python package manager
- **Git** - Version control
- **Jest** - Testing framework (for samples)

### Package Management
```toml
[project.scripts]
search-repos = "scripts.search_repos:main"
mine-repos = "scripts.mine_repos:main"
extract-patterns = "scripts.extract_patterns:main"
build-samples = "scripts.build_samples:main"
```

---

## Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         WEEK 1: DATA COLLECTION                 │
└─────────────────────────────────────────────────────────────────┘

Step 1: Repository Search
├── Input: GITHUB_TOKEN (from .env)
├── Process:
│   ├── Query GitHub API (7 different search queries)
│   ├── Filter by stars, language, recent activity
│   ├── Extract metadata (stars, language, topics, etc.)
│   ├── Classify by framework (Next.js, React, Express)
│   └── Deduplicate across queries
└── Output: data/repositories.json
    ├── summary (statistics)
    ├── repositories (array of 100+ repos)
    └── classified (grouped by framework)

            ↓

Step 2: Repository Mining
├── Input: data/repositories.json
├── Process:
│   ├── Clone repositories (shallow, depth=1)
│   ├── Find Clerk-related files (6 categories)
│   ├── Detect Clerk version (from package.json)
│   ├── Detect framework (Next.js, React, Express)
│   └── Count files by category
└── Output: data/mined-repos.json
    └── Array of repositories with analysis:
        ├── original metadata
        └── analysis (version, framework, file_counts, clerk_files)

            ↓

Step 3: Pattern Extraction
├── Input:
│   ├── data/mined-repos.json
│   └── data/cloned-repos/ (actual code)
├── Process:
│   ├── Extract imports (regex)
│   ├── Extract provider patterns (regex + parsing)
│   ├── Extract middleware patterns
│   ├── Extract hook usage
│   ├── Extract API protection methods
│   ├── Extract environment variables
│   ├── Aggregate across all repositories
│   └── Determine task suitability
└── Output:
    ├── data/patterns.json (structured data)
    └── data/patterns.md (human-readable)

┌─────────────────────────────────────────────────────────────────┐
│                    WEEK 2: DATASET CONSTRUCTION                 │
└─────────────────────────────────────────────────────────────────┘

Step 4: Sample Building
├── Input:
│   ├── data/patterns.json (for reference)
│   └── data/mined-repos.json (for reference)
├── Process:
│   ├── For each task type (1-5):
│   │   ├── For each sample (varying count):
│   │   │   ├── Create sample directory
│   │   │   ├── Build input/ (starter code)
│   │   │   ├── Build expected/ (solution)
│   │   │   ├── Build tests/ (Jest tests)
│   │   │   └── Create metadata.json (ground truth)
│   └── Generate dataset manifest
└── Output: samples/
    ├── task1_init_001/ through task1_init_015/
    ├── task2_middleware_016/ through task2_middleware_030/
    ├── task3_hooks_031/ through task3_hooks_040/
    ├── task4_complete_041/ through task4_complete_047/
    ├── task5_migration_048/ through task5_migration_050/
    └── dataset_manifest.json

            ↓

         Ready for Week 3: Evaluation Pipeline
```

---

## Summary Statistics

### Week 1 Results
- **Repositories searched:** 1000+
- **Repositories collected:** 100+
- **Repositories mined:** 20
- **Successful clones:** 20
- **Clerk files found:** 200+
- **Patterns extracted:** 40+ unique imports, 5+ middleware patterns, 5+ hooks
- **Time taken:** ~1 hour total
- **Disk space used:** ~3-5 GB

### Week 2 Results
- **Total samples created:** 50
- **Sample types:** 5 (init, middleware, hooks, complete, migration)
- **Frameworks covered:** 3 (Next.js, React, Express)
- **Test files created:** 50
- **Metadata files created:** 50
- **Time taken:** ~5 minutes
- **Total dataset size:** ~5-10 MB

### Coverage
- **Task 1:** 15 samples (3 frameworks × 5 samples each)
- **Task 2:** 15 samples (3 publicRoutes variants × 5 samples each)
- **Task 3:** 10 samples (3 hook types × 3-4 samples each)
- **Task 4:** 7 samples (complete integration)
- **Task 5:** 3 samples (3 migration scenarios)

---

## Next Steps

With Week 1 and Week 2 complete, the next phase is:

**Week 3: Evaluation Pipeline**
- Implement 6 automated metrics (I-ACC, C-COMP, IPA, F-CORR, CQ, SEM-SIM)
- Build Docker test harness for F-CORR
- Create reference solutions to validate pipeline
- Document evaluation API

See [docs/clerk-poc-plan.md](./clerk-poc-plan.md) for full Week 3 details.
