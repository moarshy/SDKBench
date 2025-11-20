import { describe, it, expect } from '@jest/globals';
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
