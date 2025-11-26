import { describe, it, expect } from '@jest/globals';
import { readFileSync } from 'fs';
import { join } from 'path';

describe('Clerk Middleware', () => {
  const middlewarePath = join(__dirname, '../expected/middleware.ts');

  it('should have middleware function imported', () => {
    const middleware = readFileSync(middlewarePath, 'utf-8');
    expect(middleware.includes('authMiddleware') || middleware.includes('clerkMiddleware')).toBe(true);
    const hasServerImport = middleware.includes("from '@clerk/nextjs/server'") || middleware.includes('from "@clerk/nextjs/server"'); expect(hasServerImport).toBe(true);
  });

  it('should export middleware as default', () => {
    const middleware = readFileSync(middlewarePath, 'utf-8');
    expect(middleware.includes('export default authMiddleware') || middleware.includes('export default clerkMiddleware') || middleware.includes('clerkMiddleware(')).toBe(true);
  });

  it('should have publicRoutes configuration', () => {
    const middleware = readFileSync(middlewarePath, 'utf-8');
    const hasPublicRouteConfig = middleware.includes('publicRoutes:') || middleware.includes('isPublicRoute') || middleware.includes('publicRoutes'); expect(hasPublicRouteConfig).toBe(true);
  });

  it('should have matcher config', () => {
    const middleware = readFileSync(middlewarePath, 'utf-8');
    expect(middleware).toContain('export const config');
    expect(middleware).toContain('matcher:');
  });
});
