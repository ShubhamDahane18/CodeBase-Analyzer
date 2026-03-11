/* ui.js — Particle canvas background + timeline controller */

// ─── Canvas Particle Field ───────────────────────────────────────
(function initCanvas() {
  const canvas = document.getElementById('bg-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  let W, H, particles = [];

  function resize() {
    W = canvas.width = window.innerWidth;
    H = canvas.height = window.innerHeight;
  }

  class Particle {
    constructor() { this.reset(true); }
    reset(init = false) {
      this.x = Math.random() * W;
      this.y = init ? Math.random() * H : H + 10;
      this.r = Math.random() * 1.5 + 0.3;
      this.speed = Math.random() * 0.4 + 0.15;
      this.opacity = Math.random() * 0.4 + 0.05;
      this.pulse = Math.random() * Math.PI * 2;
      this.drift = (Math.random() - 0.5) * 0.3;
    }
    update() {
      this.y -= this.speed;
      this.x += this.drift;
      this.pulse += 0.02;
      this.opacity = (Math.sin(this.pulse) * 0.15 + 0.2);
      if (this.y < -10) this.reset();
    }
    draw() {
      ctx.save();
      ctx.globalAlpha = this.opacity;
      ctx.fillStyle = '#a855f7';
      ctx.shadowBlur = 6;
      ctx.shadowColor = '#7c3aed';
      ctx.beginPath();
      ctx.arc(this.x, this.y, this.r, 0, Math.PI * 2);
      ctx.fill();
      ctx.restore();
    }
  }

  function init() {
    resize();
    particles = Array.from({ length: 80 }, () => new Particle());
  }

  function animate() {
    ctx.clearRect(0, 0, W, H);
    particles.forEach(p => { p.update(); p.draw(); });
    requestAnimationFrame(animate);
  }

  window.addEventListener('resize', resize);
  init();
  animate();
})();


// ─── Timeline Step Animation ─────────────────────────────────────
const STEP_SUBSTEXTS = [
  "Pulling source code from GitHub...",
  "Identifying code structures and file types...",
  "Extracting functions, classes and signatures...",
  "Calling Groq AI to generate documentation...",
  "Compiling MkDocs + Mermaid site...",
];

const STEP_IDS = ['step-1', 'step-2', 'step-3', 'step-4', 'step-5'];

let currentStep = 0;
let stepInterval = null;

function advanceTimeline(stepIndex) {
  // Mark all previous steps as done
  for (let i = 0; i < stepIndex; i++) {
    const el = document.getElementById(STEP_IDS[i]);
    if (el) {
      el.classList.remove('active');
      el.classList.add('done');
      const icon = el.querySelector('.step-icon');
      if (icon) icon.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>`;
    }
  }
  // Mark current step as active
  const activeEl = document.getElementById(STEP_IDS[stepIndex]);
  if (activeEl) {
    activeEl.classList.add('active');
    activeEl.classList.remove('done');
  }
  // Update status subtext
  const sub = document.getElementById('status-subtext');
  if (sub && STEP_SUBSTEXTS[stepIndex]) sub.textContent = STEP_SUBSTEXTS[stepIndex];
}

function startTimeline() {
  currentStep = 0;
  STEP_IDS.forEach(id => {
    const el = document.getElementById(id);
    if (el) { el.classList.remove('active', 'done'); }
  });
  advanceTimeline(0);
  stepInterval = setInterval(() => {
    currentStep++;
    if (currentStep < STEP_IDS.length) {
      advanceTimeline(currentStep);
    }
  }, 7500); // advance every 7.5s to keep pace with typical pipeline
}

function stopTimeline() {
  if (stepInterval) clearInterval(stepInterval);
  stepInterval = null;
  // Mark all steps done
  STEP_IDS.forEach(id => {
    const el = document.getElementById(id);
    if (el) {
      el.classList.remove('active');
      el.classList.add('done');
      const icon = el.querySelector('.step-icon');
      if (icon) icon.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>`;
    }
  });
}

// Expose to app.js
window._uiTimeline = { start: startTimeline, stop: stopTimeline };
