import requests
import re
import json
import sys
import tomllib
from packaging import version
from datetime import datetime

GITHUB_API = "https://api.github.com"
PYPI_API = "https://pypi.org/pypi"
NPM_API = "https://registry.npmjs.org"


def get_github_file(repo_url, filename):
    """Fetch a file from a public GitHub repo."""
    # Extract owner/repo from URL
    match = re.search(r"github\.com/([^/]+)/([^/]+)", repo_url)
    if not match:
        print("Invalid GitHub URL")
        return None
    owner, repo = match.group(1), match.group(2).replace(".git", "")

    url = f"{GITHUB_API}/repos/{owner}/{repo}/contents/{filename}"
    headers = {"Accept": "application/vnd.github.v3.raw"}
    response = requests.get(url, headers=headers)

    print(url)
    print(response.status_code)

    if response.status_code == 200:
        return response.text
    return None


def check_pypi(package, current_version):
    """Check PyPI for latest version of a package."""
    try:
        response = requests.get(f"{PYPI_API}/{package}/json", timeout=5)
        if response.status_code == 200:
            data = response.json()
            latest = data["info"]["version"]
            status = "UP TO DATE" if version.parse(current_version) >= version.parse(latest) else "OUTDATED"
            return {"package": package, "current": current_version, "latest": latest, "status": status}
    except Exception:
        pass
    return {"package": package, "current": current_version, "latest": "unknown", "status": "NOT FOUND"}


def check_npm(package, current_version):
    """Check npm for latest version of a package."""
    try:
        response = requests.get(f"{NPM_API}/{package}/latest", timeout=5)
        if response.status_code == 200:
            latest = response.json().get("version", "unknown")
            cur = current_version.lstrip("^~>=")
            status = "UP TO DATE" if version.parse(cur) >= version.parse(latest) else "OUTDATED"
            return {"package": package, "current": current_version, "latest": latest, "status": status}
    except Exception:
        pass
    return {"package": package, "current": current_version, "latest": "unknown", "status": "NOT FOUND"}


def parse_requirements(content):
    """Parse requirements.txt into package:version pairs."""
    packages = {}
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        match = re.match(r"([a-zA-Z0-9_\-]+)[>=<~!]+([0-9][^\s]*)", line)
        if match:
            packages[match.group(1)] = match.group(2)
        elif re.match(r"[a-zA-Z0-9_\-]+$", line):
            packages[line] = "unknown"
    return packages


def parse_package_json(content):
    """Parse package.json into package:version pairs."""
    try:
        data = json.loads(content)
        deps = {}
        deps.update(data.get("dependencies", {}))
        deps.update(data.get("devDependencies", {}))
        return deps
    except Exception:
        return {}

def parse_pyproject(content):
    """Parse pyproject.toml dependencies."""
    try:
        data = tomllib.loads(content)

        deps = {}

        # Poetry projects
        poetry = data.get("tool", {}).get("poetry", {})
        for pkg, ver in poetry.get("dependencies", {}).items():
            if pkg != "python":
                deps[pkg] = str(ver)

        return deps

    except Exception:
        return {}


def generate_html_report(results, repo_url, ecosystem):
    """Generate a clean HTML report."""
    up_to_date = [r for r in results if r["status"] == "UP TO DATE"]
    outdated = [r for r in results if r["status"] == "OUTDATED"]
    not_found = [r for r in results if r["status"] == "NOT FOUND"]

    score = int((len(up_to_date) / len(results)) * 100) if results else 0

    rows = ""
    for r in results:
        color = {"UP TO DATE": "#2ecc71", "OUTDATED": "#e74c3c", "NOT FOUND": "#f39c12"}[r["status"]]
        rows += f"""
        <tr>
            <td>{r['package']}</td>
            <td>{r['current']}</td>
            <td>{r['latest']}</td>
            <td style="color:{color}; font-weight:bold">{r['status']}</td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Dep Health Scanner</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 900px; margin: 40px auto; padding: 0 20px; background: #f5f5f5; }}
        h1 {{ color: #2c3e50; }}
        .score {{ font-size: 48px; font-weight: bold; color: {'#2ecc71' if score >= 80 else '#e74c3c'}; }}
        table {{ width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; }}
        th {{ background: #2c3e50; color: white; padding: 12px; text-align: left; }}
        td {{ padding: 10px 12px; border-bottom: 1px solid #eee; }}
        .summary {{ display: flex; gap: 20px; margin: 20px 0; }}
        .card {{ background: white; padding: 20px; border-radius: 8px; flex: 1; text-align: center; }}
    </style>
</head>
<body>
    <h1>Dependency Health Scanner</h1>
    <p>Repo: <a href="{repo_url}">{repo_url}</a> | Ecosystem: {ecosystem} | {datetime.now().strftime("%d %b %Y")}</p>
    <div class="score">Health Score: {score}%</div>
    <div class="summary">
        <div class="card"><h3 style="color:#2ecc71">{len(up_to_date)}</h3><p>Up to Date</p></div>
        <div class="card"><h3 style="color:#e74c3c">{len(outdated)}</h3><p>Outdated</p></div>
        <div class="card"><h3 style="color:#f39c12">{len(not_found)}</h3><p>Not Found</p></div>
    </div>
    <table>
        <tr><th>Package</th><th>Current</th><th>Latest</th><th>Status</th></tr>
        {rows}
    </table>
</body>
</html>"""

    with open("report.html", "w") as f:
        f.write(html)
    print("\nReport saved to report.html — open it in your browser.")


def scan(repo_url):
    print(f"\nScanning: {repo_url}\n")

    # Try requirements.txt
    content = get_github_file(repo_url, "requirements.txt")
    if content:
        print("Found requirements.txt — checking PyPI...")
        packages = parse_requirements(content)
        results = [check_pypi(pkg, ver) for pkg, ver in packages.items()]
        generate_html_report(results, repo_url, "Python/PyPI")
        return

    # Try pyproject.toml
    content = get_github_file(repo_url, "pyproject.toml")
    if content:
        print("Found pyproject.toml — checking PyPI...")
        packages = parse_pyproject(content)
        results = [check_pypi(pkg, ver) for pkg, ver in packages.items()]
        generate_html_report(results, repo_url, "Python/PyPI")
        return

    # Try package.json
    content = get_github_file(repo_url, "package.json")
    if content:
        print("Found package.json — checking npm...")
        packages = parse_package_json(content)
        results = [check_npm(pkg, ver) for pkg, ver in packages.items()]
        generate_html_report(results, repo_url, "Node.js/npm")
        return

    print(
        "No supported dependency files found "
        "(requirements.txt, pyproject.toml, package.json)."
    )

if __name__ == "__main__":
    if len(sys.argv) < 2:
         print("Usage: python scanner.py <github_repo_url>")
         print("Example: python scanner.py https://github.com/psf/requests")
    else:
        scan(sys.argv[1])