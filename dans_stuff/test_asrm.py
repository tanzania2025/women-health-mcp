#!/usr/bin/env python3
"""
Test script for ASRM MCP Server

This script tests the core functionality of the ASRM server without
requiring the full MCP protocol setup.
"""

import asyncio
import sys
from asrm_server import (
    parse_practice_documents,
    parse_ethics_opinions,
    search_guidelines,
    get_guideline_content
)


async def test_parse_practice_documents():
    """Test fetching practice documents list."""
    print("\n=== Testing Practice Documents Parsing ===")
    try:
        documents = await parse_practice_documents()
        print(f"✓ Successfully fetched {len(documents)} practice documents")

        if documents:
            print(f"\nSample document:")
            print(f"  Title: {documents[0]['title']}")
            print(f"  URL: {documents[0]['url']}")
            if documents[0]['description']:
                print(f"  Description: {documents[0]['description'][:100]}...")

        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


async def test_parse_ethics_opinions():
    """Test fetching ethics opinions list."""
    print("\n=== Testing Ethics Opinions Parsing ===")
    try:
        opinions = await parse_ethics_opinions()
        print(f"✓ Successfully fetched {len(opinions)} ethics opinions")

        if opinions:
            print(f"\nSample opinion:")
            print(f"  Title: {opinions[0]['title']}")
            print(f"  URL: {opinions[0]['url']}")

        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


async def test_search_guidelines():
    """Test searching guidelines."""
    print("\n=== Testing Guidelines Search ===")
    try:
        # Test search for common topic
        results = await search_guidelines("IVF", category=None)
        print(f"✓ Search for 'IVF' returned {len(results)} results")

        if results:
            print(f"\nSample result:")
            print(f"  Title: {results[0]['title']}")
            print(f"  Type: {results[0]['type']}")

        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


async def test_get_guideline_content():
    """Test fetching guideline content."""
    print("\n=== Testing Guideline Content Retrieval ===")
    try:
        # First get a document URL
        documents = await parse_practice_documents()

        if not documents:
            print("⚠ No documents available to test content retrieval")
            return True

        # Get content of first document
        test_url = documents[0]['url']
        print(f"Fetching content from: {test_url}")

        content = await get_guideline_content(test_url)
        print(f"✓ Successfully retrieved content")
        print(f"  Title: {content['title']}")
        print(f"  Word count: {content['word_count']}")
        print(f"  Content preview: {content['content'][:200]}...")

        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


async def main():
    """Run all tests."""
    print("=" * 60)
    print("ASRM MCP Server Test Suite")
    print("=" * 60)

    tests = [
        ("Parse Practice Documents", test_parse_practice_documents),
        ("Parse Ethics Opinions", test_parse_ethics_opinions),
        ("Search Guidelines", test_search_guidelines),
        ("Get Guideline Content", test_get_guideline_content),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ Test '{test_name}' failed with exception: {e}")
            results.append((test_name, False))

    # Print summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
