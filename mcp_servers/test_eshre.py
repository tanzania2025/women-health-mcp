#!/usr/bin/env python3
"""
Test script for ESHRE Guidelines MCP Server

This script tests the functionality of the ESHRE server by:
1. Listing all available guidelines
2. Searching for specific topics
3. Retrieving full guideline content
"""

import asyncio
import sys
from eshre_server import (
    parse_guidelines_list,
    search_guidelines,
    get_guideline_content
)


async def test_list_guidelines():
    """Test listing all guidelines."""
    print("\n" + "="*80)
    print("TEST 1: Listing all ESHRE guidelines")
    print("="*80)

    try:
        guidelines = await parse_guidelines_list()
        print(f"\n✓ Successfully retrieved {len(guidelines)} guidelines\n")

        # Display first 10 guidelines
        print("First 10 guidelines:")
        for i, guideline in enumerate(guidelines[:10], 1):
            print(f"\n{i}. {guideline['title']}")
            if guideline['description']:
                print(f"   Description: {guideline['description'][:100]}...")
            print(f"   URL: {guideline['url']}")

        if len(guidelines) > 10:
            print(f"\n... and {len(guidelines) - 10} more guidelines")

        return True
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        return False


async def test_search_guidelines():
    """Test searching for guidelines."""
    print("\n" + "="*80)
    print("TEST 2: Searching for guidelines")
    print("="*80)

    search_terms = ["endometriosis", "IVF", "PCOS", "fertility preservation"]

    all_passed = True
    for term in search_terms:
        print(f"\nSearching for: '{term}'")
        try:
            results = await search_guidelines(term)
            print(f"✓ Found {len(results)} results")

            for i, result in enumerate(results[:3], 1):
                print(f"  {i}. {result['title']}")
        except Exception as e:
            print(f"✗ Error searching for '{term}': {str(e)}")
            all_passed = False

    return all_passed


async def test_get_guideline_content():
    """Test retrieving full guideline content."""
    print("\n" + "="*80)
    print("TEST 3: Retrieving guideline content")
    print("="*80)

    # First, get a guideline URL
    try:
        guidelines = await parse_guidelines_list()
        if not guidelines:
            print("✗ No guidelines found to test with")
            return False

        # Test with the first guideline
        test_guideline = guidelines[0]
        print(f"\nRetrieving: {test_guideline['title']}")
        print(f"URL: {test_guideline['url']}")

        content = await get_guideline_content(test_guideline['url'])

        print(f"\n✓ Successfully retrieved guideline content")
        print(f"  Title: {content['title']}")
        print(f"  Date: {content['date']}")
        print(f"  Word count: {content['word_count']}")
        print(f"  Number of downloads: {len(content['downloads'])}")

        if content['downloads']:
            print(f"\n  Download links:")
            for i, dl in enumerate(content['downloads'][:5], 1):
                print(f"    {i}. {dl['title']}")
                print(f"       {dl['url']}")

        # Display first 500 characters of content
        if content['content']:
            print(f"\n  Content preview (first 500 chars):")
            print(f"  {content['content'][:500]}...")

        return True
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("ESHRE MCP Server Test Suite")
    print("="*80)

    results = []

    # Run tests
    results.append(("List Guidelines", await test_list_guidelines()))
    results.append(("Search Guidelines", await test_search_guidelines()))
    results.append(("Get Guideline Content", await test_get_guideline_content()))

    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n✓ All tests passed successfully!")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
