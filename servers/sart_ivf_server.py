#!/usr/bin/env python3
"""
SART IVF Calculator MCP Server

This MCP server provides tools to calculate IVF success rates using the
SART (Society for Assisted Reproductive Technology) IVF calculator.
"""

import asyncio
from typing import Any
import httpx
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio

# SART calculator URL
SART_URL = "https://w3.abdn.ac.uk/clsm/SARTIVF/tool/ivf1"

# Create server instance
server = Server("sart-ivf-server")


async def calculate_ivf_success(
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


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    List available tools for SART IVF calculator.
    """
    return [
        types.Tool(
            name="calculate_ivf_success",
            description="Calculate the probability of successful IVF outcome (live birth) using the SART IVF calculator. Returns success rates for 1, 2, and 3 complete IVF cycles based on patient characteristics.",
            inputSchema={
                "type": "object",
                "properties": {
                    "age": {
                        "type": "number",
                        "description": "Patient age in years (must be 18-45)",
                        "minimum": 18,
                        "maximum": 45,
                    },
                    "height_cm": {
                        "type": "number",
                        "description": "Height in centimeters (120-220). Use this OR height_ft/height_in, not both.",
                    },
                    "weight_kg": {
                        "type": "number",
                        "description": "Weight in kilograms (30-160). Use this OR weight_lbs, not both.",
                    },
                    "height_ft": {
                        "type": "number",
                        "description": "Height in feet (4-7). Use with height_in if not using height_cm.",
                    },
                    "height_in": {
                        "type": "number",
                        "description": "Height in inches (0-11). Use with height_ft if not using height_cm.",
                    },
                    "weight_lbs": {
                        "type": "number",
                        "description": "Weight in pounds (70-350). Use if not using weight_kg.",
                    },
                    "previous_full_term": {
                        "type": "boolean",
                        "description": "Has the patient ever had a baby born at full term (>37 weeks)?",
                        "default": False,
                    },
                    "male_factor": {
                        "type": "boolean",
                        "description": "Does the partner have a problem with their sperm?",
                        "default": False,
                    },
                    "polycystic": {
                        "type": "boolean",
                        "description": "Does the patient have polycystic ovaries or PCOS?",
                        "default": False,
                    },
                    "uterine_problems": {
                        "type": "boolean",
                        "description": "Does the patient have uterine problems (septum, myoma, intrauterine adhesions, congenital anomalies)?",
                        "default": False,
                    },
                    "unexplained_infertility": {
                        "type": "boolean",
                        "description": "Has the patient been diagnosed with unexplained infertility?",
                        "default": False,
                    },
                    "low_ovarian_reserve": {
                        "type": "boolean",
                        "description": "Has the patient been diagnosed with low ovarian reserve?",
                        "default": False,
                    },
                    "amh_available": {
                        "type": "boolean",
                        "description": "Is the patient's AMH (Anti-Müllerian Hormone) level known?",
                        "default": False,
                    },
                    "amh_value": {
                        "type": "number",
                        "description": "AMH level in ng/ml (only if amh_available is true)",
                        "default": 0,
                    },
                },
                "required": ["age"],
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict[str, Any] | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    Handle tool execution requests.
    """
    if not arguments:
        raise ValueError("Missing arguments")

    if name == "calculate_ivf_success":
        age = arguments.get("age")
        if not age:
            raise ValueError("Missing required argument: age")

        if age < 18 or age > 45:
            raise ValueError("Age must be between 18 and 45")

        # Calculate IVF success rates
        result = await calculate_ivf_success(
            age=int(age),
            height_cm=arguments.get("height_cm"),
            weight_kg=arguments.get("weight_kg"),
            height_ft=arguments.get("height_ft"),
            height_in=arguments.get("height_in"),
            weight_lbs=arguments.get("weight_lbs"),
            previous_full_term=arguments.get("previous_full_term", False),
            male_factor=arguments.get("male_factor", False),
            polycystic=arguments.get("polycystic", False),
            uterine_problems=arguments.get("uterine_problems", False),
            unexplained_infertility=arguments.get("unexplained_infertility", False),
            low_ovarian_reserve=arguments.get("low_ovarian_reserve", False),
            amh_available=arguments.get("amh_available", False),
            amh_value=arguments.get("amh_value", 0.0),
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

        return [types.TextContent(type="text", text=response)]

    else:
        raise ValueError(f"Unknown tool: {name}")


async def main():
    """Run the SART IVF Calculator MCP server."""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="sart-ivf-server",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
