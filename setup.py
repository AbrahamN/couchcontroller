"""
CouchController Setup Configuration
"""

from setuptools import setup, find_packages
import os

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read version from __init__.py
version = {}
with open("couchcontroller/__init__.py", "r", encoding="utf-8") as f:
    for line in f:
        if line.startswith("__version__"):
            exec(line, version)
            break

setup(
    name="couchcontroller",
    version=version.get("__version__", "0.1.0"),
    author="Abraham N",
    description="Local-first network game controller sharing for couch co-op games",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/abrahamn/couchcontroller",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Games/Entertainment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: Microsoft :: Windows :: Windows 10",
        "Operating System :: Microsoft :: Windows :: Windows 11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.21.0",
        "opencv-python>=4.5.0",
        "mss>=6.1.0",
        "Pillow>=9.0.0",
        "pygame>=2.1.0",
        "av>=10.0.0",
    ],
    extras_require={
        "host": [
            "vgamepad>=0.0.8",  # Windows only, for virtual controllers
        ],
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "couchcontroller-host=couchcontroller.cli.host:main",
            "couchcontroller-client=couchcontroller.cli.client:main",
            "couchcontroller-test=couchcontroller.cli.test:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="game streaming controller network multiplayer couch coop lan",
    project_urls={
        "Bug Reports": "https://github.com/abrahamn/couchcontroller/issues",
        "Source": "https://github.com/abrahamn/couchcontroller",
        "Documentation": "https://github.com/abrahamn/couchcontroller#readme",
    },
)
