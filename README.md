<div align="center">

# Google Forms Test Filler & Auto Submitter 🚀

**A fast, dependency-free Python CLI tool to automate, populate, and submit synthetic test responses to public Google Forms.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/Ali-HF/google-forms-test-filler/pulls)
[![GitHub Stars](https://img.shields.io/github/stars/Ali-HF/google-forms-test-filler?style=social)](https://github.com/Ali-HF/google-forms-test-filler)

[Features](#-key-features) •
[Quick Start](#-quick-start) •
[Comparison](#-why-not-selenium-or-the-official-api) •
[Question Types](#-supported-google-form-question-types) •
[FAQ](#-frequently-asked-questions-faq) •
[Safety & Guidelines](#-ethical-use--safety-guardrails)

</div>

---

## 📌 Overview

**Google Forms Test Filler** is an open-source automation utility designed for developers, QA engineers, students, and researchers who need to **smoke-test Google Forms workflows** without manually typing dozens or hundreds of test submissions.

If you are developing **Google Sheets automations**, **Google Apps Script triggers (`onFormSubmit`)**, **pivot tables**, or **webhook pipelines**, this tool lets you generate diverse, realistic test responses in seconds.

> **💡 Zero setup required:** No Google Cloud project, no OAuth2 credentials, no API keys, and no heavy browser dependencies like Selenium or Puppeteer.

---

## ⚡ Why Not Selenium or the Official API?

| Feature | `google-forms-test-filler` | Official Google Forms API | Selenium / Playwright |
|---|---|---|---|
| **Setup Complexity** | ⚡ **Zero (1 command)** | ❌ Complex (GCP Project, OAuth, Scopes) | ⚠️ High (Chromedriver, browser binaries) |
| **Speed & Resource Usage** | ⚡ **Blazing Fast (<10MB RAM)** | ⚡ Fast (REST API) | 🐢 Heavy & Slow (Spawns full browser) |
| **Google Sign-in Required?** | 🔓 **No (Anonymous public forms)** | 🔐 Yes (Service account / OAuth) | 🔐 Often prompts Google 2FA/login |
| **Multi-page & Grids Support** | ✅ **Full Support** | ⚠️ Complex response schema | ✅ Supported |
| **Verification of Success** | ✅ **Inspects DOM response** | ✅ API response code | ✅ UI confirmation |
| **Dependencies** | 📦 **Only `requests`** | 📦 `google-api-python-client` | 📦 Browser engines & drivers |

---

## ✨ Key Features

- **🚀 Lightweight & Pure Python:** Operates using only standard `requests`. Runs on Windows, macOS, Linux, and CI/CD pipelines.
- **🔍 Automated Schema Discovery:** Automatically inspects and parses Google Forms' internal `FB_PUBLIC_LOAD_DATA_` JSON blob, discovering every question ID (`entry.XXXXX`), question type, required flags, and choices.
- **🛡️ Built-in Rate-Limiting & Guardrails:**
  - Includes `--dry-run` to preview questions and payloads with **zero live submissions**.
  - Enforces configurable delay intervals (`--delay 1.0`) to respect Google's infrastructure.
  - Safe batch thresholds (`--force` required for submissions exceeding 100).
- **🎯 Full Google Question Type Compatibility:**
  - 📝 **Short Answer & Paragraphs:** Heuristic context generation for realistic names, dummy emails, phone numbers, ages, and survey feedback.
  - 🔘 **Multiple Choice & Dropdowns:** Random selection across available options.
  - ☑️ **Checkboxes:** Generates realistic non-empty random subsets.
  - 📏 **Linear Scales:** Random values across defined scale ranges.
  - 📊 **Grids:** Full row-by-row mapping for multiple-choice and checkbox grids.
  - 📅 **Dates & Times:** Formats `_year`, `_month`, `_day`, `_hour`, and `_minute` accurately.
  - 📄 **Multi-Page Forms:** Automatically tracks and passes `pageHistory` across section breaks.
- **🔎 "Silent 200 OK" Protection:** Unlike typical APIs, Google Forms returns HTTP `200` even when validation fails. This tool inspects the returned HTML body to verify confirmation and detect rejected submissions.

---

## 📦 Installation

```bash
# 1. Clone the repository
git clone https://github.com/Ali-HF/google-forms-test-filler.git
cd google-forms-test-filler

# 2. Install dependencies (only requests is required)
pip install -r requirements.txt
```

---

## 🚀 Quick Start

### 1. Dry Run (Inspect Form Schema without Submitting)
Always run a dry run first to inspect the discovered question schema:
```bash
python fill_form.py "https://docs.google.com/forms/d/e/XXXX/viewform" --dry-run
```
*(Also supports short links like `https://forms.gle/XXXX`)*

**Sample Dry Run Output:**
```text
=================================================================
 DRY RUN: INSPECTING FORM (ZERO RESPONSES WILL BE SUBMITTED)
=================================================================
Target Submission Endpoint: https://docs.google.com/forms/d/e/.../formResponse
Collects Email Field      : No
Anti-CSRF fbzx Token      : 614052815911483... (present)
-----------------------------------------------------------------
Question #1:
  Title      : Have you ever used digital lending applications?
  Type       : Multiple choice
  Entry ID   : entry.1513773183
  Required   : True
  Options    : ['Yes', 'No', 'Maybe']
...
[DRY RUN COMPLETE] Schema parsed and verified. 0 submissions sent.
```

### 2. Submit Synthetic Responses
Submit 10 test responses with a 1-second delay:
```bash
python fill_form.py "https://docs.google.com/forms/d/e/XXXX/viewform" -n 10 --delay 1.0
```

### 3. CLI Command Options

| Argument | Type | Default | Description |
|---|---|---|---|
| `url` | `str` | *Required* | Public Google Form URL (`/viewform` or `forms.gle`) |
| `-n` | `int` | `10` | Total number of synthetic test responses to submit |
| `--delay` | `float` | `1.0` | Delay in seconds between consecutive submissions |
| `--dry-run` | `flag` | `False` | Inspect schema and preview test payload without submitting |
| `--force` | `flag` | `False` | Safety bypass required when submitting batches > 100 |

---

## 📋 Form Configuration Requirements

For automated testing, verify these settings in your Google Form (**Settings** tab):

1. **"Limit to 1 response":** Must be **OFF** *(Enabling this requires Google account login)*.
2. **"Collect email addresses":** Set to **"Responder input"** or **"Do not collect"** *(Setting to "Verified" forces Google account login)*.
3. **Workspace Domain Restrictions:** Must be **disabled** if created under an institutional or university Google Workspace.

---

## ❓ Frequently Asked Questions (FAQ)

### Can I use this without a Google Cloud API Key or Service Account?
**Yes.** This tool interacts with the public web endpoint of your Google Form (`/formResponse`), the exact same way a standard web browser does. No GCP project or API billing is needed.

### How does it generate varying test responses?
On every iteration, multiple-choice options, dropdowns, and checkboxes are randomly sampled from the form's discovered options. Text inputs use heuristic pattern matching: questions containing "email" receive synthetic emails, questions with "name" receive realistic names, and feedback fields receive randomized testing remarks.

### Will this trigger Google's rate limits or CAPTCHAs?
When testing in small or medium batches (10–100 responses) with a `--delay` of 1.0s to 1.5s, requests mimic normal browser pacing. Blasting hundreds of requests with `0s` delay may cause Google to throttle your IP address. Always keep a safe delay between submissions.

### How do I clear or delete test submissions after testing?
In your Google Form editor, navigate to the **Responses** tab, click the **three dots (⋮)** menu in the upper right corner, and select **"Delete all responses"**. If connected to Google Sheets, you can also wipe test rows directly from the spreadsheet.

---

## 🛡️ Ethical Use & Safety Guardrails

> **⚠️ DISCLAIMER:** This project is intended solely for developer testing, automated QA, and educational purposes on forms that you own or have explicit authorization to test. 
> 
> Unauthorized automation, spamming, denial-of-service (DoS), or mass-submitting unwanted data to third-party forms violates Google's Terms of Service and this repository's Code of Conduct. Please test responsibly.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE) — free for personal, academic, and commercial use.

---

## 🌟 Show Your Support

If this tool saved you time testing your Google Forms or Google Sheets workflows, consider giving it a **Star ⭐** on GitHub!
