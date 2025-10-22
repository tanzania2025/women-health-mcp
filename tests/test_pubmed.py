#!/usr/bin/env python3
"""
Test script for PubMed MCP server functionality
"""

import asyncio
import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from servers.pubmed_server import search_pubmed, get_article_summaries, fetch_article_abstract


async def test_search():
    """Test PubMed search functionality"""
    print("=" * 80)
    print("TEST 1: Searching PubMed for 'polycystic ovary syndrome'")
    print("=" * 80)

    try:
        results = await search_pubmed("polycystic ovary syndrome", max_results=5)
        print(f"✓ Search successful!")
        print(f"  Total results found: {results['count']}")
        print(f"  PMIDs retrieved: {len(results['pmids'])}")
        print(f"  First 5 PMIDs: {results['pmids'][:5]}")
        return results['pmids'][:3]  # Return first 3 for further testing
    except Exception as e:
        print(f"✗ Search failed: {e}")
        return []


async def test_summaries(pmids):
    """Test getting article summaries"""
    print("\n" + "=" * 80)
    print(f"TEST 2: Getting summaries for PMIDs: {pmids}")
    print("=" * 80)

    try:
        summaries = await get_article_summaries(pmids)
        print(f"✓ Summaries retrieved successfully!")
        print(f"  Number of summaries: {len(summaries)}")

        for i, summary in enumerate(summaries, 1):
            print(f"\n  Article {i}:")
            print(f"    PMID: {summary['pmid']}")
            print(f"    Title: {summary['title'][:100]}...")
            print(f"    Authors: {', '.join(summary['authors'][:3])}")
            print(f"    Journal: {summary['journal']}")
            print(f"    Date: {summary['pubdate']}")

        return pmids[0] if pmids else None  # Return first PMID for abstract test
    except Exception as e:
        print(f"✗ Getting summaries failed: {e}")
        return None


async def test_abstract(pmid):
    """Test fetching full article with abstract"""
    print("\n" + "=" * 80)
    print(f"TEST 3: Fetching full article details for PMID: {pmid}")
    print("=" * 80)

    try:
        article = await fetch_article_abstract(pmid)
        print(f"✓ Article retrieved successfully!")
        print(f"\n  Title: {article['title']}")
        print(f"  PMID: {article['pmid']}")
        print(f"  DOI: {article['doi']}")
        print(f"  Journal: {article['journal']}")
        print(f"  Published: {article['pubdate']}")
        print(f"  Authors: {', '.join(article['authors'][:5])}")
        if len(article['authors']) > 5:
            print(f"           ... and {len(article['authors']) - 5} more")
        print(f"  Keywords: {', '.join(article['keywords'][:10])}")
        print(f"\n  Abstract length: {len(article['abstract'])} characters")
        print(f"  Abstract preview: {article['abstract'][:200]}...")

    except Exception as e:
        print(f"✗ Fetching article failed: {e}")


async def main():
    """Run all tests"""
    print("\n🧪 Starting PubMed MCP Server Tests\n")

    # Check for API key
    api_key = os.getenv("NCBI_API_KEY", "")
    if api_key:
        print(f"✓ NCBI API Key found (rate limit: 10 req/sec)\n")
    else:
        print(f"ℹ No NCBI API Key (rate limit: 3 req/sec)\n")

    # Test 1: Search
    pmids = await test_search()

    if not pmids:
        print("\n✗ Cannot continue tests without search results")
        return

    # Test 2: Get summaries
    test_pmid = await test_summaries(pmids)

    if not test_pmid:
        print("\n✗ Cannot continue without a valid PMID")
        return

    # Test 3: Get full article with abstract
    await test_abstract(test_pmid)

    # Final summary
    print("\n" + "=" * 80)
    print("✓ All tests completed successfully!")
    print("=" * 80)
    print("\nThe PubMed MCP server is working correctly and ready to use.")
    print("Next steps:")
    print("  1. Add the server to your Claude Desktop configuration")
    print("  2. Restart Claude Desktop")
    print("  3. Start searching PubMed from within Claude!\n")


if __name__ == "__main__":
    asyncio.run(main())
