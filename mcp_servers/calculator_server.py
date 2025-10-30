#!/usr/bin/env python3
"""
Women's Health Calculator Server - FastMCP Implementation
Provides clinical calculation tools for reproductive medicine:
- SART IVF success predictions
- Clinical recommendations based on SART data
"""

import asyncio
import sys
from pathlib import Path
from typing import Optional
import json

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastmcp import FastMCP

# Import SART IVF server module
sys.path.insert(0, str(Path(__file__).parent.parent / "servers"))
from servers import sart_ivf_server

# Create FastMCP server
mcp = FastMCP("women-health-calculator")


@mcp.tool()
async def calculate_ivf_success(
    age: int,
    height_cm: Optional[float] = None,
    weight_kg: Optional[float] = None,
    height_ft: Optional[int] = None,
    height_in: Optional[int] = None,
    weight_lbs: Optional[float] = None,
    previous_full_term: bool = False,
    male_factor: bool = False,
    polycystic: bool = False,
    uterine_problems: bool = False,
    unexplained_infertility: bool = False,
    low_ovarian_reserve: bool = False,
    amh_available: bool = False,
    amh_value: float = 0.0
) -> str:
    """
    Calculate IVF success rates using SART (Society for Assisted Reproductive Technology) data.
    
    Predicts live birth probability for 1, 2, and 3 complete IVF cycles based on patient
    demographics, medical history, and treatment parameters. Uses validated SART prediction
    model from Aberdeen University.
    
    Args:
        age: Patient age in years (18-45)
        height_cm: Height in centimeters (120-220). Use this OR height_ft/height_in
        weight_kg: Weight in kilograms (30-160). Use this OR weight_lbs
        height_ft: Height in feet (4-7). Use with height_in if not using height_cm
        height_in: Height in inches (0-11). Use with height_ft if not using height_cm
        weight_lbs: Weight in pounds (70-350). Use if not using weight_kg
        previous_full_term: Has patient had a previous full-term pregnancy (>37 weeks)?
        male_factor: Does partner have sperm problems?
        polycystic: Does patient have polycystic ovaries or PCOS?
        uterine_problems: Does patient have uterine problems (septum, myoma, adhesions, anomalies)?
        unexplained_infertility: Has patient been diagnosed with unexplained infertility?
        low_ovarian_reserve: Has patient been diagnosed with low ovarian reserve?
        amh_available: Is AMH (Anti-Müllerian Hormone) level known?
        amh_value: AMH level in ng/ml (only if amh_available is true)
    """
    # Validate age range
    if age < 18 or age > 45:
        return json.dumps({
            "error": "Age must be between 18 and 45 years",
            "provided_age": age
        }, indent=2)

    # Call SART server calculation
    result = await sart_ivf_server.calculate_ivf_success(
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
        amh_value=amh_value
    )

    return json.dumps(result, indent=2)


@mcp.tool()
async def predict_ivf_success(
    age: int,
    amh: float,
    height_cm: Optional[float] = None,
    weight_kg: Optional[float] = None,
    height_ft: Optional[int] = None,
    height_in: Optional[int] = None,
    weight_lbs: Optional[float] = None,
    prior_pregnancies: int = 0,
    male_factor: bool = False,
    polycystic: bool = False,
    uterine_problems: bool = False,
    unexplained_infertility: bool = False,
    low_ovarian_reserve: bool = False,
    bmi: Optional[float] = None
) -> str:
    """
    Predict IVF success rates using SART Calculator API with enhanced formatting.
    
    This is an enhanced wrapper that provides formatted results with clinical
    recommendations. Calculates live birth probability for 1, 2, and 3 complete
    IVF cycles based on patient characteristics.
    
    Args:
        age: Patient age in years (18-45)
        amh: Anti-Müllerian Hormone level in ng/mL
        height_cm: Height in centimeters (120-220). Use this OR height_ft/height_in
        weight_kg: Weight in kilograms (30-160). Use this OR weight_lbs
        height_ft: Height in feet (4-7). Use with height_in if not using height_cm
        height_in: Height in inches (0-11). Use with height_ft if not using height_cm
        weight_lbs: Weight in pounds (70-350). Use if not using weight_kg
        prior_pregnancies: Number of prior full-term pregnancies (>37 weeks)
        male_factor: Does partner have sperm problems?
        polycystic: Does patient have PCOS?
        uterine_problems: Does patient have uterine problems?
        unexplained_infertility: Diagnosed with unexplained infertility?
        low_ovarian_reserve: Diagnosed with low ovarian reserve?
        bmi: Body Mass Index (optional, for internal calculations)
    """
    # Build parameters for SART calculator
    calc_params = {
        "age": age,
        "amh_available": True,
        "amh_value": amh,
        "previous_full_term": prior_pregnancies > 0,
        "male_factor": male_factor,
        "polycystic": polycystic,
        "uterine_problems": uterine_problems,
        "unexplained_infertility": unexplained_infertility,
        "low_ovarian_reserve": low_ovarian_reserve,
    }

    # Add height/weight if provided
    if height_cm:
        calc_params["height_cm"] = height_cm
    if weight_kg:
        calc_params["weight_kg"] = weight_kg
    if height_ft:
        calc_params["height_ft"] = height_ft
    if height_in:
        calc_params["height_in"] = height_in
    if weight_lbs:
        calc_params["weight_lbs"] = weight_lbs

    # Calculate BMI-based weight if only BMI provided
    if bmi and not weight_kg and not weight_lbs:
        height_m = 1.65  # Assume average height
        calc_params["weight_kg"] = bmi * (height_m ** 2)

    result = await sart_ivf_server.calculate_ivf_success(**calc_params)

    # Format response with enhanced presentation
    response = {
        "tool": "predict-ivf-success",
        "patient_info": {
            "age": result["age"],
            "height_cm": result["height_cm"],
            "weight_kg": result["weight_kg"],
            "height_ft": result["height_ft"],
            "height_in": result["height_in"],
            "weight_lbs": result["weight_lbs"],
        },
        "clinical_factors": {
            "previous_full_term": result["previous_full_term"],
            "male_factor": result["male_factor"],
            "polycystic": result["polycystic"],
            "uterine_problems": result["uterine_problems"],
            "unexplained_infertility": result["unexplained_infertility"],
            "low_ovarian_reserve": result["low_ovarian_reserve"],
            "amh_value": result["amh_value"],
        },
        "success_rates": {
            "1_cycle": result["success_rate_1_cycle"],
            "2_cycles": result["success_rate_2_cycles"],
            "3_cycles": result["success_rate_3_cycles"],
        },
        "recommendations": sart_ivf_server.generate_recommendations(result),
        "data_source": "SART IVF Calculator API (University of Aberdeen)",
    }

    return json.dumps(response, indent=2)


@mcp.tool()
async def generate_recommendations(calculation_result: dict) -> str:
    """
    Generate personalized IVF treatment recommendations based on SART success predictions.
    
    Provides clinical guidance on treatment optimization, timing, and alternatives
    based on calculated success rates and patient factors.
    
    Args:
        calculation_result: Dictionary result from calculate_ivf_success
    """
    recommendations = sart_ivf_server.generate_recommendations(calculation_result)
    
    formatted_response = {
        "clinical_recommendations": recommendations,
        "recommendation_count": len(recommendations),
        "based_on": {
            "success_rate_1_cycle": calculation_result.get("success_rate_1_cycle"),
            "age": calculation_result.get("age"),
            "clinical_factors": {
                "amh_available": calculation_result.get("amh_available"),
                "amh_value": calculation_result.get("amh_value"),
                "polycystic": calculation_result.get("polycystic"),
                "low_ovarian_reserve": calculation_result.get("low_ovarian_reserve")
            }
        },
        "important_note": "These recommendations are for informational purposes. Always consult with a qualified fertility specialist for personalized medical advice."
    }
    
    return json.dumps(formatted_response, indent=2)


@mcp.tool()
async def get_sart_calculator_info() -> str:
    """
    Get information about the SART IVF Calculator and its methodology.
    
    Provides details about the calculator's data source, methodology,
    and appropriate use cases for clinical decision support.
    """
    info = {
        "calculator_name": "SART IVF Success Rate Calculator",
        "institution": "University of Aberdeen",
        "data_source": "Society for Assisted Reproductive Technology (SART)",
        "url": "https://w3.abdn.ac.uk/clsm/SARTIVF/tool/ivf1",
        "methodology": {
            "description": "Statistical model predicting live birth probability based on patient characteristics",
            "data_basis": "Large dataset of IVF cycles from SART registry",
            "validation": "Validated prediction model using logistic regression",
            "outcome_measure": "Live birth rate per complete cycle"
        },
        "input_parameters": [
            "Patient age (18-45 years)",
            "Height and weight (metric or imperial)",
            "Previous full-term pregnancies",
            "Male factor infertility",
            "Polycystic ovary syndrome (PCOS)",
            "Uterine problems",
            "Unexplained infertility",
            "Low ovarian reserve",
            "AMH level (if available)"
        ],
        "output_metrics": [
            "Success rate for 1 complete IVF cycle",
            "Cumulative success rate for 2 cycles",
            "Cumulative success rate for 3 cycles"
        ],
        "clinical_use": [
            "Patient counseling about IVF success expectations",
            "Treatment planning and cycle preparation",
            "Informed consent discussions",
            "Comparison of treatment options"
        ],
        "limitations": [
            "Population-based averages, individual results may vary",
            "Based on historical data, may not reflect latest techniques",
            "Does not account for all individual medical factors",
            "Success rates may vary by clinic and protocol"
        ],
        "disclaimer": "For informational purposes only. Clinical decisions should always be made in consultation with qualified fertility specialists."
    }
    
    return json.dumps(info, indent=2)


@mcp.tool()
async def compare_success_rates(scenarios: list[dict]) -> str:
    """
    Compare IVF success rates across multiple patient scenarios.
    
    Useful for understanding how different factors affect success rates
    and for patient counseling about optimization strategies.
    
    Args:
        scenarios: List of dictionaries, each containing patient parameters
                  for calculate_ivf_success function
    """
    if not scenarios:
        return json.dumps({"error": "No scenarios provided for comparison"}, indent=2)
    
    if len(scenarios) > 5:
        return json.dumps({"error": "Maximum 5 scenarios allowed for comparison"}, indent=2)
    
    results = []
    
    for i, scenario in enumerate(scenarios):
        try:
            # Calculate success rates for this scenario
            result = await sart_ivf_server.calculate_ivf_success(**scenario)
            
            # Create summary for comparison
            scenario_summary = {
                "scenario": i + 1,
                "input_parameters": {
                    "age": scenario.get("age"),
                    "amh_value": scenario.get("amh_value") if scenario.get("amh_available") else "Not provided",
                    "previous_full_term": scenario.get("previous_full_term", False),
                    "clinical_factors": [
                        factor for factor in ["male_factor", "polycystic", "uterine_problems", 
                                            "unexplained_infertility", "low_ovarian_reserve"]
                        if scenario.get(factor, False)
                    ]
                },
                "success_rates": {
                    "1_cycle": result["success_rate_1_cycle"],
                    "2_cycles": result["success_rate_2_cycles"],
                    "3_cycles": result["success_rate_3_cycles"]
                },
                "recommendations_count": len(sart_ivf_server.generate_recommendations(result))
            }
            
            results.append(scenario_summary)
            
        except Exception as e:
            results.append({
                "scenario": i + 1,
                "error": str(e)
            })
    
    comparison = {
        "scenario_comparison": results,
        "summary": {
            "scenarios_compared": len(results),
            "highest_1_cycle_rate": max([r.get("success_rates", {}).get("1_cycle", 0) 
                                        for r in results if "success_rates" in r], default=0),
            "lowest_1_cycle_rate": min([r.get("success_rates", {}).get("1_cycle", 100) 
                                       for r in results if "success_rates" in r], default=0)
        },
        "interpretation": "Compare success rates to understand impact of different patient factors on IVF outcomes"
    }
    
    return json.dumps(comparison, indent=2)


# Run the server
if __name__ == "__main__":
    mcp.run()