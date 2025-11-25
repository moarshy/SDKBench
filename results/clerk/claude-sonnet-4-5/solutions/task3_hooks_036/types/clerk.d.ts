/**
 * Optional: Extend Clerk types if you need custom metadata
 */
declare global {
  interface UserPublicMetadata {
    role?: string
    department?: string
  }

  interface UserPrivateMetadata {
    internalId?: string
  }
}

export {}