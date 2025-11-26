import { describe, it, expect } from '@jest/globals';
import { readFileSync } from 'fs';
import { join } from 'path';

describe('Clerk Hooks - useAuth', () => {
  const profilePath = join(__dirname, '../expected/components/UserProfile.tsx');

  it('should have useAuth imported', () => {
    const profile = readFileSync(profilePath, 'utf-8');
    expect(profile).toContain('useAuth');
    const hasClerkImport = profile.includes("from '@clerk/nextjs'") || profile.includes('from "@clerk/nextjs"'); expect(hasClerkImport).toBe(true);
  });

  it('should use client directive', () => {
    const profile = readFileSync(profilePath, 'utf-8');
    expect(profile).toContain("'use client'");
  });

  it('should call useAuth hook', () => {
    const profile = readFileSync(profilePath, 'utf-8');
    expect(profile).toContain('useAuth()');
  });

  it('should handle loading state', () => {
    const profile = readFileSync(profilePath, 'utf-8');
    const hasLoadingCheck = profile.includes('isLoaded') || profile.includes('user'); expect(hasLoadingCheck).toBe(true);
  });
});
