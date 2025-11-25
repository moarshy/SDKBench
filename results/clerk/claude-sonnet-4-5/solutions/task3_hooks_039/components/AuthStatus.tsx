'use client';

import { useAuth, useUser } from '@clerk/nextjs';

/**
 * Component demonstrating useAuth hook
 * Shows authentication status and session information
 */
export default function AuthStatus() {
  const { isLoaded, isSignedIn, userId, sessionId, orgId } = useAuth();
  const { user } = useUser();

  if (!isLoaded) {
    return <div>Loading auth status...</div>;
  }

  return (
    <div className="bg-white shadow rounded-lg p-6">
      <h2 className="text-xl font-bold mb-4">Authentication Status</h2>
      
      <div className="space-y-2">
        <div className="flex items-center">
          <span className="font-semibold mr-2">Status:</span>
          <span className={`px-3 py-1 rounded-full text-sm ${
            isSignedIn ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
          }`}>
            {isSignedIn ? 'Signed In' : 'Signed Out'}
          </span>
        </div>

        {isSignedIn && (
          <>
            <div>
              <span className="font-semibold">User ID:</span> {userId}
            </div>
            <div>
              <span className="font-semibold">Session ID:</span> {sessionId}
            </div>
            {orgId && (
              <div>
                <span className="font-semibold">Organization ID:</span> {orgId}
              </div>
            )}
            {user && (
              <div>
                <span className="font-semibold">Email:</span> {user.primaryEmailAddress?.emailAddress}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}