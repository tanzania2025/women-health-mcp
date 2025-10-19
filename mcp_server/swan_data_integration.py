"""
SWAN Data Integration for Women's Health MCP
Real integration with downloaded SWAN dataset from ICPSR_31901
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class SWANDataIntegration:
    """
    Integration with real SWAN (Study of Women's Health Across the Nation) dataset.
    Provides population-level reproductive health statistics for MCP server.
    """
    
    def __init__(self, data_path: Optional[str] = None):
        self.data_path = data_path or "/Users/sunaina/code/women-health-mcp/raw_data/ICPSR_31901/DS0001/31901-0001-Data.tsv"
        self.data = None
        self.codebook_cache = {}
        self._load_data()
    
    def _load_data(self):
        """Load SWAN dataset from TSV file."""
        try:
            data_file = Path(self.data_path)
            if not data_file.exists():
                logger.warning(f"SWAN data file not found at {self.data_path}")
                return
            
            logger.info("Loading SWAN dataset...")
            self.data = pd.read_csv(self.data_path, sep='\t', low_memory=False)
            logger.info(f"Loaded SWAN data: {len(self.data)} participants, {len(self.data.columns)} variables")
            
            # Clean and prepare key variables
            self._prepare_key_variables()
            
        except Exception as e:
            logger.error(f"Failed to load SWAN data: {e}")
            self.data = None
    
    def _prepare_key_variables(self):
        """Prepare key reproductive health variables from SWAN data."""
        if self.data is None:
            return
        
        # Clean age variable
        if 'AGE7' in self.data.columns:
            self.data['age'] = pd.to_numeric(self.data['AGE7'], errors='coerce')
        
        # Clean race/ethnicity
        if 'RACE' in self.data.columns:
            race_mapping = {
                1: 'african_american',
                2: 'caucasian', 
                3: 'chinese',
                4: 'hispanic',
                5: 'japanese'
            }
            self.data['ethnicity'] = self.data['RACE'].map(race_mapping)
        
        # Look for hormone data (AMH, FSH, etc.)
        hormone_columns = [col for col in self.data.columns if any(hormone in col.upper() for hormone in ['AMH', 'FSH', 'ESTR', 'PROG'])]
        logger.info(f"Found potential hormone columns: {hormone_columns}")
        
        # Look for menopause-related variables
        menopause_columns = [col for col in self.data.columns if any(term in col.upper() for term in ['MENO', 'PERIOD', 'CYCLE'])]
        logger.info(f"Found potential menopause columns: {menopause_columns}")
    
    def get_population_statistics(self, 
                                condition: str,
                                age_range: Optional[Tuple[int, int]] = None,
                                ethnicity: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get population statistics from SWAN data."""
        
        if self.data is None:
            return self._fallback_population_stats(condition, age_range, ethnicity)
        
        # Filter data based on criteria
        filtered_data = self.data.copy()
        
        if age_range:
            filtered_data = filtered_data[
                (filtered_data['age'] >= age_range[0]) & 
                (filtered_data['age'] <= age_range[1])
            ]
        
        if ethnicity:
            filtered_data = filtered_data[filtered_data['ethnicity'].isin(ethnicity)]
        
        if condition.lower() == "menopause timing":
            return self._get_menopause_statistics(filtered_data)
        elif "hormone" in condition.lower() or "amh" in condition.lower():
            return self._get_hormone_statistics(filtered_data)
        else:
            return self._get_general_statistics(filtered_data, condition)
    
    def _get_menopause_statistics(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Extract menopause timing statistics from SWAN data."""
        
        stats = {
            "data_source": "SWAN_ICPSR_31901",
            "visit": "Visit 07 (2003-2005)",
            "sample_size": len(data),
            "age_statistics": {
                "mean_age": float(data['age'].mean()) if 'age' in data else None,
                "median_age": float(data['age'].median()) if 'age' in data else None,
                "age_range": [float(data['age'].min()), float(data['age'].max())] if 'age' in data else None,
                "std_deviation": float(data['age'].std()) if 'age' in data else None
            }
        }
        
        # Add ethnicity breakdown
        if 'ethnicity' in data.columns:
            ethnicity_stats = {}
            for ethnicity in data['ethnicity'].dropna().unique():
                ethnic_subset = data[data['ethnicity'] == ethnicity]
                ethnicity_stats[ethnicity] = {
                    "n": len(ethnic_subset),
                    "mean_age": float(ethnic_subset['age'].mean()) if not ethnic_subset['age'].isna().all() else None
                }
            stats["ethnicity_breakdown"] = ethnicity_stats
        
        # Look for menopause-related variables in this visit
        menopause_vars = [col for col in data.columns if any(term in col.upper() for term in ['MENO', 'PERIOD', 'CYCLE'])]
        if menopause_vars:
            stats["available_menopause_variables"] = menopause_vars[:10]  # First 10 variables
        
        # Add estimated menopause timing based on age distribution
        if 'age' in data.columns:
            ages = data['age'].dropna()
            stats["menopause_timing_estimates"] = {
                "median_age_at_visit": float(ages.median()),
                "percentiles": {
                    "10th": float(ages.quantile(0.1)),
                    "25th": float(ages.quantile(0.25)),
                    "50th": float(ages.quantile(0.5)),
                    "75th": float(ages.quantile(0.75)),
                    "90th": float(ages.quantile(0.9))
                },
                "note": "Ages at Visit 07 - actual menopause timing would require longitudinal analysis"
            }
        
        return stats
    
    def _get_hormone_statistics(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Extract hormone-related statistics from SWAN data."""
        
        stats = {
            "data_source": "SWAN_ICPSR_31901",
            "visit": "Visit 07 (2003-2005)",
            "sample_size": len(data)
        }
        
        # Look for hormone columns
        hormone_columns = [col for col in data.columns if any(hormone in col.upper() for hormone in ['AMH', 'FSH', 'ESTR', 'PROG', 'HORM'])]
        
        if hormone_columns:
            stats["available_hormone_variables"] = hormone_columns
            
            # Try to extract numeric hormone values
            hormone_data = {}
            for col in hormone_columns[:5]:  # Analyze first 5 hormone columns
                try:
                    numeric_values = pd.to_numeric(data[col], errors='coerce').dropna()
                    if len(numeric_values) > 0:
                        hormone_data[col] = {
                            "n_valid": len(numeric_values),
                            "mean": float(numeric_values.mean()),
                            "median": float(numeric_values.median()),
                            "std": float(numeric_values.std()),
                            "range": [float(numeric_values.min()), float(numeric_values.max())]
                        }
                except:
                    continue
            
            if hormone_data:
                stats["hormone_statistics"] = hormone_data
        else:
            stats["note"] = "No hormone variables found in this SWAN visit dataset"
        
        return stats
    
    def _get_general_statistics(self, data: pd.DataFrame, condition: str) -> Dict[str, Any]:
        """Get general statistics for other conditions."""
        
        return {
            "data_source": "SWAN_ICPSR_31901",
            "condition": condition,
            "sample_size": len(data),
            "visit": "Visit 07 (2003-2005)",
            "age_statistics": {
                "mean_age": float(data['age'].mean()) if 'age' in data else None,
                "age_range": [float(data['age'].min()), float(data['age'].max())] if 'age' in data else None
            },
            "ethnicity_distribution": data['ethnicity'].value_counts().to_dict() if 'ethnicity' in data else None,
            "available_variables": len(data.columns),
            "note": f"Analysis for condition: {condition}"
        }
    
    def _fallback_population_stats(self, condition: str, age_range: Optional[Tuple[int, int]], ethnicity: Optional[List[str]]) -> Dict[str, Any]:
        """Fallback statistics when SWAN data is not available."""
        
        return {
            "data_source": "SWAN_MOCK_DATA",
            "note": "SWAN dataset not available - using reference values",
            "condition": condition,
            "reference_statistics": {
                "menopause_timing": {
                    "median_age": 51.4,
                    "percentiles": {
                        "10th": 46.2,
                        "25th": 49.1,
                        "50th": 51.4,
                        "75th": 53.6,
                        "90th": 56.1
                    }
                }
            },
            "warning": "Real SWAN data integration requires dataset at specified path"
        }
    
    def get_dataset_info(self) -> Dict[str, Any]:
        """Get information about the loaded SWAN dataset."""
        
        if self.data is None:
            return {
                "status": "not_loaded",
                "message": "SWAN dataset not found or failed to load",
                "expected_path": self.data_path
            }
        
        return {
            "status": "loaded",
            "dataset": "SWAN ICPSR 31901",
            "visit": "Visit 07 (2003-2005)",
            "participants": len(self.data),
            "variables": len(self.data.columns),
            "data_path": self.data_path,
            "age_range": [float(self.data['age'].min()), float(self.data['age'].max())] if 'age' in self.data else None,
            "ethnicities": list(self.data['ethnicity'].dropna().unique()) if 'ethnicity' in self.data else None,
            "sample_columns": list(self.data.columns[:20]),  # First 20 columns
            "loaded_at": datetime.now().isoformat()
        }
    
    def search_variables(self, search_term: str) -> List[str]:
        """Search for variables containing a specific term."""
        
        if self.data is None:
            return []
        
        matching_vars = [col for col in self.data.columns if search_term.upper() in col.upper()]
        return matching_vars
    
    def get_variable_summary(self, variable_name: str) -> Dict[str, Any]:
        """Get summary statistics for a specific variable."""
        
        if self.data is None or variable_name not in self.data.columns:
            return {"error": f"Variable {variable_name} not found"}
        
        var_data = self.data[variable_name]
        
        summary = {
            "variable": variable_name,
            "total_records": len(var_data),
            "missing_count": var_data.isna().sum(),
            "data_type": str(var_data.dtype)
        }
        
        # Try numeric summary
        try:
            numeric_data = pd.to_numeric(var_data, errors='coerce').dropna()
            if len(numeric_data) > 0:
                summary["numeric_summary"] = {
                    "count": len(numeric_data),
                    "mean": float(numeric_data.mean()),
                    "median": float(numeric_data.median()),
                    "std": float(numeric_data.std()),
                    "min": float(numeric_data.min()),
                    "max": float(numeric_data.max())
                }
        except:
            pass
        
        # Value counts for categorical data
        try:
            value_counts = var_data.value_counts().head(10).to_dict()
            summary["value_counts"] = {str(k): int(v) for k, v in value_counts.items()}
        except:
            pass
        
        return summary


# Global SWAN integration instance
swan_integration = SWANDataIntegration()