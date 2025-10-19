# Data Directory

This directory contains data files and datasets for the Women's Health MCP system.

## Structure

```
data/
├── samples/          # Sample datasets for testing and demos
├── schemas/          # Data schemas and validation rules
├── exports/          # Generated data exports and reports
└── uploads/          # Temporary file uploads (auto-cleaned)
```

## Data Types

### Sample Data
- **Patient profiles** - De-identified sample patient data for testing
- **Research datasets** - Curated subsets from SWAN, SART for demos
- **Clinical scenarios** - Test cases for validation

### Schemas
- **FHIR schemas** - Reproductive health FHIR resource definitions
- **MCP schemas** - Model Context Protocol message schemas
- **API schemas** - External API response schemas

### Exports
- **Audit reports** - Privacy and compliance audit exports
- **Analytics reports** - Aggregate health insights
- **FHIR bundles** - Exported patient data bundles

## Security Notes

⚠️ **IMPORTANT**: This directory is configured in `.gitignore` to prevent accidental commit of sensitive data.

- All patient data must be de-identified
- No real PHI should be stored here
- Use encrypted storage for sensitive datasets
- Follow HIPAA compliance guidelines

## Usage

The MCP server automatically manages data in this directory:
- Sample data is loaded on startup for demos
- Exports are generated on-demand via API
- Temporary files are auto-cleaned every 24 hours

For production deployment, configure external storage (S3, Azure Blob, etc.) instead of local file storage.