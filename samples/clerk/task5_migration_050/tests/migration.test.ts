import { describe, it, expect } from '@jest/globals';
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
