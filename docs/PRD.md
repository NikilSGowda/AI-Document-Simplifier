# Product Requirements: ClearDoc

## 1. Summary

ClearDoc turns dense documents into clear, plain-language explanations while
preserving their meaning. It helps people understand key points, unfamiliar
terms, and practical implications without requiring specialist knowledge.

## 2. Problem and opportunity

People encounter technical language and complex instructions in reports,
policies, forms, and other documents. This can cause confusion and poor
decisions. ClearDoc provides a short, accessible path from document to
understanding: extract its text, simplify it, and let the user inspect the
result alongside the source.

## 3. Goals and non-goals

### Goals

- Accept pasted text and a small set of common document/image uploads.
- Extract text from supported files, using Tesseract OCR when a page is an
  image or has no usable text layer.
- Produce a plain-language summary and a faithful, sectioned rewrite.
- Explain important terms and call out dates, amounts, obligations, and
  uncertainties found in the source.
- Keep the original text available for comparison.
- Be usable on desktop and mobile, with clear errors and keyboard-accessible
  controls.

### Non-goals for the first MVP

- Legal, medical, financial, or other professional advice.
- A guarantee that OCR or generated explanations are error-free.
- Accounts, document history, collaboration, or persistent document storage.
- Editing the upstream Tesseract OCR engine or building it from source.
- Broad file-format support beyond the initial allowlist.

## 4. Users and primary workflow

**Primary user:** A person without specialist knowledge who needs to understand
a report, instruction, policy, or other text-heavy document.

1. The user pastes text or selects a supported file.
2. ClearDoc validates the input and extracts text; image-based content is sent
   through Tesseract OCR.
3. The user requests a plain-language explanation.
4. ClearDoc displays a concise summary, a simplified version, key details, and
   term explanations beside or below the source.
5. The user checks the result against the source and can retry with a different
   simplification level.

## 5. MVP requirements

### Input and extraction

- Support pasted text and `.txt`, `.pdf`, `.png`, `.jpg`, and `.jpeg` uploads.
- Set a configurable upload-size and page-count limit; show it before upload.
- Extract embedded PDF text first; OCR scanned/image-only pages with Tesseract.
- Reject unsupported, empty, unreadable, or over-limit input with a useful
  message. Do not silently drop pages or return a success-shaped empty result.
- Preserve page/section boundaries where extraction makes them available.

### Simplification

- Offer one default level: plain language for a general adult reader.
- Keep factual claims, names, figures, dates, conditions, and caveats faithful
  to the source; do not invent missing details.
- Separate the summary, simplified explanation, key details, and glossary.
- Mark uncertain or low-quality extraction so users know to verify the source.
- Explain that results are informational and should be checked against the
  original, especially for consequential decisions.

### Privacy, safety, and accessibility

- Process documents transiently; do not persist uploads or extracted text in
  the MVP.
- Never expose model-provider credentials in browser code. Do not log document
  contents.
- Explain before submission if text will be sent to a configured external
  simplification provider. Provider choice and data handling must be made
  explicit during implementation.
- Treat document text as untrusted input, not as instructions to the system.
- Use semantic headings, visible focus, labels, contrast, and responsive layout.

## 6. Success criteria

- A user can submit pasted text or a supported file and see a complete result.
- Image-only content can be OCR'd through the configured Tesseract executable.
- Unsupported, corrupt, empty, and over-limit inputs produce actionable errors.
- Output sections are distinct and retain source facts without adding claims.
- The original content remains accessible for comparison.
- Tests cover parsing/validation, OCR adapter behavior, simplification response
  handling, and the primary user workflow.

## 7. Constraints and assumptions

- Delivery is time-boxed to a maximum of four hours (240 minutes); each
  Antigravity/VS Code work prompt is capped at 20 minutes.
- The repository was empty when Phase 0 began.
- Recommended MVP stack: Python, FastAPI, a minimal HTML/CSS/JavaScript
  interface, PyMuPDF for PDF text/rendering, Pillow and `pytesseract` for image
  handling, and a configurable simplification-provider adapter.
- Tesseract is an external system dependency. The official repository is the
  engine source; the MVP should use an installed binary rather than spend the
  time budget building Tesseract itself.
- A model/provider and its credentials are not yet specified. Keep that
  integration behind an adapter and ask for an explicit provider before
  enabling external document submission. If no provider is configured, show a
  clear unavailable state rather than pretending to simplify.

## 8. Delivery phases

This plan uses the full four-hour (240-minute) maximum, including planning and
verification. Keep each agent prompt to 20 minutes or less and report exact
elapsed time.

| Phase | Timebox | Deliverable |
|---|---:|---|
| 0.1 Documentation readiness | 10 min | Consistent PRD, architecture, toolchain, status, changelog, and development plan |
| 1. App skeleton and text workflow | 40 min | Responsive UI, text input, API contract, basic tests |
| 2. File validation and PDF/text extraction | 45 min | Allowlisted uploads, PyMuPDF-first PDF extraction, tests |
| 3. Tesseract OCR | 45 min | Installed-executable configuration, image/scanned-page OCR fallback, tests |
| 4. Simplification provider | 45 min | Configurable server-side adapter, structured result, consent and failure handling |
| 5. UX, accessibility, and error handling | 35 min | Result presentation, responsive/accessibility checks, clear errors |
| 6. Integration and regression verification | 20 min | End-to-end smoke checks, previous-phase regression checks, final report |

If time runs out, keep the working earlier phases intact, report deferred scope,
and ask before reducing requirements. Do not remove or regress a prior phase's
features to correct a defect; make a minimal additive/backward-compatible fix.
Each phase may use multiple prompts, but no individual prompt may exceed
20 minutes. See `DEVELOPMENT_PLAN.md` for the prompt-sized breakdown.

## 9. Definition of done for each implementation phase

- Report changed/added files and the behavior changed.
- Report tests added or updated, exact test commands, and pass/fail results.
- Report known limitations, remaining work, and actual elapsed time.
- Run the narrowest relevant tests and verify previous-phase acceptance checks.
- Do not claim a test passed unless it was run; do not remove earlier features
  when fixing existing behavior.
