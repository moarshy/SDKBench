# SDK-Bench Quick Start Guide

## Setup (5 minutes)

### 1. Install uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or with pip
pip install uv
```

### 2. Configure API keys (IMPORTANT - Do this first!)

```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your GitHub token
# Get one at: https://github.com/settings/tokens
# Required scope: public_repo (for public repos)
```

## Week 1: Data Collection

### Step 1: Search for Clerk repositories (Day 1-2)

```bash
# Use 'uv run' - it auto-creates venv and installs dependencies!
uv run search-repos --max-repos 100
```

This will:
- Search GitHub for repositories using `@clerk/nextjs`, `@clerk/clerk-react`, etc.
- Filter by stars (>10), recent activity (<6 months)
- Classify by framework (Next.js, Express, React)
- Save results to `data/repositories.json`

**Output:** `data/repositories.json` with ~100 Clerk repositories

### Step 2: Clone and mine repositories (Day 3-4)

```bash
# Mine first 20 repos (for testing)
uv run mine-repos --limit 20

# Or mine all
uv run mine-repos
```

This will:
- Clone repositories to `data/cloned-repos/`
- Find all Clerk-related files
- Detect framework and Clerk version
- Save analysis to `data/mined-repos.json`

**Warning:** This can take 10-30 minutes and use ~2-5 GB disk space

### Step 3: Extract patterns (Day 5)

```bash
uv run extract-patterns
```

This will:
- Analyze all cloned repositories
- Extract initialization, middleware, hooks, and API protection patterns
- Identify suitable repositories for each task type
- Generate `data/patterns.json` and `data/patterns.md`

### Week 1 Expected Results

After completing Week 1, you should have:

```
data/
├── repositories.json       # ~100 Clerk repos metadata
├── mined-repos.json        # Detailed analysis of repos
├── patterns.json           # Extracted patterns (JSON)
├── patterns.md             # Patterns documentation
└── cloned-repos/           # ~2-5 GB of cloned repos
    ├── user_repo1/
    ├── user_repo2/
    └── ...
```

## Week 2: Dataset Construction

### Build 50 SDK-Bench Samples

```bash
# Build all 50 samples (15 init, 15 middleware, 10 hooks, 7 complete, 3 migration)
uv run build-samples
```

This will:
- Create 50 samples in `samples/` directory
- Each sample includes:
  - `input/` - starter code without Clerk
  - `expected/` - complete implementation with Clerk
  - `tests/` - automated Jest tests
  - `metadata.json` - ground truth annotations
- Generate `samples/dataset_manifest.json` with statistics

### Task Type Details

#### **Task 1: Initialization (15 samples)**
Initialize Clerk by wrapping the app with ClerkProvider.

**Frameworks:** Next.js (App Router), React SPA, Express
**Key patterns:**
- Next.js: `ClerkProvider` in `app/layout.tsx`
- React: `ClerkProvider` in `src/index.tsx` with `publishableKey` prop
- Environment variables: `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`, `CLERK_SECRET_KEY`

**Example:**
```typescript
// expected/app/layout.tsx
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
```

#### **Task 2: Middleware (15 samples)**
Add authentication middleware to protect routes.

**Framework:** Next.js only (authMiddleware is Next.js-specific)
**Key patterns:**
- `authMiddleware` from `@clerk/nextjs/server`
- `publicRoutes` configuration (varies per sample)
- Matcher config for route protection

**Example:**
```typescript
// expected/middleware.ts
import { authMiddleware } from "@clerk/nextjs/server"

export default authMiddleware({
  publicRoutes: ["/", "/about"]
})

export const config = {
  matcher: ['/((?!.+\\.[\\w]+$|_next).*)', '/', '/(api|trpc)(.*)'],
}
```

#### **Task 3: Hooks (10 samples)**
Use Clerk hooks to access user authentication data in components.

**Framework:** Next.js
**Hook types:**
- `useUser()` - Get user object with profile data
- `useAuth()` - Get auth state and userId
- `useClerk()` - Access Clerk instance with methods like signOut

**Example:**
```typescript
// expected/components/UserProfile.tsx
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

#### **Task 4: Complete Integration (7 samples)**
Full Clerk integration with all 4 ingredients.

**Framework:** Next.js
**Components:**
1. **Initialization:** ClerkProvider in `app/layout.tsx`
2. **Configuration:** All env vars + middleware config
3. **Route Protection:** authMiddleware in `middleware.ts`
4. **Server Component:** `currentUser()` in dashboard
5. **API Protection:** `auth()` in API routes

**Example:**
```typescript
// expected/app/api/user/route.ts
import { auth } from '@clerk/nextjs/server'
import { NextResponse } from 'next/server'

export async function GET() {
  const { userId } = auth()

  if (!userId) {
    return new Response('Unauthorized', { status: 401 })
  }

  return NextResponse.json({ userId, message: 'User data' })
}
```

#### **Task 5: Migration v4→v5 (3 samples)**
Migrate Clerk implementation from v4 to v5.

**Framework:** Next.js
**Migration scenarios:**
1. **API Route:** `getAuth(req)` → `auth()` (remove request param)
2. **Middleware:** `authMiddleware` → `clerkMiddleware` + `createRouteMatcher`
3. **Server Component:** `@clerk/nextjs/app-beta` → `@clerk/nextjs/server`

**Example:**
```typescript
// V4 (input)
import { getAuth } from '@clerk/nextjs/server'
export async function GET(req: NextRequest) {
  const { userId } = getAuth(req)
  // ...
}

// V5 (expected)
import { auth } from '@clerk/nextjs/server'
export async function GET() {
  const { userId } = auth()
  // ...
}
```

### Week 2 Expected Results

After completing Week 2, you should have:

```
samples/
├── task1_init_001/
│   ├── input/
│   │   ├── app/layout.tsx
│   │   ├── package.json
│   │   └── .env.example
│   ├── expected/
│   │   ├── app/layout.tsx
│   │   ├── package.json
│   │   ├── .env.example
│   │   └── metadata.json
│   └── tests/
│       └── init.test.ts
├── task1_init_002/ through task1_init_015/
├── task2_middleware_016/ through task2_middleware_030/
├── task3_hooks_031/ through task3_hooks_040/
├── task4_complete_041/ through task4_complete_047/
├── task5_migration_048/ through task5_migration_050/
└── dataset_manifest.json
```

**Statistics:**
- Total samples: 50
- Task 1 (Init): 15 samples
- Task 2 (Middleware): 15 samples
- Task 3 (Hooks): 10 samples
- Task 4 (Complete): 7 samples
- Task 5 (Migration): 3 samples

## Troubleshooting

### Week 1 Issues

#### "GITHUB_TOKEN not found"
- Create a token at https://github.com/settings/tokens
- Add it to `.env`: `GITHUB_TOKEN=your_token_here`

#### "Rate limit exceeded"
- GitHub API has rate limits (5,000 requests/hour for authenticated)
- Wait an hour or use `--limit` flag to process fewer repos

#### "Failed to clone" errors
- Some repos may be private or deleted
- This is normal, script will continue with successful ones

#### Disk space issues
- Use `--limit` flag to clone fewer repos
- Delete `data/cloned-repos/` after pattern extraction if needed

### Week 2 Issues

#### "patterns.json not found"
- Run Week 1 scripts first: `uv run extract-patterns`

#### "mined-repos.json not found"
- Run: `uv run mine-repos`

## Quick Command Reference

```bash
# Week 1: Data Collection
uv run search-repos --max-repos 100    # Search GitHub
uv run mine-repos --limit 20           # Clone & analyze (test with 20)
uv run mine-repos                      # Clone & analyze (all)
uv run extract-patterns                # Extract patterns

# Week 2: Dataset Construction
uv run build-samples                   # Build all 50 samples

# Development
pytest                                 # Run tests
black scripts/                         # Format code
ruff check scripts/                    # Lint code
mypy scripts/                          # Type check
```

## Next Steps

**After Week 2:**
- **Week 3:** Evaluation Pipeline (implement 6 metrics)
- **Week 4:** Baseline Evaluation (test LLMs)

See [docs/clerk-poc-plan.md](docs/clerk-poc-plan.md) for full plan.

## Project Structure

```
SDKBench/
├── scripts/           # Data collection and sample building
│   ├── search_repos.py
│   ├── mine_repos.py
│   ├── extract_patterns.py
│   └── build_samples.py
├── data/             # Week 1 outputs
│   ├── repositories.json
│   ├── mined-repos.json
│   ├── patterns.json
│   ├── patterns.md
│   └── cloned-repos/
├── samples/          # Week 2 outputs (50 samples)
│   ├── task1_init_001/
│   ├── ...
│   └── dataset_manifest.json
├── evaluator/        # Week 3 (evaluation pipeline)
├── results/          # Week 4 (baseline results)
└── docs/             # Documentation
```
