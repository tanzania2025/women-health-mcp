"""
Hugging Face Integration - Mock biomedical model for ranking research papers
"""
from typing import List, Dict, Any


class MockBiomedicalModel:
    """Mock biomedical language model for demo purposes."""
    
    def __init__(self, model_name: str = "BiomedBERT-base"):
        self.model_name = model_name
        self.loaded = True
    
    def encode(self, text: str) -> List[float]:
        """Mock encoding - returns fake embeddings."""
        return [0.1 * len(text), 0.2, 0.3, 0.4, 0.5]
    
    def similarity_score(self, text1: str, text2: str) -> float:
        """Calculate mock similarity between two texts."""
        # Simple keyword matching for demo
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
            
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)


def load_biomedical_model() -> MockBiomedicalModel:
    """
    Load a mock biomedical language model.
    
    Returns:
        Mock model object
    """
    print("  → Loading biomedical model (BiomedBERT-base)...")
    model = MockBiomedicalModel()
    print("  ✓ Model loaded successfully")
    return model


def rank_papers_by_relevance(query: str, papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Rank research papers by relevance to the clinical query.
    
    Args:
        query: Clinical question
        papers: List of paper dictionaries
        
    Returns:
        Papers sorted by relevance score
    """
    model = MockBiomedicalModel()
    
    # Calculate relevance scores
    scored_papers = []
    query_terms = set(query.lower().split())
    
    for paper in papers:
        # Combine title and findings for relevance calculation
        paper_text = f"{paper['title']} {paper.get('findings', '')}".lower()
        
        # Enhanced scoring based on key terms
        score = 0.0
        
        # Direct keyword matches
        for term in query_terms:
            if term in paper_text:
                score += 0.2
        
        # Special relevance boosts
        if "amh" in query.lower() and "amh" in paper_text:
            score += 0.3
        if "ivf" in query.lower() and "ivf" in paper_text:
            score += 0.3
        if "success" in query.lower() and ("success" in paper_text or "outcome" in paper_text):
            score += 0.2
        if "age" in query.lower() and "age" in paper_text:
            score += 0.2
        
        # Recency bonus
        if paper.get('year', 0) >= 2024:
            score += 0.1
        
        # Cap score at 1.0
        score = min(score, 1.0)
        
        scored_paper = paper.copy()
        scored_paper['relevance_score'] = round(score, 2)
        scored_papers.append(scored_paper)
    
    # Sort by relevance score (highest first)
    ranked_papers = sorted(scored_papers, key=lambda x: x['relevance_score'], reverse=True)
    
    return ranked_papers


def display_ranked_papers(papers: List[Dict[str, Any]]) -> None:
    """Display papers with their relevance scores."""
    for i, paper in enumerate(papers, 1):
        print(f"  {i}. [{paper['relevance_score']:.2f}] {paper['title']} ({paper['year']})")
        if 'findings' in paper:
            print(f"     Key findings: {paper['findings'][:80]}...")


if __name__ == "__main__":
    # Test the integration
    print("=== HUGGING FACE INTEGRATION TEST ===\n")
    
    # Test loading model
    model = load_biomedical_model()
    print(f"\nModel info: {model.model_name} (loaded: {model.loaded})")
    
    # Test paper ranking
    test_papers = [
        {
            "title": "AMH levels and reproductive outcomes: systematic review",
            "year": 2024,
            "findings": "AMH is a reliable marker for ovarian reserve"
        },
        {
            "title": "General fertility guidelines update",
            "year": 2023,
            "findings": "Comprehensive update on fertility treatment approaches"
        },
        {
            "title": "IVF success in low AMH: what we learned",
            "year": 2023,
            "findings": "Low AMH alone should not exclude patients from IVF"
        }
    ]
    
    query = "Should I do IVF with low AMH?"
    print(f"\nQuery: '{query}'")
    print("\nRanking papers by relevance...")
    
    ranked = rank_papers_by_relevance(query, test_papers)
    display_ranked_papers(ranked)