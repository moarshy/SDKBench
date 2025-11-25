'use client';

import { useUser } from '@clerk/nextjs';

/**
 * Reusable avatar component using Clerk user data
 */
export default function UserAvatar({ size = 'md' }: { size?: 'sm' | 'md' | 'lg' }) {
  const { user, isLoaded } = useUser();

  const sizeClasses = {
    sm: 'w-8 h-8 text-xs',
    md: 'w-12 h-12 text-sm',
    lg: 'w-16 h-16 text-base',
  };

  if (!isLoaded) {
    return (
      <div className={`${sizeClasses[size]} rounded-full bg-gray-200 animate-pulse`} />
    );
  }

  if (!user) {
    return (
      <div className={`${sizeClasses[size]} rounded-full bg-gray-300 flex items-center justify-center text-gray-600 font-semibold`}>
        ?
      </div>
    );
  }

  return (
    <img
      src={user.imageUrl}
      alt={user.fullName || 'User avatar'}
      className={`${sizeClasses[size]} rounded-full object-cover border-2 border-gray-200`}
    />
  );
}