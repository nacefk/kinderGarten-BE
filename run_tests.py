#!/usr/bin/env python
"""
Test runner script with coverage reporting
Usage: python run_tests.py [--coverage] [--html] [--specific-tests]
"""
import subprocess
import sys
import argparse
from pathlib import Path


def run_tests(coverage=False, html_report=False, specific_tests=None):
    """Run the test suite"""

    cmd = ["pytest"]

    # Add test path
    if specific_tests:
        cmd.extend(specific_tests)
    else:
        cmd.append("tests.py")

    # Add verbosity
    cmd.extend(["-v", "--tb=short"])

    # Add coverage if requested
    if coverage:
        cmd.extend(
            [
                "--cov=core",
                "--cov=children",
                "--cov=attendance",
                "--cov=reports",
                "--cov=planning",
                "--cov=chat",
                "--cov=accounts",
                "--cov-report=term-missing",
            ]
        )

        if html_report:
            cmd.append("--cov-report=html")

    # Add color output
    cmd.append("--color=yes")

    print(f"Running: {' '.join(cmd)}")
    print("-" * 80)

    result = subprocess.run(cmd)
    return result.returncode


def main():
    parser = argparse.ArgumentParser(description="Run Django tests with coverage")
    parser.add_argument(
        "--coverage", "-c", action="store_true", help="Enable coverage reporting"
    )
    parser.add_argument(
        "--html", action="store_true", help="Generate HTML coverage report"
    )
    parser.add_argument("--tests", "-t", nargs="+", help="Specific test names to run")

    args = parser.parse_args()

    return_code = run_tests(
        coverage=args.coverage, html_report=args.html, specific_tests=args.tests
    )

    if args.coverage and args.html:
        print("\n✓ HTML coverage report generated in htmlcov/index.html")

    sys.exit(return_code)


if __name__ == "__main__":
    main()
