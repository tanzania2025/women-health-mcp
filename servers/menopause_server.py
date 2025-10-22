#!/usr/bin/env python
"""
MCP Server for Menopause Age Calculator

Based on the calculator at https://reverse.health/calculator/menopause-age-calculator
Estimates menopause age based on genetics, lifestyle, and health factors.
"""

import asyncio
import json
from typing import Any
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio


# Create server instance
server = Server("menopause-calculator")


def calculate_menopause_age(
    current_age: int,
    mothers_menopause_age: int | None = None,
    smoking_status: str = "never",
    bmi: float | None = None,
    exercise_frequency: str = "moderate",
    stress_level: str = "moderate",
    cycle_changes: bool = False
) -> dict[str, Any]:
    """
    Calculate estimated menopause age based on various factors.

    Args:
        current_age: Current age of the person
        mothers_menopause_age: Age at which mother reached menopause (None if unknown)
        smoking_status: "never", "former", "current"
        bmi: Body Mass Index (None if unknown)
        exercise_frequency: "low", "moderate", "high"
        stress_level: "low", "moderate", "high"
        cycle_changes: Whether experiencing cycle changes

    Returns:
        Dictionary with estimated age and contributing factors
    """

    # Baseline age (average menopause age)
    baseline_age = 51.0
    estimated_age = baseline_age
    adjustments = []

    # Genetic factor (strongest predictor)
    if mothers_menopause_age is not None:
        # Women often mirror maternal patterns within a few years
        genetic_adjustment = (mothers_menopause_age - baseline_age) * 0.7
        estimated_age += genetic_adjustment
        adjustments.append({
            "factor": "Genetics (mother's age)",
            "adjustment": round(genetic_adjustment, 1),
            "impact": "high"
        })

    # Smoking impact (accelerates menopause by up to 2 years)
    if smoking_status == "current":
        smoking_adjustment = -2.0
        estimated_age += smoking_adjustment
        adjustments.append({
            "factor": "Current smoking",
            "adjustment": smoking_adjustment,
            "impact": "high"
        })
    elif smoking_status == "former":
        smoking_adjustment = -0.5
        estimated_age += smoking_adjustment
        adjustments.append({
            "factor": "Former smoking",
            "adjustment": smoking_adjustment,
            "impact": "low"
        })

    # BMI factor (very low or very high BMI can affect timing)
    if bmi is not None:
        if bmi < 18.5:
            # Underweight may lead to earlier menopause
            bmi_adjustment = -1.0
            estimated_age += bmi_adjustment
            adjustments.append({
                "factor": "Low BMI (underweight)",
                "adjustment": bmi_adjustment,
                "impact": "moderate"
            })
        elif bmi > 30:
            # Obesity may delay menopause slightly
            bmi_adjustment = 0.5
            estimated_age += bmi_adjustment
            adjustments.append({
                "factor": "High BMI (obesity)",
                "adjustment": bmi_adjustment,
                "impact": "low"
            })

    # Exercise factor
    if exercise_frequency == "high":
        exercise_adjustment = 0.5
        estimated_age += exercise_adjustment
        adjustments.append({
            "factor": "High exercise frequency",
            "adjustment": exercise_adjustment,
            "impact": "low"
        })
    elif exercise_frequency == "low":
        exercise_adjustment = -0.3
        estimated_age += exercise_adjustment
        adjustments.append({
            "factor": "Low exercise frequency",
            "adjustment": exercise_adjustment,
            "impact": "low"
        })

    # Stress factor
    if stress_level == "high":
        stress_adjustment = -0.5
        estimated_age += stress_adjustment
        adjustments.append({
            "factor": "High stress levels",
            "adjustment": stress_adjustment,
            "impact": "low"
        })

    # Cycle changes (if experiencing changes, likely in perimenopause)
    if cycle_changes and current_age >= 40:
        cycle_note = "Currently experiencing cycle changes - likely in perimenopause transition"
    else:
        cycle_note = None

    # Round to 1 decimal place
    estimated_age = round(estimated_age, 1)

    # Ensure age is realistic (between 40-60)
    if estimated_age < 40:
        estimated_age = 40.0
    elif estimated_age > 60:
        estimated_age = 60.0

    # Years until estimated menopause
    years_until = max(0, estimated_age - current_age)

    return {
        "estimated_menopause_age": estimated_age,
        "years_until_menopause": round(years_until, 1),
        "current_age": current_age,
        "baseline_age": baseline_age,
        "adjustments": adjustments,
        "cycle_changes_note": cycle_note,
        "disclaimer": "This is an estimate based on statistical averages. Individual experiences vary significantly. Consult a healthcare provider for personalized guidance."
    }


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available tools."""
    return [
        types.Tool(
            name="calculate_menopause_age",
            description="""Calculate estimated menopause age based on genetics, lifestyle, and health factors.

Based on research showing:
- Typical menopause age: 51 years
- Genetics (mother's age) is the strongest predictor
- Smoking accelerates menopause by up to 2 years
- BMI, exercise, and stress also influence timing

This calculator provides an educational estimate. Always consult healthcare professionals for medical advice.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "current_age": {
                        "type": "integer",
                        "description": "Current age in years (typically 30-60)",
                        "minimum": 30,
                        "maximum": 65
                    },
                    "mothers_menopause_age": {
                        "type": "integer",
                        "description": "Age when mother reached menopause (optional, but strongest predictor)",
                        "minimum": 35,
                        "maximum": 65
                    },
                    "smoking_status": {
                        "type": "string",
                        "enum": ["never", "former", "current"],
                        "description": "Smoking history",
                        "default": "never"
                    },
                    "bmi": {
                        "type": "number",
                        "description": "Body Mass Index (optional)",
                        "minimum": 15,
                        "maximum": 50
                    },
                    "exercise_frequency": {
                        "type": "string",
                        "enum": ["low", "moderate", "high"],
                        "description": "Exercise frequency",
                        "default": "moderate"
                    },
                    "stress_level": {
                        "type": "string",
                        "enum": ["low", "moderate", "high"],
                        "description": "Overall stress level",
                        "default": "moderate"
                    },
                    "cycle_changes": {
                        "type": "boolean",
                        "description": "Currently experiencing menstrual cycle changes",
                        "default": False
                    }
                },
                "required": ["current_age"]
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool execution requests."""

    if name != "calculate_menopause_age":
        raise ValueError(f"Unknown tool: {name}")

    if not arguments:
        raise ValueError("Missing arguments")

    # Extract parameters
    current_age = arguments.get("current_age")
    mothers_age = arguments.get("mothers_menopause_age")
    smoking = arguments.get("smoking_status", "never")
    bmi = arguments.get("bmi")
    exercise = arguments.get("exercise_frequency", "moderate")
    stress = arguments.get("stress_level", "moderate")
    cycle_changes = arguments.get("cycle_changes", False)

    # Calculate menopause age
    result = calculate_menopause_age(
        current_age=current_age,
        mothers_menopause_age=mothers_age,
        smoking_status=smoking,
        bmi=bmi,
        exercise_frequency=exercise,
        stress_level=stress,
        cycle_changes=cycle_changes
    )

    # Format output
    output = f"""Menopause Age Estimate

📊 Estimated Menopause Age: {result['estimated_menopause_age']} years
⏳ Years Until Estimated Menopause: {result['years_until_menopause']} years
👤 Your Current Age: {result['current_age']} years
📈 Statistical Baseline: {result['baseline_age']} years

"""

    if result['adjustments']:
        output += "🔍 Contributing Factors:\n"
        for adj in result['adjustments']:
            sign = "+" if adj['adjustment'] > 0 else ""
            output += f"  • {adj['factor']}: {sign}{adj['adjustment']} years ({adj['impact']} impact)\n"
        output += "\n"

    if result['cycle_changes_note']:
        output += f"⚠️ {result['cycle_changes_note']}\n\n"

    output += f"ℹ️ {result['disclaimer']}\n\n"
    output += """📚 Key Information:
• Menopause typically occurs between ages 45-58
• 80% of women experience hot flashes
• Perimenopause often begins years before final period
• Genetics (mother's age) is the strongest predictor
• Smoking can advance menopause by up to 2 years
• Healthy weight and exercise may provide some protection

🏥 When to Consult a Healthcare Provider:
• Heavy bleeding or periods lasting >7 days
• Bleeding between cycles
• Severe mood changes or persistent insomnia
• Hot flashes occurring multiple times daily
• Planning for bone health and fertility considerations

Source: https://reverse.health/calculator/menopause-age-calculator
"""

    return [types.TextContent(type="text", text=output)]


async def main():
    """Main entry point for the server."""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="menopause-calculator",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
