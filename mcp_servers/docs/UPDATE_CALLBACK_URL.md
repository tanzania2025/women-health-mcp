# Update NHS Portal Callback URL

For the manual OAuth flow to work, you need to set the callback URL in your NHS Developer Portal application.

## Quick Steps

### 1. Go to Your Application

Visit: https://onboarding.prod.api.platform.nhs.uk/MyApplications/ApplicationDetails?appId=6559c867-bd8e-4796-b29d-5fbf8a03e2cc

Or:
1. Go to https://digital.nhs.uk/developer
2. Sign in
3. Navigate to "My Applications"
4. Click on "Doct-her"

### 2. Edit Callback URL

1. Find the **"Callback URL"** field (currently shows "Not set yet")
2. Click **"Edit"** next to it
3. Enter: `http://localhost:3000/callback`
4. **Important**: Use `http://` not `https://` for localhost
5. Click **"Save"**

### 3. Why HTTP Localhost Works

The NHS portal previously showed an error requiring HTTPS, but actually **HTTP localhost is allowed** for development purposes. The error message was misleading.

Try entering: `http://localhost:3000/callback`

If it still requires HTTPS, then we'll need to use the ngrok solution instead.

## If HTTP Localhost Doesn't Work

If the portal still rejects `http://localhost:3000/callback` with an error about HTTPS, you have two options:

### Option A: Leave It Blank
Keep the callback URL blank and use the manual code copy method (which still works, you just copy the code from the failed redirect).

### Option B: Use ngrok (5 minutes setup)
If you want a seamless experience:

1. Install ngrok:
   ```bash
   brew install ngrok
   ```

2. Run ngrok:
   ```bash
   ngrok http 3000
   ```

3. Copy the HTTPS URL shown (like `https://abc123.ngrok.io`)

4. Set callback URL in NHS portal to:
   ```
   https://abc123.ngrok.io/callback
   ```

5. Update your `.env`:
   ```bash
   NHS_REDIRECT_URI=https://abc123.ngrok.io/callback
   ```

6. Rebuild:
   ```bash
   npm run build
   ```

We can set this up if needed, but try the simple HTTP localhost first!

## What Happens Next

Once the callback URL is set correctly:

1. You get the authorization URL from the MCP server
2. Visit it in your browser
3. Log in with NHS credentials
4. Get redirected to `http://localhost:3000/callback?code=...`
5. Browser shows "can't connect" (normal)
6. Copy the `code` from the URL
7. Exchange it in Claude Desktop
8. Done!

## Current Status

- ✅ Application created: "Doct-her"
- ✅ APIs added (Immunisation History, NHS App, etc.)
- ✅ API key configured
- ⏳ Callback URL: **Needs to be set**

**Try setting it to `http://localhost:3000/callback` now!**
