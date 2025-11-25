'use client';

import { useUser, useAuth, useClerk } from '@clerk/nextjs';
import { useEffect, useState } from 'react';

interface UserStats {
  sessionCount: number;
  lastActive: string;
}

export default function UserProfileAdvanced() {
  const { isLoaded: userLoaded, isSignedIn, user } = useUser();
  const { isLoaded: authLoaded, userId, sessionId, getToken } = useAuth();
  const { signOut, openUserProfile } = useClerk();
  const [stats, setStats] = useState<UserStats | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Both user and auth must be loaded
  const isLoaded = userLoaded && authLoaded;

  useEffect(() => {
    // Example: Fetch additional user stats from your API
    const fetchUserStats = async () => {
      if (!userId) return;

      try {
        const token = await getToken();
        const response = await fetch('/api/user/stats', {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (response.ok) {
          const data = await response.json();
          setStats(data);
        }
      } catch (err) {
        console.error('Failed to fetch user stats:', err);
        setError('Failed to load additional user data');
      }
    };

    if (isSignedIn && userId) {
      fetchUserStats();
    }
  }, [isSignedIn, userId, getToken]);

  // Loading state
  if (!isLoaded) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading profile...</p>
        </div>
      </div>
    );
  }

  // Not signed in
  if (!isSignedIn) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <h1 className="text-3xl font-bold mb-4">Access Denied</h1>
          <p className="text-gray-600 mb-6">Please sign in to view your profile.</p>
          <a
            href="/sign-in"
            className="inline-block px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
          >
            Sign In
          </a>
        </div>
      </div>
    );
  }

  // Error state
  if (!user) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-red-600 mb-4">Error</h1>
          <p className="text-gray-600">Unable to load user data.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-8">
      <div className="bg-white shadow-lg rounded-lg overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-6 text-white">
          <div className="flex items-center space-x-4">
            {user.imageUrl && (
              <img
                src={user.imageUrl}
                alt="Profile"
                className="w-24 h-24 rounded-full border-4 border-white object-cover"
              />
            )}
            <div>
              <h1 className="text-3xl font-bold">
                {user.firstName} {user.lastName}
              </h1>
              {user.username && (
                <p className="text-blue-100">@{user.username}</p>
              )}
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Authentication Info */}
          <section>
            <h2 className="text-xl font-semibold mb-3 flex items-center">
              <span className="mr-2">🔐</span> Authentication
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-gray-50 p-4 rounded-lg">
                <label className="text-sm font-medium text-gray-500">
                  User ID
                </label>
                <p className="text-gray-900 font-mono text-sm break-all">
                  {userId}
                </p>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <label className="text-sm font-medium text-gray-500">
                  Session ID
                </label>
                <p className="text-gray-900 font-mono text-sm break-all">
                  {sessionId || 'N/A'}
                </p>
              </div>
            </div>
          </section>

          {/* Contact Information */}
          <section>
            <h2 className="text-xl font-semibold mb-3 flex items-center">
              <span className="mr-2">📧</span> Contact Information
            </h2>
            <div className="space-y-3">
              <div className="bg-gray-50 p-4 rounded-lg">
                <label className="text-sm font-medium text-gray-500">
                  Primary Email
                </label>
                <p className="text-gray-900">
                  {user.primaryEmailAddress?.emailAddress || 'No email'}
                </p>
                {user.primaryEmailAddress?.verification?.status && (
                  <span
                    className={`inline-block mt-1 px-2 py-1 text-xs rounded ${
                      user.primaryEmailAddress.verification.status === 'verified'
                        ? 'bg-green-100 text-green-800'
                        : 'bg-yellow-100 text-yellow-800'
                    }`}
                  >
                    {user.primaryEmailAddress.verification.status}
                  </span>
                )}
              </div>

              {user.emailAddresses.length > 1 && (
                <div className="bg-gray-50 p-4 rounded-lg">
                  <label className="text-sm font-medium text-gray-500">
                    Additional Emails
                  </label>
                  <ul className="mt-2 space-y-1">
                    {user.emailAddresses
                      .filter((email) => email.id !== user.primaryEmailAddress?.id)
                      .map((email) => (
                        <li key={email.id} className="text-gray-900 text-sm">
                          {email.emailAddress}
                        </li>
                      ))}
                  </ul>
                </div>
              )}
            </div>
          </section>

          {/* Account Stats */}
          {stats && (
            <section>
              <h2 className="text-xl font-semibold mb-3 flex items-center">
                <span className="mr-2">📊</span> Statistics
              </h2>
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-blue-50 p-4 rounded-lg text-center">
                  <p className="text-3xl font-bold text-blue-600">
                    {stats.sessionCount}
                  </p>
                  <p className="text-sm text-gray-600">Total Sessions</p>
                </div>
                <div className="bg-purple-50 p-4 rounded-lg text-center">
                  <p className="text-sm font-medium text-purple-600">
                    {stats.lastActive}
                  </p>
                  <p className="text-sm text-gray-600">Last Active</p>
                </div>
              </div>
            </section>
          )}

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}

          {/* Actions */}
          <section className="flex flex-wrap gap-3 pt-4 border-t">
            <button
              onClick={() => openUserProfile()}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
            >
              Edit Profile
            </button>
            <button
              onClick={() => signOut()}
              className="px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition"
            >
              Sign Out
            </button>
          </section>
        </div>
      </div>
    </div>
  );
}

## Example API Route for Stats (Optional)