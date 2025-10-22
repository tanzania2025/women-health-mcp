/**
 * NHS FHIR Data Types
 * Based on NHS FHIR API specifications
 */

export interface NHSConfig {
  apiBaseUrl: string;
  authUrl: string;
  clientId: string;
  clientSecret: string;
  apiKey?: string;
  redirectUri: string;
  accessToken?: string;
  refreshToken?: string;
}

export interface FHIRPatient {
  resourceType: "Patient";
  id: string;
  identifier?: Array<{
    system: string;
    value: string; // NHS number
  }>;
  name?: Array<{
    use: string;
    family: string;
    given: string[];
  }>;
  birthDate?: string;
  gender?: string;
  address?: Array<{
    line: string[];
    city: string;
    postalCode: string;
  }>;
}

export interface FHIRMedicationRequest {
  resourceType: "MedicationRequest";
  id: string;
  status: string;
  intent: string;
  medicationCodeableConcept?: {
    coding: Array<{
      system: string;
      code: string;
      display: string;
    }>;
    text: string;
  };
  subject: {
    reference: string;
  };
  authoredOn?: string;
  dosageInstruction?: Array<{
    text: string;
  }>;
}

export interface FHIRAppointment {
  resourceType: "Appointment";
  id: string;
  status: string;
  serviceType?: Array<{
    coding: Array<{
      display: string;
    }>;
  }>;
  description?: string;
  start?: string;
  end?: string;
  participant?: Array<{
    actor: {
      reference: string;
      display: string;
    };
  }>;
}

export interface FHIRCondition {
  resourceType: "Condition";
  id: string;
  clinicalStatus?: {
    coding: Array<{
      code: string;
    }>;
  };
  code?: {
    coding: Array<{
      system: string;
      code: string;
      display: string;
    }>;
    text: string;
  };
  subject: {
    reference: string;
  };
  recordedDate?: string;
}

export interface FHIRBundle {
  resourceType: "Bundle";
  type: string;
  total?: number;
  entry?: Array<{
    resource: FHIRPatient | FHIRMedicationRequest | FHIRAppointment | FHIRCondition;
  }>;
}

export interface OAuthTokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  scope: string;
}
