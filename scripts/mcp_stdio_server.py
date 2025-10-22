#!/usr/bin/env python3
"""
Women's Health MCP Server - Stdio Implementation
Provides clinical calculator tools via Model Context Protocol over stdio
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from core.clinical_calculators import ClinicalCalculators
from core.research_database_integration import ResearchDatabaseIntegration
from core.fhir_integration import ReproductiveHealthFHIR
import json


# Initialize calculators
calc = ClinicalCalculators()
research = ResearchDatabaseIntegration()
fhir = ReproductiveHealthFHIR()

# Create MCP server
app = Server("women-health-mcp")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available clinical calculator tools."""
    return [
        Tool(
            name="assess-ovarian-reserve",
            description="Calculate ovarian reserve using ASRM criteria. Requires age and AMH level.",
            inputSchema={
                "type": "object",
                "properties": {
                    "age": {
                        "type": "integer",
                        "description": "Patient age in years",
                        "minimum": 18,
                        "maximum": 55
                    },
                    "amh": {
                        "type": "number",
                        "description": "Anti-Müllerian Hormone level in ng/mL",
                        "minimum": 0
                    },
                    "fsh": {
                        "type": "number",
                        "description": "Optional FSH level in mIU/mL",
                        "minimum": 0
                    }
                },
                "required": ["age", "amh"]
            }
        ),
        Tool(
            name="predict-ivf-success",
            description="Predict IVF success rates using SART data. Requires age, AMH, and cycle type.",
            inputSchema={
                "type": "object",
                "properties": {
                    "age": {
                        "type": "integer",
                        "description": "Patient age in years",
                        "minimum": 18,
                        "maximum": 55
                    },
                    "amh": {
                        "type": "number",
                        "description": "Anti-Müllerian Hormone level in ng/mL",
                        "minimum": 0
                    },
                    "cycle_type": {
                        "type": "string",
                        "description": "Type of IVF cycle",
                        "enum": ["fresh", "frozen"]
                    },
                    "prior_pregnancies": {
                        "type": "integer",
                        "description": "Number of prior pregnancies",
                        "minimum": 0
                    }
                },
                "required": ["age", "amh", "cycle_type"]
            }
        ),
        Tool(
            name="predict-menopause",
            description="Predict menopause timing using SWAN algorithms. Requires age and AMH.",
            inputSchema={
                "type": "object",
                "properties": {
                    "age": {
                        "type": "integer",
                        "description": "Patient age in years",
                        "minimum": 18,
                        "maximum": 55
                    },
                    "amh": {
                        "type": "number",
                        "description": "Anti-Müllerian Hormone level in ng/mL",
                        "minimum": 0
                    },
                    "smoking": {
                        "type": "boolean",
                        "description": "Whether patient smokes"
                    },
                    "bmi": {
                        "type": "number",
                        "description": "Body Mass Index",
                        "minimum": 10,
                        "maximum": 60
                    }
                },
                "required": ["age", "amh"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Execute a clinical calculator tool."""

    try:
        if name == "assess-ovarian-reserve":
            result = calc.assess_ovarian_reserve(
                age=arguments["age"],
                amh=arguments["amh"],
                fsh=arguments.get("fsh"),
                afc=arguments.get("afc")
            )
            return [TextContent(
                type="text",
                text=json.dumps({
                    "tool": "assess-ovarian-reserve",
                    "result": result
                }, indent=2)
            )]

        elif name == "predict-ivf-success":
            result = calc.predict_ivf_success(
                age=arguments["age"],
                amh=arguments["amh"],
                cycle_type=arguments.get("cycle_type", "fresh"),
                prior_pregnancies=arguments.get("prior_pregnancies", 0),
                diagnosis=arguments.get("diagnosis")
            )
            return [TextContent(
                type="text",
                text=json.dumps({
                    "tool": "predict-ivf-success",
                    "result": result
                }, indent=2)
            )]

        elif name == "predict-menopause":
            result = calc.predict_menopause_timing(
                age=arguments["age"],
                amh=arguments["amh"],
                smoking=arguments.get("smoking", False),
                bmi=arguments.get("bmi"),
                ethnicity=arguments.get("ethnicity"),
                parity=arguments.get("parity", 0)
            )
            return [TextContent(
                type="text",
                text=json.dumps({
                    "tool": "predict-menopause",
                    "result": result
                }, indent=2)
            )]

        else:
            return [TextContent(
                type="text",
                text=json.dumps({"error": f"Unknown tool: {name}"})
            )]

    except Exception as e:
        return [TextContent(
            type="text",
            text=json.dumps({"error": str(e)})
        )]


async def main():
    """Run the MCP server over stdio."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
