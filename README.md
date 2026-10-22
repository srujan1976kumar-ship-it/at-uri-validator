# AT URI Syntax Compatibility and Round-Trip Validator

A web-based tool for validating AT URIs, inspecting their components, and checking whether a URI can be reconstructed from its parsed parts.

## Features

- Validate AT URI input using supported syntax checks.
- Support restricted lexicon-oriented and general syntax validation modes.
- Display parsed URI components, validation checks, errors, and warnings.
- Perform a round-trip reconstruction check.
- Search for records using the configured Bluesky AppView lookup.
- Provide API endpoints for validation, health checks, and search.

## Technologies Used

- Python 3.10+
- FastAPI
- HTML, CSS, and JavaScript
- Uvicorn
- Pytest

## Requirements

- Python 3.10 or newer
- Internet connection for installing packages
- Git (for cloning the repository)

## Project Structure

```text
at_uri_validator/
├── main.py
├── test_validator.py
├── requirements.txt
└── static/
    └── index.html
```

## Installation and Setup on Windows

1. Clone the repository:

   ```powershell
   git clone https://github.com/srujan1976kumar-ship-it/at-uri-validator.git
   cd at-uri-validator
   ```

2. Create a virtual environment:

   ```powershell
   py -m venv .venv
   ```

3. Install dependencies:

   ```powershell
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   ```

4. Start the application:

   ```powershell
   .\.venv\Scripts\python.exe -m uvicorn main:app --reload
   ```

5. Open http://127.0.0.1:8000 in your browser.

Keep the terminal open while using the application.

## API Endpoints

- `GET /` — Opens the web application.
- `GET /api/health` — Checks API health.
- `POST /api/validate` — Validates an AT URI.
- `POST /api/search` — Looks up a public AT Protocol record using its AT URI.

Refer to `main.py` for the exact request and response formats.

## Testing

Install the testing dependencies:

```powershell
py -m pip install pytest httpx
```

Run the automated regression tests:

```powershell
py -m pytest tests/test_uri_roundtrip.py -v
```

The regression suite currently contains 10 tests covering
basic URI validation, Lexicon record URIs, query-string
preservation, invalid URI rejection, parser components,
and selected API endpoint behavior.

The test suite passed locally during development.
Run the command above to verify the current code.


## Scope and Limitations

This project implements a set of AT URI syntax and reconstruction checks. It should not be considered fully compliant with every AT Protocol specification without further specification-based verification and comprehensive testing. Search functionality depends on the configured external service being available.

## Future Improvements

- Expand specification-based validation and edge-case coverage.
- Add automated API tests.
- Improve error messages and accessibility.
- Add screenshots and usage examples.

## Author

Developed as a software project exploring AT URI validation and search functionality.
