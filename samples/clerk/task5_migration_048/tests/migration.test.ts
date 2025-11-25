import { describe, it, expect } from '@jest/globals';
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
