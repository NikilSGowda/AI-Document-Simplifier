# ClearDoc: Development Plan

## Deadline and prompt rules

The maximum project duration is **four hours (240 minutes)**, including
integration verification. No individual Antigravity/VS Code implementation
prompt may exceed **20 minutes**. The estimates below add to exactly 240
minutes. Keep reports factual: list changed files, tests and commands actually
run, results, risks, and elapsed time.

**Current checkpoint:** Phases 1.1 and 1.2, plus Phase 2 document upload and
text extraction, are complete. Phase 3 OCR has not started.

## Roadmap

| Phase / prompt | Time | Scope and acceptance check |
|---|---:|---|
| 0.1 Documentation readiness | 10 min | Align requirements, architecture, tools, and roadmap; verify required docs |
| 1.1 App skeleton | 20 min | Create minimal runnable FastAPI app and static UI; start it successfully |
| 1.2 Pasted-text workflow | 20 min | Add text input, API contract, validation/errors, and focused tests |
| 2.1 Upload validation and TXT | 15 min | Allowlisted upload and size/type/empty-input checks |
| 2.2 PDF extraction | 20 min | Use PyMuPDF for every PDF page first; retain usable extracted text |
| 2.3 Extraction tests | 10 min | Cover valid, corrupt, unsupported, oversized, and empty documents |
| 3.1 Tesseract configuration | 20 min | Call installed Tesseract executable through `pytesseract`; report missing setup clearly |
| 3.2 OCR fallback | 15 min | OCR image uploads and only PDF pages without usable PyMuPDF text |
| 3.3 OCR verification | 10 min | Stub-based tests for OCR success/failure; document local executable/data setup |
| 4.1 Provider adapter | 20 min | Server-side configurable provider and environment-based credentials |
| 4.2 Simplification result | 15 min | Validate structured summary, rewrite, key details, glossary, and warnings |
| 4.3 Provider safety/tests | 10 min | Unconfigured/failure states, document-content handling, and external-processing notice |
| 5.1 Results UX/accessibility | 20 min | Show source and result sections with responsive, keyboard-accessible controls |
| 5.2 Error and limits review | 15 min | Verify actionable errors, configured limits, privacy behaviors, and no silent fallbacks |
| 6.1 Integration/regression | 20 min | Run available tests and smoke checks; verify earlier-phase behavior; report deferred items |
| **Total** | **240 min** | |

## Dependencies and gating

- Phase 1 can begin without an AI provider or OCR installation.
- Phases 2–3 require the Python dependencies in `TOOLS.md`; OCR also requires
  an installed Tesseract executable and language data. Do not claim OCR works
  until the executable and an OCR sample have been verified.
- Phase 4 requires the user to select a provider before external model calls
  are enabled. Until then, return a clear `provider not configured` result.
- If an environment prerequisite is unavailable, complete isolated code and
  stub-based tests where possible, report the limitation, and do not claim
  live integration verification.

## Change and regression policy

Preserve all features from completed phases. Fix existing behavior with the
smallest compatible change; do not remove a prior feature to make a later phase
pass. Each prompt must inspect the current workspace first, avoid overwriting
unrelated work, and report files changed. Run targeted tests for the change
plus relevant previous-phase regression checks.

## Open decisions

- Which language-model provider and model should be configured?
- What upload-byte limit, PDF page limit, and minimum usable PDF text threshold
  should the implementation use? Select conservative documented defaults
  during Phase 1/2 if the user has not specified values.
- Which Tesseract language data should the first release support? Default to
  English only unless the user requests otherwise.
