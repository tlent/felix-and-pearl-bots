from setuptools import setup, find_packages

setup(
    name="felix-bot",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "boto3",
        "anthropic",
        "requests",
        "python-dateutil",
        "python-dotenv",
        "beautifulsoup4",
        "pytz",
    ],
)
