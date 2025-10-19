#!/usr/bin/env python3
"""
PubMed Search Client
Simplified client for searching PubMed literature without MCP dependencies
"""

import httpx
import xml.etree.ElementTree as ET
from typing import List, Dict, Any
import os

class PubMedClient:
    """Client for searching PubMed literature."""
    
    def __init__(self):
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
        self.api_key = os.getenv("NCBI_API_KEY")  # Optional for higher rate limits
    
    async def search_articles(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search PubMed for articles."""
        # Mock implementation for demo - in production, this would use PubMed E-utilities API
        mock_results = [
            {
                "title": "Anti-Müllerian hormone as a predictor of natural menopause",
                "authors": "Freeman EW, Sammel MD, Lin H, Gracia CR",
                "journal": "Journal of Clinical Endocrinology & Metabolism",
                "year": "2012",
                "pmid": "22422826",
                "doi": "10.1210/jc.2011-1951",
                "abstract": "Context: Anti-Müllerian hormone (AMH) is a marker of ovarian reserve that declines with age and may predict the timing of menopause. Our objective was to determine whether AMH can predict natural menopause and to compare its predictive ability with that of other hormones.",
                "relevance": self._calculate_relevance(query, "AMH menopause prediction ovarian reserve"),
                "citation_count": 284
            },
            {
                "title": "AMH and ovarian reserve: update on assessing ovarian function",
                "authors": "Broer SL, Broekmans FJ, Laven JS, Fauser BC",
                "journal": "Journal of Clinical Endocrinology & Metabolism",
                "year": "2014", 
                "pmid": "24423323",
                "doi": "10.1210/jc.2013-4204",
                "abstract": "Anti-Müllerian hormone (AMH) has emerged as an important biomarker of ovarian reserve and reproductive aging. This review summarizes current evidence regarding AMH as a marker of ovarian function and its clinical applications.",
                "relevance": self._calculate_relevance(query, "AMH ovarian reserve biomarker"),
                "citation_count": 456
            },
            {
                "title": "Reproductive aging and ovarian function: is the early follicular phase FSH rise necessary to maintain adequate secretory function?",
                "authors": "Welt CK, McNicholl DJ, Taylor AE, Hall JE",
                "journal": "Human Reproduction",
                "year": "1999",
                "pmid": "10362678",
                "doi": "10.1093/humrep/14.11.2723",
                "abstract": "The reproductive aging process in women is characterized by declining fertility and eventual cessation of menses. This study examines the relationship between FSH levels and ovarian function during reproductive aging.",
                "relevance": self._calculate_relevance(query, "reproductive aging FSH ovarian function"),
                "citation_count": 198
            },
            {
                "title": "Age-specific serum anti-Müllerian hormone values for 17,120 women presenting to fertility centers within the United States",
                "authors": "Seifer DB, Baker VL, Leader B",
                "journal": "Fertility and Sterility",
                "year": "2011",
                "pmid": "21481376",
                "doi": "10.1016/j.fertnstert.2011.02.008", 
                "abstract": "To establish age-specific anti-Müllerian hormone (AMH) values in women presenting to fertility centers and to assess the relationship between AMH and other measures of ovarian reserve.",
                "relevance": self._calculate_relevance(query, "AMH age specific fertility values"),
                "citation_count": 522
            }
        ]
        
        # Sort by relevance and limit results
        mock_results.sort(key=lambda x: x["relevance"], reverse=True)
        return mock_results[:max_results]
    
    def _calculate_relevance(self, query: str, article_keywords: str) -> float:
        """Calculate relevance score between query and article keywords."""
        query_words = set(query.lower().split())
        keyword_words = set(article_keywords.lower().split())
        
        # Simple relevance calculation
        overlap = len(query_words.intersection(keyword_words))
        total_query_words = len(query_words)
        
        if total_query_words == 0:
            return 0.5
        
        base_score = overlap / total_query_words
        # Add some randomness to make it more realistic
        import random
        return min(1.0, base_score + random.uniform(-0.1, 0.1))
    
    async def get_article_details(self, pmid: str) -> Dict[str, Any]:
        """Get detailed information for a specific article."""
        # Mock implementation for demo
        return {
            "pmid": pmid,
            "title": "Detailed Article Title",
            "abstract": "Full abstract text would be here...",
            "authors": ["Author 1", "Author 2", "Author 3"],
            "journal": "Journal Name",
            "publication_date": "2023-01-01",
            "keywords": ["keyword1", "keyword2", "keyword3"],
            "mesh_terms": ["MeSH Term 1", "MeSH Term 2"],
            "doi": "10.1000/example"
        }

# Global instance for easy import
pubmed_client = PubMedClient()