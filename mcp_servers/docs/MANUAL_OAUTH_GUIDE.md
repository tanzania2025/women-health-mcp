# Manual OAuth Flow Guide - User-Restricted NHS APIs

This guide shows you how to authenticate with NHS Login using the manual code copy method. This works without needing ngrok or any HTTPS callback server.

## When to Use This

Use this method when you want to:
- Access **your personal** NHS health records
- Use **user-restricted** APIs (NHS App, personal immunization history, etc.)
- Authenticate as a patient (not as an application)

For application-restricted APIs, use `get_app_token` instead (simpler).

## Prerequisites

✅ MCP server added to Claude Desktop
✅ Claude Desktop restarted
✅ Your "Doct-her" application configured in NHS Developer Portal

## Step-by-Step Process

### Step 1: Get the Authorization URL

In Claude Desktop, ask:
```
Get my NHS authorization URL
```

Or:
```
I want to authenticate with NHS Login
```

The server will return a long URL starting with:
```
https://int.api.service.nhs.uk/oauth2/authorize?...
```

### Step 2: Visit the URL in Your Browser

1. **Copy the entire URL** from Claude's response
2. **Open a new browser tab**
3. **Paste and visit the URL**

### Step 3: Log In with NHS Login

You'll be taken to the NHS Login page. You'll need:

- **NHS Login credentials** OR
- **Development/test credentials** (if you're in the dev environment)

**Note**: Since you're using the **development environment**, you may need:
- Test NHS Login credentials
- Or actual NHS Login if you're testing with your own data

Enter your credentials and authorize the "Doct-her" application.

### Step 4: You'll Get Redirected (and See an Error - That's OK!)

After authorizing, you'll be redirected to:
```
http://localhost:3000/callback?code=XXXXXXXX&state=YYYYYYYY
```

**Your browser will show an error** like:
- "This site can't be reached"
- "Connection refused"
- "Unable to connect"

**This is completely normal!** We don't have a server running on localhost:3000, but that's fine.

### Step 5: Copy the Authorization Code

Look at your browser's **address bar**. The URL will look like:
```
http://localhost:3000/callback?code=abc123xyz789&state=random123
```

**Copy only the code value** (the part after `code=` and before `&state=`):
```
abc123xyz789
```

### Step 6: Exchange the Code for Access Token

Go back to Claude Desktop and say:
```
Exchange this authorization code: abc123xyz789
```

Or:
```
Use exchange_auth_code with code abc123xyz789
```

### Step 7: Success!

If successful, you'll see:
```
Authentication successful!

Access token obtained (expires in 3600 seconds).

You can now use the other tools to access your NHS data.

IMPORTANT: Save these tokens in your .env file:
NHS_ACCESS_TOKEN=...
NHS_REFRESH_TOKEN=...
```

The tokens are automatically stored in memory and will be used for subsequent API calls.

## Now You Can Access Your Data

Once authenticated, try:

### Get Your Patient Info
```
Show me my patient information
```

### Get Your Medications
```
What medications am I prescribed?
```

### Get Your Immunizations
```
Show me my vaccination history
```

### Get Your Appointments
```
Show my upcoming appointments
```

### Get Your Medical Conditions
```
What medical conditions are in my records?
```

## Troubleshooting

### "Invalid redirect_uri" error

**Problem**: The callback URL in NHS portal doesn't match

**Solution**:
1. Go to NHS Developer Portal
2. Edit your "Doct-her" application
3. Set Callback URL to: `http://localhost:3000/callback`
4. Save and try again

### Can't find the code in the URL

**Problem**: Browser auto-completed or hid the full URL

**Solutions**:
- Click in the address bar to see the full URL
- Right-click address bar → Copy
- Look for the part after `?code=`
- On mobile: long-press the address bar

### NHS Login page says "Invalid client"

**Problem**: Your Client ID might be wrong

**Solution**:
- Double-check `.env` has the correct `NHS_CLIENT_ID`
- Verify in NHS Developer Portal
- Rebuild: `npm run build`

### Code exchange fails

**Problem**: Code might be expired (codes are single-use and short-lived)

**Solution**:
- Get a new authorization URL
- Go through the flow again quickly
- Codes typically expire in 10 minutes

### "Authentication failed. Please re-authenticate."

**Problem**: Your access token expired

**Solution**:
- Repeat the OAuth flow to get a new token
- Or the server should auto-refresh if you have a refresh token

## Tips

### Save Your Tokens

After successful authentication, the server tells you to save tokens in `.env`:

```bash
# Add these to your .env file
NHS_ACCESS_TOKEN=your_long_access_token_here
NHS_REFRESH_TOKEN=your_refresh_token_here
```

This way, you won't need to re-authenticate every time you restart.

### Token Lifespan

- **Access Token**: Usually expires in 1 hour
- **Refresh Token**: Lasts much longer (days/weeks)
- The server automatically refreshes expired access tokens

### Development vs Production

You're currently using the **development environment**:
- Test data only (not real patient records)
- May have test NHS Login accounts
- Good for testing before production

## Comparison: Application vs User Auth

### Application-Restricted (`get_app_token`)
- ✅ Simpler (one command)
- ✅ No browser needed
- ❌ Limited data access
- ❌ Not patient-specific
- Use for: System data, immunization schedules (not personal records)

### User-Restricted (This OAuth flow)
- ✅ Full access to patient records
- ✅ Patient-specific data
- ❌ More complex (browser required)
- ❌ Requires NHS Login
- Use for: Personal health records, medications, appointments

## Next Steps

Once you've successfully authenticated:

1. ✅ Test all the data retrieval tools
2. ✅ Save tokens to `.env` for persistence
3. ✅ Explore what data is available in the dev environment
4. ⏳ Consider applying for production access for real data

## Security Notes

- **Never share your tokens** publicly or commit them to git
- Tokens give **full access** to your NHS health records
- The `.gitignore` is configured to protect `.env`
- Tokens should be treated like passwords

---

**Ready to try?** In Claude Desktop, just say: **"Get my NHS authorization URL"**
