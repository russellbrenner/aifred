from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


MODEL_PREFIXES = (
    # OpenAI
    "gpt-",
    "o4",
    "o3",
    # Anthropic
    "claude-",
)


def _is_model_token(token: str) -> bool:
    token_l = token.lower()
    return any(token_l.startswith(p) for p in MODEL_PREFIXES)


@dataclass
class Directives:
    model: Optional[str] = None
    provider: Optional[str] = None  # "openai" | "anthropic"
    temp: Optional[float] = None
    max: Optional[int] = None
    name: Optional[str] = None
    cont: bool = False
    new: bool = False
    tools: List[str] = field(default_factory=list)
    sys: Optional[str] = None
    pplx: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "model": self.model,
            "provider": self.provider,
            "temp": self.temp,
            "max": self.max,
            "name": self.name,
            "cont": self.cont,
            "new": self.new,
            "tools": self.tools or [],
            "sys": self.sys,
        }


TOKEN_RE = re.compile(r"@([A-Za-z0-9_\-]+)(?::(\"([^\"]*)\"|([^\s]+)))?")


def parse_directives(text: str) -> Tuple[str, Directives]:
    """Parse @directives from free text.

    Supports:
    - @gpt-4o / @claude-3-7-sonnet (model tokens)
    - @temp:0.7, @max:1200, @provider:openai, @name:research
    - @new, @cont
    - @tools:browse,code,python
    - @sys:"quoted string with spaces"

    Later duplicates override earlier ones. Unknown @tokens are left intact in text.
    Returns (clean_text, directives).
    """
    directives = Directives()
    remove_spans: List[Tuple[int, int]] = []

    for m in TOKEN_RE.finditer(text):
        full = m.group(0)
        key = m.group(1)
        qval = m.group(3)
        uval = m.group(4)
        val = qval if qval is not None else uval

        key_l = key.lower()

        # Model as bare token
        if val is None and _is_model_token(key_l):
            directives.model = key
            remove_spans.append(m.span())
            continue

        # Bare flags
        if val is None and key_l in {"new", "cont"}:
            if key_l == "new":
                directives.new = True
            elif key_l == "cont":
                directives.cont = True
            remove_spans.append(m.span())
            continue

        # Keyed values
        if key_l == "temp" and val is not None:
            try:
                directives.temp = float(val)
                remove_spans.append(m.span())
                continue
            except ValueError:
                pass  # leave token intact

        if key_l == "max" and val is not None:
            try:
                directives.max = int(val)
                remove_spans.append(m.span())
                continue
            except ValueError:
                pass

        if key_l == "provider" and val is not None:
            pv = val.lower()
            if pv in {"openai", "anthropic"}:
                directives.provider = pv
                remove_spans.append(m.span())
                continue

        if key_l == "name" and val is not None:
            directives.name = val
            remove_spans.append(m.span())
            continue

        if key_l == "tools" and val is not None:
            tools = [t.strip() for t in val.split(",") if t.strip()]
            directives.tools = tools
            remove_spans.append(m.span())
            continue

        if key_l in {"sys", "system"} and val is not None:
            directives.sys = val
            remove_spans.append(m.span())
            continue

        # Perplexity options: @pplx_recency:month, @pplx_depth:detailed, @pplx_domain:law, @pplx_citations:1, @pplx_images:0
        if key_l.startswith("pplx_") and val is not None:
            directives.pplx[key_l[5:]] = val
            remove_spans.append(m.span())
            continue

        if key_l == "pplx" and val is not None:
            # comma-separated k=v pairs
            try:
                pairs = [x.strip() for x in val.split(",") if x.strip()]
                for pr in pairs:
                    if "=" in pr:
                        k, v = pr.split("=", 1)
                        directives.pplx[k.strip()] = v.strip()
                remove_spans.append(m.span())
                continue
            except Exception:
                pass

        # Model provided via @model:value (rare) or @gpt-4 style handled earlier
        if key_l == "model" and val is not None:
            directives.model = val
            remove_spans.append(m.span())
            continue

        # Unrecognised token: keep in text

    # Build cleaned text excluding recognised directive spans
    if not remove_spans:
        cleaned = " ".join(text.split())
        return cleaned, directives

    # Merge spans and remove from text
    result = []
    last = 0
    for start, end in sorted(remove_spans):
        if start > last:
            result.append(text[last:start])
        last = end
    if last < len(text):
        result.append(text[last:])

    cleaned = re.sub(r"\s+", " ", "".join(result)).strip()
    return cleaned, directives


def summarise_directives(d: Directives) -> str:
    parts: List[str] = []
    if d.model:
        parts.append(d.model)
    if d.temp is not None:
        parts.append(f"temp {d.temp}")
    if d.max is not None:
        parts.append(f"max {d.max}")
    if d.tools:
        parts.append("tools: " + ",".join(d.tools))
    if d.provider:
        parts.append(d.provider)
    if d.new:
        parts.append("new")
    if d.cont:
        parts.append("cont")
    return " | ".join(parts) if parts else "defaults"
