import { describe, it, expect } from '@jest/globals';
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
