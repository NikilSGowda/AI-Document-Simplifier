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

textInput.addEventListener("input", () => {
  characterCount.textContent = `${textInput.value.length.toLocaleString()} / 10,000 characters`;
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
