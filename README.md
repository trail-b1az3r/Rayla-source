# HyperNix AltStore/SideStore Source

[![Update IPA Sources](https://github.com/trail-b1az3r/HyperNix-pip/actions/workflows/update-altstore-source.yml/badge.svg)](https://github.com/trail-b1az3r/HyperNix-pip/actions/workflows/update-altstore-source.yml)
[![License: HyperNix Dual License](https://img.shields.io/badge/License-HyperNix%20Dual-blue.svg)](LICENSE.md)

## 📱 Add Rayla Source

<p align="center">
  <iframe src="https://trail-b1az3r.github.io/HyperNix-pip/docs/public/v1/index.html" width="640" height="280" style="border: none; overflow: hidden; max-width: 100%;" title="Add Rayla Source Banner"></iframe>
</p>

<p align="center">
  <em>Can't see the banner? <a href="https://trail-b1az3r.github.io/HyperNix-pip/docs/public/v1/index.html" target="_blank">Click here to open it</a></em>
</p>

Automated AltStore and SideStore source for HyperNix applications. This repository automatically updates with the latest IPA releases from configured apps.

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

## ⚠️ Disclaimers

**Please read the following disclaimers carefully before using this source:**

### General Use
- This source is provided **as-is** for educational and personal use only
- By using this source, you acknowledge that you do so at your own risk
- The maintainers assume no responsibility for any damages, data loss, or legal consequences resulting from the use of this source

### Legal & Compliance
- All applications in this source are sourced from their respective public GitHub repositories
- We are **not affiliated with** AltStore, SideStore, Apple, or any app developers listed herein
- Use of these applications must comply with all applicable laws and regulations in your jurisdiction
- We are not responsible for ensuring third-party apps comply with local laws or platform terms of service
- Users are solely responsible for reviewing each app's terms of service and privacy policies
- **YouTube Plus is NOT made by or affiliated with this project** — it is developed and maintained by [mrdrvt99](https://github.com/mrdrvt99)

### Security & Integrity
- While we implement automated checksum verification, we cannot guarantee the absolute security or integrity of downloaded files
- Users are encouraged to independently verify app authenticity and source code
- Always download from official sources when available and review release notes before installation
- Be cautious of modified or altered builds not provided by official developers

### iOS Device Management
- Sideloading applications may void your iOS device warranty
- Installation of third-party applications requires appropriate system privileges and access credentials
- We accept no liability for any damage to your device or loss of data
- Some functionality may be restricted or disabled on your device depending on iOS version and device settings

### Content & Availability
- App availability and functionality may change without notice
- We do not guarantee continuous availability of sources, downloads, or related services
- This source may be updated, modified, or discontinued at any time without prior notice
- The information provided (version numbers, release dates, file sizes) is not guaranteed to be accurate

### Third-Party Dependencies
- This project relies on third-party services (GitHub, GitHub Actions, etc.)
- We are not responsible for service outages, data breaches, or other issues with third-party platforms
- The reliability of apps depends on the continued availability of their source repositories

## 📚 Credits

**Project Contributors & Inspirations:**
- **HyperNix Team** — Project development and maintenance (sadly just me and Claude Code)
- [Riley Testut](https://github.com/RileyTestut) — Creator of [AltStore](https://altstore.io/)
- [SideStore](https://sidestore.io/) — Alternative iOS sideloading platform
- [mrdrvt99](https://github.com/mrdrvt99) — Developer of YouTube Plus (YouProEXTRA)

**Technologies & Tools:**
- Python — Automation scripting
- GitHub API — Release fetching and app management
- GitHub Actions — Continuous integration and scheduled workflows

**Special Thanks:**
- The open-source community for tools and inspiration
- All app developers whose work is featured in this source
- Users who contribute feedback and improvements

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

When contributing:
- Follow the existing code style and conventions
- Provide clear descriptions of changes and their purpose
- Test changes thoroughly before submitting
- Respect the licensing terms of included projects

## 📧 Support

For issues or questions:
- Open an issue on [GitHub](https://github.com/trail-b1az3r/Rayla-source/issues)
- Review existing documentation and closed issues for solutions
- Include relevant error messages and system information when reporting issues

---

Made with ❤️ by the HyperNix Team
