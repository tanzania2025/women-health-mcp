#!/usr/bin/env node

/**
 * NHS Data MCP Server
 * Provides access to NHS patient health records via MCP protocol
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  ListResourcesRequestSchema,
  ReadResourceRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import * as dotenv from 'dotenv';
import { NHSAuthenticator } from './nhs-auth.js';
import { NHSClient } from './nhs-client.js';
import { NHSConfig } from './types.js';

// Load environment variables
dotenv.config();

// Initialize NHS configuration
const nhsConfig: NHSConfig = {
  apiBaseUrl: process.env.NHS_API_BASE_URL || 'https://api.service.nhs.uk/personal-demographics/FHIR/R4',
  authUrl: process.env.NHS_AUTH_URL || 'https://auth.sandpit.signin.nhs.uk',
  clientId: process.env.NHS_CLIENT_ID || '',
  clientSecret: process.env.NHS_CLIENT_SECRET || '',
  apiKey: process.env.NHS_API_KEY,
  redirectUri: process.env.NHS_REDIRECT_URI || 'http://localhost:3000/callback',
  accessToken: process.env.NHS_ACCESS_TOKEN,
  refreshToken: process.env.NHS_REFRESH_TOKEN,
};

// Initialize NHS services
const authenticator = new NHSAuthenticator(nhsConfig);
const nhsClient = new NHSClient(nhsConfig, authenticator);

// Create MCP server
const server = new Server(
  {
    name: 'nhs-data-server',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
      resources: {},
    },
  }
);

/**
 * List available tools
 */
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: 'get_patient_info',
        description: 'Get patient demographic information including name, NHS number, date of birth, and contact details',
        inputSchema: {
          type: 'object',
          properties: {
            patient_id: {
              type: 'string',
              description: 'Patient ID (defaults to "me" for authenticated user)',
              default: 'me',
            },
          },
        },
      },
      {
        name: 'get_medications',
        description: 'Get list of current and past medication requests (prescriptions)',
        inputSchema: {
          type: 'object',
          properties: {
            patient_id: {
              type: 'string',
              description: 'Patient ID (defaults to "me" for authenticated user)',
              default: 'me',
            },
          },
        },
      },
      {
        name: 'get_appointments',
        description: 'Get upcoming and past appointments',
        inputSchema: {
          type: 'object',
          properties: {
            patient_id: {
              type: 'string',
              description: 'Patient ID (defaults to "me" for authenticated user)',
              default: 'me',
            },
            status: {
              type: 'string',
              description: 'Filter by appointment status (booked, fulfilled, cancelled, etc.)',
            },
          },
        },
      },
      {
        name: 'get_conditions',
        description: 'Get list of medical conditions, diagnoses, and problems',
        inputSchema: {
          type: 'object',
          properties: {
            patient_id: {
              type: 'string',
              description: 'Patient ID (defaults to "me" for authenticated user)',
              default: 'me',
            },
          },
        },
      },
      {
        name: 'get_immunizations',
        description: 'Get vaccination and immunization history',
        inputSchema: {
          type: 'object',
          properties: {
            patient_id: {
              type: 'string',
              description: 'Patient ID (defaults to "me" for authenticated user)',
              default: 'me',
            },
          },
        },
      },
      {
        name: 'get_allergies',
        description: 'Get list of allergies and intolerances',
        inputSchema: {
          type: 'object',
          properties: {
            patient_id: {
              type: 'string',
              description: 'Patient ID (defaults to "me" for authenticated user)',
              default: 'me',
            },
          },
        },
      },
      {
        name: 'get_auth_url',
        description: 'Get the NHS Login authorization URL to authenticate and grant access to your health records',
        inputSchema: {
          type: 'object',
          properties: {},
        },
      },
      {
        name: 'exchange_auth_code',
        description: 'Exchange the authorization code for an access token after NHS Login authentication',
        inputSchema: {
          type: 'object',
          properties: {
            code: {
              type: 'string',
              description: 'Authorization code from NHS Login callback',
            },
          },
          required: ['code'],
        },
      },
      {
        name: 'get_app_token',
        description: 'Get an application access token using client credentials (for application-restricted APIs)',
        inputSchema: {
          type: 'object',
          properties: {},
        },
      },
      {
        name: 'test_config',
        description: 'Test the NHS API configuration and show diagnostic information',
        inputSchema: {
          type: 'object',
          properties: {},
        },
      },
    ],
  };
});

/**
 * Handle tool calls
 */
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    switch (name) {
      case 'get_patient_info': {
        const patientId = (args?.patient_id as string) || 'me';
        const patient = await nhsClient.getPatient(patientId);

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(patient, null, 2),
            },
          ],
        };
      }

      case 'get_medications': {
        const patientId = (args?.patient_id as string) || 'me';
        const medications = await nhsClient.getMedicationRequests(patientId);

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(medications, null, 2),
            },
          ],
        };
      }

      case 'get_appointments': {
        const patientId = (args?.patient_id as string) || 'me';
        const status = args?.status as string | undefined;
        const appointments = await nhsClient.getAppointments(patientId, status);

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(appointments, null, 2),
            },
          ],
        };
      }

      case 'get_conditions': {
        const patientId = (args?.patient_id as string) || 'me';
        const conditions = await nhsClient.getConditions(patientId);

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(conditions, null, 2),
            },
          ],
        };
      }

      case 'get_immunizations': {
        const patientId = (args?.patient_id as string) || 'me';
        const immunizations = await nhsClient.getImmunizations(patientId);

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(immunizations, null, 2),
            },
          ],
        };
      }

      case 'get_allergies': {
        const patientId = (args?.patient_id as string) || 'me';
        const allergies = await nhsClient.getAllergies(patientId);

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(allergies, null, 2),
            },
          ],
        };
      }

      case 'get_auth_url': {
        const authUrl = authenticator.getAuthorizationUrl();

        return {
          content: [
            {
              type: 'text',
              text: `🔐 NHS Login Authorization - Manual Code Copy Method

Step 1: Visit this authorization URL in your browser:

${authUrl}

Step 2: Log in with your NHS credentials and authorize access

Step 3: After authorizing, you'll be redirected to a URL that looks like:
http://localhost:3000/callback?code=AUTHORIZATION_CODE&state=...

The page won't load (that's normal - we don't have a callback server), but that's okay!

Step 4: Copy the AUTHORIZATION_CODE from the URL in your browser's address bar

Step 5: Come back here and use the exchange_auth_code tool:
"Exchange this authorization code: YOUR_CODE_HERE"

Example:
If the URL is: http://localhost:3000/callback?code=abc123xyz&state=...
Then the code is: abc123xyz`,
            },
          ],
        };
      }

      case 'exchange_auth_code': {
        const code = args?.code as string;
        if (!code) {
          throw new Error('Authorization code is required');
        }

        const tokenResponse = await authenticator.exchangeCodeForToken(code);

        return {
          content: [
            {
              type: 'text',
              text: `Authentication successful!\n\nAccess token obtained (expires in ${tokenResponse.expires_in} seconds).\n\nYou can now use the other tools to access your NHS data.\n\nIMPORTANT: Save these tokens in your .env file:\nNHS_ACCESS_TOKEN=${tokenResponse.access_token}\nNHS_REFRESH_TOKEN=${tokenResponse.refresh_token}`,
            },
          ],
        };
      }

      case 'get_app_token': {
        const tokenResponse = await authenticator.getClientCredentialsToken();

        return {
          content: [
            {
              type: 'text',
              text: `Application authentication successful!\n\nAccess token obtained using client credentials (expires in ${tokenResponse.expires_in} seconds).\n\nYou can now use the other tools to access NHS APIs in application-restricted mode.\n\nThe access token has been stored internally and will be used automatically for API requests.`,
            },
          ],
        };
      }

      case 'test_config': {
        const configInfo = {
          apiBaseUrl: nhsConfig.apiBaseUrl,
          authUrl: nhsConfig.authUrl,
          clientId: nhsConfig.clientId,
          redirectUri: nhsConfig.redirectUri,
          hasAccessToken: !!nhsConfig.accessToken,
          hasRefreshToken: !!nhsConfig.refreshToken,
        };

        return {
          content: [
            {
              type: 'text',
              text: `NHS API Configuration:

API Base URL: ${configInfo.apiBaseUrl}
Auth URL: ${configInfo.authUrl}
Client ID: ${configInfo.clientId}
Redirect URI: ${configInfo.redirectUri}
Has Access Token: ${configInfo.hasAccessToken}
Has Refresh Token: ${configInfo.hasRefreshToken}

This configuration is for the External Development (DEV) environment.

To test authentication, try:
1. "Get an application access token" - For API key auth
2. "Get my NHS authorization URL" - For user OAuth auth

If you're getting errors, they may be due to:
- The dev environment being unavailable
- API keys not being activated yet
- Needing to set up public/private key pair
- OAuth endpoints being different in dev environment`,
            },
          ],
        };
      }

      default:
        throw new Error(`Unknown tool: ${name}`);
    }
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    return {
      content: [
        {
          type: 'text',
          text: `Error: ${errorMessage}`,
        },
      ],
      isError: true,
    };
  }
});

/**
 * List available resources
 */
server.setRequestHandler(ListResourcesRequestSchema, async () => {
  return {
    resources: [
      {
        uri: 'nhs://patient/info',
        name: 'Patient Information',
        description: 'Your NHS patient demographic information',
        mimeType: 'application/json',
      },
      {
        uri: 'nhs://medications',
        name: 'Medications',
        description: 'Your current and past prescriptions',
        mimeType: 'application/json',
      },
      {
        uri: 'nhs://appointments',
        name: 'Appointments',
        description: 'Your upcoming and past appointments',
        mimeType: 'application/json',
      },
      {
        uri: 'nhs://conditions',
        name: 'Medical Conditions',
        description: 'Your diagnoses and medical problems',
        mimeType: 'application/json',
      },
      {
        uri: 'nhs://immunizations',
        name: 'Immunizations',
        description: 'Your vaccination history',
        mimeType: 'application/json',
      },
      {
        uri: 'nhs://allergies',
        name: 'Allergies',
        description: 'Your allergies and intolerances',
        mimeType: 'application/json',
      },
    ],
  };
});

/**
 * Read resource content
 */
server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
  const { uri } = request.params;

  try {
    switch (uri) {
      case 'nhs://patient/info': {
        const patient = await nhsClient.getPatient();
        return {
          contents: [
            {
              uri,
              mimeType: 'application/json',
              text: JSON.stringify(patient, null, 2),
            },
          ],
        };
      }

      case 'nhs://medications': {
        const medications = await nhsClient.getMedicationRequests();
        return {
          contents: [
            {
              uri,
              mimeType: 'application/json',
              text: JSON.stringify(medications, null, 2),
            },
          ],
        };
      }

      case 'nhs://appointments': {
        const appointments = await nhsClient.getAppointments();
        return {
          contents: [
            {
              uri,
              mimeType: 'application/json',
              text: JSON.stringify(appointments, null, 2),
            },
          ],
        };
      }

      case 'nhs://conditions': {
        const conditions = await nhsClient.getConditions();
        return {
          contents: [
            {
              uri,
              mimeType: 'application/json',
              text: JSON.stringify(conditions, null, 2),
            },
          ],
        };
      }

      case 'nhs://immunizations': {
        const immunizations = await nhsClient.getImmunizations();
        return {
          contents: [
            {
              uri,
              mimeType: 'application/json',
              text: JSON.stringify(immunizations, null, 2),
            },
          ],
        };
      }

      case 'nhs://allergies': {
        const allergies = await nhsClient.getAllergies();
        return {
          contents: [
            {
              uri,
              mimeType: 'application/json',
              text: JSON.stringify(allergies, null, 2),
            },
          ],
        };
      }

      default:
        throw new Error(`Unknown resource: ${uri}`);
    }
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    throw new Error(`Failed to read resource ${uri}: ${errorMessage}`);
  }
});

/**
 * Start the server
 */
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);

  // Log to stderr safely (ignore EPIPE errors)
  try {
    console.error('NHS Data MCP Server running on stdio');
    console.error('Configuration:', {
      apiBaseUrl: nhsConfig.apiBaseUrl,
      authUrl: nhsConfig.authUrl,
      hasAccessToken: !!nhsConfig.accessToken,
    });
  } catch (e) {
    // Ignore EPIPE errors during logging
  }
}

main().catch((error) => {
  console.error('Fatal error:', error);
  process.exit(1);
});
