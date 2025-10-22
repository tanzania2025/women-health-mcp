# NHS Sandbox Testing Setup

This guide helps you test the MCP server with the NHS sandbox environment (test data, no real patient records).

## What's Been Set Up

✅ Project dependencies installed
✅ TypeScript compiled successfully
✅ Environment configured for NHS sandbox
✅ Server tested and working

## Quick Start

### 1. Add to Claude Desktop

Copy the content from `claude_desktop_config.json` and add it to your Claude Desktop configuration:

**Location:** `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "nhs-data": {
      "command": "node",
      "args": [
        "/Users/dgordon/womens_health_mcp/build/index.js"
      ]
    }
  }
}
```

If you already have other MCP servers, just add the `nhs-data` entry to your existing `mcpServers` object.

### 2. Restart Claude Desktop

Completely quit and restart Claude Desktop for the changes to take effect.

### 3. Verify Connection

In Claude Desktop, you should see:
- A hammer icon (🔨) or tools indicator showing the NHS server is connected
- Available tools listed when you click the tools menu

### 4. Testing Without Real Authentication

The sandbox environment is configured but requires NHS sandbox API credentials. Here are your options:

#### Option A: Get NHS Sandbox Access (Recommended)

1. Visit https://digital.nhs.uk/developer
2. Sign up for a free developer account
3. Create a sandbox application
4. Get your sandbox API key and credentials
5. Update `.env` with your sandbox credentials:
   ```
   NHS_CLIENT_ID=your_sandbox_client_id
   NHS_CLIENT_SECRET=your_sandbox_client_secret
   ```
6. Rebuild: `npm run build`

#### Option B: Mock Data for Testing (Alternative)

If you want to test the MCP integration without NHS API access, we could modify the server to return mock health data instead of making real API calls. This would let you:
- Test the MCP tools and resources
- See the data format
- Verify Claude Desktop integration
- Develop your use case

Would you like me to add a mock data mode?

## Available Tools (Once Authenticated)

Once you have API access, you can use these tools in Claude Desktop:

### Get Patient Info
```
Show me my patient information
```

### Get Medications
```
What medications am I prescribed?
```

### Get Appointments
```
Show my upcoming appointments
```

### Get Medical Conditions
```
What conditions are in my medical records?
```

### Get Immunizations
```
Show my vaccination history
```

### Get Allergies
```
What allergies do I have on record?
```

## Authentication Flow (For Sandbox)

1. In Claude Desktop, ask: "Get my NHS authorization URL"
2. Visit the URL in your browser
3. Log in with sandbox/test NHS credentials
4. Copy the authorization code from the redirect URL
5. In Claude: "Exchange this auth code: [paste code]"
6. The server will save your tokens

## Current Configuration

Your `.env` file is configured with:
- **API Endpoint:** NHS Sandbox (test environment)
- **Auth URL:** NHS Sandpit authentication
- **Data:** Test data only, no real patient records

## Troubleshooting

### Server not showing in Claude Desktop
- Check the path in `claude_desktop_config.json` is correct
- Restart Claude Desktop completely
- Check Claude Desktop logs: `~/Library/Logs/Claude/`

### Authentication errors
- Sandbox may require valid test credentials from NHS Developer Portal
- Check `.env` has correct sandbox client ID and secret
- Some sandbox endpoints may be restricted

### API errors
- NHS sandbox may have limited functionality
- Some endpoints might not be fully implemented in sandbox
- Try the mock data option if sandbox isn't working

## Next Steps

1. **Get sandbox credentials** from NHS Developer Portal, or
2. **Add mock data mode** for testing without API access, or
3. **Apply for production access** when ready for real data

Let me know which option you'd like to pursue!
