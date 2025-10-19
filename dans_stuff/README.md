# NHS Data MCP Server

A Model Context Protocol (MCP) server that provides secure access to NHS patient health records. This server allows you to query your NHS data including medications, appointments, conditions, immunizations, and more through any MCP-compatible client (like Claude Desktop).

## Features

- **Patient Information**: Access demographic data, NHS number, contact details
- **Medications**: View current and past prescriptions
- **Appointments**: Get upcoming and historical appointments
- **Conditions**: Access diagnoses and medical problems
- **Immunizations**: View vaccination history
- **Allergies**: List allergies and intolerances
- **Secure Authentication**: OAuth2 authentication via NHS Login
- **Auto Token Refresh**: Automatically refreshes expired access tokens

## Prerequisites

1. **Node.js**: Version 18 or higher
2. **NHS Developer Account**: Register at [NHS Digital Developer Portal](https://digital.nhs.uk/developer)
3. **OAuth2 Credentials**: Create an application in the NHS Developer Portal to get:
   - Client ID
   - Client Secret
   - Configure redirect URI

## Installation

1. Clone or download this repository

2. Install dependencies:
```bash
npm install
```

3. Copy the example environment file:
```bash
cp .env.example .env
```

4. Edit `.env` and add your NHS API credentials:
```bash
NHS_CLIENT_ID=your_client_id_here
NHS_CLIENT_SECRET=your_client_secret_here
```

5. Build the TypeScript code:
```bash
npm run build
```

## NHS Developer Portal Setup

### Step 1: Register as a Developer

1. Visit [NHS Digital Developer Portal](https://digital.nhs.uk/developer)
2. Create an account or sign in
3. Navigate to "My Applications"

### Step 2: Create an Application

1. Click "Create New Application"
2. Fill in application details:
   - **Name**: Your application name
   - **Description**: "Personal health records access via MCP"
   - **Redirect URI**: `http://localhost:3000/callback`
3. Select the APIs you need:
   - Personal Demographics Service (PDS) FHIR API
   - GP Connect Access Record FHIR API (if available)
4. Save and note your Client ID and Client Secret

### Step 3: Configure Scopes

Ensure your application has access to these scopes:
- `openid`
- `profile`
- `email`
- `nhs-number`

## Authentication Flow

### First-Time Setup

1. Start the server in development mode:
```bash
npm run dev
```

2. Use the MCP client (e.g., Claude Desktop) to call the `get_auth_url` tool

3. Visit the returned authorization URL in your browser

4. Log in with your NHS credentials and authorize access

5. You'll be redirected to a URL like:
   ```
   http://localhost:3000/callback?code=AUTHORIZATION_CODE&state=...
   ```

6. Copy the `code` parameter value

7. Use the `exchange_auth_code` tool with the code to get access tokens

8. Save the returned tokens to your `.env` file:
   ```bash
   NHS_ACCESS_TOKEN=your_access_token
   NHS_REFRESH_TOKEN=your_refresh_token
   ```

9. Restart the server

## Usage with Claude Desktop

Add this server to your Claude Desktop configuration:

### macOS
Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "nhs-data": {
      "command": "node",
      "args": ["/Users/your-username/womens_health_mcp/build/index.js"]
    }
  }
}
```

### Windows
Edit `%APPDATA%/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "nhs-data": {
      "command": "node",
      "args": ["C:\\Users\\your-username\\womens_health_mcp\\build\\index.js"]
    }
  }
}
```

## Available Tools

### `get_patient_info`
Get your demographic information including name, NHS number, date of birth, and address.

**Example**: "Show me my patient information"

### `get_medications`
List all current and past medication requests (prescriptions).

**Example**: "What medications am I currently prescribed?"

### `get_appointments`
View upcoming and past appointments.

**Parameters**:
- `status` (optional): Filter by status (e.g., "booked", "fulfilled", "cancelled")

**Example**: "Show me my upcoming appointments"

### `get_conditions`
List medical conditions, diagnoses, and problems on record.

**Example**: "What medical conditions are in my records?"

### `get_immunizations`
View your vaccination and immunization history.

**Example**: "Show me my vaccination history"

### `get_allergies`
List known allergies and intolerances.

**Example**: "What allergies do I have on record?"

### `get_auth_url`
Generate the NHS Login authorization URL (used during initial setup).

### `exchange_auth_code`
Exchange authorization code for access tokens (used during initial setup).

## Available Resources

The server also exposes resources that can be accessed via MCP resource URIs:

- `nhs://patient/info` - Your patient information
- `nhs://medications` - Your prescriptions
- `nhs://appointments` - Your appointments
- `nhs://conditions` - Your medical conditions
- `nhs://immunizations` - Your vaccination history
- `nhs://allergies` - Your allergies

## Data Format

All data is returned in FHIR (Fast Healthcare Interoperability Resources) JSON format, which is the NHS standard. The responses include:

- Resource type
- Unique identifiers
- Coded values (SNOMED CT, ICD-10, etc.)
- Timestamps
- References to related resources

## Security Considerations

- **Never commit `.env`**: Your access tokens provide full access to your health records
- **Token Storage**: Consider using a secure credential manager instead of `.env` for production use
- **Token Expiry**: Access tokens expire; the server automatically refreshes them using the refresh token
- **HTTPS**: In production, always use HTTPS for the redirect URI
- **Scope Limitation**: Only request the minimum scopes needed for your use case
- **Data Retention**: Be mindful of where health data is stored and processed

## Sandbox vs Production

### Sandbox (Default)
- Uses test data, not real patient records
- No actual NHS credentials needed for testing
- API Base URL: `https://sandbox.api.service.nhs.uk`
- Auth URL: `https://auth.sandpit.signin.nhs.uk`

### Production
To use with real NHS data, update `.env`:
```bash
NHS_API_BASE_URL=https://api.service.nhs.uk/personal-demographics/FHIR/R4
NHS_AUTH_URL=https://auth.signin.nhs.uk
```

## Troubleshooting

### "Authentication failed"
- Check your Client ID and Client Secret are correct
- Ensure your access token hasn't expired
- Try running the OAuth flow again

### "Failed to get patient data"
- Verify you've completed the authentication flow
- Check your access token is set in `.env`
- Ensure you're using the correct API base URL for your environment

### "No refresh token available"
- Complete the initial OAuth flow to obtain tokens
- Check your `.env` file has `NHS_REFRESH_TOKEN` set

### CORS errors
- These typically occur in sandbox environments
- Try using the production API if you have access
- Contact NHS Developer Support

## Development

### Build
```bash
npm run build
```

### Watch mode
```bash
npm run watch
```

### Run
```bash
npm start
```

## API Documentation

- [NHS Developer Documentation](https://digital.nhs.uk/developer/guides-and-documentation)
- [NHS FHIR API](https://digital.nhs.uk/developer/api-catalogue/personal-demographics-service-fhir)
- [NHS Login Documentation](https://digital.nhs.uk/developer/guides-and-documentation/security-and-authorisation/nhs-login-for-developers)
- [FHIR R4 Specification](https://hl7.org/fhir/R4/)

## Privacy & GDPR

This server processes personal health information. When using this:

1. You are the data controller for your own health data
2. Ensure compliance with GDPR and UK data protection laws
3. Only access your own records unless authorized
4. Be transparent about how data is used and stored
5. Implement appropriate security measures

## License

MIT

## Disclaimer

This is a personal project for accessing your own NHS health records. It is not affiliated with or endorsed by NHS Digital or the NHS. Always verify health information with qualified healthcare professionals.

## Support

For issues with:
- **This MCP Server**: Open an issue in this repository
- **NHS APIs**: Contact [NHS Digital Developer Support](https://digital.nhs.uk/developer/guides-and-documentation/support)
- **NHS Login**: Visit [NHS Login Support](https://digital.nhs.uk/services/nhs-login)

## Contributing

Contributions are welcome! Please ensure:
- Code follows TypeScript best practices
- Security and privacy are maintained
- Documentation is updated
- No sensitive data in commits
