"""
Model Context Protocol (MCP) Implementation
Following the official MCP specification for AI agent context exchange
"""

import json
import asyncio
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
from datetime import datetime


class MCPMessageType(Enum):
    """MCP message types as per specification."""
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"


class MCPMethod(Enum):
    """Standard MCP methods."""
    INITIALIZE = "initialize"
    LIST_RESOURCES = "resources/list"
    READ_RESOURCE = "resources/read"
    LIST_PROMPTS = "prompts/list"
    GET_PROMPT = "prompts/get"
    LIST_TOOLS = "tools/list"
    CALL_TOOL = "tools/call"
    COMPLETE = "completion/complete"
    SET_LOG_LEVEL = "logging/setLevel"


@dataclass
class MCPMessage:
    """Base MCP message structure."""
    jsonrpc: str = "2.0"
    id: Optional[Union[str, int]] = None
    method: Optional[str] = None
    params: Optional[Dict[str, Any]] = None
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None


@dataclass
class MCPResource:
    """MCP Resource definition."""
    uri: str
    name: str
    description: Optional[str] = None
    mimeType: Optional[str] = None


@dataclass
class MCPTool:
    """MCP Tool definition."""
    name: str
    description: str
    inputSchema: Dict[str, Any]


@dataclass
class MCPPrompt:
    """MCP Prompt template definition."""
    name: str
    description: str
    arguments: Optional[List[Dict[str, Any]]] = None


class MCPServer:
    """
    Model Context Protocol Server for Women's Health AI.
    Provides standardized interface for AI agents to access reproductive health data.
    """
    
    def __init__(self, name: str = "women-health-mcp"):
        self.name = name
        self.version = "1.0.0"
        self.capabilities = {
            "resources": {"subscribe": True, "listChanged": True},
            "tools": {"subscribe": True, "listChanged": True},
            "prompts": {"subscribe": True, "listChanged": True},
            "logging": {},
            "completion": {"subscribe": True}
        }
        
        # Initialize resources, tools, and prompts
        self._resources = {}
        self._tools = {}
        self._prompts = {}
        self._setup_default_components()
    
    def _setup_default_components(self):
        """Setup default MCP resources, tools, and prompts for women's health."""
        
        # Resources - Data sources available to AI agents
        self._resources = {
            "patient-data": MCPResource(
                uri="mcp://women-health/patient-data",
                name="Patient Data",
                description="Standardized patient reproductive health data",
                mimeType="application/json"
            ),
            "clinical-calculators": MCPResource(
                uri="mcp://women-health/clinical-calculators",
                name="Clinical Calculators",
                description="ASRM/ESHRE validated reproductive health calculators",
                mimeType="application/json"
            ),
            "research-data": MCPResource(
                uri="mcp://women-health/research-data",
                name="Research Databases",
                description="Real-time access to SWAN, SART, and PubMed data",
                mimeType="application/json"
            ),
            "fhir-resources": MCPResource(
                uri="mcp://women-health/fhir-resources",
                name="FHIR Resources",
                description="FHIR R4 compliant reproductive health resources",
                mimeType="application/fhir+json"
            )
        }
        
        # Tools - Actions AI agents can perform
        self._tools = {
            "assess-ovarian-reserve": MCPTool(
                name="assess-ovarian-reserve",
                description="Calculate ovarian reserve using ASRM criteria",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "age": {"type": "integer", "minimum": 18, "maximum": 55},
                        "amh": {"type": "number", "minimum": 0},
                        "fsh": {"type": "number", "minimum": 0, "description": "Optional FSH level"},
                        "afc": {"type": "integer", "minimum": 0, "description": "Optional antral follicle count"}
                    },
                    "required": ["age", "amh"]
                }
            ),
            "predict-ivf-success": MCPTool(
                name="predict-ivf-success",
                description="Predict IVF success rates using SART data",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "age": {"type": "integer", "minimum": 18, "maximum": 55},
                        "amh": {"type": "number", "minimum": 0},
                        "cycle_type": {"type": "string", "enum": ["fresh", "frozen"]},
                        "prior_pregnancies": {"type": "integer", "minimum": 0},
                        "diagnosis": {"type": "string", "description": "Primary infertility diagnosis"}
                    },
                    "required": ["age", "amh", "cycle_type"]
                }
            ),
            "predict-menopause": MCPTool(
                name="predict-menopause",
                description="Predict menopause timing using SWAN algorithms",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "age": {"type": "integer", "minimum": 18, "maximum": 55},
                        "amh": {"type": "number", "minimum": 0},
                        "smoking": {"type": "boolean"},
                        "bmi": {"type": "number", "minimum": 10, "maximum": 60},
                        "ethnicity": {"type": "string"},
                        "parity": {"type": "integer", "minimum": 0}
                    },
                    "required": ["age", "amh"]
                }
            ),
            "query-research-database": MCPTool(
                name="query-research-database",
                description="Query SWAN, SART, or PubMed databases",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "database": {"type": "string", "enum": ["swan", "sart", "pubmed"]},
                        "query_type": {"type": "string", "enum": ["population_statistics", "clinical_trials", "publications"]},
                        "condition": {"type": "string"},
                        "age_range": {"type": "array", "items": {"type": "integer"}, "minItems": 2, "maxItems": 2}
                    },
                    "required": ["database", "query_type", "condition"]
                }
            ),
            "create-fhir-resource": MCPTool(
                name="create-fhir-resource",
                description="Create FHIR R4 compliant reproductive health resources",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "resource_type": {"type": "string", "enum": ["Patient", "Observation", "DiagnosticReport", "Condition"]},
                        "patient_id": {"type": "string"},
                        "data": {"type": "object", "description": "Resource-specific data"}
                    },
                    "required": ["resource_type", "patient_id", "data"]
                }
            ),
            "swan-dataset-info": MCPTool(
                name="swan-dataset-info",
                description="Get information about loaded SWAN dataset",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False
                }
            ),
            "swan-search-variables": MCPTool(
                name="swan-search-variables",
                description="Search for variables in SWAN dataset by keyword",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "search_term": {"type": "string", "description": "Term to search for in variable names"}
                    },
                    "required": ["search_term"]
                }
            ),
            "swan-variable-summary": MCPTool(
                name="swan-variable-summary",
                description="Get detailed summary of a specific SWAN variable",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "variable_name": {"type": "string", "description": "Exact variable name from SWAN dataset"}
                    },
                    "required": ["variable_name"]
                }
            )
        }
        
        # Prompts - Template prompts for AI agents
        self._prompts = {
            "fertility-consultation": MCPPrompt(
                name="fertility-consultation",
                description="Comprehensive fertility consultation prompt with evidence synthesis",
                arguments=[
                    {"name": "patient_age", "description": "Patient age in years", "required": True},
                    {"name": "amh_level", "description": "AMH level in ng/mL", "required": True},
                    {"name": "clinical_question", "description": "Patient's clinical question", "required": True},
                    {"name": "urgency_level", "description": "Clinical urgency (routine/expedited/urgent)", "required": False}
                ]
            ),
            "treatment-recommendation": MCPPrompt(
                name="treatment-recommendation",
                description="Evidence-based treatment recommendation with risk stratification",
                arguments=[
                    {"name": "patient_profile", "description": "Complete patient clinical profile", "required": True},
                    {"name": "treatment_options", "description": "Available treatment options", "required": True},
                    {"name": "research_evidence", "description": "Relevant research evidence", "required": False}
                ]
            ),
            "risk-assessment": MCPPrompt(
                name="risk-assessment",
                description="Comprehensive reproductive health risk assessment",
                arguments=[
                    {"name": "demographics", "description": "Patient demographics", "required": True},
                    {"name": "medical_history", "description": "Relevant medical history", "required": True},
                    {"name": "lifestyle_factors", "description": "Lifestyle and environmental factors", "required": False}
                ]
            )
        }
    
    async def handle_request(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming MCP requests."""
        try:
            mcp_msg = MCPMessage(**message)
            method = mcp_msg.method
            params = mcp_msg.params or {}
            
            if method == MCPMethod.INITIALIZE.value:
                return await self._handle_initialize(mcp_msg.id, params)
            elif method == MCPMethod.LIST_RESOURCES.value:
                return await self._handle_list_resources(mcp_msg.id)
            elif method == MCPMethod.READ_RESOURCE.value:
                return await self._handle_read_resource(mcp_msg.id, params)
            elif method == MCPMethod.LIST_TOOLS.value:
                return await self._handle_list_tools(mcp_msg.id)
            elif method == MCPMethod.CALL_TOOL.value:
                return await self._handle_call_tool(mcp_msg.id, params)
            elif method == MCPMethod.LIST_PROMPTS.value:
                return await self._handle_list_prompts(mcp_msg.id)
            elif method == MCPMethod.GET_PROMPT.value:
                return await self._handle_get_prompt(mcp_msg.id, params)
            else:
                return self._create_error_response(mcp_msg.id, -32601, f"Method not found: {method}")
                
        except Exception as e:
            return self._create_error_response(message.get("id"), -32603, f"Internal error: {str(e)}")
    
    async def _handle_initialize(self, request_id: Union[str, int], params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP initialize request."""
        client_info = params.get("clientInfo", {})
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": self.capabilities,
                "serverInfo": {
                    "name": self.name,
                    "version": self.version,
                    "description": "Women's Health Model Context Protocol Server"
                }
            }
        }
    
    async def _handle_list_resources(self, request_id: Union[str, int]) -> Dict[str, Any]:
        """Handle list resources request."""
        resources = [asdict(resource) for resource in self._resources.values()]
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "resources": resources
            }
        }
    
    async def _handle_read_resource(self, request_id: Union[str, int], params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle read resource request."""
        uri = params.get("uri")
        
        if not uri:
            return self._create_error_response(request_id, -32602, "Missing required parameter: uri")
        
        # Extract resource name from URI
        resource_name = uri.split("/")[-1] if "/" in uri else uri
        
        if resource_name == "patient-data":
            content = await self._get_patient_data(params)
        elif resource_name == "clinical-calculators":
            content = await self._get_clinical_calculators(params)
        elif resource_name == "research-data":
            content = await self._get_research_data(params)
        elif resource_name == "fhir-resources":
            content = await self._get_fhir_resources(params)
        else:
            return self._create_error_response(request_id, -32602, f"Unknown resource: {resource_name}")
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "contents": [
                    {
                        "uri": uri,
                        "mimeType": "application/json",
                        "text": json.dumps(content, indent=2)
                    }
                ]
            }
        }
    
    async def _handle_list_tools(self, request_id: Union[str, int]) -> Dict[str, Any]:
        """Handle list tools request."""
        tools = [asdict(tool) for tool in self._tools.values()]
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": tools
            }
        }
    
    async def _handle_call_tool(self, request_id: Union[str, int], params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tool call request."""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if tool_name not in self._tools:
            return self._create_error_response(request_id, -32602, f"Unknown tool: {tool_name}")
        
        try:
            result = await self._execute_tool(tool_name, arguments)
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, indent=2)
                        }
                    ]
                }
            }
        except Exception as e:
            return self._create_error_response(request_id, -32603, f"Tool execution failed: {str(e)}")
    
    async def _handle_list_prompts(self, request_id: Union[str, int]) -> Dict[str, Any]:
        """Handle list prompts request."""
        prompts = [asdict(prompt) for prompt in self._prompts.values()]
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "prompts": prompts
            }
        }
    
    async def _handle_get_prompt(self, request_id: Union[str, int], params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get prompt request."""
        prompt_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if prompt_name not in self._prompts:
            return self._create_error_response(request_id, -32602, f"Unknown prompt: {prompt_name}")
        
        prompt_content = await self._generate_prompt(prompt_name, arguments)
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "description": self._prompts[prompt_name].description,
                "messages": [
                    {
                        "role": "user",
                        "content": {
                            "type": "text",
                            "text": prompt_content
                        }
                    }
                ]
            }
        }
    
    async def _get_patient_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve standardized patient data."""
        # In production, this would query actual patient databases
        return {
            "data_source": "patient_ehr",
            "patient_id": params.get("patient_id", "demo_patient"),
            "demographics": {
                "age": 38,
                "reproductive_status": "trying_to_conceive"
            },
            "labs": {
                "amh": 0.8,
                "fsh": 12.5,
                "collected_date": "2024-01-15"
            },
            "note": "This is demo data. In production, real patient data would be retrieved with proper authorization."
        }
    
    async def _get_clinical_calculators(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve available clinical calculators."""
        return {
            "available_calculators": [
                {
                    "name": "ovarian_reserve_assessment",
                    "description": "ASRM/ESHRE ovarian reserve classification",
                    "inputs": ["age", "amh", "fsh", "afc"],
                    "outputs": ["category", "percentile", "interpretation"]
                },
                {
                    "name": "ivf_success_prediction",
                    "description": "SART-based IVF success rate prediction",
                    "inputs": ["age", "amh", "cycle_type", "diagnosis"],
                    "outputs": ["live_birth_rate", "confidence_interval"]
                },
                {
                    "name": "menopause_timing_prediction",
                    "description": "SWAN study-based menopause timing prediction",
                    "inputs": ["age", "amh", "lifestyle_factors"],
                    "outputs": ["predicted_age", "time_remaining", "stage"]
                }
            ]
        }
    
    async def _get_research_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve research database information."""
        return {
            "available_databases": [
                {
                    "name": "SWAN",
                    "description": "Study of Women's Health Across the Nation",
                    "data_types": ["menopause_timing", "hormone_trajectories"],
                    "sample_size": 3302
                },
                {
                    "name": "SART",
                    "description": "Society for Assisted Reproductive Technology",
                    "data_types": ["ivf_success_rates", "cycle_outcomes"],
                    "data_year": 2023
                }
            ]
        }
    
    async def _get_fhir_resources(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve FHIR resource templates."""
        return {
            "supported_resources": [
                "Patient",
                "Observation",
                "DiagnosticReport",
                "Condition",
                "Procedure"
            ],
            "extensions": [
                "reproductive-health",
                "cycle-tracking",
                "fertility-intent"
            ]
        }
    
    async def _execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool with given arguments."""
        # Import actual calculator modules
        from core.clinical_calculators import ClinicalCalculators
        from core.research_database_integration import ResearchDatabaseIntegration
        from core.fhir_integration import ReproductiveHealthFHIR
        from .swan_data_integration import swan_integration

        calc = ClinicalCalculators()
        research = ResearchDatabaseIntegration()
        fhir = ReproductiveHealthFHIR()
        
        if tool_name == "assess-ovarian-reserve":
            result = calc.assess_ovarian_reserve(
                age=arguments["age"],
                amh=arguments["amh"],
                fsh=arguments.get("fsh"),
                antral_follicle_count=arguments.get("afc")
            )
            return {
                "tool": tool_name,
                "result": {
                    "category": result.category.value,
                    "percentile": result.percentile,
                    "interpretation": result.clinical_interpretation,
                    "recommendations": result.recommendations
                }
            }
        
        elif tool_name == "predict-ivf-success":
            result = calc.predict_ivf_success(
                age=arguments["age"],
                amh=arguments["amh"],
                cycle_type=arguments["cycle_type"],
                prior_pregnancies=arguments.get("prior_pregnancies", 0),
                diagnosis=arguments.get("diagnosis")
            )
            return {
                "tool": tool_name,
                "result": {
                    "live_birth_rate": result.live_birth_rate,
                    "confidence_interval": result.confidence_interval,
                    "cumulative_success_3_cycles": result.cumulative_success_3_cycles,
                    "recommendations": result.recommendations
                }
            }
        
        elif tool_name == "query-research-database":
            database = arguments.get("database", "swan")
            query_type = arguments.get("query_type", "population_statistics")
            condition = arguments.get("condition", "")
            age_range = arguments.get("age_range")
            
            if database == "swan":
                # Use real SWAN data integration
                result = swan_integration.get_population_statistics(
                    condition=condition,
                    age_range=tuple(age_range) if age_range else None
                )
                return {
                    "tool": tool_name,
                    "database": database,
                    "result": result
                }
            else:
                # Fall back to original research integration
                return {
                    "tool": tool_name,
                    "result": "Non-SWAN databases not implemented in demo"
                }
        
        else:
            return {"tool": tool_name, "result": "Tool execution not implemented in demo"}
    
    async def _generate_prompt(self, prompt_name: str, arguments: Dict[str, Any]) -> str:
        """Generate prompt content based on template and arguments."""
        
        if prompt_name == "fertility-consultation":
            age = arguments.get("patient_age")
            amh = arguments.get("amh_level")
            question = arguments.get("clinical_question")
            urgency = arguments.get("urgency_level", "routine")
            
            return f"""
You are an expert reproductive endocrinologist providing evidence-based fertility consultation.

PATIENT PROFILE:
- Age: {age} years
- AMH Level: {amh} ng/mL
- Clinical Question: "{question}"
- Urgency Level: {urgency}

INSTRUCTIONS:
1. Assess ovarian reserve using ASRM criteria
2. Calculate age-specific IVF success rates using SART data
3. Consider menopause timing predictions from SWAN study
4. Provide evidence-based recommendations with confidence intervals
5. Include specific action items and timeline recommendations
6. Address patient's specific question directly

RESPONSE FORMAT:
- Clinical Assessment
- Evidence Synthesis  
- Recommendations
- Action Items
- Risk Factors & Considerations

Base your response on the latest ASRM guidelines, SART success rates, and peer-reviewed research.
"""
        
        elif prompt_name == "treatment-recommendation":
            return "Evidence-based treatment recommendation prompt (to be implemented)"
        
        else:
            return f"Prompt template for {prompt_name} (to be implemented)"
    
    def _create_error_response(self, request_id: Union[str, int], code: int, message: str) -> Dict[str, Any]:
        """Create standardized error response."""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": code,
                "message": message
            }
        }