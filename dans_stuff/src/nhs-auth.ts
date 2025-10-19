/**
 * NHS OAuth2 Authentication Module
 * Handles NHS Login authentication flow
 */

import axios from 'axios';
import { NHSConfig, OAuthTokenResponse } from './types.js';

export class NHSAuthenticator {
  private config: NHSConfig;

  constructor(config: NHSConfig) {
    this.config = config;
  }

  /**
   * Generate the OAuth2 authorization URL for NHS Login
   * User must visit this URL to authorize access
   */
  getAuthorizationUrl(): string {
    const params = new URLSearchParams({
      client_id: this.config.clientId,
      redirect_uri: this.config.redirectUri,
      response_type: 'code',
      scope: 'openid profile email nhs-number',
      state: this.generateState(),
    });

    // NHS Login Mock uses /auth, standard OAuth uses /authorize
    const authEndpoint = this.config.authUrl.includes('identity.ptl') ? '/auth' : '/authorize';
    return `${this.config.authUrl}${authEndpoint}?${params.toString()}`;
  }

  /**
   * Exchange authorization code for access token
   */
  async exchangeCodeForToken(code: string): Promise<OAuthTokenResponse> {
    try {
      const response = await axios.post<OAuthTokenResponse>(
        `${this.config.authUrl}/token`,
        new URLSearchParams({
          grant_type: 'authorization_code',
          code,
          redirect_uri: this.config.redirectUri,
          client_id: this.config.clientId,
          client_secret: this.config.clientSecret,
        }),
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
        }
      );

      // Store tokens in config
      this.config.accessToken = response.data.access_token;
      this.config.refreshToken = response.data.refresh_token;

      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(`Failed to exchange code for token: ${error.response?.data?.error || error.message}`);
      }
      throw error;
    }
  }

  /**
   * Refresh the access token using refresh token
   */
  async refreshAccessToken(): Promise<OAuthTokenResponse> {
    if (!this.config.refreshToken) {
      throw new Error('No refresh token available');
    }

    try {
      const response = await axios.post<OAuthTokenResponse>(
        `${this.config.authUrl}/token`,
        new URLSearchParams({
          grant_type: 'refresh_token',
          refresh_token: this.config.refreshToken,
          client_id: this.config.clientId,
          client_secret: this.config.clientSecret,
        }),
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
        }
      );

      this.config.accessToken = response.data.access_token;
      this.config.refreshToken = response.data.refresh_token;

      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(`Failed to refresh token: ${error.response?.data?.error || error.message}`);
      }
      throw error;
    }
  }

  /**
   * Get access token using client credentials flow (for application-restricted APIs)
   * This is used when the application accesses APIs on its own behalf, not on behalf of a user
   */
  async getClientCredentialsToken(): Promise<OAuthTokenResponse> {
    try {
      const response = await axios.post<OAuthTokenResponse>(
        `${this.config.authUrl}/token`,
        new URLSearchParams({
          grant_type: 'client_credentials',
          client_id: this.config.clientId,
          client_secret: this.config.clientSecret,
        }),
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
        }
      );

      // Store token in config
      this.config.accessToken = response.data.access_token;
      if (response.data.refresh_token) {
        this.config.refreshToken = response.data.refresh_token;
      }

      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(`Failed to get client credentials token: ${error.response?.data?.error || error.message}`);
      }
      throw error;
    }
  }

  /**
   * Get current access token
   */
  getAccessToken(): string | undefined {
    return this.config.accessToken;
  }

  /**
   * Set access token manually (for testing or stored credentials)
   */
  setAccessToken(token: string): void {
    this.config.accessToken = token;
  }

  /**
   * Get client ID (for OAuth authentication)
   */
  getClientId(): string {
    return this.config.clientId;
  }

  /**
   * Get API key (for API key header authentication)
   * Falls back to client ID if API key is not set
   */
  getApiKey(): string {
    return this.config.apiKey || this.config.clientId;
  }

  /**
   * Generate a random state parameter for CSRF protection
   */
  private generateState(): string {
    return Math.random().toString(36).substring(2, 15) +
           Math.random().toString(36).substring(2, 15);
  }
}
