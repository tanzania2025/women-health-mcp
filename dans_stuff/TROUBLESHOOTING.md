# Troubleshooting NHS API Authentication

## Issue Fixed: Wrong Base URL

### The Problem
You were getting authentication errors because the server was configured for the **Integration (INT)** environment (`int.api.service.nhs.uk`), but your APIs are in the **External Development (DEV)** environment.

### The Fix
✅ Updated base URL from `https://int.api.service.nhs.uk` to `https://dev.api.service.nhs.uk`
✅ Rebuilt the server
✅ Added diagnostic tool to help troubleshoot

## Next Steps

### 1. Restart Claude Desktop

The server has been rebuilt with the correct configuration. You need to restart Claude Desktop to load the changes:

1. **Quit Claude Desktop completely** (Cmd+Q)
2. **Reopen Claude Desktop**
3. **Start a new conversation**

### 2. Test the Configuration

**Ask in Claude Desktop:**
```
Test my NHS API configuration
```

This will show you the current settings and confirm everything is configured correctly.

### 3. Try Authentication Again

Now try one of these:

#### Option A: Application-Restricted (Simpler)
```
Get an application access token
```

This uses just your API key - no browser needed.

#### Option B: User-Restricted (Full Access)
```
Get my NHS authorization URL
```

Follow the OAuth flow with Postman callback.

## Common Issues & Solutions

### Error: "Internal Server Error" from OAuth

**Possible Causes:**
1. The DEV environment OAuth endpoint might be different
2. Your application might not be fully activated yet
3. OAuth might not be enabled for DEV environment

**Solutions:**
- Try the application-restricted approach first (uses API key only)
- Check NHS Developer Portal to see if there are activation steps needed
- The DEV environment might require additional setup

### Error: "Invalid client_id" or "Client not found"

**Possible Causes:**
- API key not activated yet in the DEV environment
- Wrong environment selected

**Solutions:**
- Verify in NHS portal that your application is approved/activated
- Check that APIs show as "Enabled" not just "Added"
- May need to wait for activation (can take time)

### Error: "Unauthorized" or 401

**Possible Causes:**
- API key header format might be wrong for DEV environment
- Authentication method might differ

**Solutions:**
- The DEV environment might use different authentication headers
- May need to use signed JWT instead of simple API key
- Check API documentation for specific authentication requirements

## Alternative: Mock Data Mode

If the DEV environment continues to have issues, I can add a **mock data mode** that returns fake health data for testing the MCP integration without needing NHS API access.

This would let you:
- ✅ Test Claude Desktop integration immediately
- ✅ See the data format and structure
- ✅ Develop your queries and use cases
- ✅ Switch to real APIs later when authentication is working

**Want me to add mock data mode?** Just ask!

## DEV Environment Considerations

The External Development environment may have limitations:

### May Require:
- **Public/Private Key Pair**: Some NHS APIs require RSA 4096-bit key pair
- **Additional Activation**: APIs might need manual approval/activation
- **Different Auth Flow**: DEV might use different OAuth endpoints than INT
- **Limited Availability**: DEV environment might not be 24/7

### Check In NHS Portal:
1. Are your APIs showing as "Enabled" (green checkmark)?
2. Is there an "Activation Required" message?
3. Is there a "Setup Required" for OAuth?
4. Do you need to add a public key URL?

## Getting More Details

### Check Actual Error Messages

In Claude Desktop, when you get an error, look for details like:
- HTTP status code (401, 403, 500, etc.)
- Error message from NHS API
- Endpoint that failed

Share these details and I can provide more specific fixes!

### Try Simpler Test First

Instead of full OAuth, try just testing the API key works:

**Ask Claude:**
```
Test config
```

This shows your configuration without making any API calls.

## What's Been Updated

### Configuration Files:
- ✅ `.env` - Changed to `dev.api.service.nhs.uk`
- ✅ Server code - Added diagnostic tool
- ✅ Built successfully

### New Tool Available:
- `test_config` - Shows configuration without API calls

### Should Work Now:
- Configuration matches your "External Development" APIs
- Diagnostic tool added for troubleshooting
- Better error messages

## Next Actions

1. **Restart Claude Desktop** (Cmd+Q, then reopen)
2. **Test configuration** with: "Test my NHS API configuration"
3. **Try authentication** again
4. **Share error details** if it still fails

The base URL fix should resolve the "internal server error" - but DEV environment might have other requirements we need to configure!
