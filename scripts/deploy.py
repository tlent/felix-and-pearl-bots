#!/usr/bin/env python3
import subprocess
import sys


def main():
    try:
        # Build SAM application
        print("🚀 Building SAM application...")
        subprocess.run(["sam", "build"], check=True)

        # Deploy SAM application
        print("🚀 Deploying to AWS...")
        subprocess.run(["sam", "deploy", "--guided"], check=True)

        print("✅ Deployment successful!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Deployment failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
