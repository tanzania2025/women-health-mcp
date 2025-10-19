# Quick Start Guide - NHS Data MCP Server

Your MCP server is now configured and ready to use with the NHS Development environment!

## ✅ What's Configured

- **Application**: Doct-her
- **Environment**: NHS Development (Integration)
- **API Key**: ib1b5Spxp1nci7Lxr0P7lVPML7uZFpbl
- **APIs Enabled**:
  - ✅ Immunisation History (User-Restricted)
  - ✅ Immunisation History (Application-Restricted)
  - ✅ NHS App (External Development)
  - ✅ Canary API (for testing)

## 🚀 Next Steps

### 1. Add to Claude Desktop

Edit your Claude Desktop config file:
```bash
~/Library/Application Support/Claude/claude_desktop_config.json
```

Add this configuration:
```json
{
  "mcpServers": {
    "nhs-data": {
      "command": "node",
      "args": ["/Users/dgordon/womens_health_mcp/build/index.js"]
    }
  }
}
```

### 2. Restart Claude Desktop

**Completely quit** and restart Claude Desktop (Cmd+Q, then reopen).

### 3. Verify Connection

You should see:
- 🔨 Hammer icon or tools indicator
- "nhs-data" server listed in available tools

## 🔧 Using the Server

### Authentication

Since the callback URL requires HTTPS (which we can't easily do locally), you have two options:

#### Option A: Application-Restricted Mode (Recommended for Testing)

Use the **application-restricted** APIs which only need the API key (no user OAuth):

**In Claude Desktop, ask:**
```
Get an application access token
```

This will authenticate using your API credentials and let you test the immunization history API.

#### Option B: User-Restricted Mode (For Personal Data)

For accessing your actual NHS data, you'll need to set up HTTPS callback or use the NHS Login flow differently. This is more complex and we can tackle it later.

## 📊 Available Tools

Once authenticated with `get_app_token`, you can use:

### Get Immunizations
```
Show me immunization data
```

### Get Patient Info
```
Get my patient information
```

### Get Medications
```
What medications are available?
```

### Get Appointments
```
Show appointments
```

## 🧪 Testing the API

The **Canary API** is specifically for testing. Try:

**In Claude Desktop:**
```
Can you test if the NHS API connection is working?
```

The server will use your API key to make test requests.

## 📝 Important Notes

### API Key Authentication

The server now automatically includes your API key in all requests via the `apikey` header. NHS requires this for the development environment.

### Application vs User Restricted

- **Application-Restricted**: APIs that work with just your API key (no user login needed)
  - ✅ Immunisation History - Application-Restricted
  - Good for: Testing, system access, non-patient-specific data

- **User-Restricted**: APIs that need NHS Login (OAuth)
  - ✅ Immunisation History - User-Restricted
  - ✅ NHS App APIs
  - Good for: Personal health records, patient-specific data
  - Requires: HTTPS callback URL setup (more complex)

### Current Limitations

1. **Callback URL**: We left this blank because it requires HTTPS. This means:
   - ✅ Application-restricted APIs work fine
   - ❌ User-restricted OAuth flow doesn't work yet

2. **Development Environment**: You're using the integration/dev environment, so:
   - ✅ Test data only (not real patient records)
   - ✅ Good for development and testing
   - ❌ Not production data

## 🔍 Troubleshooting

### Server not showing in Claude Desktop
- Check the path in config is correct
- Ensure the build succeeded (`npm run build`)
- Check Claude Desktop logs: `~/Library/Logs/Claude/`

### "Authentication failed" errors
Run the `get_app_token` tool first:
```
Get an application access token
```

### API errors
The development environment might have different endpoints than expected. If you get 404 errors, we may need to adjust the API base URLs for specific resources.

### Connection refused
Make sure you're using the correct API base URL. The integration environment is: `https://int.api.service.nhs.uk`

## 📚 Next Steps

### Immediate (Works Now)
1. ✅ Add to Claude Desktop
2. ✅ Test with `get_app_token`
3. ✅ Try immunization history API
4. ✅ Test canary API

### Later (Requires More Setup)
1. ⏳ Set up HTTPS callback for OAuth
2. ⏳ Enable user-restricted APIs
3. ⏳ Access personal NHS data via NHS Login
4. ⏳ Apply for production access

## 🎯 Quick Test

Once you've added the server to Claude Desktop and restarted:

**Ask Claude:**
```
Get an application access token, then show me what immunization data is available
```

This should authenticate and try to fetch immunization data from the NHS development API.

## 📞 Support

- **NHS API Issues**: https://developer.community.nhs.uk/
- **This MCP Server**: Check the main README.md
- **Claude Desktop**: Check Claude Desktop documentation

---

**You're all set!** The server is configured with your actual NHS developer credentials and ready to test in the development environment.
