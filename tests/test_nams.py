#!/usr/bin/env python
"""
Test suite for NAMS MCP Server

This script tests the NAMS position statements MCP server functionality.
"""

import asyncio
import sys
from servers.nams_server import (
    parse_position_statements,
    search_protocols,
    get_protocol_content,
    get_known_position_statements,
)


async def test_parse_position_statements():
    """Test parsing position statements from NAMS website."""
    print("\n" + "="*60)
    print("TEST 1: Parse Position Statements")
    print("="*60)

    try:
        statements = await parse_position_statements()
        print(f"\n✓ Successfully retrieved {len(statements)} position statements")

        if statements:
            print("\nFirst 3 statements:")
            for i, stmt in enumerate(statements[:3], 1):
                print(f"\n{i}. {stmt['title']}")
                print(f"   Type: {stmt['type']}")
                print(f"   URL: {stmt['url'][:80]}...")
                if stmt.get('description'):
                    print(f"   Description: {stmt['description'][:100]}...")

        return True
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        return False


async def test_known_position_statements():
    """Test the curated list of known position statements."""
    print("\n" + "="*60)
    print("TEST 2: Known Position Statements (Fallback)")
    print("="*60)

    try:
        statements = get_known_position_statements()
        print(f"\n✓ Retrieved {len(statements)} known position statements")

        print("\nKnown statements:")
        for i, stmt in enumerate(statements, 1):
            print(f"\n{i}. {stmt['title']}")
            print(f"   Topic: {stmt.get('topic', 'N/A')}")
            print(f"   Type: {stmt['type']}")

        return True
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        return False


async def test_search_protocols():
    """Test searching protocols by keyword."""
    print("\n" + "="*60)
    print("TEST 3: Search Protocols")
    print("="*60)

    search_terms = [
        ("hormone therapy", None),
        ("osteoporosis", None),
        ("vasomotor", None),
        ("hot flashes", None),
    ]

    all_passed = True

    for query, topic in search_terms:
        try:
            print(f"\nSearching for: '{query}'")
            results = await search_protocols(query, topic)
            print(f"✓ Found {len(results)} results")

            if results:
                print(f"  Top result: {results[0]['title']}")
        except Exception as e:
            print(f"✗ Error searching for '{query}': {str(e)}")
            all_passed = False

    return all_passed


async def test_search_with_topic_filter():
    """Test searching with topic filter."""
    print("\n" + "="*60)
    print("TEST 4: Search with Topic Filter")
    print("="*60)

    try:
        query = "management"
        topic = "hormone therapy"
        print(f"\nSearching for: '{query}' with topic filter: '{topic}'")
        results = await search_protocols(query, topic)
        print(f"✓ Found {len(results)} results with topic filter")

        if results:
            print("\nResults:")
            for i, result in enumerate(results[:3], 1):
                print(f"{i}. {result['title']}")
                print(f"   Topic: {result.get('topic', 'N/A')}")

        return True
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        return False


async def test_get_protocol_content():
    """Test retrieving protocol content."""
    print("\n" + "="*60)
    print("TEST 5: Get Protocol Content")
    print("="*60)

    # Test with a known PDF URL
    pdf_url = "https://menopause.org/wp-content/uploads/professional/nams-2022-hormone-therapy-position-statement.pdf"

    try:
        print(f"\nTesting PDF URL: {pdf_url[:60]}...")
        content = await get_protocol_content(pdf_url)
        print(f"✓ Retrieved content")
        print(f"  Title: {content['title']}")
        print(f"  Content Type: {content['content_type']}")
        print(f"  Word Count: {content['word_count']}")

        return True
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        return False


async def test_comprehensive():
    """Run comprehensive test of search and retrieve workflow."""
    print("\n" + "="*60)
    print("TEST 6: Comprehensive Workflow")
    print("="*60)

    try:
        # Step 1: Search for hormone therapy documents
        print("\nStep 1: Searching for 'hormone therapy'...")
        results = await search_protocols("hormone therapy")
        print(f"✓ Found {len(results)} results")

        if not results:
            print("✗ No results found, cannot continue test")
            return False

        # Step 2: Get details of first result
        print(f"\nStep 2: Retrieving content for: {results[0]['title']}")
        content = await get_protocol_content(results[0]['url'])
        print(f"✓ Retrieved content")
        print(f"  Word count: {content['word_count']}")
        print(f"  Content type: {content['content_type']}")

        return True
    except Exception as e:
        print(f"\n✗ Error in comprehensive test: {str(e)}")
        return False


async def run_all_tests():
    """Run all tests and report results."""
    print("\n" + "="*60)
    print("NAMS MCP SERVER TEST SUITE")
    print("="*60)

    tests = [
        ("Parse Position Statements", test_parse_position_statements),
        ("Known Position Statements", test_known_position_statements),
        ("Search Protocols", test_search_protocols),
        ("Search with Topic Filter", test_search_with_topic_filter),
        ("Get Protocol Content", test_get_protocol_content),
        ("Comprehensive Workflow", test_comprehensive),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ Test '{test_name}' crashed: {str(e)}")
            results.append((test_name, False))

    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(run_all_tests())
    sys.exit(exit_code)
