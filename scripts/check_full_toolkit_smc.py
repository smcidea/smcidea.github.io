"""Validate the SMC Chart app embedded in the full toolkit HTML."""
from pathlib import Path
import re
import subprocess
import tempfile

SOURCE = Path("/home/ubuntu/smc_nepse_github/smc_toolkit_github_features.html")


def decode(raw: str) -> str:
    return (raw.replace("<\\/script>", "</script>")
               .replace("\\${", "${")
               .replace("\\`", "`")
               .replace("\\\\'", "\\'")
               .replace("\\\\", "\\"))


def main() -> None:
    source = SOURCE.read_text(encoding="utf-8")
    marker = "  apps[10] = `"
    start = source.find(marker)
    if start < 0:
        raise SystemExit("apps[10] not found")
    start += len(marker)
    end = source.find("</body></html>`;", start)
    if end < 0:
        raise SystemExit("apps[10] end marker not found")
    app = decode(source[start:end] + "</body></html>")

    required = ["const CHUNK_MANIFEST_URL = REPO_ORIGIN + '/data/chunks/manifest.json';", "const fullPromise = fetchChunkedRows();"]
    for item in required:
        if item not in app:
            raise SystemExit(f"missing required GitHub loader text: {item}")
    forbidden = ["const SHEET_URL =", "SHEET_URL + '?type=fast'", "script.google.com/macros"]
    for item in forbidden:
        if item in app:
            raise SystemExit(f"forbidden SMC Chart reference remains: {item}")

    scripts = re.findall(r"<script(?:\\s[^>]*)?>(.*?)</script>", app, flags=re.S | re.I)
    js_files = []
    for idx, script in enumerate(scripts):
        if script.strip():
            path = Path(tempfile.gettempdir()) / f"smc_full_app10_{idx}.js"
            path.write_text(script, encoding="utf-8")
            js_files.append(path)
            result = subprocess.run(["node", "--check", str(path)], text=True, capture_output=True)
            if result.returncode:
                raise SystemExit(f"JavaScript syntax failed in {path}:\n{result.stderr}")
    print(f"apps[10] validated: {len(app):,} bytes, {len(js_files)} script blocks")
    print("GitHub manifest loader: OK")
    print("No SMC Chart Apps Script data reference: OK")
    print("JavaScript syntax: OK")


if __name__ == "__main__":
    main()
