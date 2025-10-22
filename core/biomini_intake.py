"""
Biomini Data Pipeline - Ingests and standardizes patient data with ASRM classification
"""
import json
from typing import Dict, Any
from datetime import datetime


def classify_ovarian_reserve(amh: float) -> str:
    """Classify ovarian reserve based on ASRM standards."""
    if amh < 0.5:
        return "critically_low"
    elif amh < 1.0:
        return "very_low"
    elif amh < 2.0:
        return "low"
    else:
        return "normal"


def ingest_patient(fhir_json: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ingest raw patient data and standardize it with ASRM classification.
    
    Args:
        fhir_json: Raw patient data in FHIR-like format
        
    Returns:
        Structured JSON with demographics, labs, and clinical context
    """
    amh_value = fhir_json.get('amh', 0)
    
    standardized_data = {
        "patient_id": fhir_json.get('patient_id', 'Unknown'),
        "timestamp": datetime.now().isoformat(),
        "demographics": {
            "age": fhir_json.get('age'),
            "years_trying_to_conceive": fhir_json.get('attempts_to_conceive', 0) / 12
        },
        "reproductive_labs": {
            "amh": amh_value,
            "fsh": fhir_json.get('fsh'),
            "lh": fhir_json.get('lh'),
            "estradiol": fhir_json.get('estradiol')
        },
        "ovarian_reserve_status": classify_ovarian_reserve(amh_value),
        "clinical_context": {
            "cycle_history": fhir_json.get('cycle_history', 'unknown'),
            "prior_ivf": fhir_json.get('prior_ivf', 'none'),
            "attempts_to_conceive_months": fhir_json.get('attempts_to_conceive', 0)
        }
    }
    
    return standardized_data


# Sample patient data
SAMPLE_PATIENT_1 = {
    "patient_id": "P001",
    "age": 38,
    "amh": 0.8,
    "fsh": 12,
    "lh": 8,
    "estradiol": 45,
    "cycle_history": "regular, 28 days",
    "attempts_to_conceive": 18,
    "prior_ivf": "none"
}

SAMPLE_PATIENT_2 = {
    "patient_id": "P002",
    "age": 45,
    "amh": 0.3,
    "fsh": 15,
    "lh": 10,
    "estradiol": 35,
    "cycle_history": "irregular, 35-45 days",
    "attempts_to_conceive": 24,
    "prior_ivf": "2 cycles, unsuccessful"
}


if __name__ == "__main__":
    # Test with sample patients
    print("=== BIOMINI DATA INTAKE TEST ===\n")
    
    patient1_data = ingest_patient(SAMPLE_PATIENT_1)
    print("Patient 1 (38 y/o, AMH 0.8):")
    print(json.dumps(patient1_data, indent=2))
    
    print("\n" + "="*50 + "\n")
    
    patient2_data = ingest_patient(SAMPLE_PATIENT_2)
    print("Patient 2 (45 y/o, AMH 0.3):")
    print(json.dumps(patient2_data, indent=2))