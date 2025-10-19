# ELSA (English Longitudinal Study of Ageing) MCP Server

An MCP (Model Context Protocol) server providing structured real-time access to ELSA data information, metadata, and documentation.

## Overview

The English Longitudinal Study of Ageing (ELSA) is a longitudinal panel study of adults aged 50 and over living in England. It provides rich multidimensional data on health, economic circumstances, social participation, and well-being.

**Study Information:**
- **Study Number**: SN 5050
- **Data Provider**: UK Data Service (UKDS)
- **Waves Available**: 0-11 (1998-2024)
- **Sample Size**: ~8,000-12,000 per wave
- **Data Collection**: Interviews, questionnaires, biomarkers (selected waves)

## Features

### 9 Comprehensive Tools

1. **list_elsa_waves** - List all available ELSA waves with basic or detailed information
2. **get_wave_details** - Get detailed information about a specific wave
3. **search_data_modules** - Search ELSA data modules and variables by topic/keyword
4. **get_data_module_info** - Get detailed information about a specific data module
5. **get_access_information** - Get step-by-step instructions for accessing ELSA data
6. **get_study_metadata** - Get comprehensive metadata about the ELSA study
7. **get_documentation_links** - Get links to questionnaires, user guides, and documentation
8. **compare_waves** - Compare variables and topics across multiple waves
9. **get_research_examples** - Get examples of research questions answerable with ELSA data

## Data Modules Covered

The server provides information on 10 major ELSA data modules:

- **Health and Disability** - Physical health, chronic conditions, ADL/IADL
- **Cognitive Function** - Memory tests, verbal fluency, processing speed
- **Mental Health** - Depression (CES-D), anxiety, life satisfaction
- **Biomarkers** - Blood pressure, blood samples, lung function, grip strength
- **Economic Circumstances** - Income, wealth, pensions, housing
- **Work and Retirement** - Employment, job characteristics, retirement planning
- **Social Networks** - Social contacts, activities, loneliness, civic engagement
- **Family and Relationships** - Marital status, children, caregiving
- **Health Behaviors** - Smoking, alcohol, physical activity, diet, sleep
- **Expectations** - Life expectancy, future health, economic expectations

## Wave Coverage

| Wave | Year | Description | Key Features |
|------|------|-------------|--------------|
| 0 | 1998-2001 | HSE Baseline | Health Survey for England cohort |
| 1 | 2002-2003 | First ELSA wave | Detailed interviews, biomarkers |
| 2 | 2004-2005 | Follow-up | Health trajectories, retirement |
| 3 | 2006-2007 | Nurse visit wave | Cognitive function, physical function |
| 4 | 2008-2009 | Fourth wave | Work, income, quality of life |
| 5 | 2010-2011 | Refreshment sample | Ageing, health service use |
| 6 | 2012-2013 | Nurse visit wave | Life course, cognitive ageing |
| 7 | 2014-2015 | Seventh wave | Healthy ageing, financial planning |
| 8 | 2016-2017 | Nurse visit wave | Biological ageing, dementia, frailty |
| 9 | 2018-2019 | Ninth wave | Social care, internet use |
| 10 | 2020-2021 | COVID-19 wave | COVID impact, mental health |
| 11 | 2023-2024 | Latest wave | Post-pandemic health, long COVID |

## Example Usage

### Finding information about a specific wave:
```json
{
  "tool": "get_wave_details",
  "arguments": {
    "wave": "8"
  }
}
```

### Searching for cognitive function data:
```json
{
  "tool": "search_data_modules",
  "arguments": {
    "query": "cognitive"
  }
}
```

### Getting data access instructions:
```json
{
  "tool": "get_access_information",
  "arguments": {
    "detailed": true
  }
}
```

### Comparing multiple waves:
```json
{
  "tool": "compare_waves",
  "arguments": {
    "waves": ["1", "5", "9"],
    "focus": "topics"
  }
}
```

## Data Access

### How to Access ELSA Data

1. **Register with UK Data Service** (https://ukdataservice.ac.uk/)
   - UK academics: Use institutional login (UKAMF)
   - Others: Create free account

2. **Find ELSA datasets**
   - Study Number: SN 5050
   - URL: https://beta.ukdataservice.ac.uk/datacatalogue/studies/study?id=5050

3. **Review documentation**
   - Check questionnaires, user guides, data dictionaries

4. **Accept End User License**
   - Agree to terms of use

5. **Download data**
   - Available formats: SPSS, Stata, tab-delimited

### Access Levels

- **Open**: Some datasets available without registration
- **Safeguarded**: Most ELSA data - requires UKDS registration
- **Controlled**: Sensitive data - requires SecureLab access

### Programmatic Access

For users who want to download data programmatically:

**R Package:**
```r
install.packages("ukds")
library(ukds)
```

**Python Package:**
```bash
pip install ukds
```

## Research Applications

ELSA data supports research on:

- **Healthy Ageing**: Trajectories of physical and cognitive health
- **Health Inequalities**: Social determinants of health in older adults
- **Economic Well-being**: Wealth accumulation, pension adequacy
- **Mental Health**: Depression, anxiety, life satisfaction
- **COVID-19 Impact**: Pandemic effects on older adults
- **Biomarkers**: Relationship between biological and subjective health
- **Social Relationships**: Social networks, loneliness, civic engagement
- **Work and Retirement**: Employment transitions, retirement planning

## Contact

- **Data Queries**: ELSAdata@natcen.ac.uk
- **Project Website**: https://www.elsa-project.ac.uk
- **Documentation**: https://www.elsa-project.ac.uk/data-and-documentation

## Citation

When using ELSA data, cite as:

> NatCen Social Research, University College London, Institute for Fiscal Studies. (2024). English Longitudinal Study of Ageing. [data collection]. UK Data Service. SN: 5050, DOI: 10.5255/UKDA-SN-5050-25

## Technical Details

- **Server Type**: MCP (Model Context Protocol)
- **Language**: Python 3
- **Dependencies**: `mcp` (Python MCP SDK)
- **Protocol**: stdio-based communication
- **Output Format**: JSON

## Configuration

The server is configured in Claude Desktop at:
```json
{
  "elsa-data": {
    "command": "/Users/dgordon/anaconda3/bin/python",
    "args": [
      "/Users/dgordon/womens_health_mcp/elsa_server.py"
    ]
  }
}
```

## Notes

- This server provides **metadata and documentation** about ELSA data
- For actual **data download**, users must register with UK Data Service
- Some sensitive data requires additional application through SecureLab
- Wave 11 data is available but without survey weights (as of 2024)
- The server does not store or transmit actual ELSA datasets, only metadata

## Future Enhancements

Potential additions:
- Integration with `ukds` Python package for authenticated data download
- Variable-level search across data dictionaries
- Citation generator for specific waves/variables
- Data quality and missingness information
- Sample composition and weighting details
