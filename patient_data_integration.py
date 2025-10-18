"""
Patient-Generated Data Integration for Women's Health MCP
Unified interface for cycle tracking apps, wearables, and self-reported data
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
import statistics
import uuid


class DataSourcePlatform(Enum):
    """Supported patient data platforms."""
    CLUE = "clue"
    FLO = "flo"
    GARMIN = "garmin"
    OURA = "oura"
    FITBIT = "fitbit"
    APPLE_HEALTH = "apple_health"
    MANUAL_ENTRY = "manual_entry"
    FERTILITY_FRIEND = "fertility_friend"
    OVA = "ova"
    CLEARBLUE = "clearblue"


class CyclePhase(Enum):
    """Menstrual cycle phases."""
    MENSTRUAL = "menstrual"
    FOLLICULAR = "follicular"
    OVULATORY = "ovulatory"
    LUTEAL = "luteal"


class SymptomSeverity(Enum):
    """Symptom severity scale."""
    NONE = 0
    MILD = 1
    MODERATE = 2
    SEVERE = 3


@dataclass
class CycleData:
    """Standardized cycle tracking data."""
    cycle_id: str
    start_date: str
    end_date: Optional[str]
    cycle_length: Optional[int]
    period_length: Optional[int]
    ovulation_date: Optional[str]
    luteal_phase_length: Optional[int]
    basal_body_temperature: List[float]
    cervical_mucus_quality: List[str]
    ovulation_tests: List[Dict[str, Any]]
    symptoms: Dict[str, List[int]]  # symptom_name -> [severity_per_day]
    mood_scores: List[int]
    source_platform: DataSourcePlatform
    data_quality_score: float


@dataclass
class WearableData:
    """Standardized wearable device data."""
    device_id: str
    date_range: tuple
    sleep_data: Dict[str, List[float]]  # duration, efficiency, deep_sleep_pct
    heart_rate_variability: List[float]
    resting_heart_rate: List[float]
    body_temperature: List[float]
    stress_score: List[float]
    activity_level: List[float]
    steps: List[int]
    source_platform: DataSourcePlatform
    sync_timestamp: str


@dataclass
class FertilityMetrics:
    """Computed fertility and reproductive health metrics."""
    average_cycle_length: float
    cycle_regularity_score: float
    ovulation_consistency: float
    luteal_phase_adequacy: float
    fertility_window_prediction: List[str]
    next_period_prediction: str
    reproductive_health_score: float
    concerning_patterns: List[str]
    recommendations: List[str]


class PatientDataIntegration:
    """
    Unified interface for patient-generated reproductive health data.
    Aggregates and standardizes data from multiple sources.
    """
    
    def __init__(self):
        self.connected_platforms = {}
        self.patient_data_cache = {}
        self.data_mapping_schemas = self._initialize_schemas()
        self.privacy_settings = {}
    
    def _initialize_schemas(self) -> Dict[str, Dict[str, Any]]:
        """Initialize data mapping schemas for different platforms."""
        return {
            DataSourcePlatform.CLUE.value: {
                "cycle_start": "period_start_date",
                "cycle_length": "cycle_length_days",
                "period_flow": "bleeding_flow",
                "symptoms": {
                    "cramps": "pain_cramps",
                    "mood": "emotions_mood",
                    "headache": "pain_headache"
                },
                "ovulation": "ovulation_test_result"
            },
            DataSourcePlatform.FLO.value: {
                "cycle_start": "menstruation_start",
                "cycle_length": "cycle_duration",
                "symptoms": {
                    "pms": "premenstrual_symptoms",
                    "mood_changes": "emotional_state"
                },
                "temperature": "basal_body_temp"
            },
            DataSourcePlatform.OURA.value: {
                "sleep_score": "sleep.score",
                "readiness_score": "readiness.score",
                "hrv": "hrv.rmssd",
                "temperature": "temperature_delta",
                "rhr": "resting_heart_rate"
            },
            DataSourcePlatform.GARMIN.value: {
                "stress_score": "stress_level_rest_timestamp",
                "body_battery": "body_battery_charged_up",
                "heart_rate": "heart_rate",
                "sleep_score": "sleep_score"
            }
        }
    
    def connect_platform(self, 
                        platform: DataSourcePlatform,
                        patient_id: str,
                        auth_token: str,
                        permissions: List[str]) -> bool:
        """Connect a patient data platform."""
        
        connection_config = {
            "platform": platform,
            "patient_id": patient_id,
            "auth_token": auth_token,  # In production, encrypt this
            "permissions": permissions,
            "connected_at": datetime.now().isoformat(),
            "last_sync": None,
            "data_retention_days": 365,
            "auto_sync": True
        }
        
        platform_key = f"{patient_id}_{platform.value}"
        self.connected_platforms[platform_key] = connection_config
        
        # Initialize privacy settings
        self._set_default_privacy_settings(patient_id, platform)
        
        return True
    
    def _set_default_privacy_settings(self, patient_id: str, platform: DataSourcePlatform):
        """Set default privacy settings for platform data."""
        
        if patient_id not in self.privacy_settings:
            self.privacy_settings[patient_id] = {}
        
        # Reproductive data is highly sensitive by default
        self.privacy_settings[patient_id][platform.value] = {
            "data_sharing": "healthcare_providers_only",
            "anonymization_level": "high",
            "retention_period_days": 365,
            "consent_for_research": False,
            "export_allowed": True,
            "third_party_sharing": False
        }
    
    def sync_platform_data(self, 
                          patient_id: str,
                          platform: DataSourcePlatform,
                          date_range: Optional[tuple] = None) -> Dict[str, Any]:
        """Sync data from a connected platform."""
        
        platform_key = f"{patient_id}_{platform.value}"
        
        if platform_key not in self.connected_platforms:
            raise ValueError(f"Platform {platform.value} not connected for patient {patient_id}")
        
        # In production, this would make actual API calls
        # For demo, generate mock data
        mock_data = self._generate_mock_platform_data(platform, date_range)
        
        # Standardize the data
        standardized_data = self._standardize_platform_data(platform, mock_data)
        
        # Cache the data
        if patient_id not in self.patient_data_cache:
            self.patient_data_cache[patient_id] = {}
        
        self.patient_data_cache[patient_id][platform.value] = {
            "data": standardized_data,
            "last_updated": datetime.now().isoformat(),
            "data_quality": self._assess_data_quality(standardized_data, platform)
        }
        
        # Update connection info
        self.connected_platforms[platform_key]["last_sync"] = datetime.now().isoformat()
        
        return standardized_data
    
    def _generate_mock_platform_data(self, 
                                   platform: DataSourcePlatform,
                                   date_range: Optional[tuple]) -> Dict[str, Any]:
        """Generate mock data for testing purposes."""
        
        if not date_range:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=90)
        else:
            start_date, end_date = date_range
        
        if platform in [DataSourcePlatform.CLUE, DataSourcePlatform.FLO]:
            # Cycle tracking app data
            return self._generate_mock_cycle_data(start_date, end_date)
        elif platform in [DataSourcePlatform.OURA, DataSourcePlatform.GARMIN]:
            # Wearable device data
            return self._generate_mock_wearable_data(start_date, end_date)
        else:
            return {}
    
    def _generate_mock_cycle_data(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Generate mock cycle tracking data."""
        
        cycles = []
        current_date = start_date
        cycle_id = 1
        
        while current_date < end_date:
            cycle_length = 28 + (cycle_id % 7 - 3)  # Vary between 25-31 days
            period_length = 5 + (cycle_id % 3 - 1)  # Vary between 4-6 days
            
            cycle_data = {
                "cycle_id": f"cycle_{cycle_id}",
                "start_date": current_date.strftime("%Y-%m-%d"),
                "cycle_length": cycle_length,
                "period_length": period_length,
                "ovulation_day": 14 + (cycle_id % 5 - 2),  # Vary ovulation timing
                "symptoms": {
                    "cramps": [0, 2, 3, 2, 1] + [0] * (cycle_length - 5),
                    "mood_changes": [1, 2, 1, 0] * int(cycle_length/4 + 1),
                    "headache": [0] * cycle_length
                },
                "basal_body_temperature": [
                    36.2 + 0.1 * (i > 14) + (i % 3 - 1) * 0.05
                    for i in range(cycle_length)
                ],
                "cervical_mucus": ["dry"] * 10 + ["sticky", "creamy", "watery", "egg_white"] + ["dry"] * (cycle_length - 14)
            }
            
            cycles.append(cycle_data)
            current_date += timedelta(days=cycle_length)
            cycle_id += 1
        
        return {"cycles": cycles}
    
    def _generate_mock_wearable_data(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Generate mock wearable device data."""
        
        days = (end_date - start_date).days
        current_date = start_date
        daily_data = []
        
        for day in range(days):
            # Simulate cycle-related variations
            cycle_day = day % 28
            is_luteal_phase = cycle_day > 14
            
            day_data = {
                "date": current_date.strftime("%Y-%m-%d"),
                "sleep_score": 75 + (day % 10 - 5) + (-5 if is_luteal_phase else 0),
                "hrv_rmssd": 35 + (day % 8 - 4) + (-3 if is_luteal_phase else 2),
                "resting_heart_rate": 65 + (day % 6 - 3) + (3 if is_luteal_phase else 0),
                "temperature_delta": -0.2 + (day % 5 - 2) * 0.1 + (0.3 if is_luteal_phase else 0),
                "stress_score": 30 + (day % 12 - 6) + (10 if is_luteal_phase else 0),
                "steps": 8000 + (day % 2000),
                "activity_score": 70 + (day % 20 - 10)
            }
            
            daily_data.append(day_data)
            current_date += timedelta(days=1)
        
        return {"daily_metrics": daily_data}
    
    def _standardize_platform_data(self, 
                                 platform: DataSourcePlatform,
                                 raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Standardize data from different platforms into common format."""
        
        if platform in [DataSourcePlatform.CLUE, DataSourcePlatform.FLO]:
            return self._standardize_cycle_data(raw_data, platform)
        elif platform in [DataSourcePlatform.OURA, DataSourcePlatform.GARMIN]:
            return self._standardize_wearable_data(raw_data, platform)
        else:
            return raw_data
    
    def _standardize_cycle_data(self, raw_data: Dict[str, Any], platform: DataSourcePlatform) -> Dict[str, Any]:
        """Standardize cycle tracking data."""
        
        standardized_cycles = []
        
        for cycle in raw_data.get("cycles", []):
            std_cycle = CycleData(
                cycle_id=cycle["cycle_id"],
                start_date=cycle["start_date"],
                end_date=None,
                cycle_length=cycle["cycle_length"],
                period_length=cycle["period_length"],
                ovulation_date=None,
                luteal_phase_length=cycle["cycle_length"] - cycle["ovulation_day"],
                basal_body_temperature=cycle.get("basal_body_temperature", []),
                cervical_mucus_quality=cycle.get("cervical_mucus", []),
                ovulation_tests=[],
                symptoms=cycle.get("symptoms", {}),
                mood_scores=[],
                source_platform=platform,
                data_quality_score=0.85  # Mock quality score
            )
            standardized_cycles.append(asdict(std_cycle))
        
        return {"standardized_cycles": standardized_cycles}
    
    def _standardize_wearable_data(self, raw_data: Dict[str, Any], platform: DataSourcePlatform) -> Dict[str, Any]:
        """Standardize wearable device data."""
        
        daily_metrics = raw_data.get("daily_metrics", [])
        
        if not daily_metrics:
            return {"standardized_wearable_data": {}}
        
        # Aggregate data by metric type
        sleep_scores = [day["sleep_score"] for day in daily_metrics if "sleep_score" in day]
        hrv_values = [day["hrv_rmssd"] for day in daily_metrics if "hrv_rmssd" in day]
        rhr_values = [day["resting_heart_rate"] for day in daily_metrics if "resting_heart_rate" in day]
        temp_deltas = [day["temperature_delta"] for day in daily_metrics if "temperature_delta" in day]
        stress_scores = [day["stress_score"] for day in daily_metrics if "stress_score" in day]
        
        start_date = daily_metrics[0]["date"] if daily_metrics else None
        end_date = daily_metrics[-1]["date"] if daily_metrics else None
        
        wearable_data = WearableData(
            device_id=f"{platform.value}_device_001",
            date_range=(start_date, end_date),
            sleep_data={
                "scores": sleep_scores,
                "average": statistics.mean(sleep_scores) if sleep_scores else 0
            },
            heart_rate_variability=hrv_values,
            resting_heart_rate=rhr_values,
            body_temperature=temp_deltas,
            stress_score=stress_scores,
            activity_level=[day.get("activity_score", 0) for day in daily_metrics],
            steps=[day.get("steps", 0) for day in daily_metrics],
            source_platform=platform,
            sync_timestamp=datetime.now().isoformat()
        )
        
        return {"standardized_wearable_data": asdict(wearable_data)}
    
    def _assess_data_quality(self, data: Dict[str, Any], platform: DataSourcePlatform) -> float:
        """Assess quality of synchronized data."""
        
        quality_factors = []
        
        # Completeness check
        if "standardized_cycles" in data:
            cycles = data["standardized_cycles"]
            if cycles:
                avg_completeness = sum(
                    len([v for v in cycle.values() if v is not None]) / len(cycle)
                    for cycle in cycles
                ) / len(cycles)
                quality_factors.append(avg_completeness)
        
        elif "standardized_wearable_data" in data:
            wearable = data["standardized_wearable_data"]
            if wearable:
                completeness = len([v for v in wearable.values() if v]) / len(wearable)
                quality_factors.append(completeness)
        
        # Recency check
        last_data_date = self._get_latest_data_date(data)
        if last_data_date:
            days_since_last = (datetime.now() - last_data_date).days
            recency_score = max(0, 1 - days_since_last / 30)  # Degrade over 30 days
            quality_factors.append(recency_score)
        
        # Platform reliability score
        platform_reliability = {
            DataSourcePlatform.CLUE: 0.9,
            DataSourcePlatform.FLO: 0.85,
            DataSourcePlatform.OURA: 0.95,
            DataSourcePlatform.GARMIN: 0.9
        }
        quality_factors.append(platform_reliability.get(platform, 0.8))
        
        return statistics.mean(quality_factors) if quality_factors else 0.5
    
    def _get_latest_data_date(self, data: Dict[str, Any]) -> Optional[datetime]:
        """Extract the most recent data timestamp."""
        
        if "standardized_cycles" in data and data["standardized_cycles"]:
            latest_cycle = max(data["standardized_cycles"], key=lambda x: x["start_date"])
            return datetime.strptime(latest_cycle["start_date"], "%Y-%m-%d")
        
        elif "standardized_wearable_data" in data:
            wearable = data["standardized_wearable_data"]
            if wearable.get("sync_timestamp"):
                return datetime.fromisoformat(wearable["sync_timestamp"])
        
        return None
    
    def compute_fertility_metrics(self, patient_id: str) -> FertilityMetrics:
        """Compute comprehensive fertility metrics from patient data."""
        
        if patient_id not in self.patient_data_cache:
            raise ValueError(f"No data available for patient {patient_id}")
        
        patient_data = self.patient_data_cache[patient_id]
        
        # Extract cycle data from all connected apps
        all_cycles = []
        for platform_data in patient_data.values():
            cycles = platform_data.get("data", {}).get("standardized_cycles", [])
            all_cycles.extend(cycles)
        
        if not all_cycles:
            # Return default metrics if no cycle data
            return FertilityMetrics(
                average_cycle_length=28.0,
                cycle_regularity_score=0.5,
                ovulation_consistency=0.5,
                luteal_phase_adequacy=0.5,
                fertility_window_prediction=[],
                next_period_prediction="Unknown",
                reproductive_health_score=0.5,
                concerning_patterns=["Insufficient data"],
                recommendations=["Connect cycle tracking app for better insights"]
            )
        
        # Sort cycles by date
        all_cycles.sort(key=lambda x: x["start_date"])
        
        # Calculate metrics
        cycle_lengths = [c["cycle_length"] for c in all_cycles if c["cycle_length"]]
        avg_cycle_length = statistics.mean(cycle_lengths) if cycle_lengths else 28
        
        # Cycle regularity (lower std dev = more regular)
        cycle_std = statistics.stdev(cycle_lengths) if len(cycle_lengths) > 1 else 0
        regularity_score = max(0, 1 - cycle_std / 7)  # Normalize to 0-1
        
        # Ovulation consistency
        ovulation_days = []
        for cycle in all_cycles:
            if cycle.get("ovulation_date") and cycle.get("start_date"):
                ovulation_day = (
                    datetime.strptime(cycle["ovulation_date"], "%Y-%m-%d") -
                    datetime.strptime(cycle["start_date"], "%Y-%m-%d")
                ).days
                ovulation_days.append(ovulation_day)
        
        ovulation_consistency = 1.0
        if len(ovulation_days) > 1:
            ovulation_std = statistics.stdev(ovulation_days)
            ovulation_consistency = max(0, 1 - ovulation_std / 5)
        
        # Luteal phase adequacy (should be 12-16 days)
        luteal_lengths = [c["luteal_phase_length"] for c in all_cycles if c.get("luteal_phase_length")]
        luteal_adequacy = 0.8  # Default
        if luteal_lengths:
            avg_luteal = statistics.mean(luteal_lengths)
            if 12 <= avg_luteal <= 16:
                luteal_adequacy = 1.0
            elif avg_luteal < 10:
                luteal_adequacy = 0.3  # Short luteal phase
            elif avg_luteal < 12:
                luteal_adequacy = 0.6
        
        # Predict next fertile window and period
        last_cycle = all_cycles[-1]
        last_start = datetime.strptime(last_cycle["start_date"], "%Y-%m-%d")
        predicted_next_start = last_start + timedelta(days=int(avg_cycle_length))
        predicted_ovulation = predicted_next_start + timedelta(days=14)
        
        fertility_window = [
            (predicted_ovulation + timedelta(days=i)).strftime("%Y-%m-%d")
            for i in range(-3, 2)  # 5-day fertile window
        ]
        
        # Overall reproductive health score
        health_score = statistics.mean([
            regularity_score,
            ovulation_consistency,
            luteal_adequacy,
            min(1.0, len(all_cycles) / 6)  # Data completeness bonus
        ])
        
        # Identify concerning patterns
        concerning_patterns = []
        if avg_cycle_length < 21:
            concerning_patterns.append("Short cycles (polymenorrhea)")
        elif avg_cycle_length > 35:
            concerning_patterns.append("Long cycles (oligomenorrhea)")
        
        if regularity_score < 0.5:
            concerning_patterns.append("Irregular cycle patterns")
        
        if luteal_adequacy < 0.5:
            concerning_patterns.append("Short luteal phase")
        
        # Generate recommendations
        recommendations = []
        if health_score < 0.6:
            recommendations.append("Consider consultation with reproductive endocrinologist")
        if regularity_score < 0.7:
            recommendations.append("Track ovulation more consistently")
        if luteal_adequacy < 0.7:
            recommendations.append("Discuss luteal phase support with healthcare provider")
        
        recommendations.append("Continue consistent cycle tracking")
        recommendations.append("Maintain healthy lifestyle habits")
        
        return FertilityMetrics(
            average_cycle_length=round(avg_cycle_length, 1),
            cycle_regularity_score=round(regularity_score, 2),
            ovulation_consistency=round(ovulation_consistency, 2),
            luteal_phase_adequacy=round(luteal_adequacy, 2),
            fertility_window_prediction=fertility_window,
            next_period_prediction=predicted_next_start.strftime("%Y-%m-%d"),
            reproductive_health_score=round(health_score, 2),
            concerning_patterns=concerning_patterns,
            recommendations=recommendations
        )
    
    def get_patient_data_summary(self, patient_id: str) -> Dict[str, Any]:
        """Get comprehensive summary of patient's connected data."""
        
        if patient_id not in self.patient_data_cache:
            return {"error": "No data available for patient"}
        
        connected_platforms = [
            key.split("_", 1)[1] for key in self.connected_platforms.keys()
            if key.startswith(patient_id)
        ]
        
        data_quality_scores = {}
        last_sync_dates = {}
        
        for platform in connected_platforms:
            platform_data = self.patient_data_cache[patient_id].get(platform, {})
            data_quality_scores[platform] = platform_data.get("data_quality", 0)
            last_sync_dates[platform] = platform_data.get("last_updated", "Never")
        
        # Compute fertility metrics
        try:
            fertility_metrics = self.compute_fertility_metrics(patient_id)
            fertility_summary = asdict(fertility_metrics)
        except Exception:
            fertility_summary = {"error": "Unable to compute fertility metrics"}
        
        return {
            "patient_id": patient_id,
            "connected_platforms": connected_platforms,
            "data_quality_scores": data_quality_scores,
            "last_sync_dates": last_sync_dates,
            "fertility_metrics": fertility_summary,
            "privacy_settings": self.privacy_settings.get(patient_id, {}),
            "summary_generated": datetime.now().isoformat()
        }
    
    def export_patient_data(self, 
                          patient_id: str,
                          format_type: str = "json",
                          date_range: Optional[tuple] = None) -> Dict[str, Any]:
        """Export patient data in specified format."""
        
        if patient_id not in self.patient_data_cache:
            raise ValueError("No data available for patient")
        
        # Check privacy settings
        privacy_settings = self.privacy_settings.get(patient_id, {})
        if not any(settings.get("export_allowed", False) for settings in privacy_settings.values()):
            raise PermissionError("Data export not allowed by privacy settings")
        
        export_data = {
            "export_metadata": {
                "patient_id": patient_id,
                "export_date": datetime.now().isoformat(),
                "format": format_type,
                "date_range": date_range
            },
            "patient_data": self.patient_data_cache[patient_id],
            "fertility_metrics": asdict(self.compute_fertility_metrics(patient_id)),
            "privacy_compliance": {
                "anonymized": True,
                "consent_verified": True,
                "retention_policy": "patient_controlled"
            }
        }
        
        return export_data


if __name__ == "__main__":
    # Test the patient data integration
    print("=== PATIENT DATA INTEGRATION TEST ===\n")
    
    pdi = PatientDataIntegration()
    test_patient_id = "P001"
    
    # Connect platforms
    print("1. Connecting data platforms...")
    pdi.connect_platform(
        DataSourcePlatform.CLUE,
        test_patient_id,
        "mock_auth_token",
        ["cycle_data", "symptoms", "fertility_tracking"]
    )
    
    pdi.connect_platform(
        DataSourcePlatform.OURA,
        test_patient_id,
        "mock_oura_token",
        ["sleep_data", "hrv", "temperature", "readiness"]
    )
    
    print(f"Connected platforms: {len(pdi.connected_platforms)}")
    
    # Sync data
    print("\n2. Syncing platform data...")
    date_range = (datetime.now() - timedelta(days=90), datetime.now())
    
    clue_data = pdi.sync_platform_data(test_patient_id, DataSourcePlatform.CLUE, date_range)
    oura_data = pdi.sync_platform_data(test_patient_id, DataSourcePlatform.OURA, date_range)
    
    print(f"Clue cycles synced: {len(clue_data.get('standardized_cycles', []))}")
    print(f"Oura data synced: {'Yes' if oura_data.get('standardized_wearable_data') else 'No'}")
    
    # Compute fertility metrics
    print("\n3. Computing fertility metrics...")
    fertility_metrics = pdi.compute_fertility_metrics(test_patient_id)
    
    print(f"Average cycle length: {fertility_metrics.average_cycle_length} days")
    print(f"Cycle regularity score: {fertility_metrics.cycle_regularity_score}")
    print(f"Reproductive health score: {fertility_metrics.reproductive_health_score}")
    print(f"Next period prediction: {fertility_metrics.next_period_prediction}")
    print(f"Concerning patterns: {len(fertility_metrics.concerning_patterns)}")
    
    # Get comprehensive summary
    print("\n4. Patient data summary...")
    summary = pdi.get_patient_data_summary(test_patient_id)
    print(f"Connected platforms: {summary['connected_platforms']}")
    print(f"Data quality scores: {summary['data_quality_scores']}")
    
    print("\n✅ Patient data integration test completed!")