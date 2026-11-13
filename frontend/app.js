const API_BASE_URL = "http://127.0.0.1:8000";
const message = document.querySelector("#connection-message");
const checkButton = document.querySelector("#check-connection");

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
