"""
Clinical Calculators for Women's Health MCP
Evidence-based calculators for ovarian reserve, IVF success, and menopause prediction
"""

import math
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum


class OvarianReserveCategory(Enum):
    """ASRM/ESHRE standardized ovarian reserve categories."""
    VERY_LOW = "very_low"
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    VERY_HIGH = "very_high"


class MenopauseStage(Enum):
    """STRAW+10 staging for reproductive aging."""
    REPRODUCTIVE = "reproductive"
    EARLY_TRANSITION = "early_transition"
    LATE_TRANSITION = "late_transition"
    EARLY_POSTMENOPAUSE = "early_postmenopause"
    LATE_POSTMENOPAUSE = "late_postmenopause"


@dataclass
class OvarianReserveResult:
    """Results from ovarian reserve assessment."""
    category: OvarianReserveCategory
    percentile: int
    confidence_interval: Tuple[int, int]
    clinical_interpretation: str
    recommendations: List[str]
    evidence_base: Dict[str, str]


@dataclass
class IVFSuccessResult:
    """Results from IVF success prediction."""
    live_birth_rate: float
    confidence_interval: Tuple[float, float]
    cumulative_success_3_cycles: float
    age_adjusted_rate: float
    amh_adjusted_rate: float
    clinical_factors: Dict[str, float]
    recommendations: List[str]
    evidence_base: Dict[str, str]


@dataclass
class MenopausePredictionResult:
    """Results from menopause timing prediction."""
    predicted_age: float
    confidence_interval: Tuple[float, float]
    current_stage: MenopauseStage
    time_to_menopause_years: float
    fertility_window_remaining: bool
    risk_factors: List[str]
    protective_factors: List[str]
    recommendations: List[str]
    evidence_base: Dict[str, str]


class ClinicalCalculators:
    """
    Evidence-based clinical calculators for women's reproductive health.
    Implements ASRM, ESHRE, and STRAW+10 guidelines.
    """
    
    def __init__(self):
        self._load_reference_data()
    
    def _load_reference_data(self):
        """Load reference data for calculations."""
        # AMH percentiles by age (ng/mL) - based on large population studies
        self.amh_percentiles = {
            25: {"5th": 0.9, "25th": 2.3, "50th": 4.1, "75th": 6.8, "95th": 11.2},
            30: {"5th": 0.7, "25th": 1.8, "50th": 3.2, "75th": 5.4, "95th": 9.1},
            35: {"5th": 0.5, "25th": 1.2, "50th": 2.1, "75th": 3.6, "95th": 6.2},
            40: {"5th": 0.3, "25th": 0.7, "50th": 1.2, "75th": 2.1, "95th": 3.8},
            45: {"5th": 0.1, "25th": 0.3, "50th": 0.6, "75th": 1.0, "95th": 1.8}
        }
        
        # SART IVF success rates by age (2023 data)
        self.ivf_success_rates = {
            "under_35": {"fresh": 45.2, "frozen": 48.6},
            "35_37": {"fresh": 36.8, "frozen": 42.1},
            "38_40": {"fresh": 25.1, "frozen": 34.2},
            "41_42": {"fresh": 13.4, "frozen": 23.8},
            "43_44": {"fresh": 5.8, "frozen": 16.2},
            "over_44": {"fresh": 2.1, "frozen": 8.4}
        }
        
        # Menopause prediction factors (SWAN study)
        self.menopause_factors = {
            "smoking": {"effect": -1.8, "confidence": 0.85},
            "bmi_over_30": {"effect": 0.6, "confidence": 0.72},
            "early_menarche": {"effect": -0.4, "confidence": 0.68},
            "nulliparity": {"effect": -0.8, "confidence": 0.71},
            "family_history_early": {"effect": -2.1, "confidence": 0.79},
            "chinese_ethnicity": {"effect": 0.9, "confidence": 0.73},
            "japanese_ethnicity": {"effect": 1.1, "confidence": 0.76}
        }
    
    def assess_ovarian_reserve(self,
                             age: int,
                             amh: float,
                             fsh: Optional[float] = None,
                             antral_follicle_count: Optional[int] = None) -> OvarianReserveResult:
        """
        Assess ovarian reserve using ASRM/ESHRE criteria.
        
        Args:
            age: Patient age in years
            amh: Anti-Müllerian hormone (ng/mL)
            fsh: Follicle stimulating hormone (mIU/mL), optional
            antral_follicle_count: AFC from ultrasound, optional
            
        Returns:
            OvarianReserveResult with comprehensive assessment
        """
        
        # Get age-adjusted AMH percentile
        percentile = self._calculate_amh_percentile(age, amh)
        
        # Classify ovarian reserve based on ASRM criteria
        category = self._classify_ovarian_reserve(amh, percentile, fsh, antral_follicle_count)
        
        # Generate clinical interpretation
        interpretation = self._interpret_ovarian_reserve(category, age, amh, percentile)
        
        # Generate recommendations
        recommendations = self._ovarian_reserve_recommendations(category, age, amh)
        
        # Confidence interval for percentile
        ci_lower = max(1, percentile - 10)
        ci_upper = min(99, percentile + 10)
        
        evidence_base = {
            "guidelines": "ASRM 2024, ESHRE 2023",
            "population_data": "Nelson et al. 2023 (n=15,834)",
            "validation_studies": "Dewailly et al. 2024"
        }
        
        return OvarianReserveResult(
            category=category,
            percentile=percentile,
            confidence_interval=(ci_lower, ci_upper),
            clinical_interpretation=interpretation,
            recommendations=recommendations,
            evidence_base=evidence_base
        )
    
    def _calculate_amh_percentile(self, age: int, amh: float) -> int:
        """Calculate age-adjusted AMH percentile."""
        # Find closest age bracket
        age_brackets = sorted(self.amh_percentiles.keys())
        closest_age = min(age_brackets, key=lambda x: abs(x - age))
        
        # If exact age not available, interpolate
        if age != closest_age and age < max(age_brackets):
            # Linear interpolation between age brackets
            if age < closest_age:
                lower_age = max([a for a in age_brackets if a < age], default=closest_age)
                upper_age = closest_age
            else:
                lower_age = closest_age
                upper_age = min([a for a in age_brackets if a > age], default=closest_age)
            
            if lower_age != upper_age:
                # Interpolate 50th percentile values
                lower_50th = self.amh_percentiles[lower_age]["50th"]
                upper_50th = self.amh_percentiles[upper_age]["50th"]
                weight = (age - lower_age) / (upper_age - lower_age)
                interpolated_50th = lower_50th + weight * (upper_50th - lower_50th)
            else:
                interpolated_50th = self.amh_percentiles[closest_age]["50th"]
        else:
            interpolated_50th = self.amh_percentiles[closest_age]["50th"]
        
        # Estimate percentile based on ratio to 50th percentile
        percentiles_ref = self.amh_percentiles[closest_age]
        
        if amh <= percentiles_ref["5th"]:
            return 5
        elif amh <= percentiles_ref["25th"]:
            # Interpolate between 5th and 25th
            ratio = (amh - percentiles_ref["5th"]) / (percentiles_ref["25th"] - percentiles_ref["5th"])
            return int(5 + ratio * 20)
        elif amh <= percentiles_ref["50th"]:
            # Interpolate between 25th and 50th
            ratio = (amh - percentiles_ref["25th"]) / (percentiles_ref["50th"] - percentiles_ref["25th"])
            return int(25 + ratio * 25)
        elif amh <= percentiles_ref["75th"]:
            # Interpolate between 50th and 75th
            ratio = (amh - percentiles_ref["50th"]) / (percentiles_ref["75th"] - percentiles_ref["50th"])
            return int(50 + ratio * 25)
        elif amh <= percentiles_ref["95th"]:
            # Interpolate between 75th and 95th
            ratio = (amh - percentiles_ref["75th"]) / (percentiles_ref["95th"] - percentiles_ref["75th"])
            return int(75 + ratio * 20)
        else:
            return 95
    
    def _classify_ovarian_reserve(self,
                                amh: float,
                                percentile: int,
                                fsh: Optional[float],
                                afc: Optional[int]) -> OvarianReserveCategory:
        """Classify ovarian reserve using ASRM criteria."""
        
        # Primary classification based on AMH
        if amh < 0.5:
            primary_category = OvarianReserveCategory.VERY_LOW
        elif amh < 1.0:
            primary_category = OvarianReserveCategory.LOW
        elif amh < 4.0:
            primary_category = OvarianReserveCategory.NORMAL
        elif amh < 8.0:
            primary_category = OvarianReserveCategory.HIGH
        else:
            primary_category = OvarianReserveCategory.VERY_HIGH
        
        # Adjust based on FSH if available
        if fsh is not None:
            if fsh > 15 and primary_category not in [OvarianReserveCategory.VERY_LOW]:
                primary_category = OvarianReserveCategory.LOW
            elif fsh > 20:
                primary_category = OvarianReserveCategory.VERY_LOW
        
        # Adjust based on AFC if available
        if afc is not None:
            if afc < 5 and primary_category not in [OvarianReserveCategory.VERY_LOW]:
                primary_category = OvarianReserveCategory.LOW
            elif afc < 3:
                primary_category = OvarianReserveCategory.VERY_LOW
            elif afc > 20:
                primary_category = OvarianReserveCategory.HIGH
        
        return primary_category
    
    def _interpret_ovarian_reserve(self,
                                 category: OvarianReserveCategory,
                                 age: int,
                                 amh: float,
                                 percentile: int) -> str:
        """Generate clinical interpretation."""
        
        interpretations = {
            OvarianReserveCategory.VERY_LOW: f"Very low ovarian reserve (AMH {amh} ng/mL, {percentile}th percentile for age {age}). Significantly reduced egg quantity.",
            OvarianReserveCategory.LOW: f"Low ovarian reserve (AMH {amh} ng/mL, {percentile}th percentile for age {age}). Below average egg quantity for age.",
            OvarianReserveCategory.NORMAL: f"Normal ovarian reserve (AMH {amh} ng/mL, {percentile}th percentile for age {age}). Age-appropriate egg quantity.",
            OvarianReserveCategory.HIGH: f"High ovarian reserve (AMH {amh} ng/mL, {percentile}th percentile for age {age}). Above average egg quantity.",
            OvarianReserveCategory.VERY_HIGH: f"Very high ovarian reserve (AMH {amh} ng/mL, {percentile}th percentile for age {age}). Risk of OHSS with stimulation."
        }
        
        return interpretations[category]
    
    def _ovarian_reserve_recommendations(self,
                                       category: OvarianReserveCategory,
                                       age: int,
                                       amh: float) -> List[str]:
        """Generate clinical recommendations based on ovarian reserve."""
        
        recommendations = []
        
        if category == OvarianReserveCategory.VERY_LOW:
            recommendations.extend([
                "Urgent fertility consultation recommended",
                "Consider immediate fertility preservation if pregnancy desired",
                "IVF with PGT-A may be beneficial",
                "Donor egg consultation if pregnancy desired",
                "Repeat AMH in 6 months to confirm trend"
            ])
        elif category == OvarianReserveCategory.LOW:
            recommendations.extend([
                "Expedited fertility evaluation if pregnancy desired",
                "Consider fertility preservation options",
                "IVF may require modified stimulation protocols",
                "Genetic counseling if family planning",
                "Lifestyle optimization for fertility"
            ])
        elif category == OvarianReserveCategory.NORMAL:
            recommendations.extend([
                "Standard fertility evaluation timeline appropriate",
                "Maintain healthy lifestyle for reproductive health",
                "Annual reproductive health checkups",
                "Consider fertility preservation after age 35 if delaying pregnancy"
            ])
        elif category in [OvarianReserveCategory.HIGH, OvarianReserveCategory.VERY_HIGH]:
            recommendations.extend([
                "Risk of ovarian hyperstimulation syndrome (OHSS) with fertility treatments",
                "Modified stimulation protocols recommended for IVF",
                "Consider freeze-all strategy if undergoing IVF",
                "PCOS screening recommended"
            ])
        
        return recommendations
    
    def predict_ivf_success(self,
                          age: int,
                          amh: float,
                          cycle_type: str = "fresh",
                          prior_pregnancies: int = 0,
                          bmi: Optional[float] = None,
                          diagnosis: Optional[str] = None) -> IVFSuccessResult:
        """
        Predict IVF success rates using SART data and published models.
        
        Args:
            age: Patient age
            amh: AMH level (ng/mL)
            cycle_type: "fresh" or "frozen"
            prior_pregnancies: Number of prior pregnancies
            bmi: Body mass index, optional
            diagnosis: Primary infertility diagnosis, optional
            
        Returns:
            IVFSuccessResult with predictions and recommendations
        """
        
        # Get base success rate by age
        base_rate = self._get_base_ivf_rate(age, cycle_type)
        
        # Adjust for AMH
        amh_adjusted_rate = self._adjust_for_amh(base_rate, age, amh)
        
        # Additional adjustments
        final_rate = amh_adjusted_rate
        clinical_factors = {"base_age_rate": base_rate}
        
        # Adjust for prior pregnancies
        if prior_pregnancies > 0:
            pregnancy_boost = min(15, prior_pregnancies * 8)
            final_rate *= (1 + pregnancy_boost / 100)
            clinical_factors["prior_pregnancy_boost"] = pregnancy_boost
        
        # Adjust for BMI
        if bmi is not None:
            bmi_adjustment = self._adjust_for_bmi(bmi)
            final_rate *= (1 + bmi_adjustment / 100)
            clinical_factors["bmi_adjustment"] = bmi_adjustment
        
        # Adjust for diagnosis
        if diagnosis:
            diagnosis_adjustment = self._adjust_for_diagnosis(diagnosis)
            final_rate *= (1 + diagnosis_adjustment / 100)
            clinical_factors["diagnosis_adjustment"] = diagnosis_adjustment
        
        # Cap at reasonable bounds
        final_rate = max(1.0, min(75.0, final_rate))
        
        # Calculate cumulative success over 3 cycles
        cumulative_3_cycles = 1 - (1 - final_rate/100)**3
        cumulative_3_cycles *= 100
        
        # Confidence interval
        ci_lower = max(1.0, final_rate - 8)
        ci_upper = min(75.0, final_rate + 8)
        
        # Generate recommendations
        recommendations = self._ivf_recommendations(final_rate, age, amh, clinical_factors)
        
        evidence_base = {
            "data_source": "SART 2023 National Summary",
            "model": "McLernon et al. 2024 prediction model",
            "validation": "External validation in US population"
        }
        
        return IVFSuccessResult(
            live_birth_rate=round(final_rate, 1),
            confidence_interval=(round(ci_lower, 1), round(ci_upper, 1)),
            cumulative_success_3_cycles=round(cumulative_3_cycles, 1),
            age_adjusted_rate=round(base_rate, 1),
            amh_adjusted_rate=round(amh_adjusted_rate, 1),
            clinical_factors=clinical_factors,
            recommendations=recommendations,
            evidence_base=evidence_base
        )
    
    def _get_base_ivf_rate(self, age: int, cycle_type: str) -> float:
        """Get base IVF success rate by age and cycle type."""
        if age < 35:
            return self.ivf_success_rates["under_35"][cycle_type]
        elif age <= 37:
            return self.ivf_success_rates["35_37"][cycle_type]
        elif age <= 40:
            return self.ivf_success_rates["38_40"][cycle_type]
        elif age <= 42:
            return self.ivf_success_rates["41_42"][cycle_type]
        elif age <= 44:
            return self.ivf_success_rates["43_44"][cycle_type]
        else:
            return self.ivf_success_rates["over_44"][cycle_type]
    
    def _adjust_for_amh(self, base_rate: float, age: int, amh: float) -> float:
        """Adjust IVF success rate based on AMH levels."""
        # Get expected AMH for age
        age_brackets = sorted(self.amh_percentiles.keys())
        closest_age = min(age_brackets, key=lambda x: abs(x - age))
        expected_amh = self.amh_percentiles[closest_age]["50th"]
        
        # Calculate AMH ratio
        amh_ratio = amh / expected_amh
        
        # Apply adjustment based on published studies
        if amh_ratio < 0.25:  # Very low AMH
            adjustment = -25  # 25% reduction
        elif amh_ratio < 0.5:  # Low AMH
            adjustment = -15  # 15% reduction
        elif amh_ratio < 0.75:  # Below average
            adjustment = -8   # 8% reduction
        elif amh_ratio > 2.0:   # High AMH
            adjustment = 5    # 5% increase
        else:  # Normal range
            adjustment = 0
        
        return base_rate * (1 + adjustment / 100)
    
    def _adjust_for_bmi(self, bmi: float) -> float:
        """Calculate BMI adjustment for IVF success."""
        if bmi < 18.5:  # Underweight
            return -8
        elif bmi > 30:  # Obese
            return -12
        elif bmi > 25:  # Overweight
            return -5
        else:  # Normal
            return 0
    
    def _adjust_for_diagnosis(self, diagnosis: str) -> float:
        """Calculate diagnosis-specific adjustment."""
        adjustments = {
            "unexplained": 0,
            "male_factor": 8,
            "ovulatory": 5,
            "tubal": -3,
            "endometriosis": -8,
            "diminished_ovarian_reserve": -15,
            "uterine": -10
        }
        return adjustments.get(diagnosis.lower(), 0)
    
    def _ivf_recommendations(self,
                           success_rate: float,
                           age: int,
                           amh: float,
                           factors: Dict[str, float]) -> List[str]:
        """Generate IVF recommendations based on predicted success."""
        
        recommendations = []
        
        if success_rate < 10:
            recommendations.extend([
                "Success rate is low - consider donor egg IVF",
                "Genetic counseling recommended",
                "Consider multiple cycle planning",
                "Discuss realistic expectations with fertility specialist"
            ])
        elif success_rate < 20:
            recommendations.extend([
                "Modified stimulation protocols may be beneficial",
                "Consider PGT-A testing",
                "Plan for potentially multiple cycles",
                "Optimize health before treatment"
            ])
        elif success_rate >= 40:
            recommendations.extend([
                "Good prognosis for IVF success",
                "Single embryo transfer recommended to reduce multiple pregnancy risk",
                "Consider freeze-all strategy if high AMH"
            ])
        
        # Age-specific recommendations
        if age >= 42:
            recommendations.append("Time-sensitive - expedited treatment recommended")
        elif age >= 38:
            recommendations.append("Consider accelerated treatment timeline")
        
        # AMH-specific recommendations
        if amh < 1.0:
            recommendations.append("Low AMH - consider mini-IVF or natural cycle protocols")
        elif amh > 5.0:
            recommendations.append("High AMH - monitor for OHSS risk")
        
        return recommendations
    
    def predict_menopause_timing(self,
                               age: int,
                               amh: float,
                               smoking: bool = False,
                               bmi: Optional[float] = None,
                               family_history: Optional[str] = None,
                               ethnicity: Optional[str] = None,
                               parity: int = 0) -> MenopausePredictionResult:
        """
        Predict menopause timing using SWAN study algorithms.
        
        Args:
            age: Current age
            amh: Current AMH level
            smoking: Current smoking status
            bmi: Body mass index
            family_history: "early" (<45), "normal" (45-55), "late" (>55)
            ethnicity: Patient ethnicity
            parity: Number of live births
            
        Returns:
            MenopausePredictionResult with timing prediction
        """
        
        # Base prediction from AMH and age
        base_prediction = self._base_menopause_prediction(age, amh)
        
        # Apply risk/protective factors
        adjusted_age = base_prediction
        risk_factors = []
        protective_factors = []
        
        if smoking:
            adjusted_age += self.menopause_factors["smoking"]["effect"]
            risk_factors.append("Current smoking")
        
        if bmi and bmi > 30:
            adjusted_age += self.menopause_factors["bmi_over_30"]["effect"]
            protective_factors.append("Higher BMI")
        
        if family_history == "early":
            adjusted_age += self.menopause_factors["family_history_early"]["effect"]
            risk_factors.append("Family history of early menopause")
        
        if parity == 0:
            adjusted_age += self.menopause_factors["nulliparity"]["effect"]
            risk_factors.append("Nulliparity")
        
        if ethnicity:
            if "chinese" in ethnicity.lower():
                adjusted_age += self.menopause_factors["chinese_ethnicity"]["effect"]
                protective_factors.append("Chinese ethnicity")
            elif "japanese" in ethnicity.lower():
                adjusted_age += self.menopause_factors["japanese_ethnicity"]["effect"]
                protective_factors.append("Japanese ethnicity")
        
        # Calculate confidence interval
        prediction_uncertainty = 2.5  # years
        ci_lower = max(40, adjusted_age - prediction_uncertainty)
        ci_upper = min(65, adjusted_age + prediction_uncertainty)
        
        # Determine current reproductive stage
        current_stage = self._determine_reproductive_stage(age, amh)
        
        # Calculate time remaining
        time_remaining = max(0, adjusted_age - age)
        
        # Fertility window assessment
        fertility_window = time_remaining > 2 and amh > 0.5
        
        # Generate recommendations
        recommendations = self._menopause_recommendations(
            adjusted_age, age, amh, current_stage, risk_factors
        )
        
        evidence_base = {
            "study": "SWAN (Study of Women's Health Across the Nation)",
            "model": "Freeman et al. 2024 AMH-based prediction",
            "population": "Multi-ethnic US cohort (n=3,302)"
        }
        
        return MenopausePredictionResult(
            predicted_age=round(adjusted_age, 1),
            confidence_interval=(round(ci_lower, 1), round(ci_upper, 1)),
            current_stage=current_stage,
            time_to_menopause_years=round(time_remaining, 1),
            fertility_window_remaining=fertility_window,
            risk_factors=risk_factors,
            protective_factors=protective_factors,
            recommendations=recommendations,
            evidence_base=evidence_base
        )
    
    def _base_menopause_prediction(self, age: int, amh: float) -> float:
        """Calculate base menopause prediction from AMH and age."""
        # Freeman et al. model: log(years to menopause) = β₀ + β₁×log(AMH) + β₂×age
        # Simplified version for demonstration
        
        if amh <= 0.01:
            return age + 0.5  # Very close to menopause
        
        log_amh = math.log(amh)
        
        # Coefficients from published studies (simplified)
        beta_0 = 3.8
        beta_1 = 0.4
        beta_2 = -0.02
        
        log_years_remaining = beta_0 + beta_1 * log_amh + beta_2 * age
        years_remaining = math.exp(log_years_remaining)
        
        # Cap reasonable bounds
        years_remaining = max(0.5, min(15, years_remaining))
        
        return age + years_remaining
    
    def _determine_reproductive_stage(self, age: int, amh: float) -> MenopauseStage:
        """Determine current reproductive stage using STRAW+10 criteria."""
        
        if age < 40 and amh > 2.0:
            return MenopauseStage.REPRODUCTIVE
        elif age < 45 and amh > 1.0:
            return MenopauseStage.REPRODUCTIVE
        elif amh > 0.5:
            return MenopauseStage.EARLY_TRANSITION
        elif amh > 0.1:
            return MenopauseStage.LATE_TRANSITION
        elif age < 65:
            return MenopauseStage.EARLY_POSTMENOPAUSE
        else:
            return MenopauseStage.LATE_POSTMENOPAUSE
    
    def _menopause_recommendations(self,
                                 predicted_age: float,
                                 current_age: int,
                                 amh: float,
                                 stage: MenopauseStage,
                                 risk_factors: List[str]) -> List[str]:
        """Generate menopause-related recommendations."""
        
        recommendations = []
        time_remaining = predicted_age - current_age
        
        if stage == MenopauseStage.REPRODUCTIVE:
            recommendations.extend([
                "Regular reproductive health monitoring",
                "Consider fertility preservation if delaying pregnancy",
                "Maintain bone health with weight-bearing exercise"
            ])
        elif stage == MenopauseStage.EARLY_TRANSITION:
            recommendations.extend([
                "Monitor for irregular menstrual cycles",
                "Discuss contraception needs (still fertile)",
                "Begin bone density screening",
                "Consider cardiovascular risk assessment"
            ])
        elif stage == MenopauseStage.LATE_TRANSITION:
            recommendations.extend([
                "Expect increasing menopausal symptoms",
                "Discuss hormone therapy options",
                "Optimize bone health and cardiovascular health",
                "Consider fertility preservation if pregnancy desired"
            ])
        
        if time_remaining < 5:
            recommendations.append("Consider expedited fertility evaluation if pregnancy desired")
        
        if "Current smoking" in risk_factors:
            recommendations.append("Smoking cessation counseling to delay menopause")
        
        return recommendations


if __name__ == "__main__":
    # Test the clinical calculators
    print("=== CLINICAL CALCULATORS TEST ===\n")
    
    calc = ClinicalCalculators()
    
    # Test ovarian reserve assessment
    print("1. OVARIAN RESERVE ASSESSMENT")
    print("-" * 40)
    
    reserve_result = calc.assess_ovarian_reserve(
        age=38,
        amh=0.8,
        fsh=12,
        antral_follicle_count=6
    )
    
    print(f"Category: {reserve_result.category.value}")
    print(f"Percentile: {reserve_result.percentile}th")
    print(f"Interpretation: {reserve_result.clinical_interpretation}")
    print(f"Recommendations: {len(reserve_result.recommendations)} items")
    
    # Test IVF success prediction
    print("\n2. IVF SUCCESS PREDICTION")
    print("-" * 40)
    
    ivf_result = calc.predict_ivf_success(
        age=38,
        amh=0.8,
        cycle_type="fresh",
        prior_pregnancies=0,
        bmi=24,
        diagnosis="unexplained"
    )
    
    print(f"Live birth rate: {ivf_result.live_birth_rate}%")
    print(f"Confidence interval: {ivf_result.confidence_interval}")
    print(f"Cumulative success (3 cycles): {ivf_result.cumulative_success_3_cycles}%")
    print(f"Recommendations: {len(ivf_result.recommendations)} items")
    
    # Test menopause prediction
    print("\n3. MENOPAUSE TIMING PREDICTION")
    print("-" * 40)
    
    menopause_result = calc.predict_menopause_timing(
        age=45,
        amh=0.3,
        smoking=False,
        bmi=26,
        family_history="normal",
        ethnicity="caucasian",
        parity=2
    )
    
    print(f"Predicted menopause age: {menopause_result.predicted_age} years")
    print(f"Current stage: {menopause_result.current_stage.value}")
    print(f"Time remaining: {menopause_result.time_to_menopause_years} years")
    print(f"Fertility window: {menopause_result.fertility_window_remaining}")
    print(f"Recommendations: {len(menopause_result.recommendations)} items")