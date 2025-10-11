#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kite Laundry Code Quality Tool
Checks and optionally fixes common code quality issues
"""

import os
import subprocess
import sys
from pathlib import Path


class CodeQualityChecker:
    def __init__(self, project_root="."):
        self.project_root = Path(project_root)
        self.core_dir = self.project_root / "Core"

    def check_dependencies(self):
        """Check if required tools are installed"""
        tools = {
            "flake8": "pip install flake8",
            "black": "pip install black",
            "isort": "pip install isort",
            "autopep8": "pip install autopep8",
        }

        missing = []
        for tool, install_cmd in tools.items():
            try:
                subprocess.run([tool, "--version"], capture_output=True, check=True)
                print(f"✓ {tool} installed")
            except (subprocess.CalledProcessError, FileNotFoundError):
                print(f"✗ {tool} not found - Install: {install_cmd}")
                missing.append(tool)

        return len(missing) == 0

    def run_flake8(self, fix=False):
        """Run flake8 to check for issues"""
        print("\n" + "=" * 60)
        print("RUNNING FLAKE8 CHECKS")
        print("=" * 60)

        cmd = [
            "flake8",
            str(self.core_dir),
            "--max-line-length=88",
            "--extend-ignore=E203,W503",  # Black-compatible ignores
            "--statistics",
            "--count",
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)

        return result.returncode == 0

    def run_autopep8(self, dry_run=True):
        """Run autopep8 to auto-fix PEP8 issues"""
        mode = "CHECK" if dry_run else "FIX"
        print(f"\n{'='*60}")
        print(f"AUTOPEP8 - {mode} MODE")
        print("=" * 60)

        cmd = [
            "autopep8",
            "--recursive",
            "--max-line-length=88",
            "--aggressive",
            "--aggressive",
        ]

        if dry_run:
            cmd.append("--diff")
        else:
            cmd.append("--in-place")

        cmd.append(str(self.core_dir))

        result = subprocess.run(cmd, capture_output=True, text=True)

        if dry_run and result.stdout:
            print("Proposed changes preview (first 2000 chars):")
            print(result.stdout[:2000])
            if len(result.stdout) > 2000:
                print(f"\n... and {len(result.stdout) - 2000} more characters")
        elif not dry_run:
            print("✓ Files updated in-place")
        else:
            print("✓ No changes needed")

        return result.returncode == 0

    def run_black(self, check_only=True):
        """Run Black formatter"""
        mode = "CHECK" if check_only else "FORMAT"
        print(f"\n{'='*60}")
        print(f"BLACK - {mode} MODE")
        print("=" * 60)

        cmd = ["black"]

        if check_only:
            cmd.extend(["--check", "--diff"])

        cmd.extend(["--line-length=88", str(self.core_dir)])

        result = subprocess.run(cmd, capture_output=True, text=True)
        print(result.stdout)

        if result.returncode != 0 and check_only:
            print("⚠ Black would reformat some files")
        elif result.returncode == 0:
            print("✓ All files properly formatted")

        return result.returncode == 0

    def run_isort(self, check_only=True):
        """Run isort to organize imports"""
        mode = "CHECK" if check_only else "FIX"
        print(f"\n{'='*60}")
        print(f"ISORT - {mode} MODE")
        print("=" * 60)

        cmd = ["isort"]

        if check_only:
            cmd.extend(["--check-only", "--diff"])

        cmd.extend(["--profile=black", str(self.core_dir)])  # Compatible with Black

        result = subprocess.run(cmd, capture_output=True, text=True)
        print(result.stdout)

        if result.returncode != 0 and check_only:
            print("⚠ Import order needs fixing")
        elif result.returncode == 0:
            print("✓ Imports properly organized")

        return result.returncode == 0

    def check_critical_issues(self):
        """Check for critical issues that need manual fixing"""
        print("\n" + "=" * 60)
        print("CRITICAL ISSUES REQUIRING MANUAL FIXES")
        print("=" * 60)

        critical_patterns = [
            ("F821", "Undefined names"),
            ("F811", "Redefined functions"),
            ("E999", "Syntax errors"),
        ]

        cmd = [
            "flake8",
            str(self.core_dir),
            "--select=" + ",".join([p[0] for p in critical_patterns]),
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.stdout:
            print("⚠ CRITICAL ISSUES FOUND:\n")
            print(result.stdout)
            print("\nThese require manual intervention!")
            return False
        else:
            print("✓ No critical issues found")
            return True

    def generate_report(self):
        """Generate a summary report"""
        print("\n" + "=" * 60)
        print("SUMMARY REPORT")
        print("=" * 60)

        # Get issue counts by category
        result = subprocess.run(
            ["flake8", str(self.core_dir), "--statistics"],
            capture_output=True,
            text=True,
        )

        if result.stdout:
            print(result.stdout)


def main():
    print(
        """
╔══════════════════════════════════════════════════════════╗
║     KITE LAUNDRY CODE QUALITY CHECKER & FIXER            ║
║     Made for macOS/BSD environments                       ║
╚══════════════════════════════════════════════════════════╝
    """
    )

    if len(sys.argv) > 1:
        project_root = sys.argv[1]
    else:
        project_root = "."

    checker = CodeQualityChecker(project_root)

    # Check dependencies
    if not checker.check_dependencies():
        print("\n⚠ Please install missing dependencies first")
        sys.exit(1)

    # Interactive menu
    while True:
        print("\n" + "=" * 60)
        print("OPTIONS:")
        print("=" * 60)
        print("1. Check all issues (no changes)")
        print("2. Check critical issues only")
        print("3. Fix with autopep8 (aggressive)")
        print("4. Fix with Black formatter")
        print("5. Fix import order (isort)")
        print("6. Fix everything (autopep8 + black + isort)")
        print("7. Generate full report")
        print("8. Exit")
        print("=" * 60)

        choice = input("\nSelect option (1-8): ").strip()

        if choice == "1":
            checker.run_flake8()
            checker.run_black(check_only=True)
            checker.run_isort(check_only=True)

        elif choice == "2":
            checker.check_critical_issues()

        elif choice == "3":
            confirm = input("Apply autopep8 fixes? (yes/no): ")
            if confirm.lower() == "yes":
                checker.run_autopep8(dry_run=False)
                print("✓ Applied! Run flake8 again to verify.")

        elif choice == "4":
            confirm = input("Apply Black formatting? (yes/no): ")
            if confirm.lower() == "yes":
                checker.run_black(check_only=False)
                print("✓ Applied! All files formatted.")

        elif choice == "5":
            confirm = input("Fix import order with isort? (yes/no): ")
            if confirm.lower() == "yes":
                checker.run_isort(check_only=False)
                print("✓ Applied! Imports reorganized.")

        elif choice == "6":
            confirm = input("Apply ALL fixes? (yes/no): ")
            if confirm.lower() == "yes":
                print("\n🔧 Applying all fixes...")
                checker.run_isort(check_only=False)
                checker.run_autopep8(dry_run=False)
                checker.run_black(check_only=False)
                print("\n✓ ALL FIXES APPLIED!")
                print("Run option 1 to verify results.")

        elif choice == "7":
            checker.generate_report()

        elif choice == "8":
            print("\n👋 Goodbye!")
            break

        else:
            print("Invalid option. Please try again.")


if __name__ == "__main__":
    main()
