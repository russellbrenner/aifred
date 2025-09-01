from __future__ import annotations

import os
from typing import Any, Dict
import re


def run_web_search(args: Dict[str, Any]) -> Dict[str, Any]:
    query = args.get("query", "").strip()
    if not query:
        return {"error": "missing query"}
    # If disabled or no network, return stub
    if os.getenv("AIFRED_DRY_RUN") == "1" or os.getenv("AIFRED_NO_NET") == "1":
        return {"results": [f"Stub result for: {query}"]}
    try:
        import requests  # lazy import
        # Prefer DuckDuckGo Instant Answer API (JSON), then fallback to HTML
        r = requests.get(
            "https://api.duckduckgo.com/",
            params={"q": query, "format": "json", "no_redirect": 1, "no_html": 1},
            timeout=10,
            headers={"User-Agent": "aifred/1.0"},
        )
        r.raise_for_status()
        data = r.json()
        results = []
        if data.get("AbstractText"):
            results.append(data["AbstractText"])
        for topic in data.get("RelatedTopics", [])[:3]:
            if isinstance(topic, dict) and topic.get("Text"):
                results.append(topic["Text"])
        if not results:
            # HTML fallback for titles
            resp = requests.get(
                "https://duckduckgo.com/html/",
                params={"q": query},
                timeout=10,
                headers={"User-Agent": "aifred/1.0"},
            )
            resp.raise_for_status()
            text = resp.text
            hits = []
            for line in text.splitlines():
                line = line.strip()
                if "result__a" in line and ">" in line:
                    title = line.split(">", 1)[-1]
                    title = title.replace("</a", "").strip()
                    hits.append(title)
                if len(hits) >= 3:
                    break
            results = hits or ["No results parsed"]
        return {"results": results}
    except Exception as e:
        return {"error": str(e)}


def run_code_run(args: Dict[str, Any]) -> Dict[str, Any]:
    instructions = args.get("instructions", "")
    return {"message": "Code generation tool placeholder", "instructions": instructions}


def run_python_run(args: Dict[str, Any]) -> Dict[str, Any]:
    code = args.get("code", "")
    return {"message": "Python execution not supported; returning code for review.", "code": code}


def run_fetch_url(args: Dict[str, Any]) -> Dict[str, Any]:
    url = args.get("url", "")
    if os.getenv("AIFRED_DRY_RUN") == "1" or os.getenv("AIFRED_NO_NET") == "1":
        return {"url": url, "text": "[dry-run] content omitted"}
    try:
        import requests
        r = requests.get(url, timeout=15, headers={"User-Agent": "aifred/1.0"})
        r.raise_for_status()
        html = r.text
        try:
            from readability import Document  # readability-lxml
            doc = Document(html)
            summary_html = doc.summary(html_partial=True)
            # remove HTML tags to text
            text = re.sub(r"<[^>]+>", " ", summary_html)
            text = re.sub(r"\s+", " ", text).strip()
        except Exception:
            # fallback crude extraction
            text = re.sub(r"<script[\s\S]*?</script>", "", html, flags=re.I)
            text = re.sub(r"<style[\s\S]*?</style>", "", text, flags=re.I)
            text = re.sub(r"<[^>]+>", " ", text)
            text = re.sub(r"\s+", " ", text).strip()
        # limit
        return {"url": url, "text": text[:5000]}
    except Exception as e:
        return {"url": url, "error": str(e)}


CASE_CIT_PATTERN = re.compile(r"\b(\d{1,4})\s+([A-Za-z][A-Za-z\.\d]*)\s+(\d{1,5})\s*\(([^)]*?\s)?(\d{4})\)")
USC_CIT_PATTERN = re.compile(r"\b(\d+)\s+U\.S\.C\.\s+§+\s*(\d+[A-Za-z0-9\-]*)")


def run_citation_extract(args: Dict[str, Any]) -> Dict[str, Any]:
    text = args.get("text", "")
    cases = [m.group(0) for m in CASE_CIT_PATTERN.finditer(text)]
    statutes = [m.group(0) for m in USC_CIT_PATTERN.finditer(text)]
    return {"cases": cases[:50], "statutes": statutes[:50]}


def run_case_search(args: Dict[str, Any]) -> Dict[str, Any]:
    query = args.get("query", "").strip()
    if not query:
        return {"error": "missing query"}
    if os.getenv("AIFRED_DRY_RUN") == "1" or os.getenv("AIFRED_NO_NET") == "1":
        return {"results": [f"[dry-run] case search for: {query}"]}
    try:
        import requests
        url = "https://www.courtlistener.com/api/rest/v3/search/"
        r = requests.get(url, params={"q": query, "type": "o"}, timeout=15, headers={"User-Agent": "aifred/1.0"})
        r.raise_for_status()
        data = r.json()
        out = []
        for res in data.get("results", [])[:3]:
            cite = res.get("citation", "")
            title = res.get("caseName", "") or res.get("title", "")
            absolute_url = res.get("absolute_url") or res.get("url") or ""
            if absolute_url and not absolute_url.startswith("http"):
                absolute_url = "https://www.courtlistener.com" + absolute_url
            out.append({"title": title, "citation": cite, "url": absolute_url})
        if not out:
            return {"results": ["No cases found"]}
        return {"results": out}
    except Exception as e:
        return {"error": str(e)}


TOOL_IMPL = {
    "web_search": run_web_search,
    "code_run": run_code_run,
    "python_run": run_python_run,
    "fetch_url": run_fetch_url,
    "citation_extract": run_citation_extract,
    "case_search": run_case_search,
}


def execute_tool_call(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    fn = TOOL_IMPL.get(name)
    if not fn:
        return {"error": f"unknown tool: {name}"}
    return fn(arguments or {})
