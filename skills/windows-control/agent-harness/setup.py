#!/usr/bin/env python3
"""
cli-anything-windows-control setup.py

Windows UI Automation CLI for AI agents.

Install:
    pip install -e .

Usage:
    cli-windows-control --help
    cli-windows-control mouse click --x 100 --y 200
    cli-windows-control --json window list
"""

from setuptools import setup, find_namespace_packages

try:
    with open("cli_anything/windows_control/README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = "Windows UI Automation CLI for AI agents."

setup(
    name="cli-anything-windows-control",
    version="1.0.0",
    author="cli-anything contributors",
    author_email="",
    description="Windows UI Automation CLI harness for AI agents - full mouse, keyboard, window, system control via jingmai-agent actions.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/HKUDS/CLI-Anything",
    packages=find_namespace_packages(include=["cli_anything.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Systems Administration",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: Microsoft :: Windows",
    ],
    python_requires=">=3.10",
    install_requires=[
        "click>=8.0.0",
        "prompt-toolkit>=3.0.0",
        "pyautogui>=0.9.54",
        "pyperclip>=1.8.2",
        "Pillow>=10.0.0",
        "psutil>=5.9.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "cli-windows-control=cli_anything.windows_control.windows_control_cli:main",
        ],
    },
    package_data={
        "cli_anything.windows_control": ["skills/*.md"],
    },
    include_package_data=True,
    zip_safe=False,
)
