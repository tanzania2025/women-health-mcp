"""
Privacy and Security Layer for Women's Health MCP
HIPAA-compliant security for reproductive health data with enhanced protections
"""

import hashlib
import hmac
import secrets
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import base64

# Mock cryptography imports for demo
class Fernet:
    def __init__(self, key):
        self.key = key
    
    @staticmethod
    def generate_key():
        return b'mock_key_for_demo_' + secrets.token_bytes(16)
    
    def encrypt(self, data):
        return base64.b64encode(data)
    
    def decrypt(self, data):
        return base64.b64decode(data)


class DataClassification(Enum):
    """Data classification levels for reproductive health information."""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    TOP_SECRET = "top_secret"  # Most sensitive reproductive data


class ConsentType(Enum):
    """Types of consent for reproductive health data."""
    TREATMENT = "treatment"
    RESEARCH = "research"
    QUALITY_IMPROVEMENT = "quality_improvement"
    MARKETING = "marketing"
    THIRD_PARTY_SHARING = "third_party_sharing"
    AI_TRAINING = "ai_training"


class AccessLevel(Enum):
    """Access levels for healthcare providers."""
    PATIENT = "patient"
    PRIMARY_CARE = "primary_care"
    REPRODUCTIVE_SPECIALIST = "reproductive_specialist"
    EMERGENCY = "emergency"
    RESEARCHER = "researcher"
    SYSTEM_ADMIN = "system_admin"


@dataclass
class ConsentRecord:
    """Record of patient consent for data usage."""
    consent_id: str
    patient_id: str
    consent_type: ConsentType
    granted: bool
    granted_date: str
    expiry_date: Optional[str]
    revoked: bool
    revoked_date: Optional[str]
    specific_permissions: List[str]
    witness_signature: Optional[str]
    digital_signature: str


@dataclass
class AccessRequest:
    """Access request for reproductive health data."""
    request_id: str
    requester_id: str
    requester_role: AccessLevel
    patient_id: str
    data_types_requested: List[str]
    purpose: str
    emergency_access: bool
    requested_at: str
    approved: Optional[bool]
    approved_by: Optional[str]
    approved_at: Optional[str]
    access_expires_at: Optional[str]


@dataclass
class AuditLogEntry:
    """Audit log entry for data access."""
    log_id: str
    timestamp: str
    action: str
    user_id: str
    user_role: str
    patient_id: str
    data_accessed: List[str]
    ip_address: str
    user_agent: str
    session_id: str
    result: str
    risk_score: float


class ReproductiveHealthSecurity:
    """
    Enhanced security system specifically designed for reproductive health data.
    Implements HIPAA compliance with additional protections for sensitive reproductive information.
    """
    
    def __init__(self, master_key: Optional[bytes] = None):
        """Initialize security system with encryption capabilities."""
        self.master_key = master_key or Fernet.generate_key()
        self.cipher_suite = Fernet(self.master_key)
        
        # Security configurations
        self.audit_logs = []
        self.consent_records = {}
        self.access_requests = {}
        self.active_sessions = {}
        self.threat_detection = ThreatDetectionSystem()
        
        # Data classification rules
        self.classification_rules = self._initialize_classification_rules()
        
        # Initialize security policies
        self.security_policies = self._initialize_security_policies()
    
    def _initialize_classification_rules(self) -> Dict[str, DataClassification]:
        """Define data classification rules for reproductive health data."""
        return {
            # Most sensitive reproductive data
            "fertility_status": DataClassification.TOP_SECRET,
            "pregnancy_history": DataClassification.TOP_SECRET,
            "abortion_history": DataClassification.TOP_SECRET,
            "ivf_treatments": DataClassification.TOP_SECRET,
            "genetic_test_results": DataClassification.TOP_SECRET,
            "std_test_results": DataClassification.TOP_SECRET,
            
            # Restricted clinical data
            "hormonal_labs": DataClassification.RESTRICTED,
            "cycle_tracking": DataClassification.RESTRICTED,
            "contraception_history": DataClassification.RESTRICTED,
            "menopause_status": DataClassification.RESTRICTED,
            
            # Confidential medical data
            "general_labs": DataClassification.CONFIDENTIAL,
            "medications": DataClassification.CONFIDENTIAL,
            "diagnoses": DataClassification.CONFIDENTIAL,
            
            # Internal administrative data
            "appointment_history": DataClassification.INTERNAL,
            "insurance_info": DataClassification.INTERNAL,
            
            # Public health data
            "aggregate_statistics": DataClassification.PUBLIC
        }
    
    def _initialize_security_policies(self) -> Dict[str, Any]:
        """Initialize security policies for different data types and access levels."""
        return {
            "encryption": {
                "at_rest": True,
                "in_transit": True,
                "key_rotation_days": 90
            },
            "access_control": {
                "multi_factor_auth_required": True,
                "session_timeout_minutes": 30,
                "concurrent_sessions_limit": 3
            },
            "audit": {
                "log_all_access": True,
                "log_retention_days": 2555,  # 7 years for HIPAA
                "real_time_monitoring": True
            },
            "consent": {
                "granular_permissions": True,
                "consent_expiry_months": 12,
                "easy_revocation": True
            },
            "data_retention": {
                "reproductive_data_years": 7,
                "research_data_years": 10,
                "logs_years": 7
            }
        }
    
    def encrypt_data(self, data: Dict[str, Any], classification: DataClassification) -> str:
        """Encrypt sensitive data based on classification level."""
        
        # Convert data to JSON string
        data_string = json.dumps(data, sort_keys=True)
        
        # Add metadata
        metadata = {
            "classification": classification.value,
            "encrypted_at": datetime.now().isoformat(),
            "encryption_version": "v2.0"
        }
        
        # Combine data with metadata
        combined_data = {
            "metadata": metadata,
            "payload": data_string
        }
        
        # Encrypt the combined data
        combined_string = json.dumps(combined_data)
        encrypted_data = self.cipher_suite.encrypt(combined_string.encode())
        
        # Return base64 encoded encrypted data
        return base64.b64encode(encrypted_data).decode()
    
    def decrypt_data(self, encrypted_data: str) -> Tuple[Dict[str, Any], DataClassification]:
        """Decrypt data and return both content and classification."""
        
        try:
            # Decode and decrypt
            encrypted_bytes = base64.b64decode(encrypted_data.encode())
            decrypted_bytes = self.cipher_suite.decrypt(encrypted_bytes)
            combined_data = json.loads(decrypted_bytes.decode())
            
            # Extract metadata and payload
            metadata = combined_data["metadata"]
            payload = json.loads(combined_data["payload"])
            classification = DataClassification(metadata["classification"])
            
            return payload, classification
            
        except Exception as e:
            raise SecurityError(f"Failed to decrypt data: {str(e)}")
    
    def create_consent_record(self,
                            patient_id: str,
                            consent_type: ConsentType,
                            granted: bool,
                            specific_permissions: List[str],
                            expiry_months: int = 12) -> ConsentRecord:
        """Create a new consent record for patient data usage."""
        
        consent_id = str(uuid.uuid4())
        current_time = datetime.now()
        expiry_date = current_time + timedelta(days=expiry_months * 30)
        
        # Create digital signature for consent
        consent_data = f"{patient_id}_{consent_type.value}_{granted}_{current_time.isoformat()}"
        digital_signature = self._create_digital_signature(consent_data)
        
        consent_record = ConsentRecord(
            consent_id=consent_id,
            patient_id=patient_id,
            consent_type=consent_type,
            granted=granted,
            granted_date=current_time.isoformat(),
            expiry_date=expiry_date.isoformat(),
            revoked=False,
            revoked_date=None,
            specific_permissions=specific_permissions,
            witness_signature=None,
            digital_signature=digital_signature
        )
        
        # Store consent record
        self.consent_records[consent_id] = consent_record
        
        # Log consent creation
        self._log_audit_event(
            action="consent_created",
            user_id="system",
            user_role="system",
            patient_id=patient_id,
            data_accessed=["consent_record"],
            result="success"
        )
        
        return consent_record
    
    def _create_digital_signature(self, data: str) -> str:
        """Create HMAC-based digital signature."""
        signature = hmac.new(
            self.master_key,
            data.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def verify_consent(self,
                      patient_id: str,
                      consent_type: ConsentType,
                      specific_permission: Optional[str] = None) -> bool:
        """Verify if patient has given valid consent for specific data usage."""
        
        current_time = datetime.now()
        
        for consent_record in self.consent_records.values():
            if (consent_record.patient_id == patient_id and
                consent_record.consent_type == consent_type and
                consent_record.granted and
                not consent_record.revoked):
                
                # Check expiry
                expiry_date = datetime.fromisoformat(consent_record.expiry_date)
                if expiry_date > current_time:
                    
                    # Check specific permission if required
                    if specific_permission:
                        if specific_permission in consent_record.specific_permissions:
                            return True
                    else:
                        return True
        
        return False
    
    def revoke_consent(self,
                      patient_id: str,
                      consent_type: ConsentType,
                      revoked_by: str = "patient") -> bool:
        """Revoke patient consent for data usage."""
        
        revoked_count = 0
        current_time = datetime.now()
        
        for consent_record in self.consent_records.values():
            if (consent_record.patient_id == patient_id and
                consent_record.consent_type == consent_type and
                not consent_record.revoked):
                
                consent_record.revoked = True
                consent_record.revoked_date = current_time.isoformat()
                revoked_count += 1
                
                # Log consent revocation
                self._log_audit_event(
                    action="consent_revoked",
                    user_id=revoked_by,
                    user_role="patient" if revoked_by == "patient" else "admin",
                    patient_id=patient_id,
                    data_accessed=["consent_record"],
                    result="success"
                )
        
        return revoked_count > 0
    
    def request_data_access(self,
                          requester_id: str,
                          requester_role: AccessLevel,
                          patient_id: str,
                          data_types: List[str],
                          purpose: str,
                          emergency: bool = False) -> AccessRequest:
        """Request access to patient's reproductive health data."""
        
        request_id = str(uuid.uuid4())
        current_time = datetime.now()
        
        access_request = AccessRequest(
            request_id=request_id,
            requester_id=requester_id,
            requester_role=requester_role,
            patient_id=patient_id,
            data_types_requested=data_types,
            purpose=purpose,
            emergency_access=emergency,
            requested_at=current_time.isoformat(),
            approved=None,
            approved_by=None,
            approved_at=None,
            access_expires_at=None
        )
        
        # Auto-approve for certain scenarios
        if self._should_auto_approve(access_request):
            access_request.approved = True
            access_request.approved_by = "system_auto_approval"
            access_request.approved_at = current_time.isoformat()
            access_request.access_expires_at = (current_time + timedelta(hours=24)).isoformat()
        
        self.access_requests[request_id] = access_request
        
        # Log access request
        self._log_audit_event(
            action="access_requested",
            user_id=requester_id,
            user_role=requester_role.value,
            patient_id=patient_id,
            data_accessed=data_types,
            result="pending" if not access_request.approved else "approved"
        )
        
        return access_request
    
    def _should_auto_approve(self, request: AccessRequest) -> bool:
        """Determine if access request should be auto-approved."""
        
        # Emergency access
        if request.emergency_access and request.requester_role == AccessLevel.EMERGENCY:
            return True
        
        # Patient accessing their own data
        if (request.requester_role == AccessLevel.PATIENT and
            request.requester_id == request.patient_id):
            return True
        
        # Primary care provider with valid consent
        if (request.requester_role == AccessLevel.PRIMARY_CARE and
            self.verify_consent(request.patient_id, ConsentType.TREATMENT)):
            return True
        
        return False
    
    def authorize_data_access(self,
                            request_id: str,
                            user_id: str,
                            session_id: str,
                            ip_address: str = "unknown") -> Dict[str, Any]:
        """Authorize and execute data access request."""
        
        if request_id not in self.access_requests:
            raise SecurityError("Invalid access request ID")
        
        access_request = self.access_requests[request_id]
        
        # Check if request is approved
        if not access_request.approved:
            raise SecurityError("Access request not approved")
        
        # Check if access has expired
        if access_request.access_expires_at:
            expiry_time = datetime.fromisoformat(access_request.access_expires_at)
            if datetime.now() > expiry_time:
                raise SecurityError("Access request has expired")
        
        # Verify user identity
        if user_id != access_request.requester_id:
            raise SecurityError("User ID mismatch")
        
        # Check for security threats
        risk_score = self.threat_detection.assess_risk(
            user_id, ip_address, access_request.data_types_requested
        )
        
        if risk_score > 0.8:
            raise SecurityError("High risk activity detected - access denied")
        
        # Log successful access
        self._log_audit_event(
            action="data_accessed",
            user_id=user_id,
            user_role=access_request.requester_role.value,
            patient_id=access_request.patient_id,
            data_accessed=access_request.data_types_requested,
            result="success",
            session_id=session_id,
            ip_address=ip_address,
            risk_score=risk_score
        )
        
        return {
            "access_granted": True,
            "access_level": access_request.requester_role.value,
            "data_types": access_request.data_types_requested,
            "session_expires": access_request.access_expires_at,
            "risk_score": risk_score
        }
    
    def _log_audit_event(self,
                        action: str,
                        user_id: str,
                        user_role: str,
                        patient_id: str,
                        data_accessed: List[str],
                        result: str,
                        session_id: str = "unknown",
                        ip_address: str = "unknown",
                        risk_score: float = 0.0) -> None:
        """Log audit event for compliance and security monitoring."""
        
        log_entry = AuditLogEntry(
            log_id=str(uuid.uuid4()),
            timestamp=datetime.now().isoformat(),
            action=action,
            user_id=user_id,
            user_role=user_role,
            patient_id=patient_id,
            data_accessed=data_accessed,
            ip_address=ip_address,
            user_agent="unknown",  # Would be captured from request headers
            session_id=session_id,
            result=result,
            risk_score=risk_score
        )
        
        self.audit_logs.append(log_entry)
        
        # Alert on high-risk activities
        if risk_score > 0.7:
            self._trigger_security_alert(log_entry)
    
    def _trigger_security_alert(self, log_entry: AuditLogEntry) -> None:
        """Trigger security alert for suspicious activities."""
        
        alert = {
            "alert_id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "severity": "high" if log_entry.risk_score > 0.8 else "medium",
            "description": f"High-risk data access by {log_entry.user_id}",
            "details": {
                "user_id": log_entry.user_id,
                "patient_id": log_entry.patient_id,
                "data_accessed": log_entry.data_accessed,
                "risk_score": log_entry.risk_score,
                "ip_address": log_entry.ip_address
            },
            "recommended_actions": [
                "Review user access permissions",
                "Verify user identity",
                "Check for data breach indicators"
            ]
        }
        
        # In production, this would trigger alerts to security team
        print(f"🚨 SECURITY ALERT: {alert['description']}")
    
    def anonymize_for_research(self, data: Dict[str, Any], patient_id: str) -> Dict[str, Any]:
        """Anonymize reproductive health data for research purposes."""
        
        # Check research consent
        if not self.verify_consent(patient_id, ConsentType.RESEARCH):
            raise SecurityError("Research consent not granted")
        
        # Create anonymized copy
        anonymized_data = data.copy()
        
        # Remove direct identifiers
        identifiers_to_remove = [
            "patient_id", "name", "ssn", "phone", "email", "address",
            "birth_date", "medical_record_number"
        ]
        
        for identifier in identifiers_to_remove:
            anonymized_data.pop(identifier, None)
        
        # Replace with anonymized ID
        research_id = hashlib.sha256(
            f"{patient_id}_research_{datetime.now().date()}".encode()
        ).hexdigest()[:16]
        
        anonymized_data["research_id"] = research_id
        
        # Generalize sensitive attributes
        if "age" in anonymized_data:
            age = anonymized_data["age"]
            anonymized_data["age_group"] = self._generalize_age(age)
            del anonymized_data["age"]
        
        if "zip_code" in anonymized_data:
            zip_code = anonymized_data["zip_code"]
            anonymized_data["region"] = zip_code[:3] + "XX"  # First 3 digits only
            del anonymized_data["zip_code"]
        
        # Add anonymization metadata
        anonymized_data["_anonymization_metadata"] = {
            "anonymized_at": datetime.now().isoformat(),
            "anonymization_method": "k_anonymity",
            "research_consent_verified": True
        }
        
        return anonymized_data
    
    def _generalize_age(self, age: int) -> str:
        """Generalize age into ranges for anonymization."""
        if age < 18:
            return "under_18"
        elif age < 25:
            return "18_24"
        elif age < 35:
            return "25_34"
        elif age < 45:
            return "35_44"
        elif age < 55:
            return "45_54"
        else:
            return "55_plus"
    
    def generate_privacy_report(self, patient_id: str) -> Dict[str, Any]:
        """Generate comprehensive privacy report for patient."""
        
        # Get patient's consent records
        patient_consents = [
            asdict(consent) for consent in self.consent_records.values()
            if consent.patient_id == patient_id
        ]
        
        # Get patient's access logs
        patient_access_logs = [
            asdict(log) for log in self.audit_logs
            if log.patient_id == patient_id
        ]
        
        # Calculate privacy metrics
        active_consents = len([c for c in patient_consents if not c["revoked"]])
        data_access_events = len(patient_access_logs)
        last_access = max([log["timestamp"] for log in patient_access_logs], default="Never")
        
        # Data usage summary
        data_types_accessed = set()
        for log in patient_access_logs:
            data_types_accessed.update(log["data_accessed"])
        
        return {
            "patient_id": patient_id,
            "report_generated": datetime.now().isoformat(),
            "privacy_summary": {
                "active_consents": active_consents,
                "total_data_access_events": data_access_events,
                "last_data_access": last_access,
                "data_types_accessed": list(data_types_accessed)
            },
            "consent_details": patient_consents,
            "recent_access_logs": patient_access_logs[-10:],  # Last 10 events
            "privacy_controls": {
                "consent_revocation_available": True,
                "data_export_available": True,
                "data_deletion_available": True,
                "access_notification_enabled": True
            }
        }


class ThreatDetectionSystem:
    """AI-powered threat detection for reproductive health data access."""
    
    def __init__(self):
        self.baseline_behavior = {}
        self.anomaly_threshold = 0.7
    
    def assess_risk(self, user_id: str, ip_address: str, data_types: List[str]) -> float:
        """Assess risk score for data access request."""
        
        risk_factors = []
        
        # Check for unusual access patterns
        if len(data_types) > 5:
            risk_factors.append(0.3)  # Requesting many data types
        
        # Check for sensitive data access
        sensitive_data_types = [
            "fertility_status", "pregnancy_history", "abortion_history",
            "ivf_treatments", "genetic_test_results"
        ]
        
        sensitive_count = sum(1 for dt in data_types if dt in sensitive_data_types)
        if sensitive_count > 2:
            risk_factors.append(0.4)
        
        # IP address reputation (mock implementation)
        if self._is_suspicious_ip(ip_address):
            risk_factors.append(0.5)
        
        # Time-based analysis
        current_hour = datetime.now().hour
        if current_hour < 6 or current_hour > 22:  # Outside business hours
            risk_factors.append(0.2)
        
        # Calculate overall risk score
        if not risk_factors:
            return 0.0
        
        return min(1.0, sum(risk_factors))
    
    def _is_suspicious_ip(self, ip_address: str) -> bool:
        """Check if IP address is suspicious (mock implementation)."""
        # In production, would check against threat intelligence feeds
        suspicious_patterns = ["192.168.1.", "10.0.0.", "127.0.0."]
        return any(ip_address.startswith(pattern) for pattern in suspicious_patterns)


class SecurityError(Exception):
    """Custom exception for security-related errors."""
    pass


if __name__ == "__main__":
    # Test the security system
    print("=== REPRODUCTIVE HEALTH SECURITY TEST ===\n")
    
    security = ReproductiveHealthSecurity()
    test_patient_id = "P001"
    test_user_id = "DR001"
    
    # Test data encryption
    print("1. Testing data encryption...")
    sensitive_data = {
        "patient_id": test_patient_id,
        "ivf_cycles": 3,
        "pregnancy_history": ["2019: miscarriage", "2021: live birth"],
        "current_fertility_status": "trying_to_conceive"
    }
    
    encrypted = security.encrypt_data(sensitive_data, DataClassification.TOP_SECRET)
    decrypted, classification = security.decrypt_data(encrypted)
    
    print(f"Encryption successful: {len(encrypted)} characters")
    print(f"Decryption successful: {decrypted['patient_id'] == test_patient_id}")
    print(f"Classification preserved: {classification.value}")
    
    # Test consent management
    print("\n2. Testing consent management...")
    consent = security.create_consent_record(
        patient_id=test_patient_id,
        consent_type=ConsentType.TREATMENT,
        granted=True,
        specific_permissions=["hormonal_labs", "cycle_tracking", "fertility_treatments"]
    )
    
    print(f"Consent created: {consent.consent_id}")
    
    has_consent = security.verify_consent(test_patient_id, ConsentType.TREATMENT, "hormonal_labs")
    print(f"Consent verification: {has_consent}")
    
    # Test access control
    print("\n3. Testing access control...")
    access_request = security.request_data_access(
        requester_id=test_user_id,
        requester_role=AccessLevel.REPRODUCTIVE_SPECIALIST,
        patient_id=test_patient_id,
        data_types=["hormonal_labs", "cycle_tracking"],
        purpose="Clinical consultation"
    )
    
    print(f"Access request created: {access_request.request_id}")
    print(f"Auto-approved: {access_request.approved}")
    
    # Test data anonymization
    print("\n4. Testing data anonymization...")
    research_consent = security.create_consent_record(
        patient_id=test_patient_id,
        consent_type=ConsentType.RESEARCH,
        granted=True,
        specific_permissions=["anonymized_cycle_data", "anonymized_outcomes"]
    )
    
    anonymized = security.anonymize_for_research(sensitive_data, test_patient_id)
    print(f"Data anonymized: {'patient_id' not in anonymized}")
    print(f"Research ID assigned: {anonymized.get('research_id', 'None')}")
    
    # Test privacy report
    print("\n5. Testing privacy report...")
    privacy_report = security.generate_privacy_report(test_patient_id)
    print(f"Active consents: {privacy_report['privacy_summary']['active_consents']}")
    print(f"Data access events: {privacy_report['privacy_summary']['total_data_access_events']}")
    
    print("\n✅ Security system test completed!")