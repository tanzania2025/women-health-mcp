#!/usr/bin/env python3
"""
Script to fix import statements after project reorganization
"""
import os
import re
from pathlib import Path

# Define the mapping of old imports to new imports
IMPORT_MAPPINGS = {
    # Core modules
    r'^from biomini_intake import': 'from core.biomini_intake import',
    r'^from netmind_router import': 'from core.netmind_router import',
    r'^from manus_agents import': 'from core.manus_agents import',
    r'^from huggingface_integration import': 'from core.huggingface_integration import',
    r'^from end_to_end_demo import': 'from demos.end_to_end_demo import',
    r'^from enhanced_mcp_demo import': 'from demos.enhanced_mcp_demo import',
    r'^from womens_health_mcp import': 'from core.womens_health_mcp import',
    r'^from clinical_calculators import': 'from core.clinical_calculators import',
    r'^from patient_data_integration import': 'from core.patient_data_integration import',
    r'^from privacy_security import': 'from core.privacy_security import',
    r'^from research_database_integration import': 'from core.research_database_integration import',
    r'^from fhir_integration import': 'from core.fhir_integration import',
    r'^from claude_mcp_integration import': 'from core.claude_mcp_integration import',
    r'^from multi_dataset_integration import': 'from core.multi_dataset_integration import',

    # Servers
    r'^from asrm_server import': 'from servers.asrm_server import',
    r'^from nams_server import': 'from servers.nams_server import',
    r'^from pubmed_server import': 'from servers.pubmed_server import',
    r'^from sart_ivf_server import': 'from servers.sart_ivf_server import',
    r'^from menopause_server import': 'from servers.menopause_server import',
    r'^from eshre_server import': 'from servers.eshre_server import',
    r'^from elsa_server import': 'from servers.elsa_server import',

    # Clients
    r'^from asrm_client import': 'from clients.asrm_client import',
    r'^from nams_client import': 'from clients.nams_client import',
    r'^from pubmed_client import': 'from clients.pubmed_client import',

    # Import statements (for non-from imports)
    r'^import biomini_intake': 'import core.biomini_intake',
    r'^import netmind_router': 'import core.netmind_router',
    r'^import manus_agents': 'import core.manus_agents',
    r'^import huggingface_integration': 'import core.huggingface_integration',
    r'^import womens_health_mcp': 'import core.womens_health_mcp',
    r'^import clinical_calculators': 'import core.clinical_calculators',
    r'^import patient_data_integration': 'import core.patient_data_integration',
    r'^import privacy_security': 'import core.privacy_security',
    r'^import research_database_integration': 'import core.research_database_integration',
    r'^import fhir_integration': 'import core.fhir_integration',
}

def fix_file_imports(file_path):
    """Fix imports in a single Python file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content
        lines = content.split('\n')
        new_lines = []

        for line in lines:
            new_line = line
            for old_pattern, new_import in IMPORT_MAPPINGS.items():
                if re.match(old_pattern, line.strip()):
                    new_line = re.sub(old_pattern, new_import, line)
                    break
            new_lines.append(new_line)

        new_content = '\n'.join(new_lines)

        if new_content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"✓ Updated: {file_path}")
            return True
        return False
    except Exception as e:
        print(f"✗ Error processing {file_path}: {e}")
        return False

def main():
    """Fix imports in all Python files."""
    root_dir = Path(__file__).parent.parent
    python_files = list(root_dir.rglob("*.py"))

    # Exclude this script and .git directory
    python_files = [f for f in python_files if '.git' not in str(f) and f.name != 'fix_imports.py']

    print(f"Scanning {len(python_files)} Python files...\n")

    updated_count = 0
    for py_file in python_files:
        if fix_file_imports(py_file):
            updated_count += 1

    print(f"\n{'='*60}")
    print(f"✓ Updated {updated_count} files")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
