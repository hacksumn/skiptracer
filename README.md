<p align="center">
  <img src="assets/banner.png" alt="Skiptracer Banner" width="100%">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.x-blue.svg" alt="Python 3.x">
  <img src="https://img.shields.io/badge/version-1.0.0-brightgreen.svg" alt="Version 1.0.0">
  <img src="https://img.shields.io/badge/license-Apache--2.0-lightgrey.svg" alt="License Apache 2.0">
  <img src="https://img.shields.io/badge/maintenance-active-success.svg" alt="Maintenance Active">
</p>

<h1 align="center">Skiptracer</h1>
<h3 align="center">OSINT Passive Recon Scraping Framework</h3>

---

## 📖 Overview

Initial attack vectors for reconnaissance usually involve utilizing pay-for-data APIs (like Recon-NG) or paying to utilize transforms (like Maltego) to get data mining results. **Skiptracer** changes the game by utilizing basic Python web scraping of PII (Personally Identifiable Information) paywall sites to compile passive information on a target—all on a ramen noodle budget.

This framework is designed to query and parse third-party services in an automated fashion to increase productivity while conducting a background investigation. It is particularly useful when trying to locate hard-to-find targets.

## 🚀 Features

Skiptracer categorizes searches to reveal additional information such as telephone numbers, physical addresses, or other useful data:

*   **Email:** Investigate using a known email address (e.g., LinkedIn, HaveIBeenPwned, Myspace, AdvancedBackgroundChecks).
*   **Name:** Investigate using a known First and Last name (e.g., Truth Finder, True People, AdvancedBackgroundChecks).
*   **Phone:** Investigate using a known Phone Number (e.g., True People, WhoCalled, 411, AdvancedBackgroundChecks).
*   **ScreenName:** Investigate using a known Screen Name (e.g., Knowem, NameChk, Tinder).
*   **Plate:** Investigate using a known License Plate.
*   **Domain:** Investigate using a known Domain Name.

Additionally, Skiptracer features a **Report Generator** that automatically compiles your queries into a clean `.docx` file for easy documentation.

## 🛠️ Installation

### Standard Installation

Clone the repository and install the required dependencies:

```bash
git clone https://github.com/hacksumn/skiptracer.git
cd skiptracer
pip install -r requirements.txt
```

### Docker Installation

You can also run Skiptracer inside a Docker container:

```bash
docker run -it --name skiptracer xshuden/skiptracer 
# OR (to delete the container when you're done)
docker run --rm -it --name skiptracer xshuden/skiptracer
```

## 💻 Usage

To launch the interactive menu, simply run:

```bash
python3 skiptracer.py
```

From the main menu, select the type of search you wish to perform (Email, Name, Phone, etc.) and follow the on-screen prompts. You can choose to run all modules for a specific category or select them individually.

## 📝 To-Do / Roadmap

Skiptracer is intended to be a community-driven application. If you are interested in helping out, drop us a note or submit a pull request!

*   [x] Complete Python 3 conversion and bug fixes
*   [ ] Add more API support
*   [ ] Integrate options for international (non-U.S.) results
*   [ ] Implement bypass methods for scraping blocks (e.g., headless Selenium)
*   [ ] Open to community ideas!

## 📄 License

This project is licensed under the Apache 2.0 License. See the [LICENSE](LICENSE) file for details.

---
*Modernized and maintained by the community.*
