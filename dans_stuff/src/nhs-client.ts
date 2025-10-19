/**
 * NHS FHIR API Client
 * Handles API requests to NHS FHIR endpoints
 */

import axios, { AxiosInstance } from 'axios';
import { NHSConfig, FHIRBundle, FHIRPatient } from './types.js';
import { NHSAuthenticator } from './nhs-auth.js';

export class NHSClient {
  private config: NHSConfig;
  private authenticator: NHSAuthenticator;
  private axiosInstance: AxiosInstance;

  constructor(config: NHSConfig, authenticator: NHSAuthenticator) {
    this.config = config;
    this.authenticator = authenticator;

    this.axiosInstance = axios.create({
      baseURL: this.config.apiBaseUrl,
      headers: {
        'Accept': 'application/fhir+json',
        'Content-Type': 'application/fhir+json',
        // NHS API Platform requires the apikey header
        'apikey': this.authenticator.getApiKey(),
      },
    });

    // Add auth interceptor
    this.axiosInstance.interceptors.request.use(
      (config) => {
        // Always add API key header
        config.headers['apikey'] = this.authenticator.getApiKey();

        // Add bearer token if available
        const token = this.authenticator.getAccessToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Add response interceptor to handle token refresh
    this.axiosInstance.interceptors.response.use(
      (response) => response,
      async (error) => {
        if (error.response?.status === 401) {
          // Try to refresh token
          try {
            await this.authenticator.refreshAccessToken();
            // Retry original request
            return this.axiosInstance.request(error.config);
          } catch (refreshError) {
            return Promise.reject(new Error('Authentication failed. Please re-authenticate.'));
          }
        }
        return Promise.reject(error);
      }
    );
  }

  /**
   * Get patient information
   */
  async getPatient(patientId: string = 'me'): Promise<FHIRPatient> {
    try {
      const response = await this.axiosInstance.get<FHIRPatient>(`/Patient/${patientId}`);
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(`Failed to get patient data: ${error.response?.data?.issue?.[0]?.diagnostics || error.message}`);
      }
      throw error;
    }
  }

  /**
   * Get medication requests (prescriptions)
   */
  async getMedicationRequests(patientId: string = 'me'): Promise<FHIRBundle> {
    try {
      const response = await this.axiosInstance.get<FHIRBundle>('/MedicationRequest', {
        params: {
          patient: patientId,
          _sort: '-authoredon',
        },
      });
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(`Failed to get medications: ${error.response?.data?.issue?.[0]?.diagnostics || error.message}`);
      }
      throw error;
    }
  }

  /**
   * Get appointments
   */
  async getAppointments(patientId: string = 'me', status?: string): Promise<FHIRBundle> {
    try {
      const params: Record<string, string> = {
        patient: patientId,
        _sort: '-date',
      };

      if (status) {
        params.status = status;
      }

      const response = await this.axiosInstance.get<FHIRBundle>('/Appointment', {
        params,
      });
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(`Failed to get appointments: ${error.response?.data?.issue?.[0]?.diagnostics || error.message}`);
      }
      throw error;
    }
  }

  /**
   * Get conditions (diagnoses, problems)
   */
  async getConditions(patientId: string = 'me'): Promise<FHIRBundle> {
    try {
      const response = await this.axiosInstance.get<FHIRBundle>('/Condition', {
        params: {
          patient: patientId,
          _sort: '-recorded-date',
        },
      });
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(`Failed to get conditions: ${error.response?.data?.issue?.[0]?.diagnostics || error.message}`);
      }
      throw error;
    }
  }

  /**
   * Get immunizations
   */
  async getImmunizations(patientId: string = 'me'): Promise<FHIRBundle> {
    try {
      const response = await this.axiosInstance.get<FHIRBundle>('/Immunization', {
        params: {
          patient: patientId,
          _sort: '-date',
        },
      });
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(`Failed to get immunizations: ${error.response?.data?.issue?.[0]?.diagnostics || error.message}`);
      }
      throw error;
    }
  }

  /**
   * Get allergies and intolerances
   */
  async getAllergies(patientId: string = 'me'): Promise<FHIRBundle> {
    try {
      const response = await this.axiosInstance.get<FHIRBundle>('/AllergyIntolerance', {
        params: {
          patient: patientId,
        },
      });
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(`Failed to get allergies: ${error.response?.data?.issue?.[0]?.diagnostics || error.message}`);
      }
      throw error;
    }
  }

  /**
   * Search for any FHIR resource with custom parameters
   */
  async searchResource(resourceType: string, params: Record<string, string>): Promise<FHIRBundle> {
    try {
      const response = await this.axiosInstance.get<FHIRBundle>(`/${resourceType}`, {
        params,
      });
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(`Failed to search ${resourceType}: ${error.response?.data?.issue?.[0]?.diagnostics || error.message}`);
      }
      throw error;
    }
  }
}
