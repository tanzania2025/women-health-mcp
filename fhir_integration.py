"""
FHIR-compliant Data Exchange for Women's Health MCP
Implements FHIR R4 standards with reproductive health extensions
"""

import json
from datetime import datetime, date
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
from decimal import Decimal


class FHIRResourceType(Enum):
    """FHIR resource types relevant to reproductive health."""
    PATIENT = "Patient"
    OBSERVATION = "Observation"
    CONDITION = "Condition"
    PROCEDURE = "Procedure"
    MEDICATION_REQUEST = "MedicationRequest"
    DIAGNOSTIC_REPORT = "DiagnosticReport"
    CARE_PLAN = "CarePlan"
    ENCOUNTER = "Encounter"
    QUESTIONNAIRE_RESPONSE = "QuestionnaireResponse"
    FAMILY_MEMBER_HISTORY = "FamilyMemberHistory"


class ObservationCategory(Enum):
    """FHIR observation categories for reproductive health."""
    REPRODUCTIVE_HEALTH = "reproductive-health"
    LABORATORY = "laboratory"
    VITAL_SIGNS = "vital-signs"
    SOCIAL_HISTORY = "social-history"
    REPRODUCTIVE_HISTORY = "reproductive-history"


@dataclass
class FHIRBundle:
    """FHIR Bundle containing multiple resources."""
    resource_type: str = "Bundle"
    id: Optional[str] = None
    type: str = "collection"
    timestamp: Optional[str] = None
    total: Optional[int] = None
    entry: List[Dict[str, Any]] = None


class ReproductiveHealthFHIR:
    """
    FHIR R4 compliant data exchange for reproductive health.
    Implements standard FHIR resources with reproductive health extensions.
    """
    
    def __init__(self):
        self.reproductive_health_codes = self._initialize_reproductive_codes()
        self.fhir_extensions = self._initialize_fhir_extensions()
    
    def _initialize_reproductive_codes(self) -> Dict[str, Dict[str, str]]:
        """Initialize LOINC and SNOMED codes for reproductive health."""
        return {
            "laboratory": {
                # Hormonal assays
                "amh": {"loinc": "33746-9", "display": "Anti-Mullerian hormone [Mass/volume] in Serum"},
                "fsh": {"loinc": "15067-2", "display": "Follitropin [Units/volume] in Serum"},
                "lh": {"loinc": "10501-5", "display": "Lutropin [Units/volume] in Serum"},
                "estradiol": {"loinc": "2243-4", "display": "Estradiol [Mass/volume] in Serum"},
                "progesterone": {"loinc": "2951-2", "display": "Progesterone [Mass/volume] in Serum"},
                "testosterone": {"loinc": "2986-8", "display": "Testosterone [Mass/volume] in Serum"},
                "prolactin": {"loinc": "2842-3", "display": "Prolactin [Mass/volume] in Serum"},
                "thyroid_stimulating_hormone": {"loinc": "3016-3", "display": "Thyrotropin [Units/volume] in Serum"}
            },
            "conditions": {
                # Reproductive conditions
                "infertility": {"snomed": "8619003", "display": "Infertile"},
                "pcos": {"snomed": "69878008", "display": "Polycystic ovary syndrome"},
                "endometriosis": {"snomed": "129103003", "display": "Endometriosis"},
                "menopause": {"snomed": "161712005", "display": "Menopause present"},
                "amenorrhea": {"snomed": "14302008", "display": "Amenorrhea"},
                "dysmenorrhea": {"snomed": "279039007", "display": "Dysmenorrhea"},
                "diminished_ovarian_reserve": {"snomed": "237046006", "display": "Diminished ovarian reserve"}
            },
            "procedures": {
                # ART procedures
                "ivf": {"snomed": "63487001", "display": "In vitro fertilization"},
                "icsi": {"snomed": "225234009", "display": "Intracytoplasmic sperm injection"},
                "iui": {"snomed": "58533008", "display": "Intrauterine insemination"},
                "embryo_transfer": {"snomed": "176837000", "display": "Embryo transfer"},
                "ovarian_stimulation": {"snomed": "265760000", "display": "Ovarian stimulation"},
                "egg_retrieval": {"snomed": "176820002", "display": "Transvaginal oocyte retrieval"}
            },
            "social_history": {
                "smoking_status": {"loinc": "72166-2", "display": "Tobacco smoking status"},
                "alcohol_use": {"loinc": "11331-6", "display": "History of alcohol use"},
                "exercise_frequency": {"loinc": "68516-4", "display": "Exercise frequency"}
            }
        }
    
    def _initialize_fhir_extensions(self) -> Dict[str, str]:
        """Initialize custom FHIR extensions for reproductive health."""
        return {
            "cycle_day": "http://hl7.org/fhir/us/reproductive-health/StructureDefinition/cycle-day",
            "cycle_phase": "http://hl7.org/fhir/us/reproductive-health/StructureDefinition/cycle-phase",
            "fertility_intent": "http://hl7.org/fhir/us/reproductive-health/StructureDefinition/fertility-intent",
            "contraceptive_method": "http://hl7.org/fhir/us/reproductive-health/StructureDefinition/contraceptive-method",
            "menstrual_flow": "http://hl7.org/fhir/us/reproductive-health/StructureDefinition/menstrual-flow",
            "ovulation_method": "http://hl7.org/fhir/us/reproductive-health/StructureDefinition/ovulation-method"
        }
    
    def create_patient_resource(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create FHIR Patient resource for reproductive health patient."""
        
        patient_resource = {
            "resourceType": "Patient",
            "id": patient_data.get("patient_id", str(uuid.uuid4())),
            "active": True,
            "name": [
                {
                    "use": "official",
                    "family": patient_data.get("family_name", "Anonymous"),
                    "given": [patient_data.get("given_name", "Patient")]
                }
            ],
            "gender": patient_data.get("gender", "female"),
            "birthDate": patient_data.get("birth_date"),
            "address": [],
            "telecom": [],
            "contact": [],
            "extension": []
        }
        
        # Add reproductive health extensions
        if patient_data.get("fertility_intent"):
            patient_resource["extension"].append({
                "url": self.fhir_extensions["fertility_intent"],
                "valueString": patient_data["fertility_intent"]
            })
        
        # Add address if provided
        if patient_data.get("address"):
            patient_resource["address"].append({
                "use": "home",
                "line": [patient_data["address"].get("street", "")],
                "city": patient_data["address"].get("city", ""),
                "state": patient_data["address"].get("state", ""),
                "postalCode": patient_data["address"].get("zip", ""),
                "country": patient_data["address"].get("country", "US")
            })
        
        return patient_resource
    
    def create_reproductive_observation(self,
                                      patient_id: str,
                                      observation_type: str,
                                      value: Union[float, str],
                                      unit: Optional[str] = None,
                                      date: Optional[str] = None,
                                      cycle_day: Optional[int] = None) -> Dict[str, Any]:
        """Create FHIR Observation for reproductive health data."""
        
        observation_id = str(uuid.uuid4())
        observation_date = date or datetime.now().isoformat()
        
        # Get coding for observation type
        if observation_type in self.reproductive_health_codes["laboratory"]:
            code_info = self.reproductive_health_codes["laboratory"][observation_type]
            category = "laboratory"
        else:
            # Default coding
            code_info = {"loinc": "33747-0", "display": "General reproductive health observation"}
            category = "reproductive-health"
        
        observation = {
            "resourceType": "Observation",
            "id": observation_id,
            "status": "final",
            "category": [
                {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                            "code": category,
                            "display": category.replace("-", " ").title()
                        }
                    ]
                }
            ],
            "code": {
                "coding": [
                    {
                        "system": "http://loinc.org",
                        "code": code_info["loinc"],
                        "display": code_info["display"]
                    }
                ]
            },
            "subject": {
                "reference": f"Patient/{patient_id}"
            },
            "effectiveDateTime": observation_date,
            "valueQuantity": {
                "value": float(value) if isinstance(value, (int, float, Decimal)) else None,
                "unit": unit or "",
                "system": "http://unitsofmeasure.org"
            } if isinstance(value, (int, float, Decimal)) else None,
            "valueString": str(value) if not isinstance(value, (int, float, Decimal)) else None,
            "extension": []
        }
        
        # Add cycle day extension if provided
        if cycle_day is not None:
            observation["extension"].append({
                "url": self.fhir_extensions["cycle_day"],
                "valueInteger": cycle_day
            })
        
        return observation
    
    def create_cycle_tracking_observations(self,
                                         patient_id: str,
                                         cycle_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create multiple FHIR observations for cycle tracking data."""
        
        observations = []
        cycle_start_date = cycle_data.get("start_date")
        
        # Menstrual flow observations
        if "flow_data" in cycle_data:
            for day, flow_level in enumerate(cycle_data["flow_data"], 1):
                if flow_level and flow_level != "none":
                    obs_date = self._add_days_to_date(cycle_start_date, day - 1)
                    
                    flow_obs = {
                        "resourceType": "Observation",
                        "id": str(uuid.uuid4()),
                        "status": "final",
                        "category": [
                            {
                                "coding": [
                                    {
                                        "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                                        "code": "reproductive-health"
                                    }
                                ]
                            }
                        ],
                        "code": {
                            "coding": [
                                {
                                    "system": "http://snomed.info/sct",
                                    "code": "289530006",
                                    "display": "Menstrual flow"
                                }
                            ]
                        },
                        "subject": {"reference": f"Patient/{patient_id}"},
                        "effectiveDate": obs_date,
                        "valueString": flow_level,
                        "extension": [
                            {
                                "url": self.fhir_extensions["cycle_day"],
                                "valueInteger": day
                            },
                            {
                                "url": self.fhir_extensions["menstrual_flow"],
                                "valueString": flow_level
                            }
                        ]
                    }
                    observations.append(flow_obs)
        
        # Basal body temperature observations
        if "temperature_data" in cycle_data:
            for day, temp in enumerate(cycle_data["temperature_data"], 1):
                if temp:
                    obs_date = self._add_days_to_date(cycle_start_date, day - 1)
                    
                    temp_obs = self.create_reproductive_observation(
                        patient_id=patient_id,
                        observation_type="basal_body_temperature",
                        value=temp,
                        unit="Cel",
                        date=obs_date,
                        cycle_day=day
                    )
                    observations.append(temp_obs)
        
        # Ovulation test observations
        if "ovulation_tests" in cycle_data:
            for test in cycle_data["ovulation_tests"]:
                test_date = test.get("date")
                result = test.get("result")
                
                ovulation_obs = {
                    "resourceType": "Observation",
                    "id": str(uuid.uuid4()),
                    "status": "final",
                    "category": [
                        {
                            "coding": [
                                {
                                    "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                                    "code": "reproductive-health"
                                }
                            ]
                        }
                    ],
                    "code": {
                        "coding": [
                            {
                                "system": "http://loinc.org",
                                "code": "33747-0",
                                "display": "Ovulation test"
                            }
                        ]
                    },
                    "subject": {"reference": f"Patient/{patient_id}"},
                    "effectiveDate": test_date,
                    "valueString": result,
                    "extension": [
                        {
                            "url": self.fhir_extensions["ovulation_method"],
                            "valueString": test.get("method", "urine_lh")
                        }
                    ]
                }
                observations.append(ovulation_obs)
        
        return observations
    
    def create_hormonal_lab_report(self,
                                 patient_id: str,
                                 lab_results: Dict[str, Any],
                                 test_date: str) -> Dict[str, Any]:
        """Create FHIR DiagnosticReport for hormonal laboratory results."""
        
        report_id = str(uuid.uuid4())
        
        # Create individual observations for each lab result
        result_observations = []
        for hormone, value in lab_results.items():
            if hormone in self.reproductive_health_codes["laboratory"]:
                unit_mapping = {
                    "amh": "ng/mL",
                    "fsh": "mIU/mL",
                    "lh": "mIU/mL",
                    "estradiol": "pg/mL",
                    "progesterone": "ng/mL",
                    "testosterone": "ng/dL",
                    "prolactin": "ng/mL"
                }
                
                obs = self.create_reproductive_observation(
                    patient_id=patient_id,
                    observation_type=hormone,
                    value=value,
                    unit=unit_mapping.get(hormone, ""),
                    date=test_date
                )
                result_observations.append(obs)
        
        # Create the diagnostic report
        diagnostic_report = {
            "resourceType": "DiagnosticReport",
            "id": report_id,
            "status": "final",
            "category": [
                {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/v2-0074",
                            "code": "LAB",
                            "display": "Laboratory"
                        }
                    ]
                }
            ],
            "code": {
                "coding": [
                    {
                        "system": "http://loinc.org",
                        "code": "33747-0",
                        "display": "Reproductive hormone panel"
                    }
                ]
            },
            "subject": {
                "reference": f"Patient/{patient_id}"
            },
            "effectiveDateTime": test_date,
            "issued": datetime.now().isoformat(),
            "result": [
                {"reference": f"Observation/{obs['id']}"} for obs in result_observations
            ],
            "conclusion": self._generate_lab_interpretation(lab_results)
        }
        
        return {
            "diagnostic_report": diagnostic_report,
            "observations": result_observations
        }
    
    def create_ivf_procedure_resource(self,
                                    patient_id: str,
                                    procedure_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create FHIR Procedure resource for IVF treatment."""
        
        procedure_id = str(uuid.uuid4())
        procedure_type = procedure_data.get("type", "ivf")
        
        # Get SNOMED code for procedure
        procedure_code = self.reproductive_health_codes["procedures"].get(
            procedure_type,
            {"snomed": "63487001", "display": "In vitro fertilization"}
        )
        
        procedure = {
            "resourceType": "Procedure",
            "id": procedure_id,
            "status": procedure_data.get("status", "completed"),
            "category": {
                "coding": [
                    {
                        "system": "http://snomed.info/sct",
                        "code": "387713003",
                        "display": "Surgical procedure"
                    }
                ]
            },
            "code": {
                "coding": [
                    {
                        "system": "http://snomed.info/sct",
                        "code": procedure_code["snomed"],
                        "display": procedure_code["display"]
                    }
                ]
            },
            "subject": {
                "reference": f"Patient/{patient_id}"
            },
            "performedDateTime": procedure_data.get("date"),
            "outcome": {
                "text": procedure_data.get("outcome", "")
            },
            "note": [
                {
                    "text": procedure_data.get("notes", "")
                }
            ]
        }
        
        # Add cycle-specific information
        if "cycle_number" in procedure_data:
            procedure["extension"] = [
                {
                    "url": "http://hl7.org/fhir/us/reproductive-health/StructureDefinition/cycle-number",
                    "valueInteger": procedure_data["cycle_number"]
                }
            ]
        
        return procedure
    
    def create_reproductive_condition(self,
                                    patient_id: str,
                                    condition_type: str,
                                    clinical_status: str = "active",
                                    onset_date: Optional[str] = None) -> Dict[str, Any]:
        """Create FHIR Condition resource for reproductive health condition."""
        
        condition_id = str(uuid.uuid4())
        
        # Get SNOMED code for condition
        condition_code = self.reproductive_health_codes["conditions"].get(
            condition_type,
            {"snomed": "8619003", "display": "Reproductive health condition"}
        )
        
        condition = {
            "resourceType": "Condition",
            "id": condition_id,
            "clinicalStatus": {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                        "code": clinical_status
                    }
                ]
            },
            "verificationStatus": {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status",
                        "code": "confirmed"
                    }
                ]
            },
            "category": [
                {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/condition-category",
                            "code": "problem-list-item"
                        }
                    ]
                }
            ],
            "code": {
                "coding": [
                    {
                        "system": "http://snomed.info/sct",
                        "code": condition_code["snomed"],
                        "display": condition_code["display"]
                    }
                ]
            },
            "subject": {
                "reference": f"Patient/{patient_id}"
            }
        }
        
        # Add onset date if provided
        if onset_date:
            condition["onsetDateTime"] = onset_date
        
        return condition
    
    def create_fhir_bundle(self, resources: List[Dict[str, Any]], bundle_type: str = "collection") -> Dict[str, Any]:
        """Create FHIR Bundle containing multiple resources."""
        
        bundle_id = str(uuid.uuid4())
        bundle_timestamp = datetime.now().isoformat()
        
        bundle_entries = []
        for resource in resources:
            entry = {
                "resource": resource
            }
            
            # Add fullUrl for searchable bundles
            if bundle_type in ["searchset", "history"]:
                entry["fullUrl"] = f"http://example.org/fhir/{resource['resourceType']}/{resource.get('id', '')}"
            
            bundle_entries.append(entry)
        
        bundle = {
            "resourceType": "Bundle",
            "id": bundle_id,
            "type": bundle_type,
            "timestamp": bundle_timestamp,
            "total": len(resources),
            "entry": bundle_entries
        }
        
        return bundle
    
    def _add_days_to_date(self, date_str: str, days: int) -> str:
        """Add days to a date string and return new date string."""
        try:
            base_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            new_date = base_date + timedelta(days=days)
            return new_date.strftime("%Y-%m-%d")
        except:
            return date_str
    
    def _generate_lab_interpretation(self, lab_results: Dict[str, Any]) -> str:
        """Generate clinical interpretation of laboratory results."""
        interpretations = []
        
        if "amh" in lab_results:
            amh_value = lab_results["amh"]
            if amh_value < 1.0:
                interpretations.append(f"AMH {amh_value} ng/mL indicates diminished ovarian reserve")
            elif amh_value > 5.0:
                interpretations.append(f"AMH {amh_value} ng/mL indicates high ovarian reserve")
            else:
                interpretations.append(f"AMH {amh_value} ng/mL within normal range")
        
        if "fsh" in lab_results:
            fsh_value = lab_results["fsh"]
            if fsh_value > 10:
                interpretations.append(f"Elevated FSH {fsh_value} mIU/mL consistent with decreased ovarian function")
        
        return "; ".join(interpretations) if interpretations else "Laboratory results reviewed"
    
    def validate_fhir_resource(self, resource: Dict[str, Any]) -> Dict[str, Any]:
        """Basic validation of FHIR resource structure."""
        
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Check required fields
        if "resourceType" not in resource:
            validation_result["valid"] = False
            validation_result["errors"].append("Missing required field: resourceType")
        
        if "id" not in resource:
            validation_result["warnings"].append("Missing recommended field: id")
        
        # Resource-specific validation
        resource_type = resource.get("resourceType")
        
        if resource_type == "Patient":
            if "gender" not in resource:
                validation_result["warnings"].append("Missing recommended field: gender")
        
        elif resource_type == "Observation":
            required_fields = ["status", "code", "subject"]
            for field in required_fields:
                if field not in resource:
                    validation_result["valid"] = False
                    validation_result["errors"].append(f"Missing required field: {field}")
        
        return validation_result


if __name__ == "__main__":
    # Test FHIR integration
    print("=== FHIR INTEGRATION TEST ===\n")
    
    fhir = ReproductiveHealthFHIR()
    test_patient_id = "P001"
    
    # Test patient resource creation
    print("1. Creating FHIR Patient resource...")
    patient_data = {
        "patient_id": test_patient_id,
        "family_name": "Smith",
        "given_name": "Jane",
        "gender": "female",
        "birth_date": "1985-06-15",
        "fertility_intent": "actively_trying"
    }
    
    patient_resource = fhir.create_patient_resource(patient_data)
    print(f"Patient resource created: {patient_resource['id']}")
    
    # Test reproductive observations
    print("\n2. Creating reproductive health observations...")
    amh_obs = fhir.create_reproductive_observation(
        patient_id=test_patient_id,
        observation_type="amh",
        value=0.8,
        unit="ng/mL",
        cycle_day=3
    )
    
    fsh_obs = fhir.create_reproductive_observation(
        patient_id=test_patient_id,
        observation_type="fsh",
        value=12.5,
        unit="mIU/mL",
        cycle_day=3
    )
    
    print(f"AMH observation: {amh_obs['code']['coding'][0]['display']}")
    print(f"FSH observation: {fsh_obs['code']['coding'][0]['display']}")
    
    # Test cycle tracking observations
    print("\n3. Creating cycle tracking observations...")
    cycle_data = {
        "start_date": "2024-01-01",
        "flow_data": ["heavy", "moderate", "light", "spotting", "none"],
        "temperature_data": [36.2, 36.3, 36.1, 36.4, 36.8],
        "ovulation_tests": [
            {"date": "2024-01-14", "result": "positive", "method": "urine_lh"}
        ]
    }
    
    cycle_observations = fhir.create_cycle_tracking_observations(test_patient_id, cycle_data)
    print(f"Created {len(cycle_observations)} cycle tracking observations")
    
    # Test lab report
    print("\n4. Creating hormonal lab report...")
    lab_results = {
        "amh": 0.8,
        "fsh": 12.5,
        "lh": 8.2,
        "estradiol": 45
    }
    
    lab_report = fhir.create_hormonal_lab_report(
        patient_id=test_patient_id,
        lab_results=lab_results,
        test_date="2024-01-03"
    )
    
    print(f"Lab report created with {len(lab_report['observations'])} observations")
    print(f"Interpretation: {lab_report['diagnostic_report']['conclusion']}")
    
    # Test procedure resource
    print("\n5. Creating IVF procedure resource...")
    procedure_data = {
        "type": "ivf",
        "status": "completed",
        "date": "2024-02-15",
        "cycle_number": 1,
        "outcome": "Embryo transfer completed",
        "notes": "Fresh cycle with 12 eggs retrieved"
    }
    
    ivf_procedure = fhir.create_ivf_procedure_resource(test_patient_id, procedure_data)
    print(f"IVF procedure: {ivf_procedure['code']['coding'][0]['display']}")
    
    # Test FHIR bundle
    print("\n6. Creating FHIR bundle...")
    all_resources = [
        patient_resource,
        amh_obs,
        fsh_obs,
        lab_report['diagnostic_report'],
        ivf_procedure
    ] + lab_report['observations'] + cycle_observations
    
    bundle = fhir.create_fhir_bundle(all_resources, "collection")
    print(f"Bundle created with {bundle['total']} resources")
    
    # Test validation
    print("\n7. Validating FHIR resources...")
    validation = fhir.validate_fhir_resource(patient_resource)
    print(f"Patient resource valid: {validation['valid']}")
    if validation['warnings']:
        print(f"Warnings: {validation['warnings']}")
    
    print("\n✅ FHIR integration test completed!")