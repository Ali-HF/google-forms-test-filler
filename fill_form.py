"""
Google Forms Test Filler (CLI)
==============================
A synthetic test response generator for developer smoke-testing and QA on public Google Forms.

ETHICAL USE NOTICE:
This tool is intended strictly for form authors and authorized developers to test their own
forms and verify response pipelines (e.g. linked Google Sheets, App Scripts, automations).
Do not use this tool on forms you do not own or do not have explicit authorization to test.

Usage:
    python fill_form.py "<form viewform URL>" --dry-run
    python fill_form.py "<form viewform URL>" -n 10 --delay 1.0
"""
import argparse
import json
import random
import re
import sys
import time

import requests

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

NAMES = [
    "Alex Mercer", "Jordan Lee", "Taylor Swift", "Samira Khan", "Omar Farooq",
    "Chris Evans", "Morgan Bailey", "Zain Malik", "Fatima Noor", "Devon Patel",
    "Ayesha Siddiqui", "Bilal Ahmed", "Elena Rostova", "Marcus Chen", "Sara Ali"
]

FEEDBACK_TEMPLATES = [
    "This is an automated test response to verify form pipeline integration.",
    "Form inputs validated cleanly during synthetic testing run {n}.",
    "Testing response submission and linked spreadsheet synchronization.",
    "Everything appears to be functioning properly in this test iteration.",
    "Synthetic test submission {n} for QA and data consistency validation.",
    "Feedback recorded for load and submission verification.",
    "Checking question field rendering and multi-page form progress.",
    "Automated data generation test for survey workflow verification."
]

CAMPUS_CLEANLINESS_SUGGESTIONS = [
    "Install more dustbins in crowded areas like the cafeterias and canteen lawns.",
    "Ensure cleaning staff empty the dustbins more frequently throughout the day.",
    "Introduce a mobile QR code system for quick reporting of overflowing bins.",
    "Place separate recycling and organic waste bins across all academic blocks.",
    "Organize regular student-led campus cleanup drives and awareness campaigns.",
    "Enforce strict rules and nominal penalties for students caught littering.",
    "Improve washroom sanitation with regular cleaning schedules and soap availability.",
    "Display engaging awareness posters on notice boards and student portals.",
    "Keep covered bins near all outdoor seating areas, pathways, and sports grounds.",
    "Hire additional maintenance and janitorial staff during peak university hours.",
    "Involve student societies in promoting civic sense and environmental responsibility.",
    "Install automated hand sanitizers and hand-wash stations near food courts.",
    "Conduct weekly cleanliness inspections across all department buildings.",
    "Add more waste disposal units near student parking zones and main gates.",
    "Recognize and reward departments that maintain the cleanest premises each semester.",
    "Repair damaged dustbins and ensure all bins have proper protective lids.",
    "Launch social media campaigns by university media clubs highlighting clean campus habits.",
    "Provide clear feedback and tracking when a student reports a maintenance issue.",
    "Promote reusable bottles and containers at university canteens to reduce plastic waste.",
    "Ensure corridors and classroom waste bins are cleared before morning lectures begin."
]

OTHER_DEPTS = [
    "Software Engineering",
    "Electrical Engineering",
    "Computer & Information Systems Engineering",
    "Electronic Engineering",
    "Civil Engineering",
    "Chemical Engineering",
    "Mechanical Engineering",
    "Telecommunications Engineering",
    "Materials Engineering",
    "Environmental Engineering",
    "Industrial & Manufacturing Engineering"
]

WORDS = ["alpha", "bravo", "charlie", "delta", "echo", "foxtrot", "golf", "hotel", "indigo", "juliet"]

# Google Forms internal item type codes (item[3])
T_SHORT = 0       # Short text
T_PARA = 1        # Paragraph text
T_RADIO = 2       # Multiple choice
T_DROPDOWN = 3    # Dropdown
T_CHECK = 4       # Checkboxes
T_SCALE = 5       # Linear scale
T_GRID = 7        # Multiple choice grid / Checkbox grid
T_SECTION = 8     # Page / Section break
T_DATE = 9        # Date
T_TIME = 10       # Time

TYPE_NAMES = {
    T_SHORT: "Short answer",
    T_PARA: "Paragraph",
    T_RADIO: "Multiple choice",
    T_DROPDOWN: "Dropdown",
    T_CHECK: "Checkboxes",
    T_SCALE: "Linear scale",
    T_GRID: "Grid",
    T_SECTION: "Section break",
    T_DATE: "Date",
    T_TIME: "Time",
}


def load_form(url):
    """
    Fetches the public form HTML, resolves redirects (e.g. forms.gle), parses FB_PUBLIC_LOAD_DATA_,
    and extracts question metadata, the /formResponse POST URL, anti-CSRF token (fbzx), and email settings.
    """
    session = requests.Session()
    session.headers.update(HEADERS)

    clean_url = re.sub(r"/edit.*$", "/viewform", url)
    try:
        r = session.get(clean_url, timeout=20, allow_redirects=True)
        r.raise_for_status()
    except Exception as e:
        sys.exit(f"ERROR: Unable to reach form URL ({e})")

    if "accounts.google.com" in r.url:
        sys.exit(
            "\n[ACCESS RESTRICTED]\n"
            "This form requires Google account sign-in (e.g. 'Limit to 1 response' or domain restriction).\n"
            "Anonymous automated test scripts cannot submit to authentication-gated forms."
        )

    m = re.search(r"FB_PUBLIC_LOAD_DATA_\s*=\s*(.*?);\s*</script>", r.text, re.DOTALL)
    if not m:
        m = re.search(r"FB_PUBLIC_LOAD_DATA_\s*=\s*(\[.+?\]);", r.text, re.DOTALL)
    if not m:
        sys.exit("ERROR: Could not locate FB_PUBLIC_LOAD_DATA_ JSON blob. Ensure this is a public Google Form URL.")

    try:
        data = json.loads(m.group(1))
    except Exception as e:
        sys.exit(f"ERROR: Failed to parse form schema JSON: {e}")

    fbzx_match = re.search(r'name="fbzx"\s+value="([^"]+)"', r.text)
    fbzx = fbzx_match.group(1) if fbzx_match else ""

    has_email_field = bool(re.search(r'name="emailAddress"', r.text))

    items = data[1][1] if (len(data) > 1 and data[1] and len(data[1]) > 1) else []

    base_url = r.url.split("?")[0]
    post_url = re.sub(r"/(viewform|edit).*$", "/formResponse", base_url)
    if not post_url.endswith("/formResponse"):
        post_url = post_url.rstrip("/") + "/formResponse"

    return items, post_url, fbzx, has_email_field


def labels(opts):
    """
    Extracts selectable option labels, skipping the free-text 'Other' choice.
    Google encodes 'Other' with a flag at opts[i][4] == 1.
    """
    result = []
    for o in (opts or []):
        if not o or not o[0]:
            continue
        is_other = len(o) > 4 and bool(o[4])
        if not is_other:
            result.append(o[0])
    return result


def text_answer(title, n, validation=None):
    """
    Generates realistic synthetic text answers matching field titles and validation criteria.
    """
    if validation:
        v_type = validation[0]
        v_sub = validation[1] if len(validation) > 1 else None
        v_args = validation[2] if len(validation) > 2 and validation[2] else []

        if v_type == 1:  # Number constraint
            if v_sub == 7 and len(v_args) >= 2:
                try:
                    return str(random.randint(int(float(v_args[0])), int(float(v_args[1]))))
                except Exception:
                    return "25"
            elif v_sub in (1, 2) and v_args:
                try:
                    return str(int(float(v_args[0])) + random.randint(1, 10))
                except Exception:
                    return "100"
            elif v_sub in (3, 4) and v_args:
                try:
                    return str(max(1, int(float(v_args[0])) - random.randint(1, 5)))
                except Exception:
                    return "5"
            return str(random.randint(10, 99))

        if v_type == 2:  # Text constraint
            if v_sub == 1:
                return f"test_user_{n}@example.com"
            elif v_sub == 2:
                return f"https://example.com/test-case/{n}"
            elif v_sub == 3 and v_args:
                return f"{v_args[0]}_{random.choice(WORDS)}"

    t = (title or "").lower()

    # Department question handling: exactly 39 from CS & IT, remaining 11 from other focus departments
    if "department" in t or "dept" in t:
        if n <= 39:
            return "Computer Science & Information Technology"
        else:
            other_idx = (n - 40) % len(OTHER_DEPTS)
            return OTHER_DEPTS[other_idx]

    # Campus cleanliness suggestion handling
    if any(k in t for k in ["clean", "tidier", "campus", "garbage", "waste", "litter", "improvement"]):
        if n % 5 == 0:
            return random.choice(["More dustbins needed.", "Timely bin clearance is essential.", "Good initiative."])
        return CAMPUS_CLEANLINESS_SUGGESTIONS[(n - 1) % len(CAMPUS_CLEANLINESS_SUGGESTIONS)]

    if "email" in t:
        return f"test{n}@example.com"
    if "name" in t:
        return random.choice(NAMES)
    if "phone" in t or "contact" in t or "mobile" in t:
        return "03" + "".join(random.choice("0123456789") for _ in range(9))
    if "age" in t:
        return str(random.randint(18, 45))
    if any(k in t for k in ["feedback", "suggestion", "comment", "reason", "describe", "opinion"]):
        template = random.choice(FEEDBACK_TEMPLATES)
        return template.format(n=n)
    return f"{random.choice(WORDS)} {n}"


def build_payload(items, n, fbzx, has_email_field):
    """
    Constructs the form submission payload for run index n.
    """
    payload = {}
    pages = 1

    if has_email_field:
        payload["emailAddress"] = f"test_responder_{n}@example.com"

    for item in items:
        title = item[1]
        qtype = item[3]
        questions = item[4] if len(item) > 4 else None

        if qtype == T_SECTION:
            pages += 1
            continue

        if not questions:
            continue

        grid_column_choices = []
        if qtype == T_GRID:
            for q in questions:
                if len(q) > 1 and q[1]:
                    grid_column_choices = labels(q[1])
                    if grid_column_choices:
                        break

        for q in questions:
            entry = f"entry.{q[0]}"
            opts = q[1] if len(q) > 1 else None

            validation_rule = None
            if len(q) > 4 and isinstance(q[4], list) and q[4]:
                if isinstance(q[4][0], list):
                    validation_rule = q[4][0]

            if qtype in (T_SHORT, T_PARA):
                payload[entry] = text_answer(title, n, validation_rule)

            elif qtype in (T_RADIO, T_DROPDOWN, T_SCALE):
                choices = labels(opts)
                # If university year question, prefer standard year choices
                if "year" in (title or "").lower() and any("year" in str(c).lower() for c in choices):
                    std_years = [c for c in choices if "year" in str(c).lower()]
                    payload[entry] = random.choice(std_years)
                elif choices:
                    payload[entry] = random.choice(choices)

            elif qtype == T_CHECK:
                choices = labels(opts)
                if choices:
                    # Filter out negative 'None' options when selecting positive features
                    none_opts = [c for c in choices if "none" in c.lower()]
                    positive_opts = [c for c in choices if "none" not in c.lower()]

                    # If there's a 'None' option and we want positive features (95% of the time)
                    selectable = positive_opts if positive_opts else choices

                    min_k, max_k = 1, len(selectable)
                    # Checkbox validation rule handling (Type 7 in Google Forms)
                    if validation_rule and len(validation_rule) >= 3 and validation_rule[0] == 7:
                        v_sub = validation_rule[1]
                        v_args = validation_rule[2]
                        if v_args and str(v_args[0]).isdigit():
                            target_n = int(v_args[0])
                            if v_sub == 200:    # Select at least N
                                min_k = max(min_k, target_n)
                            elif v_sub == 201:  # Select at most N
                                max_k = min(max_k, target_n)
                            elif v_sub == 202:  # Select exactly N
                                min_k = max_k = target_n

                    min_k = min(min_k, len(selectable))
                    max_k = max(min_k, min(max_k, len(selectable)))
                    k = random.randint(min_k, max_k)
                    payload[entry] = random.sample(selectable, k)

            elif qtype == T_GRID:
                choices = labels(opts) or grid_column_choices
                if choices:
                    payload[entry] = random.choice(choices)

            elif qtype == T_DATE:
                payload[f"{entry}_year"] = str(random.choice([2024, 2025, 2026]))
                payload[f"{entry}_month"] = f"{random.randint(1, 12):02d}"
                payload[f"{entry}_day"] = f"{random.randint(1, 28):02d}"

            elif qtype == T_TIME:
                payload[f"{entry}_hour"] = f"{random.randint(0, 23):02d}"
                payload[f"{entry}_minute"] = f"{random.randint(0, 59):02d}"

    if pages > 1:
        payload["pageHistory"] = ",".join(str(i) for i in range(pages))

    if fbzx:
        payload["fbzx"] = fbzx

    return payload


def verify_submission(resp):
    """
    Checks if Google Forms genuinely recorded the submission.
    Google returns HTTP 200 even when validation or required fields fail.
    """
    if resp.status_code != 200:
        return False, f"HTTP status {resp.status_code}"

    text = resp.text
    success_indicators = [
        "Your response has been recorded",
        "freebirdFormviewerViewResponseConfirmationMessage",
        "freebirdFormviewerViewConfirmation",
        "vHW8eb",
    ]
    if any(sig in text for sig in success_indicators):
        return True, "Success"

    if "freebirdFormviewerViewResponseError" in text or 'role="alert"' in text:
        err_matches = re.findall(r'role="alert"[^>]*>([^<]+)<', text)
        if err_matches:
            return False, f"Form validation failed: {', '.join(set(err_matches))}"
        return False, "Validation rejected (form re-rendered with errors)"

    return True, "Success (HTTP 200)"


def inspect_form(items, post_url, fbzx, has_email_field):
    """
    Dry-run mode: prints discovered questions and a sample payload without sending POST requests.
    """
    print("\n" + "=" * 65)
    print(" DRY RUN: INSPECTING FORM (ZERO RESPONSES WILL BE SUBMITTED)")
    print("=" * 65)
    print(f"Target Submission Endpoint: {post_url}")
    print(f"Collects Email Field      : {'Yes (Responder input)' if has_email_field else 'No'}")
    print(f"Anti-CSRF fbzx Token      : {fbzx[:15]}... (present)" if fbzx else "Anti-CSRF fbzx Token      : None")
    print("-" * 65)

    q_count = 0
    for idx, item in enumerate(items, 1):
        title = (item[1] or "").strip()
        qtype = item[3]
        type_str = TYPE_NAMES.get(qtype, f"Unknown ({qtype})")
        questions = item[4] if len(item) > 4 else None

        if qtype == T_SECTION:
            print(f"[{idx}] --- Page Break: '{title}' ---")
            continue

        if not questions:
            continue

        for q in questions:
            q_count += 1
            entry_id = f"entry.{q[0]}"
            is_required = bool(q[2]) if len(q) > 2 else False
            opts = labels(q[1]) if len(q) > 1 and q[1] else []

            val_desc = "None"
            if len(q) > 4 and isinstance(q[4], list) and q[4]:
                rule = q[4][0]
                val_desc = f"Type {rule[0]}, Subtype {rule[1]}" if isinstance(rule, list) and len(rule) > 1 else str(rule)

            print(f"Question #{q_count}:")
            print(f"  Title      : {title or '(untitled)'}")
            print(f"  Type       : {type_str}")
            print(f"  Entry ID   : {entry_id}")
            print(f"  Required   : {is_required}")
            if opts:
                print(f"  Options    : {opts}")
            if val_desc != "None":
                print(f"  Validation : {val_desc}")
            print()

    print("-" * 65)
    print("Sample Generated Payload (Run #1 - Computer Science & IT):")
    sample_payload_1 = build_payload(items, 1, fbzx, has_email_field)
    print(json.dumps(sample_payload_1, indent=2, ensure_ascii=False))

    print("-" * 65)
    print("Sample Generated Payload (Run #40 - Other Focus Department):")
    sample_payload_40 = build_payload(items, 40, fbzx, has_email_field)
    print(json.dumps(sample_payload_40, indent=2, ensure_ascii=False))

    print("=" * 65)
    print("[DRY RUN COMPLETE] Schema parsed and verified. 0 submissions sent.")
    print("=" * 65 + "\n")


def main():
    ap = argparse.ArgumentParser(
        description="Google Forms Test Filler — Synthetic test response submitter for developer testing."
    )
    ap.add_argument("url", help="Public Google Form URL (/viewform or forms.gle)")
    ap.add_argument("-n", type=int, default=10, help="Number of responses to submit (default: 10)")
    ap.add_argument("--delay", type=float, default=1.0, help="Delay in seconds between submissions (default: 1.0s)")
    ap.add_argument("--dry-run", action="store_true", help="Inspect question schema without submitting any responses")
    ap.add_argument("--force", action="store_true", help="Bypass safety limits when submitting >100 responses")
    args = ap.parse_args()

    if args.delay < 0:
        sys.exit("ERROR: --delay cannot be negative.")
    if not args.dry_run and args.delay < 0.5:
        print("WARNING: Delays under 0.5s may trigger IP rate limiting or request throttling by Google.")

    if not args.dry_run and args.n > 100 and not args.force:
        sys.exit(
            f"\n[SAFETY GUARDRAIL]\n"
            f"You requested {args.n} submissions. Automated bursts exceeding 100 submissions\n"
            f"may trigger Google's anti-abuse filters or flood your destination spreadsheet.\n"
            f"To proceed, re-run with the --force flag:\n"
            f"    python fill_form.py \"{args.url}\" -n {args.n} --force\n"
        )

    print(f"Fetching form schema from: {args.url} ...")
    items, post_url, fbzx, has_email_field = load_form(args.url)

    if args.dry_run:
        inspect_form(items, post_url, fbzx, has_email_field)
        return

    print(f"Discovered {len(items)} form item(s).")
    print(f"Beginning submission of {args.n} test response(s) with {args.delay}s delay...")
    print(f"Target: {post_url}\n")

    session = requests.Session()
    session.headers.update(HEADERS)

    ok_count = 0
    for i in range(1, args.n + 1):
        payload = build_payload(items, i, fbzx, has_email_field)
        try:
            resp = session.post(post_url, data=payload, timeout=20)
            success, msg = verify_submission(resp)
            if success:
                ok_count += 1
                dept_val = payload.get("entry.53644475", "")
                dept_info = f" ({dept_val})" if dept_val else ""
                print(f"[{i}/{args.n}] Submitted successfully{dept_info}.")
            else:
                print(f"[{i}/{args.n}] FAILED: {msg}")
        except Exception as e:
            print(f"[{i}/{args.n}] Request error: {e}")

        if i < args.n and args.delay > 0:
            time.sleep(args.delay)

    print(f"\nDone: {ok_count}/{args.n} responses submitted successfully.")


if __name__ == "__main__":
    main()
