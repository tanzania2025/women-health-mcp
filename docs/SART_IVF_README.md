# SART IVF Calculator MCP Server

An MCP (Model Context Protocol) server that provides access to the SART (Society for Assisted Reproductive Technology) IVF success rate calculator.

## Overview

This server allows Claude to calculate predicted IVF success rates based on patient characteristics using the validated SART calculator from Aberdeen University.

## Features

- Calculate probability of live birth after 1, 2, or 3 complete IVF cycles
- Supports both metric (kg/cm) and imperial (lbs/ft/in) measurements
- Accounts for multiple clinical factors:
  - Patient age
  - BMI (height/weight)
  - Previous full-term pregnancy history
  - Male factor infertility
  - Polycystic ovary syndrome (PCOS)
  - Uterine problems
  - Unexplained infertility
  - Low ovarian reserve
  - AMH (Anti-Müllerian Hormone) levels

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Add the server to your Claude desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "sart-ivf": {
      "command": "python",
      "args": [
        "/Users/dgordon/womens_health_mcp/sart_ivf_server.py"
      ]
    }
  }
}
```

## Usage

Once configured, you can ask Claude to calculate IVF success rates:

### Example 1: Basic calculation
```
Calculate IVF success rates for a 30-year-old woman, 165cm tall, 65kg, with no other factors.
```

### Example 2: With clinical factors
```
Calculate IVF success rates for a 35-year-old woman with PCOS, 5'6" tall, 150 lbs,
with an AMH level of 2.5 ng/ml.
```

### Example 3: Detailed scenario
```
What are the IVF success rates for a 32-year-old woman who:
- Is 5'4" and weighs 140 lbs
- Has never had a full-term pregnancy
- Has been diagnosed with unexplained infertility
- Partner has normal sperm parameters
```

## Available Tool

### `calculate_ivf_success`

Calculates IVF success probabilities based on patient characteristics.

**Required Parameters:**
- `age` (number): Patient age in years (18-45)

**Optional Parameters:**
- `height_cm` (number): Height in centimeters (120-220)
- `weight_kg` (number): Weight in kilograms (30-160)
- `height_ft` (number): Height in feet (4-7)
- `height_in` (number): Height in inches (0-11)
- `weight_lbs` (number): Weight in pounds (70-350)
- `previous_full_term` (boolean): Previous full-term pregnancy (>37 weeks)
- `male_factor` (boolean): Partner has sperm problems
- `polycystic` (boolean): Has PCOS
- `uterine_problems` (boolean): Has uterine problems
- `unexplained_infertility` (boolean): Diagnosed with unexplained infertility
- `low_ovarian_reserve` (boolean): Diagnosed with low ovarian reserve
- `amh_available` (boolean): AMH level is known
- `amh_value` (number): AMH level in ng/ml

**Returns:**
Success rates (as percentages) for 1, 2, and 3 complete IVF cycles.

## Data Source

This calculator uses the SART IVF prediction model developed by the Society for Assisted Reproductive Technology and hosted by the University of Aberdeen.

Calculator URL: https://w3.abdn.ac.uk/clsm/SARTIVF/tool/ivf1

## Notes

- A "complete cycle" includes all embryo transfers using eggs from one ovarian stimulation cycle
- Success rates represent probability of live birth
- Predictions are based on large-scale clinical data but individual results may vary
- Always consult with a fertility specialist for personalized medical advice

## License

This MCP server is provided as-is for educational and clinical decision support purposes.
