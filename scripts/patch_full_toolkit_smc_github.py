"""Patch only the embedded SMC Chart app in a full toolkit HTML file.

The outer toolkit contains each app in a JavaScript template literal.  This
script decodes apps[10], applies the GitHub chunk-loader changes to that app,
then re-encodes and reinserts it without touching the other app entries.
"""
from pathlib import Path
import re

SOURCE = Path("/home/ubuntu/upload/smc_toolkit_ohlc4(99).html")
TARGET = Path("/home/ubuntu/smc_nepse_github/smc_toolkit_github_features.html")


def decode_nested_template(raw: str) -> str:
    """Convert the nested app template literal into its standalone HTML."""
    text = raw.replace("<\\/script>", "</script>")
    text = text.replace("\\${", "${")
    text = text.replace("\\`", "`")
    text = text.replace("\\\\'", "\\'")
    text = text.replace("\\\\", "\\")
    return text


def encode_nested_template(document: str) -> str:
    """Escape a standalone app so it can safely live in apps[10] = `...`."""
    text = document.replace("\\", "\\\\")
    text = text.replace("`", "\\`")
    text = text.replace("${", "\\${")
    text = text.replace("</script>", "<\\/script>")
    return text


def patch_smc_document(document: str) -> str:
    data_config = (
        "const REPO_ORIGIN = (() => { try { return (window.top && window.top.location && window.top.location.origin && window.top.location.origin !== 'null') ? window.top.location.origin : window.location.origin; } catch (_) { return window.location.origin; } })();\n"
        "const GITHUB_DATA_URL = REPO_ORIGIN + '/data/nepse_ohlc.json';\n"
        "const GITHUB_FAST_URL = REPO_ORIGIN + '/data/nepse_ohlc_fast.json';\n"
        "const CHUNK_MANIFEST_URL = REPO_ORIGIN + '/data/chunks/manifest.json';\n"
        "const DATA_URL = CHUNK_MANIFEST_URL;"
    )
    document, n = re.subn(
        r"const SHEET_URL = '[^']+';",
        data_config,
        document,
        count=1,
    )
    if n != 1:
        raise RuntimeError("Could not find the SMC Chart SHEET_URL declaration")

    document = document.replace("SHEET_URL + '?type=fast'", "GITHUB_FAST_URL")
    document = document.replace("SHEET_URL", "DATA_URL")

    chunk_loader = """
async function fetchChunkedRows() {
    const manifestResponse = await fetchWithTimeout(CHUNK_MANIFEST_URL + '?v=' + Date.now(), { method: 'GET', redirect: 'follow', cache: 'no-store' }, 10000);
    if (!manifestResponse.ok) throw new Error('Chunk manifest request failed: ' + manifestResponse.status);
    const manifest = await manifestResponse.json();
    if (!manifest || !Array.isArray(manifest.files) || !manifest.files.length) throw new Error('No history chunks found in repository');
    const parts = await Promise.all(manifest.files.map(async (file) => {
        const response = await fetchWithTimeout(REPO_ORIGIN + '/data/chunks/' + encodeURIComponent(file) + '?v=' + Date.now(), { method: 'GET', redirect: 'follow', cache: 'no-store' }, 20000);
        if (!response.ok) throw new Error('History chunk request failed: ' + file + ' (' + response.status + ')');
        const rows = await response.json();
        return Array.isArray(rows) ? rows : [];
    }));
    return parts.flat().sort((a, b) => String(a.Date || '').localeCompare(String(b.Date || '')));
}
"""
    if "async function fetchChunkedRows()" not in document:
        document = document.replace(
            "async function loadData(options) {",
            chunk_loader + "\nasync function loadData(options) {",
            1,
        )

    document = document.replace(
        "fetchWithTimeout(GITHUB_FAST_URL, { method: 'GET', redirect: 'follow' }, 10000)",
        "fetchWithTimeout(GITHUB_FAST_URL + '?v=' + Date.now(), { method: 'GET', redirect: 'follow', cache: 'no-store' }, 10000)",
    )
    document = document.replace(
        "fetchWithTimeout(DATA_URL, { method: 'GET', redirect: 'follow' }, 14000)",
        "fetchChunkedRows()",
    )
    document = document.replace(
        "fetchWithTimeout(DATA_URL, { method: 'GET', redirect: 'follow' }, 60000)",
        "fetchChunkedRows()",
    )
    document = document.replace(
        "const fullPromise = fetchChunkedRows()\n        .then(r => { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); });",
        "const fullPromise = fetchChunkedRows();",
    )

    # Fresh namespace prevents the previous Apps Script/full-file cache from
    # overriding the newly loaded GitHub chunks.
    document = document.replace("const CACHE_KEY_FAST = 'nepse_chart_cache_fast';", "const CACHE_KEY_FAST = 'nepse_chart_cache_fast_github_features_v1';")
    document = document.replace("const CACHE_KEY_FULL = 'nepse_chart_cache_full';", "const CACHE_KEY_FULL = 'nepse_chart_cache_full_github_features_v1';")
    document = document.replace("const IDB_NAME       = 'nepse_chart_idb';", "const IDB_NAME       = 'nepse_chart_idb_github_features_v1';")

    document = document.replace("Apps Script endpoint", "repository data files")
    document = document.replace("from the Apps Script output", "from the repository JSON output")
    document = document.replace("Ensure the Apps Script is deployed with access set to \"Anyone\".", "Ensure the repository data files are uploaded and accessible, then refresh.")
    return document


def main() -> None:
    source = SOURCE.read_text(encoding="utf-8")
    marker = "  apps[10] = `"
    start = source.find(marker)
    if start < 0:
        raise RuntimeError("Could not find apps[10] in the new toolkit")
    body_start = start + len(marker)
    end_marker = "</body></html>`;"
    end = source.find(end_marker, body_start)
    if end < 0:
        raise RuntimeError("Could not find apps[10] closing marker")

    raw_app = source[body_start:end]
    standalone = decode_nested_template(raw_app) + "</body></html>"
    patched = patch_smc_document(standalone)
    encoded = encode_nested_template(patched[:-len("</body></html>")])
    output = source[:body_start] + encoded + source[end:]
    TARGET.write_text(output, encoding="utf-8")
    print(f"Wrote {TARGET} ({len(output):,} bytes)")
    print(f"SMC app bytes: {len(patched):,}; other toolkit bytes preserved outside apps[10].")


if __name__ == "__main__":
    main()
