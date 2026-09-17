# -*- coding: utf-8 -*-
"""
build_html.py
Builds the single, self-contained static site (index.html) from one template
and the two computed data files — no duplicated pages:

    index.html = site_template.html
                 with __ENGINE_DATA__ -> dashboard_data.json        (leak-detection engine)
                 and  __REAL_DATA__   -> real_dashboard_data.json    (national gap, real data)

Run after changing the template or refreshing the data:

    python build_html.py

Output is UTF-8 (no BOM); the template declares <meta charset="utf-8"> so the
Arabic renders correctly whether index.html is opened directly, served locally,
or hosted on GitHub Pages. Chart.js is loaded from the local vendor/ folder, so
the page needs no internet at runtime.
"""
import json
import os
import sys

TEMPLATE = "site_template.html"
OUTPUT = "index.html"
CHARTJS = "vendor/chart.umd.min.js"
CHARTJS_TAG = '<script src="vendor/chart.umd.min.js"></script>'
DATA = {
    "__ENGINE_DATA__": "dashboard_data.json",
    "__REAL_DATA__": "real_dashboard_data.json",
    "__NETWORK_DATA__": "network_data.json",
}


def read_text(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    os.chdir(here)

    if not os.path.exists(TEMPLATE):
        raise FileNotFoundError(f"template not found: {TEMPLATE}")
    html = read_text(TEMPLATE)

    for placeholder, data_path in DATA.items():
        if not os.path.exists(data_path):
            raise FileNotFoundError(
                f"data file not found: {data_path} "
                f"(run analysis.py / real_analysis.py to regenerate it)"
            )
        if placeholder not in html:
            raise ValueError(f"{TEMPLATE} is missing placeholder {placeholder}")
        data_text = read_text(data_path)
        json.loads(data_text)  # validate before injecting
        html = html.replace(placeholder, data_text)

    # Inline Chart.js so index.html is a SINGLE self-contained file: no vendor/
    # folder, no relative paths — trivial to upload (one file) and it works when
    # opened directly, served locally, or hosted on GitHub Pages.
    inlined = False
    if os.path.exists(CHARTJS) and CHARTJS_TAG in html:
        js = read_text(CHARTJS).replace("</script", "<\\/script")  # keep the parser safe
        html = html.replace(CHARTJS_TAG, "<script>" + js + "</script>")
        inlined = True

    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Built {OUTPUT} ({len(html):,} chars) from {TEMPLATE} + "
          f"{', '.join(DATA.values())}"
          + ("  [Chart.js inlined — single self-contained file]" if inlined else ""))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # pragma: no cover
        print(f"BUILD FAILED: {exc}", file=sys.stderr)
        sys.exit(1)
