import { describe, it, expect } from '@jest/globals';
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
