#!/usr/bin/env python3
"""Setup for CasterlyGit portfolio skills."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="casterly-skills",
    version="0.1.0",
    description="Reusable AI skills for web automation, research, and task execution",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Tarun Shankar",
    author_email="tarun@casterlygit.com",
    url="https://github.com/CasterlyGit/casterlygit.github.io",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "anthropic>=0.18.0",
    ],
    entry_points={
        "console_scripts": [
            "autobrowse=skills.autobrowse.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
