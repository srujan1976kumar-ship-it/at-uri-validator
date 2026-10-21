from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
import json
import re

app = FastAPI(title="AT URI Syntax Compatibility and Round-Trip Validator")
app.mount("/static", StaticFiles(directory="static"), name="static")

class ValidateRequest(BaseModel):
    uri: str
    mode: str = "lexicon"



def parse_at_uri(uri: str):
    """Parse an AT URI while preserving its original components."""
    pattern = r"at://([^/?#]+)(/[^?#]*)?(\?[^#]*)?(#.*)?"
    match = re.fullmatch(pattern, uri)

    if not match:
        return None

    return {
        "scheme": "at",
        "authority": match.group(1),
        "path": match.group(2) or "",
        "query": match.group(3) or "",
        "fragment": match.group(4) or "",
    }

def validate(uri: str, mode: str):
    errors, warnings, checks = [], [], []
    def check(name, passed, detail):
        checks.append({"name": name, "passed": bool(passed), "detail": detail})
    if not uri:
        return {"valid": False, "mode": mode, "errors": ["Enter an AT URI."], "warnings": [], "checks": [], "parsed": None, "round_trip": None, "round_trip_matches": False}
    if len(uri.encode("utf-8")) > 8192:
        errors.append("URI exceeds the 8 KB maximum length.")
    check("Maximum length (8 KB)", len(uri.encode("utf-8")) <= 8192, "AT URIs must be no longer than 8 KB.")
    check("ASCII character subset", all(ord(c) < 128 for c in uri), "The AT URI syntax is restricted to a subset of ASCII.")
    if any(ord(c) < 32 or ord(c) == 127 for c in uri):
        errors.append("Control characters are not allowed.")
    if not all(ord(c) < 128 for c in uri):
        errors.append("Non-ASCII characters found. Percent-encode characters where appropriate.")
    parts = parse_at_uri(uri)
    check("Absolute at:// scheme and authority", parts is not None, "URI must start with at:// and contain a non-empty authority.")
    if parts is None:
        errors.append("Invalid overall structure. Expected at://authority[/collection[/rkey]].")
        return {"valid": False, "mode": mode, "errors": errors, "warnings": warnings, "checks": checks, "parsed": None, "round_trip": None, "round_trip_matches": False}
    authority, path = parts["authority"], parts["path"]
    if "@" in authority:
        errors.append("Userinfo is not supported in the authority section.")
    if authority.endswith(":") or re.search(r":\d+$", authority):
        errors.append("Host:port authorities are not supported.")
    is_did = bool(re.fullmatch(r"did:[a-z0-9]+:[A-Za-z0-9._:%-]+", authority))
    is_handle = bool(re.fullmatch(r"(?=.{1,253}$)(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)+[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?", authority))
    authority_ok = is_did or is_handle
    check("Authority is a DID or handle", authority_ok, "Authority should be an AT Protocol DID or a domain-style handle.")
    if not authority_ok:
        errors.append("Authority is not recognized as an AT Protocol DID or handle.")
    if path.endswith("/"):
        errors.append("Trailing slashes are not allowed.")
    if "//" in path or re.search(r"(?:^|/)\.{1,2}(?:/|$)", path):
        errors.append("Duplicate slashes and dot segments are not allowed in normalized paths.")
    if parts["query"]:
        if mode == "lexicon":
            errors.append("Query parameters are not supported in restricted Lexicon AT URIs.")
        else:
            warnings.append("Query syntax is allowed in general AT URI syntax but is not currently used in Lexicon AT URIs.")
    if parts["fragment"]:
        if mode == "lexicon":
            errors.append("Fragments are not supported in restricted Lexicon AT URIs.")
        else:
            warnings.append("Fragments are allowed by the general syntax; Lexicon AT URI references do not use them.")
    if mode == "lexicon":
        if path:
            segments = path[1:].split("/")
            if len(segments) > 2:
                errors.append("Restricted Lexicon AT URIs allow at most COLLECTION/RKEY after the authority.")
            if any(s == "" for s in segments):
                errors.append("Path contains an empty segment.")
            if len(segments) >= 1:
                nsid = segments[0]
                nsid_ok = bool(re.fullmatch(r"[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+){2,}", nsid))
                check("Collection is an NSID", nsid_ok, "Collection names use a reverse-domain NSID form, such as app.bsky.feed.post.")
                if not nsid_ok:
                    errors.append("Collection is not in NSID form (for example, app.bsky.feed.post).")
            if len(segments) == 2:
                rkey = segments[1]
                rkey_ok = bool(rkey) and len(rkey) <= 512 and bool(re.fullmatch(r"[A-Za-z0-9._~:-]+", rkey))
                check("Record key syntax", rkey_ok, "Record keys must follow AT Protocol record-key restrictions.")
                if not rkey_ok:
                    errors.append("Record key has unsupported characters or length.")
        else:
            warnings.append("This is a repository-level URI; no collection or record key is present.")
    else:
        if not path:
            warnings.append("Repository-level URI: no path segments were supplied.")
        if path:
            segments = path[1:].split("/")
            check("Path has no empty segments", all(segments), "Path segments are separated by a single slash.")
    # Simple normalized-form hints
    if authority == authority.lower() and is_handle:
        check("Handle authority lowercase", True, "Handle authority is lowercase.")
    elif is_handle:
        warnings.append("Handle authority is not lowercase; normalized AT URIs use lowercase handles.")
        check("Handle authority lowercase", False, "Consider lowercasing the handle authority.")
    else:
        check("Handle authority lowercase", True, "Not applicable to DID authorities.")
    if re.search(r"%[0-9a-f]{2}", uri):
        warnings.append("Percent-encoding uses lowercase hex digits; normalized form uses uppercase hex digits.")
    # Exact parse/serialize round trip
    round_trip = "at://" + parts["authority"] + parts["path"] + parts["query"] + parts["fragment"]
    round_trip_matches = round_trip == uri
    check("Parse → serialize round trip", round_trip_matches, "The serialized URI should match the original string exactly.")
    if not round_trip_matches:
        errors.append("Round-trip mismatch: serialized URI differs from input.")
    return {
        "valid": len(errors) == 0,
        "mode": mode,
        "errors": errors,
        "warnings": warnings,
        "checks": checks,
        "parsed": parts,
        "round_trip": round_trip,
        "round_trip_matches": round_trip_matches,
    }

@app.get("/")
def home():
    return FileResponse("static/index.html")

@app.post("/api/validate")
def validate_endpoint(body: ValidateRequest):
    mode = body.mode if body.mode in ("lexicon", "general") else "lexicon"
    return validate(body.uri.strip(), mode)

@app.get("/api/health")
def health():
    return {"status": "ok"}


class SearchRequest(BaseModel):
    uri: str

@app.post("/api/search")
def search_record(body: SearchRequest):
    """
    Look up a public AT Protocol record through the public Bluesky AppView.
    This endpoint only accepts an AT URI and never fetches a user-supplied URL.
    """
    uri = body.uri.strip()
    parts = parse_at_uri(uri)
    if not parts:
        return {"found": False, "error": "The URI could not be parsed. Validate the AT URI first."}
    if parts["query"] or parts["fragment"]:
        return {"found": False, "error": "Live record lookup requires a restricted AT URI without query or fragment."}
    segments = parts["path"].lstrip("/").split("/") if parts["path"] else []
    if len(segments) != 2 or not all(segments):
        return {"found": False, "error": "Enter a record AT URI with both a collection and record key, for example at://alice.example/app.bsky.feed.post/RECORD_KEY."}
    repo = parts["authority"]
    collection, rkey = segments
    params = urlencode({"repo": repo, "collection": collection, "rkey": rkey})
    endpoint = "https://public.api.bsky.app/xrpc/com.atproto.repo.getRecord?" + params
    request = Request(endpoint, headers={"Accept": "application/json", "User-Agent": "AT-URI-Validator-Hackathon/0.1"})
    try:
        with urlopen(request, timeout=8) as response:
            payload = json.loads(response.read(1_000_000).decode("utf-8"))
        return {
            "found": True,
            "requested_uri": uri,
            "resolved_uri": payload.get("uri"),
            "cid": payload.get("cid"),
            "record": payload.get("value"),
            "message": "Record retrieved from the public AT Protocol API."
        }
    except HTTPError as exc:
        try:
            detail = exc.read(4096).decode("utf-8", errors="replace")
            parsed_detail = json.loads(detail)
            message = parsed_detail.get("message") or parsed_detail.get("error") or detail
        except Exception:
            message = "The public API returned an HTTP error."
        return {"found": False, "status_code": exc.code, "error": str(message)}
    except (URLError, TimeoutError) as exc:
        return {"found": False, "error": "Could not reach the public AT Protocol API. Check your internet connection and try again."}
    except Exception:
        return {"found": False, "error": "The response could not be processed as JSON."}
