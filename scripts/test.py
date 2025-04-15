#!/usr/bin/env python3
import subprocess
import sys


def main():
    try:
        # Run linters
        print("🔍 Running linters...")
        subprocess.run(["flake8", "src", "scripts", "tests"], check=True)
        subprocess.run(["black", "--check", "src", "scripts", "tests"], check=True)
        subprocess.run(["isort", "--check-only", "src", "scripts", "tests"], check=True)
        subprocess.run(["mypy", "src", "scripts", "tests"], check=True)

        # Run tests
        print("🧪 Running tests...")
        subprocess.run(["pytest"], check=True)

        print("✅ All checks passed!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Checks failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
