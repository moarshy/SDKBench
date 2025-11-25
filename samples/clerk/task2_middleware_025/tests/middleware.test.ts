import { describe, it, expect } from '@jest/globals';
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
