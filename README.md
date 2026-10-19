# AT URI Syntax Compatibility and Round-Trip Validator

A starter hackathon prototype with a FastAPI backend and browser frontend.

## Requirements
- Python 3.10 or newer
- Internet connection for the first install (to install packages)

## Run on Windows
1. Extract this ZIP.
2. Open the extracted `at_uri_validator` folder in VS Code.
3. Open **Terminal → New Terminal**.
4. Run:
   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   uvicorn main:app --reload
   ```
   If PowerShell blocks activation, you can skip activation and run:
   ```powershell
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   .\.venv\Scripts\python.exe -m uvicorn main:app --reload
   ```
5. Open http://127.0.0.1:8000 in your browser.

## Features
- General and restricted Lexicon validation modes
- Component breakdown (scheme, authority, path, query, fragment)
- Round-trip parse/serialize equality check
- Warnings for common normalization issues
- API endpoint: `POST /api/validate`
- Health endpoint: `GET /api/health`

## Important scope note
This is a hackathon starter, not a complete conformance implementation. Before presenting as standards-complete, expand the tests against the official AT URI specification and reference implementation, especially DID, handle, NSID, record-key, percent-encoding, query, and fragment edge cases. Syntax validation does not prove that a handle or record resolves.
