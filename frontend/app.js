const API_BASE_URL = "http://127.0.0.1:8000";
const message = document.querySelector("#connection-message");
const checkButton = document.querySelector("#check-connection");
const form = document.querySelector("#simplify-form");
const textInput = document.querySelector("#source-text");
const simplifyButton = document.querySelector("#simplify-button");
const characterCount = document.querySelector("#character-count");
const workflowMessage = document.querySelector("#workflow-message");
const resultSection = document.querySelector("#result-section");
const resultText = document.querySelector("#result-text");
const resultNotice = document.querySelector("#result-notice");
const copyButton = document.querySelector("#copy-result");
const uploadForm = document.querySelector("#upload-form");
const documentFile = document.querySelector("#document-file");
const selectedFilename = document.querySelector("#selected-filename");
const uploadButton = document.querySelector("#upload-button");
const uploadMessage = document.querySelector("#upload-message");
const uploadResult = document.querySelector("#upload-result");
const documentSummary = document.querySelector("#document-summary");
const documentWarnings = document.querySelector("#document-warnings");
const extractedText = document.querySelector("#extracted-text");
const useExtractedTextButton = document.querySelector("#use-extracted-text");
let currentExtractedText = "";

textInput.addEventListener("input", () => {
  characterCount.textContent = `${textInput.value.length.toLocaleString()} / 10,000 characters`;
});

documentFile.addEventListener("change", () => {
  const file = documentFile.files[0];
  selectedFilename.textContent = file
    ? `${file.name} (${(file.size / (1024 * 1024)).toFixed(2)} MB)`
    : "No file selected";
  uploadMessage.textContent = "";
  uploadResult.hidden = true;
});

uploadForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const file = documentFile.files[0];
  if (!file) {
    uploadMessage.textContent = "Choose a TXT, PDF, or DOCX file first.";
    return;
  }

  uploadButton.disabled = true;
  uploadButton.textContent = "Uploading and extracting…";
  uploadMessage.textContent = "Uploading and extracting the document…";
  uploadResult.hidden = true;

  try {
    const formData = new FormData();
    formData.append("file", file);
    const response = await fetch(`${API_BASE_URL}/api/upload-document`, {
      method: "POST",
      body: formData,
    });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      const detail =
        typeof payload.detail === "string"
          ? payload.detail
          : "The document could not be processed. Check the file and try again.";
      throw new Error(detail);
    }

    currentExtractedText = payload.extracted_text;
    extractedText.textContent =
      currentExtractedText ||
      "No text could be extracted. The listed PDF pages require OCR, which is not available yet.";
    documentSummary.textContent =
      `${payload.filename} · ${payload.file_type.toUpperCase()} · ` +
      `${payload.character_count.toLocaleString()} characters extracted`;
    documentWarnings.replaceChildren();
    for (const warning of payload.warnings) {
      const item = document.createElement("li");
      item.textContent = warning;
      documentWarnings.append(item);
    }
    documentWarnings.hidden = payload.warnings.length === 0;
    uploadResult.hidden = false;
    uploadMessage.textContent = "Document extraction complete.";
  } catch (error) {
    uploadMessage.textContent =
      error instanceof Error
        ? `Could not extract the document: ${error.message}`
        : "Could not extract the document. Check that the backend is running.";
  } finally {
    uploadButton.disabled = false;
    uploadButton.textContent = "Upload and extract";
  }
});

useExtractedTextButton.addEventListener("click", () => {
  if (currentExtractedText.length > 10_000) {
    uploadMessage.textContent =
      "The extracted text exceeds the 10,000-character limit. Shorten it before using the pasted-text workflow.";
    return;
  }

  textInput.value = currentExtractedText;
  textInput.dispatchEvent(new Event("input"));
  uploadMessage.textContent = "Extracted text added to the text workflow.";
  textInput.focus();
  textInput.scrollIntoView({ behavior: "smooth", block: "center" });
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const text = textInput.value;

  if (!text.trim()) {
    workflowMessage.textContent = "Enter some text before submitting.";
    textInput.focus();
    return;
  }

  simplifyButton.disabled = true;
  simplifyButton.textContent = "Processing…";
  workflowMessage.textContent = "Processing your text…";
  resultSection.hidden = true;

  try {
    const response = await fetch(`${API_BASE_URL}/api/simplify-text`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });

    const payload = await response.json();
    if (!response.ok) {
      const detail =
        typeof payload.detail === "string"
          ? payload.detail
          : "The request was invalid. Check the text and try again.";
      throw new Error(detail);
    }

    resultText.textContent = payload.result_text;
    resultNotice.textContent = payload.notice;
    resultSection.hidden = false;
    workflowMessage.textContent = "Demonstration output is ready.";
  } catch (error) {
    workflowMessage.textContent =
      error instanceof Error
        ? `Could not process the text: ${error.message}`
        : "Could not process the text. Check that the backend is running.";
  } finally {
    simplifyButton.disabled = false;
    simplifyButton.textContent = "Simplify";
  }
});

copyButton.addEventListener("click", async () => {
  try {
    await navigator.clipboard.writeText(resultText.textContent);
    workflowMessage.textContent = "Result copied to clipboard.";
  } catch {
    workflowMessage.textContent =
      "Could not copy the result. Select and copy the text manually.";
  }
});

async function checkBackend() {
  checkButton.disabled = true;
  message.textContent = "Checking the backend…";

  try {
    const response = await fetch(`${API_BASE_URL}/api/health`);
    if (!response.ok) {
      throw new Error(`The backend returned HTTP ${response.status}.`);
    }

    const result = await response.json();
    if (result.status !== "ok") {
      throw new Error("The backend returned an unexpected health response.");
    }

    message.textContent = "Connected. The backend is ready.";
  } catch (error) {
    message.textContent =
      error instanceof Error
        ? `Could not connect to the backend: ${error.message}`
        : "Could not connect to the backend. Check that the server is running.";
  } finally {
    checkButton.disabled = false;
  }
}

checkButton.addEventListener("click", checkBackend);
checkBackend();
