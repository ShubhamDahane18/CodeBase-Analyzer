// app.js — DocuVerse.AI pipeline controller

// ─── DOM References ───────────────────────────
const form         = document.getElementById('docs-form');
const inputUrl     = document.getElementById('repo-url');
const generateBtn  = document.getElementById('generate-btn');
const errorMessage = document.getElementById('error-message');
const formCard     = document.getElementById('form-card');
const heroSection  = document.getElementById('hero-section');
const statusCard   = document.getElementById('status-card');
const successCard  = document.getElementById('success-card');
const statusText   = document.getElementById('status-text');
const statusSubtext = document.getElementById('status-subtext');
const previewBtn   = document.getElementById('preview-btn');
const resetBtn     = document.getElementById('reset-btn');

// ─── Config ───────────────────────────────────
const API_BASE_URL = 'http://localhost:8000/api';

// ─── State ────────────────────────────────────
let currentProjectId = null;
let pollInterval = null;

// ─── Form Submit ──────────────────────────────
form.addEventListener('submit', async (e) => {
  e.preventDefault();
  hideError();

  const repoUrl = inputUrl.value.trim();
  if (!repoUrl || !repoUrl.includes('github.com')) {
    showError('Please enter a valid GitHub repository URL.');
    return;
  }

  setLoadingState();

  try {
    const res = await fetch(`${API_BASE_URL}/generate-docs`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ repo_url: repoUrl })
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to contact API.');
    }

    const data = await res.json();
    currentProjectId = data.project_id;
    startStatusPolling(currentProjectId);

  } catch (err) {
    setIdleState();
    showError(err.message || 'Could not reach the backend. Make sure the server is running.');
  }
});

// ─── Status Polling ───────────────────────────
function startStatusPolling(projectId) {
  // Start the visual timeline
  if (window._uiTimeline) window._uiTimeline.start();

  pollInterval = setInterval(async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/status/${projectId}`);
      if (!res.ok) return;

      const data = await res.json();

      if (data.status === 'completed') {
        clearInterval(pollInterval);
        if (window._uiTimeline) window._uiTimeline.stop();
        setSuccessState(projectId);

      } else if (data.status === 'failed') {
        clearInterval(pollInterval);
        if (window._uiTimeline) window._uiTimeline.stop();
        setIdleState();
        showError('Pipeline failed: ' + (data.error || 'Unknown error.'));
      }
    } catch (err) {
      console.warn('Poll error:', err);
    }
  }, 3000);
}

// ─── State Transitions ────────────────────────
function setLoadingState() {
  generateBtn.disabled = true;
  generateBtn.querySelector('.btn-text').textContent = 'Generating...';
  inputUrl.disabled = true;
  statusText.textContent = 'Analyzing Repository';

  heroSection.style.display = 'none';
  statusCard.style.display  = 'block';
  successCard.style.display = 'none';
}

function setIdleState() {
  generateBtn.disabled = false;
  generateBtn.querySelector('.btn-text').textContent = 'Generate';
  inputUrl.disabled = false;

  heroSection.style.display = '';
  statusCard.style.display  = 'none';
  successCard.style.display = 'none';
}

function setSuccessState(projectId) {
  statusCard.style.display  = 'none';
  successCard.style.display = 'block';

  previewBtn.onclick = () => {
    window.open(`${API_BASE_URL}/preview/${projectId}`, '_blank');
  };
}

// ─── Reset Button ─────────────────────────────
resetBtn.addEventListener('click', () => {
  currentProjectId = null;
  inputUrl.value = '';
  setIdleState();
});

// ─── Error Helpers ────────────────────────────
function showError(msg) {
  errorMessage.textContent = msg;
  errorMessage.style.display = 'block';
}
function hideError() {
  errorMessage.style.display = 'none';
  errorMessage.textContent = '';
}
