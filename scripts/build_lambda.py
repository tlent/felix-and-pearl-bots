#!/usr/bin/env python3
import shutil
import subprocess
import sys
from pathlib import Path


def main():
    try:
        # Clean up previous builds
        build_dir = Path("build")
        if build_dir.exists():
            shutil.rmtree(build_dir)
        build_dir.mkdir()

        # Install poetry-export-plugin if not present
        try:
            subprocess.run(
                ["poetry", "export", "--help"], check=True, capture_output=True
            )
        except subprocess.CalledProcessError:
            print("Installing poetry-export-plugin...")
            subprocess.run(
                ["poetry", "self", "add", "poetry-export-plugin"], check=True
            )

        # Export dependencies
        print("Exporting dependencies...")
        subprocess.run(
            [
                "poetry",
                "export",
                "--without-hashes",
                "-f",
                "requirements.txt",
                "-o",
                "requirements.txt",
            ],
            check=True,
        )

        # Install dependencies to build directory
        print("Installing dependencies...")
        subprocess.run(
            [
                "pip",
                "install",
                "-r",
                "requirements.txt",
                "--target",
                "build",
                "--platform",
                "manylinux2014_x86_64",
                "--implementation",
                "cp",
                "--python-version",
                "3.9",
                "--only-binary=:all:",
                "--upgrade",
            ],
            check=True,
        )

        # Copy source code
        print("Copying source code...")
        src_dir = Path("src")
        for file in src_dir.glob("**/*.py"):
            target = build_dir / file.relative_to(src_dir)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file, target)

        # Create deployment package
        print("Creating deployment package...")
        shutil.make_archive("deployment", "zip", "build")
        print("✅ Lambda deployment package created: deployment.zip")

    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
