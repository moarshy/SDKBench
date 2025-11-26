import { describe, it, expect } from '@jest/globals';
import { readFileSync, existsSync } from 'fs';
import { join } from 'path';

describe('Clerk Complete Integration', () => {
  it('should have ClerkProvider in layout', () => {
    const layout = readFileSync(join(__dirname, '../expected/app/layout.tsx'), 'utf-8');
    expect(layout).toContain('ClerkProvider');
  });

  it('should have authMiddleware in middleware', () => {
    const middleware = readFileSync(join(__dirname, '../expected/middleware.ts'), 'utf-8');
    expect(middleware.includes('authMiddleware') || middleware.includes('clerkMiddleware')).toBe(true);
  });

  it('should protect dashboard with currentUser', () => {
    const dashboard = readFileSync(join(__dirname, '../expected/app/dashboard/page.tsx'), 'utf-8');
    expect(dashboard).toContain('currentUser');
  });

  it('should protect API route with auth()', () => {
    const api = readFileSync(join(__dirname, '../expected/app/api/user/route.ts'), 'utf-8');
    expect(api).toContain('auth()');
    expect(api).toContain('userId');
  });

  it('should have environment variables configured', () => {
    const env = readFileSync(join(__dirname, '../expected/.env.example'), 'utf-8');
    expect(env).toContain('NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY');
    expect(env).toContain('CLERK_SECRET_KEY');
  });
});
