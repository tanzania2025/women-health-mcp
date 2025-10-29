#!/usr/bin/env python3
"""
SART IVF Calculator MCP Server - FastMCP Implementation

This MCP server provides tools to calculate IVF success rates using the
SART (Society for Assisted Reproductive Technology) IVF calculator.
"""

from typing import Any, Optional
import requests
from fastmcp import FastMCP
from pydantic import Field

# SART calculator URL
SART_URL = "https://w3.abdn.ac.uk/clsm/SARTIVF/tool/ivf1"

# Create FastMCP server
mcp = FastMCP("sart-ivf-server")


def calculate_ivf_success(
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
) -> dict[str, Any]:
    """
    Calculate IVF success rates using the SART calculator.

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
        Dictionary containing success probability results
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

    response = requests.post(
        SART_URL,
        data=form_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=30.0,
        allow_redirects=True,
    )
    response.raise_for_status()
    data = response.json()

    # Extract cumulative probabilities (for 1, 2, and 3 cycles)
    cumulative_probs = data.get("CumulativeProbabilityResult", [])

    return {
        "age": age,
        "height_cm": height if is_metric else None,
        "weight_kg": weight if is_metric_weight else None,
        "height_ft": feet if not is_metric else None,
        "height_in": inches if not is_metric else None,
        "weight_lbs": pounds if not is_metric_weight else None,
        "previous_full_term": previous_full_term,
        "male_factor": male_factor,
        "polycystic": polycystic,
        "uterine_problems": uterine_problems,
        "unexplained_infertility": unexplained_infertility,
        "low_ovarian_reserve": low_ovarian_reserve,
        "amh_available": amh_available,
        "amh_value": amh_value if amh_available else None,
        "success_rate_1_cycle": round(cumulative_probs[0], 2) if len(cumulative_probs) > 0 else None,
        "success_rate_2_cycles": round(cumulative_probs[1], 2) if len(cumulative_probs) > 1 else None,
        "success_rate_3_cycles": round(cumulative_probs[2], 2) if len(cumulative_probs) > 2 else None,
        "raw_response": data,
    }


# ==================== FastMCP Tools ====================

@mcp.tool(
    name="calculate_ivf_success_rates",
    description="Calculate the probability of successful IVF outcome (live birth) using the SART IVF calculator. Returns success rates for 1, 2, and 3 complete IVF cycles based on patient characteristics."
)
def calculate_ivf_success_rates(
    age: int = Field(description="Patient age in years (must be 18-45)", ge=18, le=45),
    height_cm: Optional[float] = Field(None, description="Height in centimeters (120-220). Use this OR height_ft/height_in, not both.", ge=120, le=220),
    weight_kg: Optional[float] = Field(None, description="Weight in kilograms (30-160). Use this OR weight_lbs, not both.", ge=30, le=160),
    height_ft: Optional[int] = Field(None, description="Height in feet (4-7). Use with height_in if not using height_cm.", ge=4, le=7),
    height_in: Optional[int] = Field(None, description="Height in inches (0-11). Use with height_ft if not using height_cm.", ge=0, le=11),
    weight_lbs: Optional[float] = Field(None, description="Weight in pounds (70-350). Use if not using weight_kg.", ge=70, le=350),
    previous_full_term: bool = Field(False, description="Has the patient ever had a baby born at full term (>37 weeks)?"),
    male_factor: bool = Field(False, description="Does the partner have a problem with their sperm?"),
    polycystic: bool = Field(False, description="Does the patient have polycystic ovaries or PCOS?"),
    uterine_problems: bool = Field(False, description="Does the patient have uterine problems (septum, myoma, intrauterine adhesions, congenital anomalies)?"),
    unexplained_infertility: bool = Field(False, description="Has the patient been diagnosed with unexplained infertility?"),
    low_ovarian_reserve: bool = Field(False, description="Has the patient been diagnosed with low ovarian reserve?"),
    amh_available: bool = Field(False, description="Is the patient's AMH (Anti-Müllerian Hormone) level known?"),
    amh_value: float = Field(0.0, description="AMH level in ng/ml (only if amh_available is true)")
) -> str:
    # Calculate IVF success rates using the original function
    result = calculate_ivf_success(
        age=age,
        height_cm=height_cm,
        weight_kg=weight_kg,
        height_ft=height_ft,
        height_in=height_in,
        weight_lbs=weight_lbs,
        previous_full_term=previous_full_term,
        male_factor=male_factor,
        polycystic=polycystic,
        uterine_problems=uterine_problems,
        unexplained_infertility=unexplained_infertility,
        low_ovarian_reserve=low_ovarian_reserve,
        amh_available=amh_available,
        amh_value=amh_value,
    )

    # Format the response
    response = "# SART IVF Success Rate Calculator Results\n\n"
    response += "## Patient Information\n"
    response += f"- **Age:** {result['age']} years\n"

    if result.get('height_cm'):
        response += f"- **Height:** {result['height_cm']} cm\n"
    elif result.get('height_ft'):
        response += f"- **Height:** {result['height_ft']}'{result['height_in']}\"\n"

    if result.get('weight_kg'):
        response += f"- **Weight:** {result['weight_kg']} kg\n"
    elif result.get('weight_lbs'):
        response += f"- **Weight:** {result['weight_lbs']} lbs\n"

    response += "\n## Clinical Factors\n"
    response += f"- **Previous full-term pregnancy:** {'Yes' if result['previous_full_term'] else 'No'}\n"
    response += f"- **Male factor infertility:** {'Yes' if result['male_factor'] else 'No'}\n"
    response += f"- **PCOS:** {'Yes' if result['polycystic'] else 'No'}\n"
    response += f"- **Uterine problems:** {'Yes' if result['uterine_problems'] else 'No'}\n"
    response += f"- **Unexplained infertility:** {'Yes' if result['unexplained_infertility'] else 'No'}\n"
    response += f"- **Low ovarian reserve:** {'Yes' if result['low_ovarian_reserve'] else 'No'}\n"

    if result['amh_available'] and result['amh_value'] is not None:
        response += f"- **AMH level:** {result['amh_value']} ng/ml\n"

    response += "\n## Success Rates (Probability of Live Birth)\n\n"

    if result['success_rate_1_cycle'] is not None:
        response += f"- **After 1 complete IVF cycle:** {result['success_rate_1_cycle']}%\n"
    if result['success_rate_2_cycles'] is not None:
        response += f"- **After 2 complete IVF cycles:** {result['success_rate_2_cycles']}%\n"
    if result['success_rate_3_cycles'] is not None:
        response += f"- **After 3 complete IVF cycles:** {result['success_rate_3_cycles']}%\n"

    response += "\n---\n"
    response += "*Note: A complete cycle includes all embryo transfers using eggs from one ovarian stimulation cycle. These estimates are based on SART data and individual results may vary.*\n"

    return response


# ==================== Resources ====================

@mcp.resource("sart://calculator", mime_type="application/json")
def sart_calculator_info() -> dict:
    """Information about the SART IVF calculator."""
    return {
        "calculator": "SART IVF Success Rate Calculator",
        "source": "Society for Assisted Reproductive Technology",
        "age_range": "18-45 years",
        "factors_included": [
            "patient_age", "height_weight", "previous_pregnancy", "male_factor", 
            "PCOS", "uterine_problems", "unexplained_infertility", "ovarian_reserve", "AMH_level"
        ],
        "cycles_calculated": [1, 2, 3],
        "outcome_measured": "Live birth probability",
        "data_source": "SART registry data"
    }


# Run the server
if __name__ == "__main__":
    mcp.run()
