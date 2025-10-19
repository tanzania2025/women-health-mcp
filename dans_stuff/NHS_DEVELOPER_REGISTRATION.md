# NHS Developer Portal Registration Guide

Step-by-step guide to creating an NHS sandbox application and getting API credentials for testing.

## Overview

The NHS Digital Developer Portal allows you to:
- Access sandbox/test environments with sample data
- Test APIs before production deployment
- Get API keys and OAuth credentials
- Access integration testing environments

## Important URLs

- **Main Developer Portal**: https://digital.nhs.uk/developer
- **Personal Demographics Service FHIR API**: https://digital.nhs.uk/developer/api-catalogue/personal-demographics-service-fhir
- **Testing Guide**: https://digital.nhs.uk/developer/guides-and-documentation/testing

## Step-by-Step Registration

### Step 1: Create a Developer Account

1. Visit https://digital.nhs.uk/developer
2. Look for "Sign in" or "Register" button (usually top right)
3. Click "Create an account" if you don't have one
4. Fill in your details:
   - Email address
   - Name
   - Organization (can be "Personal" or "Individual Developer")
   - Purpose (select "Testing" or "Development")
5. Verify your email address
6. Sign in to your new account

### Step 2: Navigate to "My Developer Account"

1. Once signed in, find "My Developer Account" in the menu
2. This is where you'll manage your applications and API access

### Step 3: Create a New Application

1. In "My Developer Account", select **"Environment access"**
2. Click **"Add new application"**
3. Fill in the application details:
   - **Application name**: e.g., "NHS Health Records MCP Server"
   - **Application owner**: Your name
   - **Description**: e.g., "Personal health records access via Model Context Protocol"
   - **Purpose**: "Testing" or "Development"
4. Click "Create" or "Submit"

### Step 4: Select Environment

Choose your testing environment:
- **Sandbox**: Limited canned responses, no real data (good for initial testing)
- **Integration**: Full test environment with 100+ test patients (better for comprehensive testing)

For our MCP server, select **Sandbox** to start.

### Step 5: Add APIs to Your Application

1. After creating your application, click **"Add APIs"**
2. Search for and select:
   - **Personal Demographics Service - FHIR API** (for patient demographics)
   - **GP Connect** (if available, for GP records)
   - **National Record Locator** (optional, for finding records)
3. For each API, you'll need to configure:
   - **Callback URL**: `http://localhost:3000/callback` (for OAuth redirect)
   - **Access mode**: Select "User-restricted" (for NHS Login authentication)

### Step 6: Get Your API Credentials

1. Click **"View your application"** or **"Edit"**
2. You should see:
   - **API Key** (also called Client ID)
   - **API Secret** (click "Show" or "Reveal" to see it)
3. **Copy these credentials** - you'll need them for the `.env` file

### Step 7: Configure OAuth Settings

For user-restricted access (NHS Login):
1. Set **Redirect URI**: `http://localhost:3000/callback`
2. Select **Scopes**:
   - `openid`
   - `profile`
   - `email`
   - `nhs-number`
   - Any PDS-specific scopes listed

### Step 8: Update Your `.env` File

Once you have credentials, update your `.env` file:

```bash
# Replace with your actual credentials
NHS_CLIENT_ID=your_actual_client_id_from_portal
NHS_CLIENT_SECRET=your_actual_client_secret_from_portal

# Keep these as-is for sandbox
NHS_API_BASE_URL=https://sandbox.api.service.nhs.uk/personal-demographics/FHIR/R4
NHS_AUTH_URL=https://auth.sandpit.signin.nhs.uk
NHS_REDIRECT_URI=http://localhost:3000/callback
```

### Step 9: Rebuild and Test

```bash
npm run build
```

Then add to Claude Desktop and test!

## Understanding Access Modes

NHS APIs have different access modes:

### User-Restricted (NHS Login)
- **Use case**: Patient accessing their own records
- **Authentication**: NHS Login OAuth2 (what we've built)
- **Best for**: Personal health record access
- **Our use case**: ✅ This is what you want

### Application-Restricted
- **Use case**: Backend systems, batch processing
- **Authentication**: API key + JWT
- **Best for**: System-to-system integration
- **Our use case**: ❌ Not suitable for personal access

### Healthcare Worker Access
- **Use case**: Clinicians accessing patient records
- **Authentication**: NHS Smartcard + CIS2
- **Best for**: Clinical systems
- **Our use case**: ❌ Requires healthcare credentials

## Sandbox vs Integration vs Production

### Sandbox
- **Data**: Canned responses, limited scenarios
- **Access**: Immediate after application creation
- **Best for**: Initial development, proof of concept
- **Limitations**: Limited test scenarios, may not have all endpoints

### Integration
- **Data**: 100+ realistic test patients
- **Access**: May require approval
- **Best for**: Full integration testing
- **Limitations**: Still test data, not real patients

### Production
- **Data**: Real patient data
- **Access**: Requires full onboarding and assurance
- **Best for**: Live systems with real users
- **Requirements**: Clinical safety, IG compliance, security assurance

## Common Issues

### "Cannot create application"
- Ensure you've verified your email
- Try signing out and back in
- Contact NHS Digital support if issues persist

### "API not available"
- Some APIs require additional approval
- Start with PDS FHIR API (most accessible)
- Check if API is available in sandbox environment

### "No API credentials shown"
- Click "Edit" on your application
- Look for "API Key" or "Credentials" section
- May need to generate credentials explicitly

### "Callback URL validation error"
- Use exact URL: `http://localhost:3000/callback`
- No trailing slash
- Must be HTTP for localhost (HTTPS not required for local testing)

## Additional Resources

- **API Documentation**: https://digital.nhs.uk/developer/api-catalogue/personal-demographics-service-fhir
- **Testing Guide**: https://digital.nhs.uk/developer/guides-and-documentation/testing
- **NHS Login for Developers**: https://digital.nhs.uk/developer/guides-and-documentation/security-and-authorisation/nhs-login-for-developers
- **Developer Community**: https://developer.community.nhs.uk/
- **Support Email**: Check the developer portal for current support contact

## Expected Timeline

- **Account creation**: Immediate
- **Application creation**: Immediate
- **Sandbox access**: Usually immediate
- **Integration access**: May take a few days
- **Production access**: Requires full onboarding (weeks to months)

## What If Sandbox Registration is Complex?

If the sandbox registration is taking too long or proving difficult, I can add a **mock data mode** to the MCP server. This would:
- Return realistic fake health data
- Let you test the MCP integration immediately
- Help you develop your queries and use cases
- Work without any NHS API credentials

Just let me know if you'd like me to add that option!

## Next Steps After Getting Credentials

1. Update `.env` with your credentials
2. Run `npm run build`
3. Add to Claude Desktop config
4. Restart Claude Desktop
5. Test the authentication flow
6. Start querying your (test) health data!

---

**Note**: The NHS Developer Portal interface may change. These instructions are based on the latest available information as of 2025. If you encounter different screens or options, the general flow should be similar.
