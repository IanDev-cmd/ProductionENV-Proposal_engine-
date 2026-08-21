"""
cover_contact.py
----------------
Page 1 (cover) and contact/RM sign-off handlers, plus house-style formatters.
Uses batched redaction for speed and measured TemplateProfile geometry.
"""

from datetime import datetime
import logging
import re

import config
from pdf_ops import prepare_field_draw, draw_fields_batched

_log = logging.getLogger("weott.cover_contact")


def _parse_iso_datetime(raw: str):
    s = raw.strip()
    if not s:
        return None
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(s)
    except ValueError:
        pass
    try:
        return datetime.strptime(s[:10], "%Y-%m-%d")
    except ValueError:
        return None


_ORDINAL = {1: "st", 2: "nd", 3: "rd"}


def _ordinal(n: int) -> str:
    if 10 <= (n % 100) <= 20:
        return "th"
    return _ORDINAL.get(n % 10, "th")


def format_event_date(value: str) -> str:
    if value is None:
        return ""
    raw = str(value).strip()
    if not raw:
        return ""
    if re.match(r"^(date\s*)?tbc$", raw, re.I) or raw.upper() == "TBC":
        return "Date TBC"

    flexible = bool(
        re.search(r"(?i)(?:\n\s*tbc\s*$|\(date\s*tbc\)|\(tbc\)|\bflexible\b)", raw)
    ) or bool(re.search(r"(?i)\btbc\b", raw))

    date_part = re.sub(r"(?i)\s*\n\s*tbc\s*$", "", raw)
    date_part = re.sub(r"(?i)\s*\(date\s*tbc\)\s*", "", date_part)
    date_part = re.sub(r"(?i)\s*\(tbc\)\s*", "", date_part)
    date_part = re.sub(r"(?i)\s*\bflexible\b\s*", "", date_part).strip()
    date_part = re.sub(r"(?i)\s*\btbc\b\s*$", "", date_part).strip()

    if not date_part or re.match(r"^(date\s*)?tbc$", date_part, re.I):
        return "Date TBC"

    iso = _parse_iso_datetime(date_part)
    if iso:
        formatted = f"{iso.strftime('%A')} {iso.day}{_ordinal(iso.day)} {iso.strftime('%B %Y')}"
    else:
        _log.info("event_date regex fallback for %r", date_part[:80])
        months = "January February March April May June July August September October November December"
        if any(m in date_part for m in months.split()) and re.search(r"\d", date_part):
            formatted = date_part
        else:
            formatted = date_part
            for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d"):
                try:
                    dt = datetime.strptime(date_part[:10], fmt)
                    formatted = f"{dt.strftime('%A')} {dt.day}{_ordinal(dt.day)} {dt.strftime('%B %Y')}"
                    break
                except ValueError:
                    continue

    if flexible:
        return f"{formatted}\nTBC"
    return formatted


def format_event_date_compact(value: str) -> str:
    """Shorter house style when the full weekday date won't fit the panel."""
    raw = format_event_date(value)
    if raw in ("", "TBC", "Date TBC"):
        return raw
    flexible = "\nTBC" in raw
    date_only = raw.replace("\nTBC", "").strip()
    source = str(value).strip().split("\n")[0]
    source = re.sub(r"(?i)\s*\(date\s*tbc\)\s*", "", source).strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            dt = datetime.strptime(source[:10], fmt)
            compact = f"{dt.strftime('%a')} {dt.day}{_ordinal(dt.day)} {dt.strftime('%b %Y')}"
            return f"{compact}\nTBC" if flexible else compact
        except ValueError:
            continue
    m = re.match(
        r"(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\s+(\d{1,2})(st|nd|rd|th)\s+"
        r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})",
        date_only,
    )
    if m:
        day_map = {
            "Monday": "Mon", "Tuesday": "Tue", "Wednesday": "Wed", "Thursday": "Thu",
            "Friday": "Fri", "Saturday": "Sat", "Sunday": "Sun",
        }
        mon_map = {
            "January": "Jan", "February": "Feb", "March": "Mar", "April": "Apr",
            "May": "May", "June": "Jun", "July": "Jul", "August": "Aug",
            "September": "Sep", "October": "Oct", "November": "Nov", "December": "Dec",
        }
        compact = f"{day_map[m.group(1)]} {m.group(2)}{m.group(3)} {mon_map[m.group(4)]} {m.group(5)}"
        return f"{compact}\nTBC" if flexible else compact
    return raw


def format_event_timings(value: str, *, include_tbc: bool = True) -> str:
    if value is None:
        return ""
    raw = str(value).strip()
    if not raw:
        return ""
    times = re.findall(r"(\d{1,2}:\d{2})", raw)
    if len(times) >= 2:
        def norm(t):
            h, m = t.split(":")
            return f"{int(h):02d}:{m}"
        out = f"{norm(times[0])}hrs – {norm(times[1])}hrs"
    else:
        out = raw.replace("-", "–").replace(" - ", " – ")
        out = re.sub(r"(\d{1,2}:\d{2})(?!\s*hrs)", r"\1hrs", out)
    has_tbc = bool(re.search(r"\(?\s*TBC\s*\)?", raw, re.I))
    if has_tbc and "(TBC)" not in out:
        out = f"{out} (TBC)"
    return out


def format_quote_date(value: str) -> str:
    if value is None:
        return ""
    raw = str(value).strip()
    raw = re.split(r"\s*\|\s*Quotation valid", raw, maxsplit=1)[0].strip()
    months = "January February March April May June July August September October November December"
    if any(m in raw for m in months.split()):
        return raw
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            dt = datetime.strptime(raw[:10], fmt)
            return f"{dt.day} {dt.strftime('%B %Y')}"
        except ValueError:
            continue
    return raw


def format_guest_range(value) -> str:
    if value is None:
        return ""
    raw = str(value).strip()
    m = re.match(r"(\d+)\s*[-–—to]+\s*(\d+)", raw, re.I)
    if m:
        return f"{m.group(1)} \u2013 {m.group(2)}"
    return raw


_PHONE_PLACEHOLDERS = {"", "—", "-", "–", "n/a", "na", "none", "tbc"}
_PHONE_LABEL_RE = re.compile(r"^\s*(?:t|m|tel|mob(?:ile)?|phone)\s*[:.\-]?\s*", re.I)
_LABELED_PHONE_RE = re.compile(
    r"(?:^|[\s,;/|])(?:(tel|t)|(mobile|mob|m))\s*[:.\-]?\s*([\d+()\s.-]{7,})",
    re.I,
)


def strip_phone_label(raw: str) -> str:
    return _PHONE_LABEL_RE.sub("", str(raw or "")).strip()


def _phone_digits(raw: str) -> str:
    d = re.sub(r"\D", "", str(raw or ""))
    if d.startswith("44") and len(d) > 10:
        d = d[2:]
    if d and not d.startswith("0") and len(d) == 10:
        d = "0" + d
    return d


def format_uk_phone(raw) -> str:
    """House-style UK number. Never includes T: / M: labels."""
    s = str(raw or "").strip()
    if not s:
        return ""
    if s.lower() in _PHONE_PLACEHOLDERS:
        return "—" if s == "—" else ""
    stripped = strip_phone_label(s)
    if stripped.lower() in _PHONE_PLACEHOLDERS:
        return "—" if stripped == "—" else ""
    d = _phone_digits(stripped)
    if len(d) != 11:
        return stripped
    if d.startswith("02"):
        return f"{d[:3]} {d[3:7]} {d[7:]}"
    if d.startswith(("07", "03")):
        return f"{d[:5]} {d[5:8]} {d[8:]}"
    if d.startswith("08"):
        return f"{d[:4]} {d[4:7]} {d[7:]}"
    if d.startswith("01"):
        if d[1:3] in ("11", "21", "31", "41", "51", "61", "71", "81", "91"):
            return f"{d[:4]} {d[4:7]} {d[7:]}"
        return f"{d[:5]} {d[5:8]} {d[8:]}"
    return f"{d[:5]} {d[5:8]} {d[8:]}"


def parse_phone_fields(raw) -> dict:
    """Split CRM blobs such as 'T: 03309 005 500 M: 07407 780 281'."""
    text = str(raw or "").strip()
    if not text:
        return {"landline": "", "mobile": "", "display": "", "telephone": ""}
    if text == "—":
        return {"landline": "", "mobile": "", "display": "—", "telephone": "—"}

    landline = ""
    mobile = ""
    extras = []
    for match in _LABELED_PHONE_RE.finditer(text):
        formatted = format_uk_phone(match.group(3))
        if match.group(1):
            landline = landline or formatted
        elif match.group(2):
            mobile = mobile or formatted

    remainder = _LABELED_PHONE_RE.sub(" ", text)
    remainder = re.sub(r"\b(?:t|m|tel|mob(?:ile)?|phone)\s*[:.\-]?\s*", " ", remainder, flags=re.I)
    for part in re.split(r"\s*(?:[/|,;]|\band\b)\s*", remainder, flags=re.I):
        if re.search(r"\d", part or ""):
            formatted = format_uk_phone(part)
            if formatted and formatted not in extras:
                extras.append(formatted)

    def _kind(formatted: str) -> str:
        d = _phone_digits(formatted)
        if d.startswith("07"):
            return "mobile"
        if len(d) >= 10:
            return "landline"
        return ""

    if not landline and not mobile and not extras:
        one = format_uk_phone(text)
        if _kind(one) == "mobile":
            mobile = one
        else:
            landline = one
    else:
        for extra in extras:
            kind = _kind(extra)
            if kind == "mobile" and not mobile:
                mobile = extra
            elif not landline:
                landline = extra
            elif not mobile:
                mobile = extra

    display = " / ".join(p for p in (landline, mobile) if p)
    return {
        "landline": landline,
        "mobile": mobile,
        "display": display,
        "telephone": landline or mobile,
    }


_STAFF_FULL_NAMES = {
    "natasha": "Natasha Minter",
    "katherine": "Katherine Bulaon",
    "sapphire": "Sapphire Adams",
    "elizabeth": "Elizabeth Hillier",
    "ellie": "Ellie Kirotar",
    "lily-may": "Lily-May Cameron",
    "lily may": "Lily-May Cameron",
}


def format_prepared_by_name(raw: str) -> str:
    s = re.sub(r"^\s*prepared\s+by\s+", "", str(raw or "").strip(), flags=re.I).strip()
    if "|" in s:
        s = s.split("|", 1)[0].strip()
    s = " ".join(s.split())
    key = s.lower()
    if key in _STAFF_FULL_NAMES:
        return _STAFF_FULL_NAMES[key]
    first = key.split()[0] if key else ""
    if first in _STAFF_FULL_NAMES and " " not in s:
        return _STAFF_FULL_NAMES[first]
    return s


def normalize_cover_lead(lead: dict) -> dict:
    out = dict(lead)
    if "prepared_by" in out:
        out["prepared_by"] = format_prepared_by_name(out.get("prepared_by") or "")
    if "event_date" in out:
        out["event_date"] = format_event_date(out["event_date"])
    if "event_timings" in out:
        original = str(lead.get("event_timings", ""))
        formatted = format_event_timings(original, include_tbc=False)
        if re.search(r"TBC", original, re.I) and "(TBC)" not in formatted:
            formatted = f"{formatted} (TBC)"
        out["event_timings"] = formatted
    if "quote_date" in out:
        out["quote_date"] = format_quote_date(out["quote_date"])
    if "telephone" in out:
        parsed = parse_phone_fields(out.get("telephone"))
        out["telephone"] = parsed["display"] or parsed["telephone"]
    if "contact_phone" in out:
        parsed = parse_phone_fields(out.get("contact_phone"))
        out["contact_phone"] = parsed["landline"] or parsed["telephone"]
        if parsed["mobile"] and not out.get("contact_mobile"):
            out["contact_mobile"] = parsed["mobile"]
    if "contact_mobile" in out:
        parsed = parse_phone_fields(out.get("contact_mobile"))
        out["contact_mobile"] = parsed["mobile"] or parsed["telephone"]
    if "guest_range" in out:
        out["guest_range"] = format_guest_range(out["guest_range"])
    if "guest_quote_n" in out:
        out["guest_quote_n"] = str(out["guest_quote_n"]).strip()
    return out


def fill_cover_page(doc, data: dict, font_mgr, warnings: list, profile=None):
    page_index = profile.page_cover if profile else config.PAGE_COVER
    fields = profile.cover_fields if profile and profile.cover_fields else config.COVER_FIELDS
    page = doc[page_index]
    font_mgr.ensure_registered(page)
    data = normalize_cover_lead(data)

    prepared = []
    for field_name, spec in fields.items():
        if field_name not in data or not spec:
            continue
        value = str(data[field_name])
        # If event_date won't fit at designed size, use compact form before shrink
        tbc_under = False
        if field_name == "event_date":
            if "\n" in value:
                parts = value.split("\n", 1)
                value = parts[0].strip()
                tbc_under = "TBC" in parts[1].upper()
            max_w = spec.get("max_width", 56)
            if font_mgr.text_length(value, spec["size"], spec.get("bold", False)) > max_w:
                compact = format_event_date_compact(data[field_name])
                if "\n" in compact:
                    cparts = compact.split("\n", 1)
                    value = cparts[0].strip()
                    tbc_under = True
                else:
                    value = compact
        # Page 1 must stay pixel-perfect with the chosen template: measured
        # span colour + Century Gothic only. Page-13 pure-white / Fallback-Bold
        # styling must not leak onto the cover.
        spec = dict(spec)
        spec["color"] = _cover_ink_from_template(spec.get("color"))
        # Keep brand CG on cover even for "bold" fields (template-extracted CG
        # Bold subsets can't re-embed; Fallback Bold reads as a different face).
        want_weight = bool(spec.get("bold"))
        spec["bold"] = False
        spec["deep_bold"] = want_weight  # light echo approximates template bold
        prepared.append(prepare_field_draw(spec, value, font_mgr, warnings, field_name))
        if field_name == "event_date" and tbc_under:
            # Date origin is (410.4, 52.0); place TBC ~5pt below so it stays
            # readable under the date without overlapping neighbouring panel copy.
            x0, y = spec["origin"]
            tbc_y = y + 5.0
            tbc_spec = dict(
                bbox=spec["bbox"],
                origin=(x0, tbc_y),
                size=float(spec.get("size") or 4.63),
                bold=False,
                deep_bold=False,
                color=spec["color"],
                max_width=float(spec.get("max_width") or 56),
                skip_redact=True,
            )
            prepared.append(prepare_field_draw(tbc_spec, "TBC", font_mgr, warnings, "event_date_tbc"))

    draw_fields_batched(page, prepared, font_mgr, clear_graphics=False)


def _cover_ink_from_template(color) -> tuple:
    """
    Cover ink must match the template PDF, not Page-13 pure white.

    Catalog templates store panel copy as RGB(230,242,243). Re-inserting with
    that exact triplet keeps edited values identical to static labels.
    """
    if color and isinstance(color, (tuple, list)) and len(color) >= 3:
        return (float(color[0]), float(color[1]), float(color[2]))
    # Same triplet measured from assets/templates/catalog/**/template.pdf covers
    return (230 / 255, 242 / 255, 243 / 255)


def fill_contact_page(doc, data: dict, font_mgr, warnings: list, profile=None):
    fields = profile.contact_fields if profile and profile.contact_fields else config.CONTACT_FIELDS
    # Group by page for batched apply
    by_page: dict[int, list] = {}
    for field_name, spec in fields.items():
        if field_name not in data or not spec:
            continue
        page_i = spec.get("page", profile.page_contact if profile else config.PAGE_CONTACT)
        value = str(data[field_name])
        if field_name == "contact_email":
            value = re.sub(r"^\s*E:\s*", "", value, flags=re.I)
        elif field_name == "contact_phone":
            parsed = parse_phone_fields(value)
            value = parsed["landline"] or parsed["telephone"]
        elif field_name == "contact_mobile":
            parsed = parse_phone_fields(value)
            value = parsed["mobile"] or parsed["telephone"]
        page = doc[page_i]
        font_mgr.ensure_registered(page)
        item = prepare_field_draw(spec, value, font_mgr, warnings, field_name)
        by_page.setdefault(page_i, []).append(item)

    for page_i, items in by_page.items():
        draw_fields_batched(doc[page_i], items, font_mgr, clear_graphics=False)
