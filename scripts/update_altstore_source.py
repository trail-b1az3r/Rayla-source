#!/usr/bin/env python3
"""
update_altstore_source.py

Fetches the latest HyperLink IPA from GitHub Actions artifacts and
YouTube Plus IPA from GitHub Releases, then updates the SideStore/AltStore-compatible source JSON file.

Environment variables:
  SOURCE_JSON_PATH    Path to the source JSON file (default: docs/public/v1/altstore-source.json)
  MANUAL_RUN_REASON   Optional note when triggered via workflow_dispatch
  GITHUB_TOKEN        GitHub token for API authentication (required for artifact access)
"""

import json
import os
import sys
import hashlib
import urllib.request
from datetime import datetime, timezone

SOURCE_JSON_PATH = os.environ.get("SOURCE_JSON_PATH", "docs/public/v1/altstore-source.json")
MANUAL_RUN_REASON = os.environ.get("MANUAL_RUN_REASON", "").strip()
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")

# App configurations
APPS_CONFIG = [
    {
        "name": "HyperLink",
        "bundleIdentifier": "com.hypernix.link",
        "developerName": "HyperNix Team",
        "subtitle": "Chat with local AI models on your device",
        "localizedDescription": "HyperLink is an iOS companion app that lets you chat with AI models running on your local machine. Connect over your home network or remotely via Tailscale. Send photos, upload files and code, and resolve Hugging Face GGUF links into real downloads.",
        "iconURL": "https://raw.githubusercontent.com/trail-b1az3r/HyperNix-pip/main/assets/logo-new/hypernix-icon.svg",
        "category": "utilities",
        "repo_owner": "trail-b1az3r",
        "repo_name": "HyperNix-pip",
        "sourceCodeURL": "https://github.com/trail-b1az3r/HyperNix-pip",
        "ipa_source": "artifact",  # Get IPA from workflow artifacts
        "workflow_id": "340345583",  # ios.yml workflow ID
        "artifact_pattern": "hyperlink-ipa-",  # Look for artifacts starting with this pattern
    },
    {
        "name": "YouTube Plus",
        "bundleIdentifier": "com.google.ios.youtube",
        "developerName": "Google LLC (modified by zarzelworkshop)",
        "subtitle": "Enhanced YouTube experience with extra features",
        "localizedDescription": "YouTube Plus is a modified version of the official YouTube app with additional features including ad-blocking, background playback, Picture-in-Picture, download manager, and many more tweaks. This build includes YouPip, YTUHD, Return YouTube Dislikes, and other enhancements.",
        "iconURL": "https://is1-ssl.mzstatic.com/image/thumb/Purple126/v6/97/45/ab/9745ab48-7f6e-cb98-d0cd-f6c9a8e7d4d5/logo_youtube_color-0-1x_U003emarketing-0-7-00-85-2.png/230x0w.webp",
        "category": "entertainment",
        "repo_owner": "mrdrvt99",
        "repo_name": "YouProEXTRA",
        "sourceCodeURL": "https://github.com/mrdrvt99/YouProEXTRA",
        "ipa_source": "release",  # Get IPA from GitHub Releases
    }
]

# Standard AltStore/SideStore source format
# See: https://github.com/RileyTestut/AltStore/wiki/AltStore-Source-Format
DEFAULT_SOURCE = {
    "name": "HyperNix",
    "identifier": "com.hypernix.source",
    "subtitle": "Official HyperNix app source for AltStore and SideStore",
    "iconURL": "https://raw.githubusercontent.com/trail-b1az3r/HyperNix-pip/main/assets/logo-new/hypernix-icon.svg",
    "tintColor": "#5B5FC7",
    "apps": [],
    "news": []
}


def fetch_json(url, require_auth=False):
    """Fetch JSON from a URL."""
    headers = {"User-Agent": "HyperNix-AltStore-Bot/1.0"}
    
    # Add authorization header for GitHub API requests
    if require_auth and GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    elif require_auth:
        print(f"warning: GitHub API request without token may be rate limited", file=sys.stderr)
    
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())


def fetch_url_content(url, require_auth=False):
    """Fetch raw content from a URL and return it as bytes."""
    headers = {"User-Agent": "HyperNix-AltStore-Bot/1.0"}
    
    # Add authorization header for GitHub API requests
    if require_auth and GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read()


def calculate_sha256(data_bytes):
    """Calculate SHA-256 hash of bytes."""
    return hashlib.sha256(data_bytes).hexdigest()


def get_latest_release_with_ipa(repo_owner, repo_name):
    """
    Fetch the latest GitHub release that contains an IPA asset.
    Returns (release_info, ipa_asset) or (None, None) if not found.
    """
    try:
        releases = fetch_json(f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases?per_page=50")
        
        for release in releases:
            if release.get("draft") or release.get("prerelease"):
                continue
            
            assets = release.get("assets", [])
            for asset in assets:
                if asset.get("name", "").endswith(".ipa"):
                    return release, asset
        
        return None, None
    except Exception as e:
        print(f"warning: could not fetch releases for {repo_owner}/{repo_name}: {e}", file=sys.stderr)
        return None, None


def get_latest_artifact_ipa(repo_owner, repo_name, workflow_id, artifact_pattern=""):
    """
    Fetch the latest successful workflow run and its artifact containing the IPA.
    For HyperLink, we look for artifacts from the ios workflow matching the pattern.
    Returns (run_info, artifact_info) or (None, None) if not found.
    """
    try:
        # Get recent successful workflow runs
        runs_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/actions/workflows/{workflow_id}/runs?status=success&per_page=10"
        runs_data = fetch_json(runs_url, require_auth=True)
        
        runs = runs_data.get("workflow_runs", [])
        if not runs:
            print(f"warning: no successful runs found for workflow {workflow_id}", file=sys.stderr)
            return None, None
        
        # Find the most recent run with a matching artifact
        for run in runs:
            run_id = run["id"]
            created_at = run["created_at"]
            
            # Get artifacts for this run
            artifacts_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/actions/runs/{run_id}/artifacts"
            artifacts_data = fetch_json(artifacts_url, require_auth=True)
            
            artifacts = artifacts_data.get("artifacts", [])
            for artifact in artifacts:
                artifact_name = artifact.get("name", "")
                # Skip expired artifacts
                if artifact.get("expired", False):
                    continue
                
                # If pattern specified, match against it
                if artifact_pattern:
                    if not artifact_name.startswith(artifact_pattern):
                        continue
                elif "ipa" not in artifact_name.lower():
                    # Default: look for artifacts with 'ipa' in the name
                    continue
                
                # Extract version from artifact name (e.g., hyperlink-ipa-1.0.26.9.2.1-b8)
                version_info = extract_version_from_artifact_name(artifact_name, artifact_pattern)
                
                return {
                    "id": run_id,
                    "created_at": created_at,
                    "head_branch": run.get("head_branch", "main"),
                    "head_sha": run.get("head_sha", "")[:7],
                    "version": version_info[0],
                    "build": version_info[1],
                }, {
                    "id": artifact["id"],
                    "name": artifact_name,
                    "size": artifact.get("size_in_bytes", 0),
                    "download_url": artifact.get("archive_download_url", ""),
                    "digest": artifact.get("digest", ""),
                    "created_at": artifact.get("created_at", created_at),
                }
        
        print(f"warning: no suitable artifact found in recent runs", file=sys.stderr)
        return None, None
        
    except Exception as e:
        print(f"warning: could not fetch artifacts for {repo_owner}/{repo_name}: {e}", file=sys.stderr)
        return None, None


def extract_version_from_artifact_name(artifact_name, pattern=""):
    """
    Extract version info from artifact name.
    For HyperLink: hyperlink-ipa-1.0.26.9.2.1-b8 -> version=1.0.26.9.2.1, build=b8
    """
    # Remove the prefix pattern
    if pattern and artifact_name.startswith(pattern):
        artifact_name = artifact_name[len(pattern):]
    
    # Pattern: version-build (e.g., 1.0.26.9.2.1-b8)
    import re
    match = re.search(r'([0-9.]+)-b(\d+)', artifact_name)
    if match:
        return match.group(1), match.group(2)
    
    # Fallback: try to find any version-like pattern
    match = re.search(r'([0-9]+\.[0-9.]+)', artifact_name)
    if match:
        build_match = re.search(r'b(\d+)', artifact_name)
        build = build_match.group(1) if build_match else "1"
        return match.group(1), build
    
    return "1.0.0", "1"


def extract_version_from_ipa_name(ipa_name, app_name="App"):
    """
    Extract version info from IPA filename.
    Handles various naming conventions.
    """
    # Remove .ipa suffix and -unsigned marker
    base = ipa_name.replace("-unsigned", "").replace(".ipa", "")
    
    # Pattern 1: HyperLink-X.Y.Z-bN
    if "-b" in base and app_name == "HyperLink":
        parts = base.split("-b")
        if len(parts) == 2:
            version_part = parts[0].replace(f"{app_name}-", "")
            build_part = parts[1]
            return version_part, build_part
    
    # Pattern 2: YouTubePlus_X.Y.Z_A.B.C.ipa
    if "_" in base and "YouTubePlus" in base:
        parts = base.split("_")
        if len(parts) >= 3:
            version_part = parts[1]  # e.g., 21.24.3
            build_part = parts[2]    # e.g., 5.2.2
            return version_part, build_part
    
    # Pattern 3: AppName-X.Y.Z.ipa or AppName-vX.Y.Z.ipa
    import re
    match = re.search(r'[-_]?v?(\d+\.\d+\.?\d*)', base)
    if match:
        version = match.group(1)
        # Try to find build number
        build_match = re.search(r'b(\d+)', base)
        build = build_match.group(1) if build_match else "1"
        return version, build
    
    return "1.0.0", "1"


def load_existing_source(path):
    """Load existing source JSON or return default."""
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"warning: could not parse existing {path}, starting fresh: {e}", file=sys.stderr)
    return DEFAULT_SOURCE.copy()


def update_or_add_app(source, app_config, ipa_url, version, build_number, size_bytes, sha256_hash, release_date):
    """
    Update the app entry in the source or add it if missing.
    Returns True if changes were made, False otherwise.
    """
    apps = source.get("apps", [])
    bundle_id = app_config["bundleIdentifier"]
    
    # Find existing app by bundle identifier
    existing_app = None
    app_index = -1
    for i, app in enumerate(apps):
        if app.get("bundleIdentifier") == bundle_id:
            existing_app = app
            app_index = i
            break
    
    # Create new version entry
    new_version = {
        "version": version,
        "versionDate": release_date,
        "downloadURL": ipa_url,
        "size": size_bytes,
        "localizedDescription": app_config["localizedDescription"],
        "sourceCodeURL": app_config["sourceCodeURL"],
    }
    
    # Add SHA-256 hash (supported by AltStore/SideStore)
    if sha256_hash:
        new_version["sha256"] = sha256_hash
    
    # Add build number if available
    if build_number:
        new_version["buildVersion"] = build_number
    
    # Check if this version already exists
    if existing_app:
        versions = existing_app.get("versions", [])
        if versions:
            latest_version = versions[0]
            # Compare to see if we need to update
            if (latest_version.get("version") == version and 
                latest_version.get("buildVersion") == build_number and
                latest_version.get("downloadURL") == ipa_url):
                print(f"No update needed: {app_config['name']} {version} (build {build_number}) is already current")
                return False
        
        # Prepend new version to the front of the versions array
        existing_app["versions"].insert(0, new_version)
        
        # Keep only the last 5 versions to avoid bloating the source
        if len(existing_app["versions"]) > 5:
            existing_app["versions"] = existing_app["versions"][:5]
        
        # Update app-level metadata
        existing_app["version"] = version
        existing_app["versionDate"] = release_date
        existing_app["downloadURL"] = ipa_url
        existing_app["size"] = size_bytes
        
        apps[app_index] = existing_app
        print(f"Updated {app_config['name']} to version {version} (build {build_number})")
    else:
        # Create new app entry from config template
        new_app = {k: v for k, v in app_config.items() if k not in ['ipa_source', 'workflow_id', 'artifact_pattern']}
        new_app["version"] = version
        new_app["versionDate"] = release_date
        new_app["downloadURL"] = ipa_url
        new_app["size"] = size_bytes
        new_app["versions"] = [new_version]
        apps.append(new_app)
        source["apps"] = apps
        print(f"Added {app_config['name']} version {version} (build {build_number})")
    
    source["apps"] = apps
    return True


def main():
    print("=" * 60)
    print("HyperNix AltStore Source Updater")
    print("=" * 60)
    
    updated_apps = []
    failed_apps = []
    
    for app_config in APPS_CONFIG:
        app_name = app_config["name"]
        repo_owner = app_config["repo_owner"]
        repo_name = app_config["repo_name"]
        ipa_source = app_config.get("ipa_source", "release")
        
        print(f"\n[{app_name}] Fetching latest IPA from {repo_owner}/{repo_name}...")
        
        # Use artifact or release based on configuration
        if ipa_source == "artifact":
            workflow_id = app_config.get("workflow_id", "")
            artifact_pattern = app_config.get("artifact_pattern", "")
            
            if not workflow_id:
                print(f"[{app_name}] error: workflow_id required for artifact source", file=sys.stderr)
                failed_apps.append(app_name)
                continue
            
            run_info, artifact_info = get_latest_artifact_ipa(repo_owner, repo_name, workflow_id, artifact_pattern)
            
            if not run_info or not artifact_info:
                print(f"[{app_name}] warning: Could not find any artifact with IPA", file=sys.stderr)
                failed_apps.append(app_name)
                continue
            
            release_date = run_info.get("created_at", datetime.now(timezone.utc).isoformat())
            version = run_info.get("version", "1.0.0")
            build_number = run_info.get("build", "1")
            ipa_name = artifact_info.get("name", f"{app_name}.ipa")
            ipa_size = artifact_info.get("size", 0)
            
            # For artifacts, we need to use the archive download URL
            # The actual IPA is inside the zip archive
            ipa_url = artifact_info.get("download_url", "")
            
            print(f"[{app_name}] Found artifact: {ipa_name}")
            print(f"[{app_name}] Run ID: {run_info['id']}")
            print(f"[{app_name}] Version: {version}, Build: {build_number}")
            print(f"[{app_name}] Size: {ipa_size} bytes")
            print(f"[{app_name}] Download URL: {ipa_url}")
            
            # Calculate SHA-256 using the digest from GitHub API
            sha256_hash = None
            gh_digest = artifact_info.get("digest", "")
            if gh_digest.startswith("sha256:"):
                sha256_hash = gh_digest.replace("sha256:", "")
                print(f"[{app_name}] SHA-256 (from GitHub): {sha256_hash}")
            
            # Note: We can't directly download the IPA from artifact URL without authentication
            # The download_url requires auth, so we rely on GitHub's digest
        else:
            # Use releases (original behavior)
            release, ipa_asset = get_latest_release_with_ipa(repo_owner, repo_name)
            
            if not release or not ipa_asset:
                print(f"[{app_name}] warning: Could not find any release with an IPA asset", file=sys.stderr)
                failed_apps.append(app_name)
                continue
            
            release_tag = release.get("tag_name", "unknown")
            release_date = release.get("published_at", datetime.now(timezone.utc).isoformat())
            ipa_name = ipa_asset.get("name", f"{app_name}.ipa")
            ipa_url = ipa_asset.get("browser_download_url")
            ipa_size = ipa_asset.get("size", 0)
            
            print(f"[{app_name}] Found IPA: {ipa_name}")
            print(f"[{app_name}] Release: {release_tag}")
            print(f"[{app_name}] Size: {ipa_size} bytes")
            print(f"[{app_name}] URL: {ipa_url}")
            
            # Extract version from IPA name
            version, build_number = extract_version_from_ipa_name(ipa_name, app_name)
            print(f"[{app_name}] Parsed version: {version}, build: {build_number}")
            
            # Calculate SHA-256 hash by downloading the IPA
            sha256_hash = None
            try:
                print(f"[{app_name}] Downloading IPA to calculate SHA-256...")
                ipa_data = fetch_url_content(ipa_url)
                sha256_hash = calculate_sha256(ipa_data)
                print(f"[{app_name}] SHA-256: {sha256_hash}")
            except Exception as e:
                print(f"[{app_name}] warning: Could not download IPA for SHA-256 calculation: {e}", file=sys.stderr)
                # Use the digest from GitHub API if available
                gh_digest = ipa_asset.get("digest", "")
                if gh_digest.startswith("sha256:"):
                    sha256_hash = gh_digest.replace("sha256:", "")
                    print(f"[{app_name}] Using GitHub digest: {sha256_hash}")
        
        # Load or create source JSON
        source = load_existing_source(SOURCE_JSON_PATH)
        
        # Ensure required fields exist
        if "name" not in source:
            source["name"] = DEFAULT_SOURCE["name"]
        if "identifier" not in source:
            source["identifier"] = DEFAULT_SOURCE["identifier"]
        if "apps" not in source:
            source["apps"] = []
        
        # Update app
        changed = update_or_add_app(
            source,
            app_config,
            ipa_url,
            version,
            build_number,
            ipa_size,
            sha256_hash,
            release_date
        )
        
        if changed:
            updated_apps.append(app_name)
    
    if not updated_apps and not failed_apps:
        print("\nNo apps configured or all apps are up to date")
    elif not updated_apps:
        print(f"\nFailed to update any apps. Failed: {', '.join(failed_apps)}", file=sys.stderr)
        sys.exit(1)
    else:
        # Update timestamp
        source["updated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        
        if MANUAL_RUN_REASON:
            source["last_manual_run_reason"] = MANUAL_RUN_REASON
        
        print(f"\nSuccessfully updated: {', '.join(updated_apps)}")
    
    # Write output
    os.makedirs(os.path.dirname(SOURCE_JSON_PATH) or ".", exist_ok=True)
    with open(SOURCE_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(source, f, indent=2)
        f.write("\n")
    
    print(f"\nWrote {SOURCE_JSON_PATH}")
    print(json.dumps(source, indent=2))


if __name__ == "__main__":
    main()
