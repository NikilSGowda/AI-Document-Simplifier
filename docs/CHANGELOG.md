# Changelog

Documentation updates are recorded newest first.

## 2026-11-13 — Phase 1.2 pasted-text workflow

- Added `POST /api/simplify-text` with request validation, a 10,000-character
  input limit, and structured response fields.
- Added a deterministic echo demonstration processor that explicitly marks AI
  as unconfigured and states that the text was not simplified.
- Added the frontend text form, loading and error states, result display, and
  copy action while retaining the backend health check.
- Added API tests for valid, empty, invalid, max-length, and over-limit input,
  response structure, and local POST CORS.
- Updated the architecture, development checkpoint, and project status.
- Verified the full suite (10 passed), Python compilation, dependency
  consistency, live browser submission/result/copy, and health check.

## 2026-11-13 — Phase 1.1 application foundation

- Added the initial FastAPI/Uvicorn application and `/api/health` endpoint.
- Added the vanilla frontend, local CORS configuration, and explicit health
  connection/error display.
- Added Python 3.14.10-compatible pinned dependencies and an isolated `.venv`.
- Added tests for health, frontend routes/assets, and CORS.
- Verified 4 tests pass, package consistency, and browser connectivity from the
  API-served page and a separate local static server.
- No OCR, document processing, or AI provider was implemented.

## 2026-11-13 — Phase 0.1 documentation readiness

- Updated the delivery roadmap to a maximum of four hours (240 minutes) while
  keeping every individual agent prompt within 20 minutes.
- Clarified PyMuPDF-first PDF extraction and page-level Tesseract OCR fallback.
- Confirmed the planned OCR integration is the installed Tesseract executable
  invoked through `pytesseract`.
- Clarified the configurable, server-side simplification provider boundary.
- Added `PROJECT_STATUS.md` and `DEVELOPMENT_PLAN.md`.
- Checked the local environment without installing dependencies; Tesseract,
  `pytesseract`, and PyMuPDF were not available at check time.
- Git status and remotes could not be checked because the workspace was not a
  Git repository at that point.

## 2026-11-13 — Phase 0 planning baseline

- Added the initial ClearDoc product requirements, architecture, and tools
  documentation.
