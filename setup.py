"""
Setup script for European Youth Portal Scraper - Professional Edition
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="european-youth-scraper",
    version="2.0.0",
    author="European Youth Portal Scraper Team",
    author_email="team@europeyouthscraper.dev",
    description="Professional web scraper for European Youth Portal opportunities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/europeyouth/scraper",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
            "pre-commit>=2.17.0",
        ],
        "viz": [
            "wordcloud>=1.9.0",
            "matplotlib>=3.5.0",
            "seaborn>=0.11.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "youth-scraper=main_professional:main",
            "european-youth-scraper=main_professional:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.json", "*.yml", "*.yaml"],
    },
    keywords=[
        "web-scraping",
        "european-youth",
        "opportunities",
        "data-analysis",
        "async",
        "database",
        "cli",
        "analytics",
    ],
    project_urls={
        "Bug Reports": "https://github.com/europeyouth/scraper/issues",
        "Source": "https://github.com/europeyouth/scraper",
        "Documentation": "https://github.com/europeyouth/scraper/wiki",
    },
) 