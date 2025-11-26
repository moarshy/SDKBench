import { describe, it, expect } from '@jest/globals';
import { readFileSync } from 'fs';
import { join } from 'path';

describe('Clerk Middleware', () => {
  const middlewarePath = join(__dirname, '../expected/middleware.ts');

  it('should have middleware function imported', () => {
    const middleware = readFileSync(middlewarePath, 'utf-8');
    expect(middleware.includes('authMiddleware') || middleware.includes('clerkMiddleware')).toBe(true);
    expect(middleware).toContain("from '@clerk/nextjs/server'");
  });

  it('should export middleware as default', () => {
    const middleware = readFileSync(middlewarePath, 'utf-8');
    expect(middleware.includes('export default authMiddleware') || middleware.includes('export default clerkMiddleware') || middleware.includes('clerkMiddleware(')).toBe(true);
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
