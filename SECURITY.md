# Security & Ethical Use Policy

## Ethical Use Guidelines

`google-forms-test-filler` is a testing and QA utility designed solely for developers, educators, researchers, and form creators who need to:
- Test Google Form submission pipelines.
- Verify linked Google Sheets formulas, pivot tables, and automations.
- Test Google Apps Script triggers (`onFormSubmit`) and webhook integrations.
- Populate demo environments with realistic synthetic data.

### Strictly Prohibited Uses
- **Unauthorized Submissions:** Do not use this tool on forms that you do not own or do not have explicit written permission to test.
- **Denial of Service (DoS) or Spamming:** Do not use this tool to flood, spam, or degrade third-party services.
- **Bypassing Access Controls:** This tool will not bypass Google account authentication, CAPTCHA challenges, or workspace domain restrictions. Attempting to bypass security controls is against Google's Terms of Service and this project's code of conduct.

---

## Built-in Safety Guardrails

To prevent accidental abuse or runaway automation:
1. **Rate Limit Warning:** A minimum delay of `1.0s` is set by default. Delays under `0.5s` trigger terminal warnings.
2. **Batch Cap Safeguard:** Submissions exceeding 100 responses require an explicit `--force` flag to prevent accidental flooding.
3. **Authentication Check:** The tool automatically detects forms gated by Google sign-in ("Limit to 1 response") and halts execution.
4. **Dry-Run Mode:** Users are encouraged to run `--dry-run` to inspect schemas and verify payloads before sending any live requests.

---

## Reporting Vulnerabilities

If you identify a security issue or vulnerability within this project, please report it privately by opening a security advisory on GitHub or emailing the repository maintainer directly.
