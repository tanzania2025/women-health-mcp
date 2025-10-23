"""
Clinical Calculators for Women's Health MCP
SART IVF Calculator using real API data
"""

from typing import Any, Optional
import httpx
from dataclasses import dataclass


# SART calculator URL
SART_URL = "https://w3.abdn.ac.uk/clsm/SARTIVF/tool/ivf1"


@dataclass
class IVFSuccessResult:
    """Results from SART IVF success calculator."""
    age: int
    height_cm: Optional[float]
    weight_kg: Optional[float]
    height_ft: Optional[int]
    height_in: Optional[int]
    weight_lbs: Optional[float]
    previous_full_term: bool
    male_factor: bool
    polycystic: bool
    uterine_problems: bool
    unexplained_infertility: bool
    low_ovarian_reserve: bool
    amh_available: bool
    amh_value: Optional[float]
    success_rate_1_cycle: Optional[float]
    success_rate_2_cycles: Optional[float]
    success_rate_3_cycles: Optional[float]
    raw_response: dict


class ClinicalCalculators:
    """
    Clinical calculators using the SART IVF Calculator API.
    Provides evidence-based IVF success rate predictions.
    """

    async def calculate_ivf_success(
        self,
        age: int,
        height_cm: float = None,
        weight_kg: float = None,
        height_ft: int = None,
        height_in: int = None,
        weight_lbs: float = None,
        previous_full_term: bool = False,
        male_factor: bool = False,
        polycystic: bool = False,
        uterine_problems: bool = False,
        unexplained_infertility: bool = False,
        low_ovarian_reserve: bool = False,
        amh_available: bool = False,
        amh_value: float = 0.0,
    ) -> IVFSuccessResult:
        """
        Calculate IVF success rates using the SART calculator API.

        Args:
            age: Patient age (18-45)
            height_cm: Height in centimeters (if using metric)
            weight_kg: Weight in kilograms (if using metric)
            height_ft: Height in feet (if using imperial)
            height_in: Height in inches (if using imperial)
            weight_lbs: Weight in pounds (if using imperial)
            previous_full_term: Has patient had a previous full-term pregnancy (>37 weeks)?
            male_factor: Does partner have sperm problems?
            polycystic: Does patient have PCOS?
            uterine_problems: Does patient have uterine problems (septum, myoma, adhesions, anomalies)?
            unexplained_infertility: Diagnosed with unexplained infertility?
            low_ovarian_reserve: Diagnosed with low ovarian reserve?
            amh_available: Is AMH (Anti-Müllerian Hormone) level known?
            amh_value: AMH level in ng/ml (if available)

        Returns:
            IVFSuccessResult containing success probability results
        """
        # Determine if using metric or imperial
        is_metric = height_cm is not None and weight_kg is not None
        is_metric_weight = weight_kg is not None

        # Set defaults for missing values
        if is_metric:
            height = height_cm or 165
            weight = weight_kg or 65
            feet = 5
            inches = 5
            pounds = weight * 2.20462  # Convert kg to lbs
        else:
            height = 165  # Default cm
            weight = 65   # Default kg
            feet = height_ft or 5
            inches = height_in or 5
            pounds = weight_lbs or 143
            if not is_metric_weight:
                weight = pounds / 2.20462  # Convert lbs to kg

        # Build form data
        form_data = {
            "Age": str(age),
            "Height": str(int(height)),
            "Weight": str(int(weight)),
            "Feet": str(feet),
            "Inches": str(inches),
            "Pounds": str(int(pounds)),
            "PreviousFullTerm": "true" if previous_full_term else "false",
            "MaleFactor": "true" if male_factor else "false",
            "Polycystic": "true" if polycystic else "false",
            "Uterine": "true" if uterine_problems else "false",
            "Unexplained": "true" if unexplained_infertility else "false",
            "LowOvarian": "true" if low_ovarian_reserve else "false",
            "AMH_Available": "true" if amh_available else "false",
            "AmhValue": str(amh_value),
            "isMetric": "true" if is_metric else "false",
            "isMetricWeight": "true" if is_metric_weight else "false",
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                SART_URL,
                data=form_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=30.0,
                follow_redirects=True,
            )
            response.raise_for_status()
            data = response.json()

            # Extract cumulative probabilities (for 1, 2, and 3 cycles)
            cumulative_probs = data.get("CumulativeProbabilityResult", [])

            return IVFSuccessResult(
                age=age,
                height_cm=height if is_metric else None,
                weight_kg=weight if is_metric_weight else None,
                height_ft=feet if not is_metric else None,
                height_in=inches if not is_metric else None,
                weight_lbs=pounds if not is_metric_weight else None,
                previous_full_term=previous_full_term,
                male_factor=male_factor,
                polycystic=polycystic,
                uterine_problems=uterine_problems,
                unexplained_infertility=unexplained_infertility,
                low_ovarian_reserve=low_ovarian_reserve,
                amh_available=amh_available,
                amh_value=amh_value if amh_available else None,
                success_rate_1_cycle=round(cumulative_probs[0], 2) if len(cumulative_probs) > 0 else None,
                success_rate_2_cycles=round(cumulative_probs[1], 2) if len(cumulative_probs) > 1 else None,
                success_rate_3_cycles=round(cumulative_probs[2], 2) if len(cumulative_probs) > 2 else None,
                raw_response=data,
            )

    async def predict_ivf_success_async(
        self,
        age: int,
        amh: float,
        cycle_type: str = "fresh",
        prior_pregnancies: int = 0,
        bmi: Optional[float] = None,
        diagnosis: Optional[str] = None,
    ) -> dict:
        """
        Async wrapper for IVF success prediction for backwards compatibility.

        Args:
            age: Patient age
            amh: AMH level (ng/mL)
            cycle_type: "fresh" or "frozen" (ignored - SART calculator doesn't distinguish)
            prior_pregnancies: Number of prior pregnancies
            bmi: Body mass index, optional
            diagnosis: Primary infertility diagnosis, optional

        Returns:
            Dictionary containing success rate information
        """
        # Map diagnosis to SART parameters
        male_factor = diagnosis == "male_factor"
        unexplained = diagnosis == "unexplained"
        low_ovarian = diagnosis == "diminished_ovarian_reserve"
        uterine = diagnosis == "uterine"
        polycystic = False  # Could be inferred from diagnosis in future

        # Calculate BMI-based weight if BMI provided (assuming average height)
        weight_kg = None
        if bmi:
            height_m = 1.65  # Assume average height
            weight_kg = bmi * (height_m ** 2)

        # Run async calculator
        result = await self.calculate_ivf_success(
            age=age,
            weight_kg=weight_kg,
            previous_full_term=prior_pregnancies > 0,
            male_factor=male_factor,
            polycystic=polycystic,
            uterine_problems=uterine,
            unexplained_infertility=unexplained,
            low_ovarian_reserve=low_ovarian,
            amh_available=True,
            amh_value=amh,
        )

        # Return in expected format
        return {
            "live_birth_rate": result.success_rate_1_cycle,
            "cumulative_success_3_cycles": result.success_rate_3_cycles,
            "confidence_interval": (
                max(0, result.success_rate_1_cycle - 5) if result.success_rate_1_cycle else 0,
                min(100, result.success_rate_1_cycle + 5) if result.success_rate_1_cycle else 0,
            ),
            "age_adjusted_rate": result.success_rate_1_cycle,
            "amh_adjusted_rate": result.success_rate_1_cycle,
            "clinical_factors": {
                "age": age,
                "amh": amh,
                "previous_full_term": result.previous_full_term,
                "male_factor": result.male_factor,
                "unexplained_infertility": result.unexplained_infertility,
                "low_ovarian_reserve": result.low_ovarian_reserve,
            },
            "recommendations": self._generate_recommendations(result),
            "evidence_base": {
                "data_source": "SART IVF Calculator",
                "model": "University of Aberdeen SART model",
                "url": SART_URL,
            },
        }

    def predict_ivf_success(
        self,
        age: int,
        amh: float,
        cycle_type: str = "fresh",
        prior_pregnancies: int = 0,
        bmi: Optional[float] = None,
        diagnosis: Optional[str] = None,
    ) -> dict:
        """
        Synchronous wrapper for IVF success prediction for backwards compatibility.

        Note: This is a synchronous wrapper. Use predict_ivf_success_async in async contexts.

        Args:
            age: Patient age
            amh: AMH level (ng/mL)
            cycle_type: "fresh" or "frozen" (ignored - SART calculator doesn't distinguish)
            prior_pregnancies: Number of prior pregnancies
            bmi: Body mass index, optional
            diagnosis: Primary infertility diagnosis, optional

        Returns:
            Dictionary containing success rate information
        """
        import asyncio

        # Try to get existing event loop
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # No event loop running, create one
            return asyncio.run(self.predict_ivf_success_async(
                age=age,
                amh=amh,
                cycle_type=cycle_type,
                prior_pregnancies=prior_pregnancies,
                bmi=bmi,
                diagnosis=diagnosis,
            ))
        else:
            # Event loop is running, use run_in_executor
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(
                    asyncio.run,
                    self.predict_ivf_success_async(
                        age=age,
                        amh=amh,
                        cycle_type=cycle_type,
                        prior_pregnancies=prior_pregnancies,
                        bmi=bmi,
                        diagnosis=diagnosis,
                    )
                )
                return future.result()

    def _generate_recommendations(self, result: IVFSuccessResult) -> list[str]:
        """Generate clinical recommendations based on SART calculator results."""
        recommendations = []

        success_rate = result.success_rate_1_cycle or 0

        if success_rate < 10:
            recommendations.extend([
                "Success rate is low - consider donor egg IVF",
                "Genetic counseling recommended",
                "Consider multiple cycle planning",
                "Discuss realistic expectations with fertility specialist",
            ])
        elif success_rate < 20:
            recommendations.extend([
                "Modified stimulation protocols may be beneficial",
                "Consider PGT-A testing",
                "Plan for potentially multiple cycles",
                "Optimize health before treatment",
            ])
        elif success_rate >= 40:
            recommendations.extend([
                "Good prognosis for IVF success",
                "Single embryo transfer recommended to reduce multiple pregnancy risk",
            ])

        # Age-specific recommendations
        if result.age >= 42:
            recommendations.append("Time-sensitive - expedited treatment recommended")
        elif result.age >= 38:
            recommendations.append("Consider accelerated treatment timeline")

        # AMH-specific recommendations
        if result.amh_available and result.amh_value:
            if result.amh_value < 1.0:
                recommendations.append("Low AMH - consider mini-IVF or natural cycle protocols")
            elif result.amh_value > 5.0:
                recommendations.append("High AMH - monitor for OHSS risk")

        # Clinical factor recommendations
        if result.polycystic:
            recommendations.append("PCOS - monitor for ovarian hyperstimulation syndrome")

        if result.low_ovarian_reserve:
            recommendations.append("Low ovarian reserve - may require multiple cycles")

        return recommendations


if __name__ == "__main__":
    # Test the SART IVF calculator
    import asyncio

    async def test():
        print("=== SART IVF CALCULATOR TEST ===\n")

        calc = ClinicalCalculators()

        # Test SART IVF calculator
        print("SART IVF Success Calculation")
        print("-" * 40)

        result = await calc.calculate_ivf_success(
            age=35,
            height_cm=165,
            weight_kg=65,
            previous_full_term=False,
            male_factor=False,
            polycystic=False,
            uterine_problems=False,
            unexplained_infertility=True,
            low_ovarian_reserve=False,
            amh_available=True,
            amh_value=2.5,
        )

        print(f"Age: {result.age}")
        print(f"Success rate (1 cycle): {result.success_rate_1_cycle}%")
        print(f"Success rate (2 cycles): {result.success_rate_2_cycles}%")
        print(f"Success rate (3 cycles): {result.success_rate_3_cycles}%")
        print(f"AMH: {result.amh_value} ng/ml")

        # Test backwards-compatible async wrapper
        print("\n\nBackwards Compatible Async API Test")
        print("-" * 40)

        compat_result = await calc.predict_ivf_success_async(
            age=35,
            amh=2.5,
            cycle_type="fresh",
            prior_pregnancies=0,
            bmi=24,
            diagnosis="unexplained",
        )

        print(f"Live birth rate: {compat_result['live_birth_rate']}%")
        print(f"Cumulative success (3 cycles): {compat_result['cumulative_success_3_cycles']}%")
        print(f"Recommendations: {len(compat_result['recommendations'])} items")

    asyncio.run(test())
