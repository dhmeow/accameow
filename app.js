(() => {
  const bootScreen = document.getElementById("boot-screen");
  const challengeScreen = document.getElementById("challenge-screen");
  const bootLog = document.getElementById("boot-log");
  const progressBar = document.getElementById("boot-progress");
  const progressPercent = document.getElementById("progress-percent");
  const bootStatus = document.getElementById("boot-status");
  const yesBtn = document.getElementById("yes-btn");
  const noBtn = document.getElementById("no-btn");
  const overlay = document.getElementById("transition-overlay");
  const transitionText = document.getElementById("transition-text");

  if (!bootScreen || !challengeScreen) return;

  const bootLines = [
    ["INITIALIZING SYSTEM...", "ok"],
    ["LOADING CHALLENGE PROTOCOL...", "ok"],
    ["CONNECTING USER INTERFACE...", "ok"],
    ["VERIFYING ACCESS...", "warn"],
    ["SCANNING DATABASE...", "ok"],
    [`NEURAL LINK ESTABLISHED // 0x${Math.floor(Math.random()*0xffffff).toString(16).toUpperCase()}`, "ok"],
    ["SYSTEM STATUS: ONLINE", "ok"]
  ];

  let bootIndex = 0;
  let progress = 0;
  let bootComplete = false;

  function typeLine(text, className = "") {
    return new Promise((resolve) => {
      const row = document.createElement("div");
      row.className = className;
      bootLog.appendChild(row);
      let i = 0;
      const step = () => {
        row.textContent = text.slice(0, i) + (i < text.length ? "█" : "");
        if (i < text.length) {
          i += 1;
          setTimeout(step, 12);
        } else {
          resolve();
        }
      };
      step();
    });
  }

  async function boot() {
    while (bootIndex < bootLines.length) {
      const [line, cls] = bootLines[bootIndex++];
      await typeLine(line, cls);
      await new Promise(r => setTimeout(r, 100));
    }
  }

  function randomData() {
    const row = document.createElement("div");
    row.style.opacity = ".35";
    row.textContent = `SYS// ${randomHex(4)}  ${randomHex(4)}  ${randomHex(4)}  ${randomHex(4)}`;
    bootLog.appendChild(row);
    if (bootLog.children.length > 10) bootLog.removeChild(bootLog.firstElementChild);
  }

  function randomHex(len) {
    const chars = "0123456789ABCDEF";
    return Array.from({length:len}, () => chars[Math.floor(Math.random()*chars.length)]).join("");
  }

  const interval = setInterval(() => {
    progress = Math.min(100, progress + 1.65 + Math.random()*2.25);
    progressBar.style.width = progress + "%";
    progressPercent.textContent = String(Math.floor(progress)).padStart(2, "0") + "%";
    if (Math.random() > .58) randomData();
    if (progress >= 100) clearInterval(interval);
  }, 70);

  boot().then(() => {
    const wait = setInterval(() => {
      if (progress >= 100) {
        clearInterval(wait);
        bootComplete = true;
        bootStatus.textContent = "SYSTEM ONLINE";
        bootStatus.classList.add("glitch-pulse");
        setTimeout(() => {
          bootScreen.classList.add("hidden");
          challengeScreen.classList.remove("hidden");
          CyberEffects?.attachGlitchPulse?.();
        }, 550);
      }
    }, 80);
  });

  function transitionTo(url, text) {
    transitionText.textContent = text;
    overlay.classList.add("active");
    overlay.setAttribute("aria-hidden", "false");
    setTimeout(() => window.location.href = url, 760);
  }

  yesBtn?.addEventListener("click", () => {
    if (!bootComplete) return;
    transitionTo("selection.html", "ACCESS GRANTED // SUBJECT DATABASE LOADED");
  });

  noBtn?.addEventListener("click", () => {
    transitionText.textContent = "CHALLENGE ABORTED // SYSTEM FAILURE";
    overlay.classList.add("active");
    overlay.style.background = "rgba(40,0,5,.96)";
    overlay.setAttribute("aria-hidden", "false");
    setTimeout(() => window.location.href = "game-over.html", 820);
  });

  if (new URLSearchParams(location.search).has("restart")) {
    // Restart links arrive here and simply replay the cinematic boot.
  }
})();
