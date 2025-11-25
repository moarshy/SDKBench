import { describe, it, expect } from '@jest/globals';
import { readFileSync } from 'fs';
import { join } from 'path';

describe('Clerk Hooks - useClerk', () => {
  const profilePath = join(__dirname, '../expected/components/UserProfile.tsx');

  it('should have useClerk imported', () => {
    const profile = readFileSync(profilePath, 'utf-8');
    expect(profile).toContain('useClerk');
    expect(profile).toContain("from '@clerk/nextjs'");
  });

  it('should use client directive', () => {
    const profile = readFileSync(profilePath, 'utf-8');
    expect(profile).toContain("'use client'");
  });

  it('should call useClerk hook', () => {
    const profile = readFileSync(profilePath, 'utf-8');
    expect(profile).toContain('useClerk()');
  });

  it('should handle loading state', () => {
    const profile = readFileSync(profilePath, 'utf-8');
    expect(profile).toContain('isLoaded') || expect(profile).toContain('user');
  });
});
