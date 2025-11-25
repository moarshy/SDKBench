'use client';

import { useUser } from '@clerk/nextjs';

/**
 * Custom hook that wraps Clerk's useUser with additional utilities
 */
export function useClerkUser() {
  const { user, isLoaded, isSignedIn } = useUser();

  const getUserDisplayName = () => {
    if (!user) return 'Guest';
    return user.fullName || user.username || user.primaryEmailAddress?.emailAddress || 'User';
  };

  const getUserInitials = () => {
    if (!user?.fullName) return '?';
    const names = user.fullName.split(' ');
    if (names.length >= 2) {
      return `${names[0][0]}${names[names.length - 1][0]}`.toUpperCase();
    }
    return user.fullName[0].toUpperCase();
  };

  const isEmailVerified = () => {
    return user?.primaryEmailAddress?.verification?.status === 'verified';
  };

  const hasPhoneNumber = () => {
    return !!user?.primaryPhoneNumber;
  };

  return {
    user,
    isLoaded,
    isSignedIn,
    getUserDisplayName,
    getUserInitials,
    isEmailVerified,
    hasPhoneNumber,
  };
}