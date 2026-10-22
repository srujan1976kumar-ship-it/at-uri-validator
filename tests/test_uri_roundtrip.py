
from fastapi.testclient import TestClient

from main import app, parse_at_uri, validate

client = TestClient(app)


def test_basic_uri_round_trip():
    result = validate("at://alice.example", "general")

    assert result["valid"] is True
    assert result["round_trip_matches"] is True
    assert result["round_trip"] == "at://alice.example"


def test_lexicon_record_uri():
    uri = "at://alice.example/app.bsky.feed.post/123"
    result = validate(uri, "lexicon")

    assert result["valid"] is True
    assert result["round_trip_matches"] is True
    assert result["round_trip"] == uri


def test_query_preserved_in_general_mode():
    uri = "at://alice.example/app.bsky.feed.post/123?x=1"
    result = validate(uri, "general")

    assert result["round_trip_matches"] is True
    assert result["round_trip"] == uri
    assert any("Query syntax" in warning
               for warning in result["warnings"])


def test_https_is_not_an_at_uri():
    result = validate("https://example.com", "general")

    assert result["valid"] is False
    assert result["round_trip_matches"] is False


def test_parser_preserves_components():
    uri = "at://alice.example/app.bsky.feed.post/123?x=1"
    parts = parse_at_uri(uri)

    assert parts is not None
    assert parts["authority"] == "alice.example"
    assert parts["path"] == "/app.bsky.feed.post/123"
    assert parts["query"] == "?x=1"


def test_health_endpoint():
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_search_endpoint_still_rejects_invalid_uri():
    response = client.post(
        "/api/search",
        json={"uri": "https://example.com"},
    )

    assert response.status_code == 200
    assert response.json()["found"] is False

def test_rejects_empty_uri():
    result = validate("", "general")
    assert result["valid"] is False


def test_rejects_trailing_slash_in_lexicon_mode():
    result = validate(
        "at://alice.example/app.bsky.feed.post/",
        "lexicon",
    )
    assert result["valid"] is False


def test_query_rejected_in_lexicon_mode():
    result = validate(
        "at://alice.example/app.bsky.feed.post/123?x=1",
        "lexicon",
    )
    assert result["valid"] is False
    assert result["round_trip_matches"] is True
