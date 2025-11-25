/// <reference types="react-scripts" />

declare namespace NodeJS {
  interface ProcessEnv {
    REACT_APP_CLERK_PUBLISHABLE_KEY: string;
  }
}

## Step 7: Create a .gitignore entry