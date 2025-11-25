// Wait for Clerk to load
window.addEventListener('load', async () => {
    // Initialize Clerk
    const clerkPublishableKey = 'YOUR_PUBLISHABLE_KEY'; // Replace with your actual key
    
    if (window.Clerk) {
        try {
            await window.Clerk.load({
                publishableKey: clerkPublishableKey
            });

            // Check authentication status
            if (window.Clerk.user) {
                displayAuthenticatedState(window.Clerk.user);
            } else {
                displayUnauthenticatedState();
            }

            // Mount Clerk components
            mountClerkComponents();
        } catch (error) {
            console.error('Error initializing Clerk:', error);
            document.getElementById('auth-status').innerHTML = 
                '<span class="error">Failed to initialize Clerk</span>';
        }
    }
});

function displayAuthenticatedState(user) {
    const authStatus = document.getElementById('auth-status');
    authStatus.innerHTML = '<span class="success">✓ Authenticated</span>';
    
    const userInfo = document.getElementById('user-info');
    userInfo.style.display = 'block';
    userInfo.innerHTML = `
        <h3>User Information</h3>
        <p><strong>User ID:</strong> ${user.id}</p>
        <p><strong>Email:</strong> ${user.primaryEmailAddress?.emailAddress || 'N/A'}</p>
        <p><strong>Name:</strong> ${user.fullName || 'N/A'}</p>
    `;
}

function displayUnauthenticatedState() {
    const authStatus = document.getElementById('auth-status');
    authStatus.innerHTML = '<span class="error">✗ Not authenticated</span>';
    
    const userInfo = document.getElementById('user-info');
    userInfo.style.display = 'none';
}

function mountClerkComponents() {
    if (window.Clerk.user) {
        // Mount UserButton for authenticated users
        window.Clerk.mountUserButton(document.getElementById('user-button'));
    } else {
        // Mount SignIn component for unauthenticated users
        window.Clerk.mountSignIn(document.getElementById('sign-in'));
    }
}

// API Testing Functions
async function testPublicEndpoint() {
    try {
        const response = await fetch('/api/public');
        const data = await response.json();
        displayApiResponse(data, response.ok);
    } catch (error) {
        displayApiResponse({ error: error.message }, false);
    }
}

async function testProtectedEndpoint() {
    try {
        // Get the session token from Clerk
        const token = await window.Clerk.session?.getToken();
        
        const response = await fetch('/api/protected', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        const data = await response.json();
        displayApiResponse(data, response.ok);
    } catch (error) {
        displayApiResponse({ error: error.message }, false);
    }
}

function displayApiResponse(data, success) {
    const responseDiv = document.getElementById('api-response');
    responseDiv.innerHTML = `
        <div class="${success ? 'success' : 'error'}">
            <h4>API Response:</h4>
            <pre>${JSON.stringify(data, null, 2)}</pre>
        </div>
    `;
}

### 6. Middleware Helper (Optional - for custom middleware)