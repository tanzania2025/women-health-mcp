#!/usr/bin/env python3
"""
Multi-Dataset Integration for Women's Health MCP
Enhanced system supporting multiple SWAN visits and longitudinal analysis
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class MultiDatasetIntegration:
    """
    Enhanced integration supporting multiple SWAN visits and longitudinal analysis.
    Provides comprehensive population-level reproductive health statistics.
    """
    
    def __init__(self, base_path: Optional[str] = None):
        self.base_path = base_path or "/Users/sunaina/code/women-health-mcp/raw_data"
        self.datasets = {}
        self.dataset_info = {}
        self._discover_datasets()
        self._load_available_datasets()
    
    def _discover_datasets(self):
        """Discover all available SWAN datasets."""
        
        self.dataset_catalog = {
            "ICPSR_30142": {
                "visit": "Visit 04",
                "period": "2000-2002", 
                "description": "Early menopause transition",
                "focus": "Baseline reproductive health"
            },
            "ICPSR_31901": {
                "visit": "Visit 07",
                "period": "2003-2005",
                "description": "Mid menopause transition", 
                "focus": "Hormone changes and symptoms"
            },
            "ICPSR_32122": {
                "visit": "Visit 08",
                "period": "2004-2006",
                "description": "Late menopause transition",
                "focus": "Menopause completion and beyond"
            },
            "ICPSR_28762": {
                "visit": "Visit 01",
                "period": "1996-1997",
                "description": "Premenopause baseline",
                "focus": "Early reproductive health baseline"
            },
            "ICPSR_29221": {
                "visit": "Visit 02", 
                "period": "1997-1999",
                "description": "Early transition tracking",
                "focus": "Initial transition markers"
            },
            "ICPSR_29401": {
                "visit": "Visit 03",
                "period": "1999-2000", 
                "description": "Transition progression",
                "focus": "Reproductive aging markers"
            }
        }
        
        logger.info(f"Discovered {len(self.dataset_catalog)} potential SWAN datasets")
    
    def _load_available_datasets(self):
        """Load all available SWAN datasets."""
        
        base_path = Path(self.base_path)
        
        for dataset_id, info in self.dataset_catalog.items():
            dataset_path = base_path / dataset_id / "DS0001" / f"{dataset_id.split('_')[1]}-0001-Data.tsv"
            
            if dataset_path.exists():
                try:
                    logger.info(f"Loading {dataset_id} ({info['visit']})...")
                    data = pd.read_csv(dataset_path, sep='\t', low_memory=False)
                    
                    self.datasets[dataset_id] = data
                    self.dataset_info[dataset_id] = {
                        **info,
                        "participants": len(data),
                        "variables": len(data.columns),
                        "loaded": True,
                        "data_path": str(dataset_path)
                    }
                    
                    # Clean and prepare key variables
                    self._prepare_dataset_variables(dataset_id, data)
                    
                    logger.info(f"  ✅ {len(data)} participants, {len(data.columns)} variables")
                    
                except Exception as e:
                    logger.error(f"Failed to load {dataset_id}: {e}")
                    self.dataset_info[dataset_id] = {**info, "loaded": False, "error": str(e)}
            else:
                self.dataset_info[dataset_id] = {**info, "loaded": False, "reason": "File not found"}
        
        logger.info(f"Successfully loaded {len(self.datasets)} datasets")
    
    def _prepare_dataset_variables(self, dataset_id: str, data: pd.DataFrame):
        """Prepare key variables for each dataset."""
        
        # Standardize age variables (different visits may use different column names)
        age_columns = [col for col in data.columns if 'AGE' in col.upper()]
        if age_columns:
            # Use the most relevant age column
            primary_age_col = age_columns[0]
            data['age_std'] = pd.to_numeric(data[primary_age_col], errors='coerce')
        
        # Standardize race/ethnicity 
        race_columns = [col for col in data.columns if 'RACE' in col.upper()]
        if race_columns:
            race_mapping = {
                1: 'african_american',
                2: 'caucasian', 
                3: 'chinese',
                4: 'hispanic',
                5: 'japanese'
            }
            data['ethnicity_std'] = data[race_columns[0]].map(race_mapping)
        
        # Identify hormone variables
        hormone_columns = [col for col in data.columns if any(
            hormone in col.upper() for hormone in ['AMH', 'FSH', 'ESTR', 'PROG', 'HORM', 'TESTOS']
        )]
        
        # Identify menopause variables
        menopause_columns = [col for col in data.columns if any(
            term in col.upper() for term in ['MENO', 'PERIOD', 'CYCLE', 'BLEED']
        )]
        
        # Store variable categories for easy access
        self.dataset_info[dataset_id]['variable_categories'] = {
            'age_columns': age_columns,
            'race_columns': race_columns,
            'hormone_columns': hormone_columns,
            'menopause_columns': menopause_columns
        }
    
    def get_datasets_overview(self) -> Dict[str, Any]:
        """Get overview of all available datasets."""
        
        overview = {
            "total_datasets": len(self.dataset_catalog),
            "loaded_datasets": len(self.datasets),
            "datasets": {}
        }
        
        for dataset_id, info in self.dataset_info.items():
            overview["datasets"][dataset_id] = {
                "visit": info.get("visit", "Unknown"),
                "period": info.get("period", "Unknown"),
                "description": info.get("description", ""),
                "loaded": info.get("loaded", False),
                "participants": info.get("participants", 0),
                "variables": info.get("variables", 0)
            }
        
        # Calculate totals for loaded datasets
        loaded_data = [info for info in self.dataset_info.values() if info.get("loaded")]
        if loaded_data:
            overview["total_participants"] = sum(info["participants"] for info in loaded_data)
            overview["total_variables"] = sum(info["variables"] for info in loaded_data)
            overview["date_range"] = f"{min(info['period'].split('-')[0] for info in loaded_data)}-{max(info['period'].split('-')[1] for info in loaded_data)}"
        
        return overview
    
    def get_longitudinal_analysis(self, 
                                condition: str,
                                age_range: Optional[Tuple[int, int]] = None) -> Dict[str, Any]:
        """Perform longitudinal analysis across multiple SWAN visits."""
        
        if not self.datasets:
            return {"error": "No datasets loaded"}
        
        longitudinal_data = {}
        
        for dataset_id, data in self.datasets.items():
            visit_info = self.dataset_info[dataset_id]
            
            # Filter by age if specified
            filtered_data = data.copy()
            if age_range and 'age_std' in filtered_data.columns:
                filtered_data = filtered_data[
                    (filtered_data['age_std'] >= age_range[0]) & 
                    (filtered_data['age_std'] <= age_range[1])
                ]
            
            # Analyze based on condition
            if condition.lower() == "menopause progression":
                analysis = self._analyze_menopause_progression(dataset_id, filtered_data)
            elif condition.lower() == "hormone trajectories":
                analysis = self._analyze_hormone_trajectories(dataset_id, filtered_data)
            elif condition.lower() == "population demographics":
                analysis = self._analyze_population_demographics(dataset_id, filtered_data)
            else:
                analysis = self._analyze_general_trends(dataset_id, filtered_data, condition)
            
            longitudinal_data[dataset_id] = {
                **visit_info,
                "analysis": analysis,
                "sample_size": len(filtered_data)
            }
        
        return {
            "condition": condition,
            "age_filter": age_range,
            "visits_analyzed": len(longitudinal_data),
            "longitudinal_data": longitudinal_data,
            "summary": self._create_longitudinal_summary(longitudinal_data, condition)
        }
    
    def _analyze_menopause_progression(self, dataset_id: str, data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze menopause progression for a specific visit."""
        
        analysis = {
            "visit": self.dataset_info[dataset_id]["visit"],
            "period": self.dataset_info[dataset_id]["period"]
        }
        
        # Age statistics
        if 'age_std' in data.columns:
            ages = data['age_std'].dropna()
            analysis["age_stats"] = {
                "mean": float(ages.mean()),
                "median": float(ages.median()),
                "std": float(ages.std()),
                "range": [float(ages.min()), float(ages.max())]
            }
        
        # Menopause-related variables analysis
        meno_vars = self.dataset_info[dataset_id]["variable_categories"]["menopause_columns"]
        if meno_vars:
            analysis["menopause_variables"] = {
                "available": meno_vars[:10],  # First 10
                "total_count": len(meno_vars)
            }
        
        # Ethnicity breakdown
        if 'ethnicity_std' in data.columns:
            ethnicity_counts = data['ethnicity_std'].value_counts().to_dict()
            analysis["ethnicity_distribution"] = {
                str(k): int(v) for k, v in ethnicity_counts.items() if pd.notna(k)
            }
        
        return analysis
    
    def _analyze_hormone_trajectories(self, dataset_id: str, data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze hormone trajectories for a specific visit."""
        
        analysis = {
            "visit": self.dataset_info[dataset_id]["visit"],
            "period": self.dataset_info[dataset_id]["period"]
        }
        
        # Hormone variables analysis
        hormone_vars = self.dataset_info[dataset_id]["variable_categories"]["hormone_columns"]
        
        if hormone_vars:
            analysis["hormone_variables"] = {
                "available": hormone_vars,
                "total_count": len(hormone_vars)
            }
            
            # Analyze specific hormone patterns
            hormone_stats = {}
            for var in hormone_vars[:5]:  # Analyze first 5 hormone variables
                try:
                    numeric_values = pd.to_numeric(data[var], errors='coerce').dropna()
                    if len(numeric_values) > 0:
                        hormone_stats[var] = {
                            "n_valid": len(numeric_values),
                            "mean": float(numeric_values.mean()),
                            "median": float(numeric_values.median()),
                            "std": float(numeric_values.std()),
                            "percentiles": {
                                "25th": float(numeric_values.quantile(0.25)),
                                "75th": float(numeric_values.quantile(0.75))
                            }
                        }
                except:
                    continue
            
            if hormone_stats:
                analysis["hormone_statistics"] = hormone_stats
        
        return analysis
    
    def _analyze_population_demographics(self, dataset_id: str, data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze population demographics for a specific visit."""
        
        analysis = {
            "visit": self.dataset_info[dataset_id]["visit"],
            "period": self.dataset_info[dataset_id]["period"],
            "total_participants": len(data)
        }
        
        # Age distribution
        if 'age_std' in data.columns:
            ages = data['age_std'].dropna()
            analysis["age_distribution"] = {
                "mean": float(ages.mean()),
                "by_decade": {
                    "40s": len(ages[(ages >= 40) & (ages < 50)]),
                    "50s": len(ages[(ages >= 50) & (ages < 60)]),
                    "60s": len(ages[(ages >= 60) & (ages < 70)])
                }
            }
        
        # Ethnicity analysis
        if 'ethnicity_std' in data.columns:
            ethnicity_stats = {}
            for ethnicity in data['ethnicity_std'].dropna().unique():
                ethnic_subset = data[data['ethnicity_std'] == ethnicity]
                ethnicity_stats[ethnicity] = {
                    "count": len(ethnic_subset),
                    "percentage": float(len(ethnic_subset) / len(data) * 100),
                    "mean_age": float(ethnic_subset['age_std'].mean()) if 'age_std' in ethnic_subset else None
                }
            
            analysis["ethnicity_breakdown"] = ethnicity_stats
        
        return analysis
    
    def _analyze_general_trends(self, dataset_id: str, data: pd.DataFrame, condition: str) -> Dict[str, Any]:
        """Analyze general trends for any condition."""
        
        return {
            "visit": self.dataset_info[dataset_id]["visit"],
            "period": self.dataset_info[dataset_id]["period"],
            "condition": condition,
            "sample_size": len(data),
            "variables_available": len(data.columns),
            "note": f"General analysis for {condition} in {self.dataset_info[dataset_id]['visit']}"
        }
    
    def _create_longitudinal_summary(self, longitudinal_data: Dict, condition: str) -> Dict[str, Any]:
        """Create summary of longitudinal analysis."""
        
        visits = sorted(longitudinal_data.keys(), 
                       key=lambda x: longitudinal_data[x]["period"])
        
        summary = {
            "condition": condition,
            "visits_included": len(visits),
            "date_range": f"{longitudinal_data[visits[0]]['period']} to {longitudinal_data[visits[-1]]['period']}",
            "total_unique_visits": len(visits)
        }
        
        # Calculate trends if we have multiple visits
        if len(visits) > 1:
            sample_sizes = [longitudinal_data[v]["sample_size"] for v in visits]
            summary["sample_size_trend"] = {
                "visits": [longitudinal_data[v]["visit"] for v in visits],
                "sizes": sample_sizes,
                "total_observations": sum(sample_sizes)
            }
        
        return summary
    
    def search_variables_across_datasets(self, search_term: str) -> Dict[str, List[str]]:
        """Search for variables across all loaded datasets."""
        
        results = {}
        
        for dataset_id, data in self.datasets.items():
            matching_vars = [col for col in data.columns if search_term.upper() in col.upper()]
            if matching_vars:
                results[dataset_id] = {
                    "visit": self.dataset_info[dataset_id]["visit"],
                    "period": self.dataset_info[dataset_id]["period"],
                    "variables": matching_vars,
                    "count": len(matching_vars)
                }
        
        return results
    
    def get_cross_visit_variable_analysis(self, variable_pattern: str) -> Dict[str, Any]:
        """Analyze how variables change across visits."""
        
        cross_visit_data = {}
        
        for dataset_id, data in self.datasets.items():
            matching_vars = [col for col in data.columns if variable_pattern.upper() in col.upper()]
            
            if matching_vars:
                var_analysis = {}
                for var in matching_vars[:3]:  # Analyze first 3 matches
                    try:
                        numeric_data = pd.to_numeric(data[var], errors='coerce').dropna()
                        if len(numeric_data) > 0:
                            var_analysis[var] = {
                                "n": len(numeric_data),
                                "mean": float(numeric_data.mean()),
                                "std": float(numeric_data.std())
                            }
                    except:
                        continue
                
                cross_visit_data[dataset_id] = {
                    "visit": self.dataset_info[dataset_id]["visit"],
                    "period": self.dataset_info[dataset_id]["period"],
                    "variables_found": matching_vars,
                    "analysis": var_analysis
                }
        
        return {
            "variable_pattern": variable_pattern,
            "visits_with_data": len(cross_visit_data),
            "cross_visit_analysis": cross_visit_data
        }


# Global multi-dataset integration instance
multi_dataset_integration = MultiDatasetIntegration()