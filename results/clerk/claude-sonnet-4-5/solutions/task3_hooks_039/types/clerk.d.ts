/**
 * Type definitions for Clerk user data
 * Extend these as needed for your application
 */

import { User } from '@clerk/nextjs/server';

export type ClerkUser = User;

export interface UserMetadata {
  // Add your custom user metadata types here
  preferences?: {
    theme?: 'light' | 'dark';
    notifications?: boolean;
  };
  onboardingCompleted?: boolean;
}