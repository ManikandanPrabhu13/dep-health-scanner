# Dependency Health Scanner

Scans any public GitHub repository, checks each dependency against 
PyPI/npm registry, and generates an HTML health report showing 
outdated, up-to-date, and unknown packages.

## Tech Stack
Python, GitHub REST API, PyPI API, npm Registry API

## What it does
- Takes any public GitHub repo URL as input
- Fetches requirements.txt or package.json automatically
- Checks each package version against live PyPI/npm registry
- Outputs a colour-coded HTML report: outdated / up-to-date / not found

## Usage
pip install -r requirements.txt
python scanner.py <github_repo_url>

## Status
In Progress — core scanner and HTML report generation complete.
Next: CLI flags, batch repo scanning