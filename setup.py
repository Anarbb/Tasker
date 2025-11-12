#!/usr/bin/env python3
"""Setup script for Tasker."""
from setuptools import setup

setup(
    name="tasker",
    version="1.0.0",
    description="A simple GTK4 GUI for managing cron jobs",
    author="Anas Arbaoui",
    author_email="anas@arbaoui.me",
    url="https://github.com/Anarbb/tasker",
    py_modules=["main", "cron_manager", "task_dialog"],
    data_files=[
        ("share/applications", ["me.arbaoui.tasker.desktop"]),
        ("share/tasker", ["ui.css"]),
    ],
    entry_points={
        "console_scripts": [
            "tasker=main:main",
        ],
    },
    scripts=[],
    python_requires=">=3.10",
    install_requires=[
        "PyGObject>=3.42.0",
    ],
    license="GPL-3.0-or-later",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)

