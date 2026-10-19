
from main import validate

tests = [
    ("Valid record", "at://alice.example/app.bsky.feed.post/record456", True),
    ("Valid DID", "at://did:plc:vwzwgnygau7ed7b7wt5ux7y2/app.bsky.feed.post/record456", True),
    ("Missing authority", "at:///app.bsky.feed.post/record456", False),
    ("Trailing slash", "at://foo.com/", False),
    ("Invalid collection", "at://alice.example/not-a-valid-collection/record456", False),
    ("Host port", "at://example.com:3000", False),
]

passed = 0

for name, uri, expected in tests:
    result = validate(uri, "lexicon")
    ok = result["valid"] == expected
    print(f"{'PASS' if ok else 'FAIL'}: {name}")
    passed += ok

print(f"\nResult: {passed}/{len(tests)} tests passed.")
