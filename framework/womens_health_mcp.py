"""
Women's Health Model Context Protocol (WH-MCP)
Standardized protocol for AI systems to access women's health data sources
"""

import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
import uuid


class DataSourceType(Enum):
    """Standardized data source types for women's health."""
    EHR_FHIR = "ehr_fhir"
    RESEARCH_DATABASE = "research_database"
    CLINICAL_CALCULATOR = "clinical_calculator"
    PATIENT_GENERATED = "patient_generated"
    CLINICAL_GUIDELINES = "clinical_guidelines"
    WEARABLE_DATA = "wearable_data"
    CYCLE_TRACKING = "cycle_tracking"


class SecurityLevel(Enum):
    """Security levels for reproductive health data."""
    PUBLIC = "public"
    RESTRICTED = "restricted"
    PHI_PROTECTED = "phi_protected"
    REPRODUCTIVE_SENSITIVE = "reproductive_sensitive"


@dataclass
class MCPRequest:
    """Standardized MCP request structure."""
    request_id: str
    timestamp: str
    patient_id: str
    query_type: str
    data_sources: List[str]
    security_context: Dict[str, Any]
    clinical_context: Dict[str, Any]
    consent_tokens: List[str]


@dataclass
class MCPResponse:
    """Standardized MCP response structure."""
    request_id: str
    timestamp: str
    status: str
    data: Dict[str, Any]
    metadata: Dict[str, Any]
    privacy_audit: Dict[str, Any]


class WomensHealthMCP:
    """
    Women's Health Model Context Protocol implementation.
    Provides standardized access to women's health data sources.
    """
    
    def __init__(self):
        self.registered_sources = {}
        self.security_policies = {}
        self.audit_log = []
        self._initialize_default_sources()
    
    def _initialize_default_sources(self):
        """Initialize default data sources."""
        default_sources = {
            "swan_database": {
                "type": DataSourceType.RESEARCH_DATABASE,
                "name": "Study of Women's Health Across the Nation",
                "security_level": SecurityLevel.PUBLIC,
                "endpoints": ["menopause_timing", "hormone_trajectories", "symptom_patterns"],
                "rate_limit": 100
            },
            "sart_database": {
                "type": DataSourceType.RESEARCH_DATABASE,
                "name": "Society for Assisted Reproductive Technology",
                "security_level": SecurityLevel.RESTRICTED,
                "endpoints": ["ivf_success_rates", "clinic_outcomes", "age_specific_data"],
                "rate_limit": 50
            },
            "ehr_fhir": {
                "type": DataSourceType.EHR_FHIR,
                "name": "Electronic Health Record (FHIR)",
                "security_level": SecurityLevel.PHI_PROTECTED,
                "endpoints": ["patient_summary", "lab_results", "medications", "procedures"],
                "rate_limit": 1000
            },
            "reproductive_calculators": {
                "type": DataSourceType.CLINICAL_CALCULATOR,
                "name": "Clinical Calculators for Reproductive Health",
                "security_level": SecurityLevel.PUBLIC,
                "endpoints": ["ovarian_reserve", "ivf_success", "menopause_prediction"],
                "rate_limit": 200
            },
            "patient_cycle_data": {
                "type": DataSourceType.CYCLE_TRACKING,
                "name": "Patient Cycle Tracking Data",
                "security_level": SecurityLevel.REPRODUCTIVE_SENSITIVE,
                "endpoints": ["cycle_patterns", "symptom_tracking", "fertility_windows"],
                "rate_limit": 500
            },
            "wearable_integration": {
                "type": DataSourceType.WEARABLE_DATA,
                "name": "Wearable Device Integration",
                "security_level": SecurityLevel.REPRODUCTIVE_SENSITIVE,
                "endpoints": ["temperature_data", "sleep_patterns", "stress_metrics"],
                "rate_limit": 1000
            }
        }
        
        for source_id, config in default_sources.items():
            self.register_data_source(source_id, config)
    
    def register_data_source(self, source_id: str, config: Dict[str, Any]) -> bool:
        """Register a new data source with the MCP."""
        self.registered_sources[source_id] = {
            **config,
            "registered_at": datetime.now().isoformat(),
            "request_count": 0,
            "last_accessed": None
        }
        return True
    
    def create_request(self, 
                      patient_id: str,
                      query_type: str,
                      data_sources: List[str],
                      clinical_context: Dict[str, Any],
                      consent_tokens: List[str] = None) -> MCPRequest:
        """Create a standardized MCP request."""
        
        # Generate security context based on data sources
        security_context = self._generate_security_context(data_sources, patient_id)
        
        request = MCPRequest(
            request_id=str(uuid.uuid4()),
            timestamp=datetime.now().isoformat(),
            patient_id=patient_id,
            query_type=query_type,
            data_sources=data_sources,
            security_context=security_context,
            clinical_context=clinical_context,
            consent_tokens=consent_tokens or []
        )
        
        return request
    
    def _generate_security_context(self, data_sources: List[str], patient_id: str) -> Dict[str, Any]:
        """Generate security context for the request."""
        max_security_level = SecurityLevel.PUBLIC
        required_consents = []
        
        for source_id in data_sources:
            if source_id in self.registered_sources:
                source = self.registered_sources[source_id]
                level = source.get("security_level", SecurityLevel.PUBLIC)
                
                if level.value > max_security_level.value:
                    max_security_level = level
                
                if level in [SecurityLevel.PHI_PROTECTED, SecurityLevel.REPRODUCTIVE_SENSITIVE]:
                    required_consents.append(f"{source_id}_consent")
        
        return {
            "security_level": max_security_level.value,
            "required_consents": required_consents,
            "patient_hash": hashlib.sha256(patient_id.encode()).hexdigest()[:16],
            "access_timestamp": datetime.now().isoformat()
        }
    
    def execute_request(self, request: MCPRequest) -> MCPResponse:
        """Execute an MCP request and return structured response."""
        
        # Validate security and consent
        if not self._validate_security(request):
            return self._create_error_response(request.request_id, "Security validation failed")
        
        # Route to appropriate data sources
        aggregated_data = {}
        metadata = {"sources_accessed": [], "processing_time": {}}
        
        for source_id in request.data_sources:
            start_time = datetime.now()
            
            try:
                source_data = self._query_data_source(source_id, request)
                aggregated_data[source_id] = source_data
                metadata["sources_accessed"].append(source_id)
                
                # Update source statistics
                self.registered_sources[source_id]["request_count"] += 1
                self.registered_sources[source_id]["last_accessed"] = datetime.now().isoformat()
                
            except Exception as e:
                aggregated_data[source_id] = {"error": str(e)}
            
            processing_time = (datetime.now() - start_time).total_seconds()
            metadata["processing_time"][source_id] = processing_time
        
        # Create audit entry
        audit_entry = self._create_audit_entry(request, metadata)
        self.audit_log.append(audit_entry)
        
        response = MCPResponse(
            request_id=request.request_id,
            timestamp=datetime.now().isoformat(),
            status="success",
            data=aggregated_data,
            metadata=metadata,
            privacy_audit=audit_entry
        )
        
        return response
    
    def _validate_security(self, request: MCPRequest) -> bool:
        """Validate security requirements for the request."""
        security_context = request.security_context
        required_consents = security_context.get("required_consents", [])
        
        # Check if all required consents are provided
        for consent in required_consents:
            if consent not in request.consent_tokens:
                return False
        
        return True
    
    def _query_data_source(self, source_id: str, request: MCPRequest) -> Dict[str, Any]:
        """Query a specific data source."""
        if source_id not in self.registered_sources:
            raise ValueError(f"Data source {source_id} not registered")
        
        source = self.registered_sources[source_id]
        source_type = source["type"]
        
        # Route to appropriate handler based on source type
        if source_type == DataSourceType.RESEARCH_DATABASE:
            return self._query_research_database(source_id, request)
        elif source_type == DataSourceType.EHR_FHIR:
            return self._query_ehr_fhir(source_id, request)
        elif source_type == DataSourceType.CLINICAL_CALCULATOR:
            return self._query_clinical_calculator(source_id, request)
        elif source_type == DataSourceType.PATIENT_GENERATED:
            return self._query_patient_generated(source_id, request)
        elif source_type == DataSourceType.CYCLE_TRACKING:
            return self._query_cycle_tracking(source_id, request)
        elif source_type == DataSourceType.WEARABLE_DATA:
            return self._query_wearable_data(source_id, request)
        else:
            raise ValueError(f"Unknown source type: {source_type}")
    
    def _query_research_database(self, source_id: str, request: MCPRequest) -> Dict[str, Any]:
        """Query research databases like SWAN, SART."""
        # Mock implementation - in production would connect to actual APIs
        if source_id == "swan_database":
            return {
                "menopause_timing": {
                    "median_age": 51.4,
                    "range": [45, 58],
                    "factors": ["smoking", "bmi", "ethnicity"]
                },
                "hormone_trajectories": {
                    "fsh_trend": "increasing",
                    "estradiol_trend": "decreasing",
                    "prediction_window": "2-3 years"
                }
            }
        elif source_id == "sart_database":
            patient_age = request.clinical_context.get("age", 35)
            return {
                "ivf_success_rates": {
                    "age_group": f"{patient_age}-{patient_age+2}",
                    "live_birth_rate": max(5, 45 - (patient_age - 30) * 3),
                    "cycle_count": "per fresh cycle",
                    "data_year": 2023
                }
            }
        
        return {"status": "no_data"}
    
    def _query_ehr_fhir(self, source_id: str, request: MCPRequest) -> Dict[str, Any]:
        """Query FHIR-compliant EHR data."""
        # Mock FHIR response
        return {
            "patient_summary": {
                "resourceType": "Patient",
                "id": request.patient_id,
                "demographics": request.clinical_context.get("demographics", {}),
                "active": True
            },
            "lab_results": {
                "resourceType": "Observation",
                "category": "laboratory",
                "results": request.clinical_context.get("reproductive_labs", {})
            }
        }
    
    def _query_clinical_calculator(self, source_id: str, request: MCPRequest) -> Dict[str, Any]:
        """Query clinical calculators."""
        # Will be implemented in clinical_calculators.py
        return {"calculator_results": "pending_implementation"}
    
    def _query_patient_generated(self, source_id: str, request: MCPRequest) -> Dict[str, Any]:
        """Query patient-generated data."""
        return {"patient_data": "pending_implementation"}
    
    def _query_cycle_tracking(self, source_id: str, request: MCPRequest) -> Dict[str, Any]:
        """Query cycle tracking data."""
        return {"cycle_data": "pending_implementation"}
    
    def _query_wearable_data(self, source_id: str, request: MCPRequest) -> Dict[str, Any]:
        """Query wearable device data."""
        return {"wearable_data": "pending_implementation"}
    
    def _create_audit_entry(self, request: MCPRequest, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Create audit log entry for privacy compliance."""
        return {
            "audit_id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "request_id": request.request_id,
            "patient_hash": request.security_context["patient_hash"],
            "data_sources_accessed": metadata["sources_accessed"],
            "security_level": request.security_context["security_level"],
            "consents_verified": len(request.consent_tokens),
            "purpose": request.query_type,
            "retention_policy": "30_days"
        }
    
    def _create_error_response(self, request_id: str, error_message: str) -> MCPResponse:
        """Create error response."""
        return MCPResponse(
            request_id=request_id,
            timestamp=datetime.now().isoformat(),
            status="error",
            data={"error": error_message},
            metadata={},
            privacy_audit={}
        )
    
    def get_available_sources(self) -> Dict[str, Any]:
        """Get list of available data sources."""
        return {
            source_id: {
                "name": config["name"],
                "type": config["type"].value,
                "security_level": config["security_level"].value,
                "endpoints": config["endpoints"],
                "status": "active"
            }
            for source_id, config in self.registered_sources.items()
        }
    
    def get_audit_summary(self, days: int = 7) -> Dict[str, Any]:
        """Get privacy audit summary."""
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_audits = [
            audit for audit in self.audit_log
            if datetime.fromisoformat(audit["timestamp"]) > cutoff_date
        ]
        
        return {
            "period_days": days,
            "total_requests": len(recent_audits),
            "unique_patients": len(set(audit["patient_hash"] for audit in recent_audits)),
            "data_sources_usage": self._summarize_source_usage(recent_audits),
            "security_levels": self._summarize_security_levels(recent_audits)
        }
    
    def _summarize_source_usage(self, audits: List[Dict[str, Any]]) -> Dict[str, int]:
        """Summarize data source usage from audit logs."""
        usage = {}
        for audit in audits:
            for source in audit["data_sources_accessed"]:
                usage[source] = usage.get(source, 0) + 1
        return usage
    
    def _summarize_security_levels(self, audits: List[Dict[str, Any]]) -> Dict[str, int]:
        """Summarize security level usage from audit logs."""
        levels = {}
        for audit in audits:
            level = audit["security_level"]
            levels[level] = levels.get(level, 0) + 1
        return levels


# Example usage functions
def create_fertility_consultation_request(patient_data: Dict[str, Any]) -> MCPRequest:
    """Create an MCP request for fertility consultation."""
    mcp = WomensHealthMCP()
    
    return mcp.create_request(
        patient_id=patient_data["patient_id"],
        query_type="fertility_consultation",
        data_sources=["ehr_fhir", "sart_database", "reproductive_calculators", "patient_cycle_data"],
        clinical_context={
            "age": patient_data.get("age"),
            "reproductive_labs": patient_data.get("reproductive_labs", {}),
            "clinical_question": patient_data.get("clinical_question")
        },
        consent_tokens=["ehr_fhir_consent", "patient_cycle_data_consent"]
    )


def create_menopause_prediction_request(patient_data: Dict[str, Any]) -> MCPRequest:
    """Create an MCP request for menopause prediction."""
    mcp = WomensHealthMCP()
    
    return mcp.create_request(
        patient_id=patient_data["patient_id"],
        query_type="menopause_prediction",
        data_sources=["swan_database", "ehr_fhir", "reproductive_calculators", "wearable_integration"],
        clinical_context={
            "age": patient_data.get("age"),
            "reproductive_labs": patient_data.get("reproductive_labs", {}),
            "symptoms": patient_data.get("symptoms", [])
        },
        consent_tokens=["ehr_fhir_consent", "wearable_integration_consent"]
    )


if __name__ == "__main__":
    # Test the MCP implementation
    print("=== WOMEN'S HEALTH MCP TEST ===\n")
    
    mcp = WomensHealthMCP()
    
    # Show available sources
    print("Available Data Sources:")
    sources = mcp.get_available_sources()
    for source_id, info in sources.items():
        print(f"  {source_id}: {info['name']} ({info['type']})")
    
    # Test fertility consultation request
    print("\n" + "="*50)
    print("Testing Fertility Consultation Request")
    
    test_patient = {
        "patient_id": "P001",
        "age": 38,
        "reproductive_labs": {"amh": 0.8, "fsh": 12},
        "clinical_question": "Should I do IVF now?"
    }
    
    request = create_fertility_consultation_request(test_patient)
    response = mcp.execute_request(request)
    
    print(f"Request ID: {response.request_id}")
    print(f"Status: {response.status}")
    print(f"Sources accessed: {response.metadata['sources_accessed']}")
    print(f"Privacy audit ID: {response.privacy_audit['audit_id']}")
    
    # Show audit summary
    print("\n" + "="*50)
    print("Privacy Audit Summary:")
    audit_summary = mcp.get_audit_summary()
    print(json.dumps(audit_summary, indent=2))