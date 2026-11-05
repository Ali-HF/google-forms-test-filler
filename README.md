# Google Forms Test Filler 🚀

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/Ali-HF)

A lightweight, dependency-free Python CLI tool designed to populate and smoke-test public Google Forms with realistic synthetic test responses.

Built for developers, QA engineers, and researchers to verify **Google Sheets pipelines**, **Google Apps Script triggers**, and **webhook automations** without manually filling out forms dozens of times.

---

## ⚠️ Ethical Use & Safety Disclaimer

> **IMPORTANT:** This tool is intended **strictly for testing forms that you own or have explicit authorization to test**. 
>
> Automated spamming, denial-of-service (DoS) attacks, or submitting unwanted data to third-party forms violates Google's Terms of Service and is strictly prohibited. Use responsibly.

---

## ✨ Features

- **Zero Heavy Dependencies:** Relies only on the standard `requests` library. Single-file CLI implementation.
- **Dynamic Schema Discovery:** Directly extracts and parses Google's internal `FB_PUBLIC_LOAD_DATA_` payload and hidden anti-CSRF tokens (`fbzx`).
- **Comprehensive Question Support:**
  - 📝 **Short Answer & Paragraph** (with intelligent contextual heuristics for names, emails, phones, numbers, and feedback)
  - 🔘 **Multiple Choice & Dropdown**
  - ☑️ **Checkboxes** (selects random non-empty subsets)
  - 📏 **Linear Scale**
  - 📊 **Grids** (Multiple-choice & Checkbox grids across all rows and columns)
  - 📅 **Date & Time** (handles `_year`, `_month`, `_day`, `_hour`, `_minute` fields)
  - 📄 **Multi-page Forms** (properly constructs sequential `pageHistory`)
- **Real Submission Verification:** Detects Google Forms' "Silent 200 OK" trap by inspecting the response body to confirm whether submissions were actually recorded or if validation failed.
- **Schema Validation Detection:** Identifies field-level validation rules (e.g., number ranges, regex constraints) from the form metadata.
- **Safety Guardrails:**
  - Includes `--dry-run` to inspect questions and preview payloads with **zero live submissions**.
  - Default rate-limiting delays to prevent IP throttling or silent CAPTCHAs.
  - Hard cap safeguards (`--force` required for batches > 100).
  - Halts with clean notices on sign-in gated forms.

---

## 📦 Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Ali-HF/google-forms-test-filler.git
   cd google-forms-test-filler
   ```

2. **Install requirements:**
   ```bash
   pip install -r requirements.txt
   ```

---

## 🚀 Usage

### 1. Dry Run (Inspect Form Schema without Submitting)
Always inspect the form first to verify question discovery and test payload generation:
```bash
python fill_form.py "https://docs.google.com/forms/d/e/XXXX/viewform" --dry-run
```
*(Also supports short links like `https://forms.gle/XXXX`)*

### 2. Submit Test Responses
Submit 10 test responses with a 1-second delay:
```bash
python fill_form.py "https://docs.google.com/forms/d/e/XXXX/viewform" -n 10 --delay 1.0
```

### 3. CLI Options

| Argument | Type | Default | Description |
|---|---|---|---|
| `url` | `str` | *Required* | Public Google Form URL (`/viewform` or `forms.gle`) |
| `-n` | `int` | `10` | Total number of synthetic responses to submit |
| `--delay` | `float` | `1.0` | Delay between consecutive submissions (seconds) |
| `--dry-run` | `flag` | `False` | Inspect questions and preview payload with zero submissions |
| `--force` | `flag` | `False` | Safety bypass required when submitting batches > 100 |

---

## 🛡️ Form Configuration Checklist

For this tool to submit test data, your Google Form must be publicly accessible:

1. **"Limit to 1 response":** Must be **OFF** *(Requires Google sign-in)*.
2. **"Collect email addresses":** Set to **"Responder input"** or **"Do not collect"** *(Setting to "Verified" forces Google account login)*.
3. **Workspace Domain Restrictions:** Must be **disabled** if created under an organizational or university Google Workspace account.

---

## 🔍 How It Works

1. **Schema Discovery:** Google Forms embeds the full form structure in an inline script assigned to `window.FB_PUBLIC_LOAD_DATA_`. The tool parses this JSON structure to obtain question IDs (`entry.XXXXX`), question types, and option lists.
2. **Hidden Tokens:** Extracts the `fbzx` anti-spam token and computes the `pageHistory` string for multi-page section breaks.
3. **Synthetic Payload Construction:** Generates varied, valid data per field type on each iteration.
4. **Targeted Dispatch:** Replaces the `/viewform` path with `/formResponse` and dispatches standard `application/x-www-form-urlencoded` POST requests.
5. **Response Integrity Check:** Verifies confirmation markers (e.g. `Your response has been recorded` or container class `vHW8eb`) rather than solely relying on HTTP 200 status codes.

---

## 📄 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for more information.

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!
Feel free to check the [issues page](https://github.com/Ali-HF/google-forms-test-filler/issues).
