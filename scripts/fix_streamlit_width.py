#!/usr/bin/env python3
"""
Script to fix deprecated width='stretch' parameters in Streamlit apps
Replace with use_container_width=True
"""
import re
from pathlib import Path

def fix_width_parameter(file_path):
    """Fix width parameter in a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        # Fix st.plotly_chart width parameter
        content = re.sub(
            r"st\.plotly_chart\((.*?),\s*width=['\"]stretch['\"]",
            r"st.plotly_chart(\1, use_container_width=True",
            content
        )

        # Fix st.dataframe width parameter (in case we missed any)
        content = re.sub(
            r"st\.dataframe\((.*?),\s*width=['\"]stretch['\"]",
            r"st.dataframe(\1, use_container_width=True",
            content
        )

        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ Updated: {file_path}")
            return True
        return False
    except Exception as e:
        print(f"✗ Error processing {file_path}: {e}")
        return False

def main():
    """Fix width parameters in all demo files."""
    demos_dir = Path(__file__).parent.parent / "demos"
    files_to_fix = [
        "streamlit_demo.py",
        "enhanced_streamlit_demo.py",
        "complete_hackathon_demo.py"
    ]

    print("Fixing deprecated width='stretch' parameters...\n")

    updated_count = 0
    for filename in files_to_fix:
        file_path = demos_dir / filename
        if file_path.exists():
            if fix_width_parameter(file_path):
                updated_count += 1
        else:
            print(f"✗ File not found: {file_path}")

    print(f"\n{'='*60}")
    print(f"✓ Updated {updated_count} files")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
