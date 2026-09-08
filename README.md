# HyperNix AltStore/SideStore Source

[![Update IPA Sources](https://github.com/trail-b1az3r/HyperNix-pip/actions/workflows/update-altstore-source.yml/badge.svg)](https://github.com/trail-b1az3r/HyperNix-pip/actions/workflows/update-altstore-source.yml)
[![License: HyperNix Dual License](https://img.shields.io/badge/License-HyperNix%20Dual-blue.svg)](LICENSE.md)

Automated AltStore and SideStore source for HyperNix applications (and a youtube ipa). This repository automatically updates with the latest IPA releases from configured apps.

## 📱 Available Apps

| App | Description | Source Repository |
|-----|-------------|-------------------|
| **HyperLink** | Chat with local AI models on your device | [trail-b1az3r/HyperNix-pip](https://github.com/trail-b1az3r/HyperNix-pip) |
| **YouTube Plus** | Enhanced YouTube experience with extra features | [mrdrvt99/YouProEXTRA](https://github.com/mrdrvt99/YouProEXTRA) |

## 🔗 Installation

### AltStore

1. Open AltStore on your iOS device
2. Tap the **+** button in the top-left corner
3. Enter the following URL:
   ```
   https://raw.githubusercontent.com/trail-b1az3r/HyperNix-pip/main/docs/public/v1/altstore-source.json
   ```
4. Tap **Add** to add the source

### SideStore

1. Open SideStore on your iOS device
2. Go to **Sources** tab
3. Tap **+** to add a new source
4. Enter the following URL:
   ```
   https://raw.githubusercontent.com/trail-b1az3r/HyperNix-pip/main/docs/public/v1/altstore-source.json
   ```
5. Tap **Done** to add the source

## ⚙️ Automation

This repository uses GitHub Actions to automatically update the AltStore/SideStore source JSON file:

- **Schedule**: Runs daily at 02:00 UTC
- **Manual Trigger**: Can be triggered manually from the Actions tab
- **Apps Updated**:
  - HyperLink (from `trail-b1az3r/HyperNix-pip` releases)
  - YouTube Plus (from `mrdrvt99/YouProEXTRA` releases)

### How It Works

1. The workflow fetches the latest GitHub releases for each configured app
2. Finds releases containing `.ipa` assets
3. Downloads each IPA to calculate its SHA-256 checksum
4. Updates the source JSON with:
   - Latest version number
   - Download URL
   - File size
   - SHA-256 hash
   - Release date
5. Commits changes only if updates were detected

### Manual Trigger

To manually trigger an update:

1. Go to the **Actions** tab in this repository
2. Select **"update-altstore-source"** workflow
3. Click **"Run workflow"**
4. Optionally add a reason for the manual run
5. Click **"Run workflow"** button

## 📄 Source Format

The source JSON follows the [AltStore Source Format specification](https://github.com/RileyTestut/AltStore/wiki/AltStore-Source-Format).

### Example Entry Structure

```json
{
  "name": "App Name",
  "bundleIdentifier": "com.example.app",
  "developerName": "Developer",
  "version": "1.0.0",
  "versionDate": "2024-01-01T00:00:00Z",
  "downloadURL": "https://...",
  "size": 12345678,
  "versions": [
    {
      "version": "1.0.0",
      "versionDate": "2024-01-01T00:00:00Z",
      "downloadURL": "https://...",
      "size": 12345678,
      "sha256": "abc123...",
      "buildVersion": "1"
    }
  ]
}
```

## 📝 Adding New Apps

To add a new app to the automated source, edit `scripts/update_altstore_source.py` and add a new entry to the `APPS_CONFIG` array:

```python
{
    "name": "Your App Name",
    "bundleIdentifier": "com.example.bundleid",
    "developerName": "Developer Name",
    "subtitle": "Short description",
    "localizedDescription": "Full description of the app",
    "iconURL": "https://example.com/icon.png",
    "category": "utilities",  # or "games", "entertainment", etc.
    "repo_owner": "github-username",
    "repo_name": "repository-name",
    "sourceCodeURL": "https://github.com/github-username/repository-name",
}
```

## ⚖️ License

This project is licensed under the **HyperNix Dual License**. See [LICENSE.md](LICENSE.md) for details.

The license offers two options:
- **(A) HyperNix OpenCode Light Limited Use License v0.1 (LLU-0.1)** - Source-available with use restrictions
- **(B) HyperNix Open Source License v1.0 (HOS-1.0)** - OSI-compliant open source license

You may choose either license. If no choice is made explicitly, option (A) applies by default.

## ⚠️ Disclaimer
- YouTubeProExtra IS NOT made by me in ANY way
- This source is provided for educational and personal use only
- All apps are sourced from their respective public GitHub repositories
- I am not affiliated with AltStore, SideStore, or any app developers
- Use at your own risk

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## 📧 Support

For issues or questions:
- Open an issue on [GitHub](https://github.com/trail-b1az3r/HyperNix-pip/issues)
- Check existing documentation

---

Made with ❤️ by the HyperNix Team (Rayla and claude code) 
