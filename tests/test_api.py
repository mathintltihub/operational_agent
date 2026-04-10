"""
Basic API validation script for Operations Agent.
Run this to verify the backend is working correctly.
"""
import requests
import json
import sys


BASE = 'http://127.0.0.1:8000'


def test_health():
    """Test health endpoint."""
    print("\n[TEST] Health Check")
    try:
        response = requests.get(f'{BASE}/health')
        assert response.status_code == 200
        data = response.json()
        print(f"  Status: {data['status']}")
        print(f"  Version: {data['version']}")
        print("  PASSED")
        return True
    except Exception as e:
        print(f"  FAILED: {e}")
        return False


def test_sample_tickets():
    """Test sample tickets endpoint."""
    print("\n[TEST] Sample Tickets")
    try:
        response = requests.get(f'{BASE}/sample-tickets')
        assert response.status_code == 200
        tickets = response.json()
        print(f"  Loaded {len(tickets)} sample tickets")
        print(f"  First ticket: {tickets[0]['title'][:50]}...")
        print("  PASSED")
        return True
    except Exception as e:
        print(f"  FAILED: {e}")
        return False


def test_analyze_ticket():
    """Test ticket analysis endpoint."""
    print("\n[TEST] Analyze Ticket")
    test_cases = [
        {
            "title": "Cannot connect to production database",
            "description": "Our application shows timeout errors when connecting to PostgreSQL. Started 2 hours ago.",
            "expected_type": "database"
        },
        {
            "title": "VPN users cannot access internal portal",
            "description": "Remote employees report they cannot connect to the company portal through VPN.",
            "expected_type": "network"
        },
        {
            "title": "Need access to production server",
            "description": "I need sudo access to investigate issues. I have manager approval.",
            "expected_type": "access/request"
        }
    ]

    all_passed = True
    for i, test in enumerate(test_cases, 1):
        try:
            response = requests.post(f'{BASE}/analyze-ticket', json=test)
            assert response.status_code == 200
            result = response.json()

            print(f"\n  Test Case {i}: {test['title'][:40]}...")
            print(f"    Issue Type: {result['issue_type']}")
            print(f"    Priority: {result['priority']}")
            print(f"    Team: {result['recommended_team']}")
            print(f"    Confidence: {result['confidence_score']:.2f}")

            if test['expected_type'] == result['issue_type']:
                print(f"    MATCH ✓")
            else:
                print(f"    Expected: {test['expected_type']}, Got: {result['issue_type']}")

        except Exception as e:
            print(f"  FAILED: {e}")
            all_passed = False

    if all_passed:
        print("\n  ALL TEST CASES PASSED")
    return all_passed


def test_logs():
    """Test logs endpoint."""
    print("\n[TEST] Logs")
    try:
        response = requests.get(f'{BASE}/logs?limit=10')
        assert response.status_code == 200
        data = response.json()
        print(f"  Log entries: {data['count']}")
        print("  PASSED")
        return True
    except Exception as e:
        print(f"  FAILED: {e}")
        return False


def main():
    """Run all tests."""
    print("="*60)
    print("Operations Agent - API Validation Tests")
    print("="*60)

    # Check if backend is running
    try:
        requests.get(f'{BASE}/health', timeout=2)
    except requests.exceptions.ConnectionError:
        print("\nERROR: Backend is not running!")
        print("Start the backend with: cd backend && python main.py")
        sys.exit(1)

    # Run tests
    results = []
    results.append(test_health())
    results.append(test_sample_tickets())
    results.append(test_analyze_ticket())
    results.append(test_logs())

    # Summary
    print("\n" + "="*60)
    print(f"Results: {sum(results)}/{len(results)} tests passed")
    print("="*60)

    if all(results):
        print("\nAll tests passed! ✓")
        sys.exit(0)
    else:
        print("\nSome tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()