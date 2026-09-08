#!/usr/bin/env python3
"""
update_altstore_source.py

Fetches the latest HyperLink IPA from GitHub Releases or artifacts and updates
the SideStore/AltStore-compatible source JSON file.

Environment variables:
  SOURCE_JSON_PATH    Path to the source JSON file (default: docs/public/v1/altstore-source.json)
  MANUAL_RUN_REASON   Optional note when triggered via workflow_dispatch
"""

import json
import os
import sys
import hashlib
import urllib.request
from datetime import datetime, timezone

SOURCE_JSON_PATH = os.environ.get("SOURCE_JSON_PATH", "docs/public/v1/altstore-source.json")
MANUAL_RUN_REASON = os.environ.get("MANUAL_RUN_REASON", "").strip()

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


def fetch_json(url):
    """Fetch JSON from a URL."""
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "HyperNix-AltStore-Bot/1.0"}
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())


def fetch_url_content(url):
    """Fetch raw content from a URL and return it as bytes."""
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "HyperNix-AltStore-Bot/1.0"}
    )
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
        new_app = app_config.copy()
        new_app["version"] = version
        new_app["versionDate"] = release_date
        new_app["downloadURL"] = ipa_url
        new_app["size"] = size_bytes
        new_app["versions"] = [new_version]
        # Remove sourceCodeURL from top level as it belongs in versions
        new_app.pop("sourceCodeURL", None)
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
        
        print(f"\n[{app_name}] Fetching latest IPA from {repo_owner}/{repo_name}...")
        
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
        # Note: For large files, we might want to use the digest from GitHub API if available
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
