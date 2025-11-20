#!/usr/bin/env python3
"""
Week 2: Dataset Construction Script

Builds 50 SDK-Bench samples across 5 task types using patterns from Week 1.
"""

import os
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import click
from tqdm import tqdm


class SampleBuilder:
    """Build SDK-Bench samples from mined repositories."""

    def __init__(self, patterns_file: Path, mined_repos_file: Path, output_dir: Path):
        """Initialize sample builder."""
        self.patterns = self._load_json(patterns_file)
        self.mined_repos = self._load_json(mined_repos_file)
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Sample counts per task type
        self.task_counts = {
            1: 15,  # Initialization
            2: 15,  # Middleware
            3: 10,  # Hooks
            4: 7,   # Complete Integration
            5: 3,   # Migration v4→v5
        }

    def _load_json(self, file_path: Path) -> Dict:
        """Load JSON file."""
        with open(file_path) as f:
            return json.load(f)

    def build_all_samples(self):
        """Build all 50 samples."""
        print("\n🚀 SDK-Bench: Sample Construction")
        print(f"   Output: {self.output_dir}")
        print(f"   Total samples: {sum(self.task_counts.values())}\n")

        samples_created = []
        sample_counter = 1

        for task_type, count in self.task_counts.items():
            print(f"\n📦 Building Task Type {task_type} samples ({count} samples)...")

            for i in range(count):
                sample_id = f"task{task_type}_{self._task_name(task_type)}_{sample_counter:03d}"

                try:
                    sample_dir = self.output_dir / sample_id
                    self._create_sample(task_type, sample_id, sample_dir, i)
                    samples_created.append({
                        "sample_id": sample_id,
                        "task_type": task_type,
                        "created_at": datetime.now().isoformat()
                    })
                    print(f"   ✓ {sample_id}")
                    sample_counter += 1
                except Exception as e:
                    print(f"   ✗ Failed to create {sample_id}: {e}")

        # Save dataset manifest
        manifest = {
            "dataset_version": "1.0",
            "created_at": datetime.now().isoformat(),
            "total_samples": len(samples_created),
            "by_task_type": {
                task_type: len([s for s in samples_created if s["task_type"] == task_type])
                for task_type in self.task_counts.keys()
            },
            "samples": samples_created
        }

        manifest_path = self.output_dir / "dataset_manifest.json"
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)

        print(f"\n✅ Created {len(samples_created)} samples")
        print(f"   Manifest: {manifest_path}")

    def _task_name(self, task_type: int) -> str:
        """Get task type name."""
        names = {
            1: "init",
            2: "middleware",
            3: "hooks",
            4: "complete",
            5: "migration"
        }
        return names[task_type]

    def _create_sample(self, task_type: int, sample_id: str, sample_dir: Path, index: int):
        """Create a single sample."""
        # Create directory structure
        input_dir = sample_dir / "input"
        expected_dir = sample_dir / "expected"
        tests_dir = sample_dir / "tests"

        for dir in [input_dir, expected_dir, tests_dir]:
            dir.mkdir(parents=True, exist_ok=True)

        # Build sample based on task type
        if task_type == 1:
            self._build_init_sample(sample_id, input_dir, expected_dir, tests_dir, index)
        elif task_type == 2:
            self._build_middleware_sample(sample_id, input_dir, expected_dir, tests_dir, index)
        elif task_type == 3:
            self._build_hooks_sample(sample_id, input_dir, expected_dir, tests_dir, index)
        elif task_type == 4:
            self._build_complete_sample(sample_id, input_dir, expected_dir, tests_dir, index)
        elif task_type == 5:
            self._build_migration_sample(sample_id, input_dir, expected_dir, tests_dir, index)

    # ==================== Task Type 1: Initialization ====================

    def _build_init_sample(self, sample_id: str, input_dir: Path, expected_dir: Path, tests_dir: Path, index: int):
        """Build Task 1 (Initialization) sample."""
        # Determine framework (rotate through Next.js, React, Express)
        frameworks = ["nextjs", "nextjs", "nextjs", "react", "express"]
        framework = frameworks[index % len(frameworks)]

        # Create input files (without Clerk)
        self._create_input_init(input_dir, framework)

        # Create expected files (with Clerk)
        self._create_expected_init(expected_dir, framework)

        # Create test file
        self._create_test_init(tests_dir, framework)

        # Create metadata
        metadata = self._create_metadata_init(sample_id, framework, input_dir, expected_dir)
        with open(expected_dir / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)

    def _create_input_init(self, input_dir: Path, framework: str):
        """Create input files for initialization task."""
        if framework == "nextjs":
            # Create Next.js App Router structure
            app_dir = input_dir / "app"
            app_dir.mkdir(parents=True, exist_ok=True)

            # layout.tsx (without ClerkProvider)
            layout_content = '''export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        {/* TODO: Add Clerk authentication provider */}
        {children}
      </body>
    </html>
  )
}
'''
            (app_dir / "layout.tsx").write_text(layout_content)

            # page.tsx
            page_content = '''export default function Home() {
  return (
    <main>
      <h1>Welcome</h1>
      <p>This app needs Clerk authentication.</p>
    </main>
  )
}
'''
            (app_dir / "page.tsx").write_text(page_content)

            # package.json (without Clerk)
            package_json = {
                "name": "nextjs-app",
                "version": "0.1.0",
                "private": True,
                "scripts": {
                    "dev": "next dev",
                    "build": "next build",
                    "start": "next start"
                },
                "dependencies": {
                    "react": "^18.2.0",
                    "react-dom": "^18.2.0",
                    "next": "^14.0.0"
                }
            }
            with open(input_dir / "package.json", "w") as f:
                json.dump(package_json, f, indent=2)

            # .env.example (empty)
            (input_dir / ".env.example").write_text("# Add environment variables here\n")

        elif framework == "react":
            # Create React SPA structure
            src_dir = input_dir / "src"
            src_dir.mkdir(parents=True, exist_ok=True)

            # index.tsx (without ClerkProvider)
            index_content = '''import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

root.render(
  <React.StrictMode>
    {/* TODO: Add Clerk authentication provider */}
    <App />
  </React.StrictMode>
);
'''
            (src_dir / "index.tsx").write_text(index_content)

            # App.tsx
            app_content = '''function App() {
  return (
    <div>
      <h1>Welcome</h1>
      <p>This app needs Clerk authentication.</p>
    </div>
  );
}

export default App;
'''
            (src_dir / "App.tsx").write_text(app_content)

            # package.json
            package_json = {
                "name": "react-app",
                "version": "0.1.0",
                "dependencies": {
                    "react": "^18.2.0",
                    "react-dom": "^18.2.0",
                    "react-router-dom": "^6.20.0"
                }
            }
            with open(input_dir / "package.json", "w") as f:
                json.dump(package_json, f, indent=2)

            (input_dir / ".env.example").write_text("# Add environment variables here\n")

    def _create_expected_init(self, expected_dir: Path, framework: str):
        """Create expected files with Clerk initialization."""
        if framework == "nextjs":
            app_dir = expected_dir / "app"
            app_dir.mkdir(parents=True, exist_ok=True)

            # layout.tsx (with ClerkProvider)
            layout_content = '''import { ClerkProvider } from '@clerk/nextjs'

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <ClerkProvider>
      <html lang="en">
        <body>{children}</body>
      </html>
    </ClerkProvider>
  )
}
'''
            (app_dir / "layout.tsx").write_text(layout_content)

            # page.tsx (same as input)
            page_content = '''export default function Home() {
  return (
    <main>
      <h1>Welcome</h1>
      <p>This app needs Clerk authentication.</p>
    </main>
  )
}
'''
            (app_dir / "page.tsx").write_text(page_content)

            # package.json (with Clerk)
            package_json = {
                "name": "nextjs-app",
                "version": "0.1.0",
                "private": True,
                "scripts": {
                    "dev": "next dev",
                    "build": "next build",
                    "start": "next start"
                },
                "dependencies": {
                    "react": "^18.2.0",
                    "react-dom": "^18.2.0",
                    "next": "^14.0.0",
                    "@clerk/nextjs": "^5.0.0"
                }
            }
            with open(expected_dir / "package.json", "w") as f:
                json.dump(package_json, f, indent=2)

            # .env.example (with Clerk vars)
            env_content = '''# Clerk Configuration
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
CLERK_SECRET_KEY=sk_test_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
'''
            (expected_dir / ".env.example").write_text(env_content)

        elif framework == "react":
            src_dir = expected_dir / "src"
            src_dir.mkdir(parents=True, exist_ok=True)

            # index.tsx (with ClerkProvider)
            index_content = '''import React from 'react';
import ReactDOM from 'react-dom/client';
import { ClerkProvider } from '@clerk/clerk-react';
import App from './App';

const publishableKey = process.env.REACT_APP_CLERK_PUBLISHABLE_KEY!;

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

root.render(
  <React.StrictMode>
    <ClerkProvider publishableKey={publishableKey}>
      <App />
    </ClerkProvider>
  </React.StrictMode>
);
'''
            (src_dir / "index.tsx").write_text(index_content)

            # App.tsx (same)
            app_content = '''function App() {
  return (
    <div>
      <h1>Welcome</h1>
      <p>This app needs Clerk authentication.</p>
    </div>
  );
}

export default App;
'''
            (src_dir / "App.tsx").write_text(app_content)

            # package.json
            package_json = {
                "name": "react-app",
                "version": "0.1.0",
                "dependencies": {
                    "react": "^18.2.0",
                    "react-dom": "^18.2.0",
                    "react-router-dom": "^6.20.0",
                    "@clerk/clerk-react": "^5.0.0"
                }
            }
            with open(expected_dir / "package.json", "w") as f:
                json.dump(package_json, f, indent=2)

            env_content = '''# Clerk Configuration
REACT_APP_CLERK_PUBLISHABLE_KEY=pk_test_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
'''
            (expected_dir / ".env.example").write_text(env_content)

    def _create_test_init(self, tests_dir: Path, framework: str):
        """Create test file for initialization."""
        if framework == "nextjs":
            test_content = '''import { describe, it, expect } from '@jest/globals';
import { readFileSync, existsSync } from 'fs';
import { join } from 'path';

describe('Clerk Initialization - Next.js', () => {
  const layoutPath = join(__dirname, '../expected/app/layout.tsx');
  const packagePath = join(__dirname, '../expected/package.json');
  const envPath = join(__dirname, '../expected/.env.example');

  it('should have ClerkProvider in layout.tsx', () => {
    const layout = readFileSync(layoutPath, 'utf-8');
    expect(layout).toContain('ClerkProvider');
    expect(layout).toContain("from '@clerk/nextjs'");
  });

  it('should have @clerk/nextjs in package.json', () => {
    const pkg = JSON.parse(readFileSync(packagePath, 'utf-8'));
    expect(pkg.dependencies).toHaveProperty('@clerk/nextjs');
  });

  it('should have required environment variables', () => {
    const env = readFileSync(envPath, 'utf-8');
    expect(env).toContain('NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY');
    expect(env).toContain('CLERK_SECRET_KEY');
  });
});
'''
            (tests_dir / "init.test.ts").write_text(test_content)

        elif framework == "react":
            test_content = '''import { describe, it, expect } from '@jest/globals';
import { readFileSync } from 'fs';
import { join } from 'path';

describe('Clerk Initialization - React', () => {
  const indexPath = join(__dirname, '../expected/src/index.tsx');
  const packagePath = join(__dirname, '../expected/package.json');
  const envPath = join(__dirname, '../expected/.env.example');

  it('should have ClerkProvider in index.tsx', () => {
    const index = readFileSync(indexPath, 'utf-8');
    expect(index).toContain('ClerkProvider');
    expect(index).toContain("from '@clerk/clerk-react'");
    expect(index).toContain('publishableKey');
  });

  it('should have @clerk/clerk-react in package.json', () => {
    const pkg = JSON.parse(readFileSync(packagePath, 'utf-8'));
    expect(pkg.dependencies).toHaveProperty('@clerk/clerk-react');
  });

  it('should have publishable key in .env.example', () => {
    const env = readFileSync(envPath, 'utf-8');
    expect(env).toContain('REACT_APP_CLERK_PUBLISHABLE_KEY');
  });
});
'''
            (tests_dir / "init.test.ts").write_text(test_content)

    def _create_metadata_init(self, sample_id: str, framework: str, input_dir: Path, expected_dir: Path) -> Dict:
        """Create metadata for initialization sample."""
        return {
            "sample_id": sample_id,
            "task_type": 1,
            "task_name": "initialization",
            "framework": framework,
            "clerk_version": "5.0.0",
            "difficulty": "easy",
            "estimated_lines": 10,
            "description": "Initialize Clerk authentication by wrapping the application with ClerkProvider",
            "ground_truth": {
                "ingredients": {
                    "initialization": {
                        "location": "app/layout.tsx" if framework == "nextjs" else "src/index.tsx",
                        "pattern": "ClerkProvider wrapper",
                        "imports": ["@clerk/nextjs" if framework == "nextjs" else "@clerk/clerk-react"]
                    },
                    "configuration": {
                        "env_vars": [
                            "NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY",
                            "CLERK_SECRET_KEY"
                        ] if framework == "nextjs" else [
                            "REACT_APP_CLERK_PUBLISHABLE_KEY"
                        ],
                        "provider_props": ["publishableKey"] if framework == "react" else [],
                        "optional_config": []
                    }
                }
            },
            "evaluation_targets": {
                "i_acc": {
                    "correct_file": "app/layout.tsx" if framework == "nextjs" else "src/index.tsx",
                    "correct_pattern": "ClerkProvider",
                    "correct_imports": ["ClerkProvider from @clerk/nextjs" if framework == "nextjs" else "ClerkProvider from @clerk/clerk-react"]
                },
                "c_comp": {
                    "required_env_vars": 2 if framework == "nextjs" else 1,
                    "optional_env_vars": 0
                },
                "f_corr": {
                    "test_command": "npm test -- init.test.ts",
                    "expected_pass": True
                }
            }
        }

    # ==================== Task Type 2: Middleware ====================

    def _build_middleware_sample(self, sample_id: str, input_dir: Path, expected_dir: Path, tests_dir: Path, index: int):
        """Build Task 2 (Middleware) sample."""
        # All middleware samples are Next.js (authMiddleware is Next.js specific)
        self._create_input_middleware(input_dir)
        self._create_expected_middleware(expected_dir, index)
        self._create_test_middleware(tests_dir)

        metadata = self._create_metadata_middleware(sample_id, index)
        with open(expected_dir / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)

    def _create_input_middleware(self, input_dir: Path):
        """Create input files for middleware task."""
        # middleware.ts (basic Next.js middleware without auth)
        middleware_content = '''import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  // TODO: Add Clerk authentication middleware
  return NextResponse.next()
}

export const config = {
  matcher: ['/((?!.+\\.[\\w]+$|_next).*)', '/', '/(api|trpc)(.*)'],
}
'''
        (input_dir / "middleware.ts").write_text(middleware_content)

        # app/dashboard/page.tsx (unprotected)
        app_dir = input_dir / "app" / "dashboard"
        app_dir.mkdir(parents=True, exist_ok=True)

        dashboard_content = '''export default function Dashboard() {
  return (
    <div>
      <h1>Dashboard</h1>
      <p>This should be protected but currently isn't.</p>
    </div>
  )
}
'''
        (app_dir / "page.tsx").write_text(dashboard_content)

        # app/api/protected/route.ts
        api_dir = input_dir / "app" / "api" / "protected"
        api_dir.mkdir(parents=True, exist_ok=True)

        api_content = '''import { NextResponse } from 'next/server'

export async function GET() {
  // TODO: This API route should be protected
  return NextResponse.json({ message: 'This should be protected' })
}
'''
        (api_dir / "route.ts").write_text(api_content)

    def _create_expected_middleware(self, expected_dir: Path, index: int):
        """Create expected files with middleware."""
        # Vary the publicRoutes pattern
        public_routes_variants = [
            '["/", "/about"]',
            '["/", "/api/webhook"]',
            '["/"]',
        ]
        public_routes = public_routes_variants[index % len(public_routes_variants)]

        # middleware.ts (with authMiddleware)
        middleware_content = f'''import {{ authMiddleware }} from "@clerk/nextjs/server"

export default authMiddleware({{
  publicRoutes: {public_routes}
}})

export const config = {{
  matcher: ['/((?!.+\\.[\\w]+$|_next).*)', '/', '/(api|trpc)(.*)'],
}}
'''
        (expected_dir / "middleware.ts").write_text(middleware_content)

        # app/dashboard/page.tsx (same as input)
        app_dir = expected_dir / "app" / "dashboard"
        app_dir.mkdir(parents=True, exist_ok=True)

        dashboard_content = '''export default function Dashboard() {
  return (
    <div>
      <h1>Dashboard</h1>
      <p>This should be protected but currently isn't.</p>
    </div>
  )
}
'''
        (app_dir / "page.tsx").write_text(dashboard_content)

        # app/api/protected/route.ts (same as input)
        api_dir = expected_dir / "app" / "api" / "protected"
        api_dir.mkdir(parents=True, exist_ok=True)

        api_content = '''import { NextResponse } from 'next/server'

export async function GET() {
  // TODO: This API route should be protected
  return NextResponse.json({ message: 'This should be protected' })
}
'''
        (api_dir / "route.ts").write_text(api_content)

    def _create_test_middleware(self, tests_dir: Path):
        """Create test for middleware."""
        test_content = '''import { describe, it, expect } from '@jest/globals';
import { readFileSync } from 'fs';
import { join } from 'path';

describe('Clerk Middleware', () => {
  const middlewarePath = join(__dirname, '../expected/middleware.ts');

  it('should have authMiddleware imported', () => {
    const middleware = readFileSync(middlewarePath, 'utf-8');
    expect(middleware).toContain('authMiddleware');
    expect(middleware).toContain("from '@clerk/nextjs/server'");
  });

  it('should export authMiddleware as default', () => {
    const middleware = readFileSync(middlewarePath, 'utf-8');
    expect(middleware).toContain('export default authMiddleware');
  });

  it('should have publicRoutes configuration', () => {
    const middleware = readFileSync(middlewarePath, 'utf-8');
    expect(middleware).toContain('publicRoutes:');
  });

  it('should have matcher config', () => {
    const middleware = readFileSync(middlewarePath, 'utf-8');
    expect(middleware).toContain('export const config');
    expect(middleware).toContain('matcher:');
  });
});
'''
        (tests_dir / "middleware.test.ts").write_text(test_content)

    def _create_metadata_middleware(self, sample_id: str, index: int) -> Dict:
        """Create metadata for middleware sample."""
        return {
            "sample_id": sample_id,
            "task_type": 2,
            "task_name": "middleware",
            "framework": "nextjs",
            "clerk_version": "5.0.0",
            "difficulty": "medium",
            "estimated_lines": 15,
            "description": "Add Clerk authentication middleware to protect routes",
            "ground_truth": {
                "ingredients": {
                    "initialization": {
                        "location": "middleware.ts",
                        "pattern": "authMiddleware",
                        "imports": ["@clerk/nextjs/server"]
                    },
                    "configuration": {
                        "middleware_config": ["publicRoutes"],
                        "optional_config": ["ignoredRoutes"]
                    },
                    "integration_points": [
                        {"location": "middleware.ts", "type": "route_protection"}
                    ]
                }
            },
            "evaluation_targets": {
                "i_acc": {
                    "correct_file": "middleware.ts",
                    "correct_pattern": "authMiddleware",
                    "correct_imports": ["authMiddleware from @clerk/nextjs/server"]
                },
                "c_comp": {
                    "required_middleware_config": ["publicRoutes"],
                    "optional_middleware_config": ["ignoredRoutes"]
                },
                "ipa": {
                    "expected_protection_points": ["middleware.ts"]
                },
                "f_corr": {
                    "test_command": "npm test -- middleware.test.ts",
                    "expected_pass": True
                }
            }
        }

    # ==================== Task Type 3: Hooks ====================

    def _build_hooks_sample(self, sample_id: str, input_dir: Path, expected_dir: Path, tests_dir: Path, index: int):
        """Build Task 3 (Hooks) sample."""
        # Vary the hook type
        hook_types = ["useUser", "useAuth", "useClerk"]
        hook_type = hook_types[index % len(hook_types)]

        self._create_input_hooks(input_dir)
        self._create_expected_hooks(expected_dir, hook_type)
        self._create_test_hooks(tests_dir, hook_type)

        metadata = self._create_metadata_hooks(sample_id, hook_type)
        with open(expected_dir / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)

    def _create_input_hooks(self, input_dir: Path):
        """Create input files for hooks task."""
        components_dir = input_dir / "components"
        components_dir.mkdir(parents=True, exist_ok=True)

        # UserProfile component without auth
        profile_content = '''export default function UserProfile() {
  // TODO: Add Clerk hook to get user data
  return (
    <div>
      <h1>User Profile</h1>
      <p>User data should appear here</p>
    </div>
  )
}
'''
        (components_dir / "UserProfile.tsx").write_text(profile_content)

    def _create_expected_hooks(self, expected_dir: Path, hook_type: str):
        """Create expected files with hooks."""
        components_dir = expected_dir / "components"
        components_dir.mkdir(parents=True, exist_ok=True)

        if hook_type == "useUser":
            profile_content = '''\'use client\'
import { useUser } from '@clerk/nextjs'

export default function UserProfile() {
  const { isLoaded, isSignedIn, user } = useUser()

  if (!isLoaded) {
    return <div>Loading...</div>
  }

  if (!isSignedIn) {
    return <div>Please sign in</div>
  }

  return (
    <div>
      <h1>Welcome, {user.firstName}!</h1>
      <p>Email: {user.primaryEmailAddress?.emailAddress}</p>
    </div>
  )
}
'''
        elif hook_type == "useAuth":
            profile_content = '''\'use client\'
import { useAuth } from '@clerk/nextjs'

export default function UserProfile() {
  const { isLoaded, isSignedIn, userId } = useAuth()

  if (!isLoaded) {
    return <div>Loading...</div>
  }

  if (!isSignedIn) {
    return <div>Please sign in</div>
  }

  return (
    <div>
      <h1>User Profile</h1>
      <p>User ID: {userId}</p>
    </div>
  )
}
'''
        else:  # useClerk
            profile_content = '''\'use client\'
import { useClerk } from '@clerk/nextjs'

export default function UserProfile() {
  const { user, signOut } = useClerk()

  if (!user) {
    return <div>Please sign in</div>
  }

  return (
    <div>
      <h1>Welcome, {user.firstName}!</h1>
      <button onClick={() => signOut()}>Sign Out</button>
    </div>
  )
}
'''
        (components_dir / "UserProfile.tsx").write_text(profile_content)

    def _create_test_hooks(self, tests_dir: Path, hook_type: str):
        """Create test for hooks."""
        test_content = f'''import {{ describe, it, expect }} from '@jest/globals';
import {{ readFileSync }} from 'fs';
import {{ join }} from 'path';

describe('Clerk Hooks - {hook_type}', () => {{
  const profilePath = join(__dirname, '../expected/components/UserProfile.tsx');

  it('should have {hook_type} imported', () => {{
    const profile = readFileSync(profilePath, 'utf-8');
    expect(profile).toContain('{hook_type}');
    expect(profile).toContain("from '@clerk/nextjs'");
  }});

  it('should use client directive', () => {{
    const profile = readFileSync(profilePath, 'utf-8');
    expect(profile).toContain("'use client'");
  }});

  it('should call {hook_type} hook', () => {{
    const profile = readFileSync(profilePath, 'utf-8');
    expect(profile).toContain('{hook_type}()');
  }});

  it('should handle loading state', () => {{
    const profile = readFileSync(profilePath, 'utf-8');
    expect(profile).toContain('isLoaded') || expect(profile).toContain('user');
  }});
}});
'''
        (tests_dir / "hooks.test.ts").write_text(test_content)

    def _create_metadata_hooks(self, sample_id: str, hook_type: str) -> Dict:
        """Create metadata for hooks sample."""
        return {
            "sample_id": sample_id,
            "task_type": 3,
            "task_name": "hooks",
            "framework": "nextjs",
            "clerk_version": "5.0.0",
            "difficulty": "medium",
            "estimated_lines": 20,
            "description": f"Use {hook_type} hook to access user authentication data",
            "ground_truth": {
                "ingredients": {
                    "integration_points": [
                        {
                            "location": "components/UserProfile.tsx",
                            "type": "hook_usage",
                            "hook": hook_type
                        }
                    ]
                }
            },
            "evaluation_targets": {
                "i_acc": {
                    "correct_file": "components/UserProfile.tsx",
                    "correct_pattern": hook_type,
                    "correct_imports": [f"{hook_type} from @clerk/nextjs"]
                },
                "ipa": {
                    "expected_hooks": [hook_type]
                },
                "f_corr": {
                    "test_command": "npm test -- hooks.test.ts",
                    "expected_pass": True
                }
            }
        }

    # ==================== Task Type 4: Complete Integration ====================

    def _build_complete_sample(self, sample_id: str, input_dir: Path, expected_dir: Path, tests_dir: Path, index: int):
        """Build Task 4 (Complete Integration) sample."""
        self._create_input_complete(input_dir)
        self._create_expected_complete(expected_dir)
        self._create_test_complete(tests_dir)

        metadata = self._create_metadata_complete(sample_id)
        with open(expected_dir / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)

    def _create_input_complete(self, input_dir: Path):
        """Create input files for complete integration task."""
        # app/layout.tsx (no ClerkProvider)
        app_dir = input_dir / "app"
        app_dir.mkdir(parents=True, exist_ok=True)

        layout_content = '''export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        {/* TODO: Add Clerk authentication */}
        {children}
      </body>
    </html>
  )
}
'''
        (app_dir / "layout.tsx").write_text(layout_content)

        # middleware.ts (basic)
        middleware_content = '''import { NextResponse } from 'next/server'

export function middleware(request: any) {
  return NextResponse.next()
}
'''
        (input_dir / "middleware.ts").write_text(middleware_content)

        # app/dashboard/page.tsx
        dashboard_dir = app_dir / "dashboard"
        dashboard_dir.mkdir(parents=True, exist_ok=True)

        dashboard_content = '''export default function Dashboard() {
  // TODO: Add authentication check
  return <div>Dashboard</div>
}
'''
        (dashboard_dir / "page.tsx").write_text(dashboard_content)

        # app/api/user/route.ts
        api_dir = app_dir / "api" / "user"
        api_dir.mkdir(parents=True, exist_ok=True)

        api_content = '''import { NextResponse } from 'next/server'

export async function GET() {
  // TODO: Protect this API route
  return NextResponse.json({ message: 'User data' })
}
'''
        (api_dir / "route.ts").write_text(api_content)

    def _create_expected_complete(self, expected_dir: Path):
        """Create expected files with complete integration."""
        # app/layout.tsx (with ClerkProvider)
        app_dir = expected_dir / "app"
        app_dir.mkdir(parents=True, exist_ok=True)

        layout_content = '''import { ClerkProvider } from '@clerk/nextjs'

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <ClerkProvider>
      <html lang="en">
        <body>{children}</body>
      </html>
    </ClerkProvider>
  )
}
'''
        (app_dir / "layout.tsx").write_text(layout_content)

        # middleware.ts (with authMiddleware)
        middleware_content = '''import { authMiddleware } from "@clerk/nextjs/server"

export default authMiddleware({
  publicRoutes: ["/"]
})

export const config = {
  matcher: ['/((?!.+\\.[\\w]+$|_next).*)', '/', '/(api|trpc)(.*)'],
}
'''
        (expected_dir / "middleware.ts").write_text(middleware_content)

        # app/dashboard/page.tsx (with currentUser)
        dashboard_dir = app_dir / "dashboard"
        dashboard_dir.mkdir(parents=True, exist_ok=True)

        dashboard_content = '''import { currentUser } from '@clerk/nextjs/server'
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
'''
        (dashboard_dir / "page.tsx").write_text(dashboard_content)

        # app/api/user/route.ts (with auth)
        api_dir = app_dir / "api" / "user"
        api_dir.mkdir(parents=True, exist_ok=True)

        api_content = '''import { auth } from '@clerk/nextjs/server'
import { NextResponse } from 'next/server'

export async function GET() {
  const { userId } = auth()

  if (!userId) {
    return new Response('Unauthorized', { status: 401 })
  }

  return NextResponse.json({ userId, message: 'User data' })
}
'''
        (api_dir / "route.ts").write_text(api_content)

        # .env.example
        env_content = '''# Clerk Configuration
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
CLERK_SECRET_KEY=sk_test_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/dashboard
'''
        (expected_dir / ".env.example").write_text(env_content)

    def _create_test_complete(self, tests_dir: Path):
        """Create test for complete integration."""
        test_content = '''import { describe, it, expect } from '@jest/globals';
import { readFileSync, existsSync } from 'fs';
import { join } from 'path';

describe('Clerk Complete Integration', () => {
  it('should have ClerkProvider in layout', () => {
    const layout = readFileSync(join(__dirname, '../expected/app/layout.tsx'), 'utf-8');
    expect(layout).toContain('ClerkProvider');
  });

  it('should have authMiddleware in middleware', () => {
    const middleware = readFileSync(join(__dirname, '../expected/middleware.ts'), 'utf-8');
    expect(middleware).toContain('authMiddleware');
  });

  it('should protect dashboard with currentUser', () => {
    const dashboard = readFileSync(join(__dirname, '../expected/app/dashboard/page.tsx'), 'utf-8');
    expect(dashboard).toContain('currentUser');
  });

  it('should protect API route with auth()', () => {
    const api = readFileSync(join(__dirname, '../expected/app/api/user/route.ts'), 'utf-8');
    expect(api).toContain('auth()');
    expect(api).toContain('userId');
  });

  it('should have environment variables configured', () => {
    const env = readFileSync(join(__dirname, '../expected/.env.example'), 'utf-8');
    expect(env).toContain('NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY');
    expect(env).toContain('CLERK_SECRET_KEY');
  });
});
'''
        (tests_dir / "integration.test.ts").write_text(test_content)

    def _create_metadata_complete(self, sample_id: str) -> Dict:
        """Create metadata for complete integration sample."""
        return {
            "sample_id": sample_id,
            "task_type": 4,
            "task_name": "complete_integration",
            "framework": "nextjs",
            "clerk_version": "5.0.0",
            "difficulty": "hard",
            "estimated_lines": 50,
            "description": "Complete Clerk integration with all 4 ingredients: initialization, configuration, middleware, and API protection",
            "ground_truth": {
                "ingredients": {
                    "initialization": {
                        "location": "app/layout.tsx",
                        "pattern": "ClerkProvider",
                        "imports": ["@clerk/nextjs"]
                    },
                    "configuration": {
                        "env_vars": [
                            "NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY",
                            "CLERK_SECRET_KEY",
                            "NEXT_PUBLIC_CLERK_SIGN_IN_URL",
                            "NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL"
                        ],
                        "middleware_config": ["publicRoutes"]
                    },
                    "integration_points": [
                        {"location": "middleware.ts", "type": "authMiddleware"},
                        {"location": "app/dashboard/page.tsx", "type": "currentUser"},
                        {"location": "app/api/user/route.ts", "type": "auth()"}
                    ]
                }
            },
            "evaluation_targets": {
                "i_acc": {
                    "correct_files": ["app/layout.tsx", "middleware.ts", "app/dashboard/page.tsx", "app/api/user/route.ts"],
                    "all_patterns_present": True
                },
                "c_comp": {
                    "required_env_vars": 4
                },
                "ipa": {
                    "expected_protection_points": 3
                },
                "f_corr": {
                    "test_command": "npm test -- integration.test.ts",
                    "expected_pass": True
                }
            }
        }

    # ==================== Task Type 5: Migration ====================

    def _build_migration_sample(self, sample_id: str, input_dir: Path, expected_dir: Path, tests_dir: Path, index: int):
        """Build Task 5 (Migration v4→v5) sample."""
        # Vary the migration scenario
        scenarios = ["api_route", "middleware", "server_component"]
        scenario = scenarios[index % len(scenarios)]

        self._create_input_migration(input_dir, scenario)
        self._create_expected_migration(expected_dir, scenario)
        self._create_test_migration(tests_dir, scenario)

        metadata = self._create_metadata_migration(sample_id, scenario)
        with open(expected_dir / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)

    def _create_input_migration(self, input_dir: Path, scenario: str):
        """Create input files for migration task (v4 code)."""
        if scenario == "api_route":
            # Old v4 API route using getAuth
            api_dir = input_dir / "app" / "api" / "data"
            api_dir.mkdir(parents=True, exist_ok=True)

            api_content = '''import { getAuth } from '@clerk/nextjs/server'
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export async function GET(req: NextRequest) {
  const { userId } = getAuth(req)

  if (!userId) {
    return new Response('Unauthorized', { status: 401 })
  }

  return NextResponse.json({ userId, data: 'Protected data' })
}
'''
            (api_dir / "route.ts").write_text(api_content)

        elif scenario == "middleware":
            # Old v4 middleware using ClerkMiddleware
            middleware_content = '''import { authMiddleware } from "@clerk/nextjs"

export default authMiddleware({
  publicRoutes: ["/"]
})

export const config = {
  matcher: ['/((?!.*\\..*|_next).*)', '/', '/(api|trpc)(.*)'],
}
'''
            (input_dir / "middleware.ts").write_text(middleware_content)

        else:  # server_component
            # Old v4 server component using currentUser
            app_dir = input_dir / "app" / "profile"
            app_dir.mkdir(parents=True, exist_ok=True)

            profile_content = '''import { currentUser } from '@clerk/nextjs/app-beta'

export default async function Profile() {
  const user = await currentUser()

  if (!user) {
    return <div>Not signed in</div>
  }

  return (
    <div>
      <h1>{user.firstName}</h1>
      <p>{user.emailAddresses[0]?.emailAddress}</p>
    </div>
  )
}
'''
            (app_dir / "page.tsx").write_text(profile_content)

    def _create_expected_migration(self, expected_dir: Path, scenario: str):
        """Create expected files with v5 code."""
        if scenario == "api_route":
            # New v5 API route using auth()
            api_dir = expected_dir / "app" / "api" / "data"
            api_dir.mkdir(parents=True, exist_ok=True)

            api_content = '''import { auth } from '@clerk/nextjs/server'
import { NextResponse } from 'next/server'

export async function GET() {
  const { userId } = auth()

  if (!userId) {
    return new Response('Unauthorized', { status: 401 })
  }

  return NextResponse.json({ userId, data: 'Protected data' })
}
'''
            (api_dir / "route.ts").write_text(api_content)

        elif scenario == "middleware":
            # New v5 middleware using clerkMiddleware
            middleware_content = '''import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server'

const isPublicRoute = createRouteMatcher(['/'])

export default clerkMiddleware((auth, request) => {
  if (!isPublicRoute(request)) {
    auth().protect()
  }
})

export const config = {
  matcher: ['/((?!.*\\..*|_next).*)', '/', '/(api|trpc)(.*)'],
}
'''
            (expected_dir / "middleware.ts").write_text(middleware_content)

        else:  # server_component
            # New v5 server component
            app_dir = expected_dir / "app" / "profile"
            app_dir.mkdir(parents=True, exist_ok=True)

            profile_content = '''import { currentUser } from '@clerk/nextjs/server'

export default async function Profile() {
  const user = await currentUser()

  if (!user) {
    return <div>Not signed in</div>
  }

  return (
    <div>
      <h1>{user.firstName}</h1>
      <p>{user.emailAddresses[0]?.emailAddress}</p>
    </div>
  )
}
'''
            (app_dir / "page.tsx").write_text(profile_content)

    def _create_test_migration(self, tests_dir: Path, scenario: str):
        """Create test for migration."""
        if scenario == "api_route":
            test_content = '''import { describe, it, expect } from '@jest/globals';
import { readFileSync } from 'fs';
import { join } from 'path';

describe('Migration: API Route v4→v5', () => {
  const apiPath = join(__dirname, '../expected/app/api/data/route.ts');

  it('should use auth() instead of getAuth()', () => {
    const api = readFileSync(apiPath, 'utf-8');
    expect(api).toContain('auth()');
    expect(api).not.toContain('getAuth(req)');
  });

  it('should import from @clerk/nextjs/server', () => {
    const api = readFileSync(apiPath, 'utf-8');
    expect(api).toContain("from '@clerk/nextjs/server'");
  });

  it('should not take request parameter in GET', () => {
    const api = readFileSync(apiPath, 'utf-8');
    expect(api).toContain('export async function GET()');
  });
});
'''
        elif scenario == "middleware":
            test_content = '''import { describe, it, expect } from '@jest/globals';
import { readFileSync } from 'fs';
import { join } from 'path';

describe('Migration: Middleware v4→v5', () => {
  const middlewarePath = join(__dirname, '../expected/middleware.ts');

  it('should use clerkMiddleware instead of authMiddleware', () => {
    const middleware = readFileSync(middlewarePath, 'utf-8');
    expect(middleware).toContain('clerkMiddleware');
    expect(middleware).not.toContain('authMiddleware');
  });

  it('should use createRouteMatcher for public routes', () => {
    const middleware = readFileSync(middlewarePath, 'utf-8');
    expect(middleware).toContain('createRouteMatcher');
  });

  it('should have auth().protect() pattern', () => {
    const middleware = readFileSync(middlewarePath, 'utf-8');
    expect(middleware).toContain('auth().protect()');
  });
});
'''
        else:  # server_component
            test_content = '''import { describe, it, expect } from '@jest/globals';
import { readFileSync } from 'fs';
import { join } from 'path';

describe('Migration: Server Component v4→v5', () => {
  const profilePath = join(__dirname, '../expected/app/profile/page.tsx');

  it('should import from @clerk/nextjs/server', () => {
    const profile = readFileSync(profilePath, 'utf-8');
    expect(profile).toContain("from '@clerk/nextjs/server'");
    expect(profile).not.toContain('/app-beta');
  });

  it('should use currentUser from stable path', () => {
    const profile = readFileSync(profilePath, 'utf-8');
    expect(profile).toContain('currentUser');
  });
});
'''
        (tests_dir / "migration.test.ts").write_text(test_content)

    def _create_metadata_migration(self, sample_id: str, scenario: str) -> Dict:
        """Create metadata for migration sample."""
        return {
            "sample_id": sample_id,
            "task_type": 5,
            "task_name": "migration_v4_to_v5",
            "framework": "nextjs",
            "clerk_version_from": "4.x",
            "clerk_version_to": "5.0.0",
            "difficulty": "hard",
            "estimated_lines": 25,
            "description": f"Migrate Clerk v4 to v5: {scenario} breaking changes",
            "migration_scenario": scenario,
            "breaking_changes": {
                "api_route": ["getAuth(req) → auth()", "Remove request parameter"],
                "middleware": ["authMiddleware → clerkMiddleware", "publicRoutes → createRouteMatcher"],
                "server_component": ["@clerk/nextjs/app-beta → @clerk/nextjs/server"]
            }[scenario],
            "ground_truth": {
                "changes_required": [
                    {
                        "file": {
                            "api_route": "app/api/data/route.ts",
                            "middleware": "middleware.ts",
                            "server_component": "app/profile/page.tsx"
                        }[scenario],
                        "changes": ["Update imports", "Update function calls", "Update patterns"]
                    }
                ]
            },
            "evaluation_targets": {
                "i_acc": {
                    "v5_patterns_present": True,
                    "v4_patterns_absent": True
                },
                "f_corr": {
                    "test_command": "npm test -- migration.test.ts",
                    "expected_pass": True
                }
            }
        }


@click.command()
@click.option("--patterns", default="data/patterns.json", help="Path to patterns.json")
@click.option("--mined-repos", default="data/mined-repos.json", help="Path to mined-repos.json")
@click.option("--output", default="samples", help="Output directory for samples")
@click.option("--task-type", type=int, help="Build only specific task type (1-5)")
def main(patterns: str, mined_repos: str, output: str, task_type: Optional[int]):
    """Build SDK-Bench samples from Week 1 data."""

    patterns_path = Path(patterns)
    mined_repos_path = Path(mined_repos)
    output_dir = Path(output)

    if not patterns_path.exists():
        print(f"❌ Error: {patterns} not found")
        print("   Run: python -m scripts.extract_patterns first")
        return

    if not mined_repos_path.exists():
        print(f"❌ Error: {mined_repos} not found")
        print("   Run: python -m scripts.mine_repos first")
        return

    builder = SampleBuilder(patterns_path, mined_repos_path, output_dir)

    if task_type:
        print(f"Building only Task Type {task_type} samples...")
        # TODO: Implement single task type building
        print("Not yet implemented - building all samples")

    builder.build_all_samples()
    print("\n✨ Sample construction complete!")
    print(f"   Next: Implement tests and validate samples")


if __name__ == "__main__":
    main()
