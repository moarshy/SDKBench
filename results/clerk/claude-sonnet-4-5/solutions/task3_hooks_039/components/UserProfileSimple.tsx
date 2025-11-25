'use client';

import { useUser } from '@clerk/nextjs';

/**
 * Simplified version of UserProfile component
 * Use this if you want a minimal implementation
 */
export default function UserProfileSimple() {
  const { user, isLoaded, isSignedIn } = useUser();

  if (!isLoaded) {
    return <div>Loading...</div>;
  }

  if (!isSignedIn) {
    return <div>Please sign in to view your profile.</div>;
  }

  return (
    <div>
      <h1>User Profile</h1>
      <img src={user.imageUrl} alt="Profile" />
      <p>Name: {user.fullName}</p>
      <p>Email: {user.primaryEmailAddress?.emailAddress}</p>
      <p>Username: {user.username}</p>
    </div>
  );
}