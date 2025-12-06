# Auth0 Setup Guide

This guide will help you set up Auth0 for BuyHive backend authentication.

## Step 1: Create Auth0 Account

1. Go to https://auth0.com/
2. Sign up for a free account (free tier: up to 7,500 active users/month)
3. Complete the setup wizard

## Step 2: Create an API (Backend)

1. In Auth0 Dashboard, go to **Applications** → **APIs**
2. Click **Create API**
3. Fill in:
   - **Name**: BuyHive API (or any name)
   - **Identifier**: `https://buyhive-api` (this is your **AUDIENCE**)
   - **Signing Algorithm**: RS256 (default)
4. Click **Create**
5. **Copy the Identifier** - this is your `AUTH0_AUDIENCE`

## Step 3: Create an Application (Frontend)

1. In Auth0 Dashboard, go to **Applications** → **Applications**
2. Click **Create Application**
3. Fill in:
   - **Name**: BuyHive Frontend (or any name)
   - **Application Type**: Single Page Application (or Regular Web Application)
4. Click **Create**
5. Go to **Settings** tab
6. Configure:
   - **Allowed Callback URLs**: `http://localhost:3000/callback` (or your frontend URL)
   - **Allowed Logout URLs**: `http://localhost:3000` (or your frontend URL)
   - **Allowed Web Origins**: `http://localhost:3000` (or your frontend URL)
7. **Copy the Domain** - this is your `AUTH0_DOMAIN` (format: `your-tenant.auth0.com`)

## Step 4: Configure Environment Variables

Add these to your `.env` file:

```env
# Auth0 Configuration
AUTH0_DOMAIN=your-tenant.auth0.com
AUTH0_AUDIENCE=https://buyhive-api
AUTH0_ALGORITHMS=RS256
```

## Step 5: Frontend Integration

Your frontend needs to:

1. Install Auth0 SDK (e.g., `@auth0/auth0-spa-js` for React)
2. Initialize Auth0 with your domain and client ID
3. Handle login/logout
4. Get access token and send it in `Authorization: Bearer <token>` header to backend

Example frontend code (React):
```javascript
import { useAuth0 } from '@auth0/auth0-spa-js';

const { getAccessTokenSilently } = useAuth0();

// In your API calls:
const token = await getAccessTokenSilently({
  audience: 'https://buyhive-api'  // Your AUTH0_AUDIENCE
});

fetch('/api/carts', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
```

## Step 6: Test Authentication

1. Start your backend server
2. Test the `/auth/me` endpoint with a valid Auth0 token
3. All protected routes should now require Auth0 authentication

## Notes

- **Free Tier**: Up to 7,500 active users/month
- **Token Refresh**: Auth0 handles token refresh automatically
- **Multiple Providers**: You can enable Google, Facebook, etc. in Auth0 Dashboard → Authentication → Social
- **User Management**: Auth0 provides a user management dashboard

## Migration from Google OAuth

If you were using Google OAuth directly:
- No need for Google Client ID/Secret anymore
- Frontend handles all OAuth flow through Auth0
- Backend just validates tokens
- Much simpler!

## Troubleshooting

- **Invalid token**: Check that `AUTH0_AUDIENCE` matches the API Identifier
- **Token expired**: Auth0 tokens expire after 24 hours by default (configurable)
- **User not found**: Backend automatically creates users on first login

