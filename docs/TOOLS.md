# ClearDoc: Tools and Dependencies

## Recommended MVP toolchain

| Tool | Purpose | Notes |
|---|---|---|
| VS Code or Antigravity | Edit, run, and test the project | Keep each agent prompt at 20 minutes or less |
| Python 3 | Application runtime | Use the installed project interpreter; record the chosen version in setup docs |
| FastAPI + Uvicorn | Backend and local development server | Keep API and services in one small application |
| HTML, CSS, JavaScript | Responsive browser interface | No frontend build system required for the time-boxed MVP |
| PyMuPDF (`pymupdf`) | PDF text extraction and scanned-page rendering | Always extract PDF text first; OCR only pages with no usable extracted text |
| Pillow | Image loading/preprocessing | Enforce image dimensions and upload limits |
| `pytesseract` | Python wrapper for Tesseract | It does not install the Tesseract executable or language data |
| Tesseract OCR | Local OCR engine | Install the upstream binary separately; configure executable and language data |
| `pytest` + FastAPI `TestClient` | Automated tests | Stub OCR/model boundaries; no external service required for unit tests |
| Git | Version control | Do not overwrite or remove pre-existing user work |

## Phase 1 setup and compatibility

The Phase 1 dependencies are pinned in the repository's `requirements.txt` and
were installed and tested with Python 3.14.10. Create and activate an isolated
environment from the project root:

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --reload
```

Open `http://127.0.0.1:8000`. To serve the frontend separately for CORS
development, use another terminal:

```powershell
.\.venv\Scripts\python.exe -m http.server 5500 --directory frontend --bind 127.0.0.1
```

`.env.example` documents local frontend origins. Copy it to `.env` only if you
need to customize them, then set `FRONTEND_ORIGINS` in the process environment;
the application does not load `.env` files automatically. `.env` is ignored by
Git. No API credentials are used by Phase 1.

## Tesseract resource

- Upstream: https://github.com/tesseract-ocr/tesseract
- App integration: `pytesseract` invokes the installed Tesseract executable.
- Install the executable and required trained-data files using the official
  installer/package appropriate to the user's operating system. On Windows,
  configure the executable path in environment/configuration rather than
  hard-coding a machine-specific location.
- Verify setup with `tesseract --version` and a known sample image before
  testing the app's OCR path.
- Do not build the upstream C++ source during the four-hour MVP unless the
  user specifically requires a source build.

## Provider decision

The user has not selected a language-model provider. Keep the provider
configurable behind a server-side adapter. Do not add a real external provider
or ask users to paste credentials into browser code until a provider is
selected. Configure its key through server-side environment variables and add
an explicit external-processing notice. The app should clearly report
`provider not configured` until then.

## Scope discipline

Use dependencies only when the corresponding phase needs them. Do not add a
database, user accounts, a queue, Docker, cloud storage, or a complex frontend
framework for this MVP. Keep secrets and user documents out of source control.
