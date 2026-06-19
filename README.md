# Dependency Health Scanner

**Status:** Developer Tooling Project • API Integration • Automated Dependency AnalysiS

A Python-based tool that scans public GitHub repositories, checks dependencies against live package registries, and generates a colour-coded HTML report highlighting outdated, up-to-date, and missing packages.

## Why I Built This

Modern software projects often rely on many third-party libraries, and keeping dependencies updated is important for maintainability and security. I built this project to gain hands-on experience in working with external APIs, parsing dependency files, and building a practical developer tool that automates dependency analysis.

## Approach

### Repository Analysis

* Accepts any public GitHub repository URL.
* Fetches dependency files directly from GitHub using the GitHub REST API.
* Supports:

  * `requirements.txt` (Python)
  * `pyproject.toml` (Python)
  * `package.json` (Node.js)

### Dependency Parsing

* Extracts package names and version information from dependency files.
* Handles both Python and Node.js dependency formats.

### Version Checking

* Queries the PyPI API for Python packages.
* Queries the npm Registry API for Node.js packages.
* Compares repository versions against the latest available versions.

### Report Generation

Classifies dependencies into:

* 🟢 Up to Date
* 🟡 Outdated
* 🔴 Not Found

Generates a self-contained HTML report containing:

* Package name
* Current version
* Latest available version
* Dependency status
* Overall dependency health summary

## Tech Stack

* Python
* GitHub REST API
* PyPI API
* npm Registry API
* HTML and CSS

## Project Structure

```text
dep-health-scanner/
├── scanner.py
├── report.html
├── requirements.txt
└── README.md
```

## Run It Locally

```bash
pip install -r requirements.txt
python scanner.py <github-repository-url>
```

Example:

```bash
python scanner.py https://github.com/psf/requests
```

The tool generates `report.html`, which can be opened in any web browser.

## Future Improvements

* Add support for additional dependency formats such as `pom.xml` and `Gemfile`.
* Integrate vulnerability databases such as the OSV API to flag known security issues.
* Export reports in JSON format for CI/CD pipeline integration.
* Add support for recursively scanning dependency files in subdirectories.

## Learning Outcome

This project helped me gain practical experience in API integration, file parsing, version comparison, HTML report generation, and building developer tools that automate real-world software maintenance tasks.
