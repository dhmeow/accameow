(() => {
  function getSubject() {
    return (window.CURRENT_SUBJECT || "").toUpperCase();
  }

  function isConfigured(url) {
    return typeof url === "string" && url && !url.includes("_URL");
  }

  async function secureRedirect(url, subject, kind) {
    const overlay = document.getElementById("resource-transition");
    const label = document.getElementById("resource-transition-text");
    if (!overlay || !label) {
      if (isConfigured(url)) window.location.assign(url);
      else window.alert(`Replace the placeholder URL in assets/js/config.js for ${subject} ${kind}.`);
      return;
    }

    overlay.classList.add("active");
    overlay.setAttribute("aria-hidden", "false");

    const phases = [
      "ESTABLISHING SECURE CONNECTION...",
      "RESOURCE LOCATED",
      "ACCESSING DATABASE..."
    ];

    for (const phase of phases) {
      label.textContent = phase;
      await new Promise(r => setTimeout(r, 230));
    }

    if (!isConfigured(url)) {
      overlay.classList.remove("active");
      label.textContent = "URL PLACEHOLDER // CONFIG REQUIRED";
      overlay.style.color = "#ff2cf7";
      setTimeout(() => {
        overlay.style.color = "";
      }, 400);
      window.alert(`No real URL is configured yet.\n\nSet:\n${subject}_${kind === "practice" ? "QUESTION_PRACTICE" : "NOTES"}_URL\ninside assets/js/config.js.`);
      return;
    }

    window.location.assign(url);
  }

  document.addEventListener("DOMContentLoaded", () => {
    CyberEffects?.orientationGate?.();
    CyberEffects?.attachGlitchPulse?.();
    CyberEffects?.attachMagneticCards?.();
    CyberEffects?.attachButtonNoise?.();

    const subject = getSubject();
    if (subject && window.CYBER_RESOURCES?.[subject]) {
      document.querySelectorAll("[data-resource]").forEach(btn => {
        btn.addEventListener("click", () => {
          const kind = btn.dataset.resource;
          secureRedirect(window.CYBER_RESOURCES[subject][kind], subject, kind);
        });
      });
    }

    // Small glitch on internal navigation without breaking native links.
    document.querySelectorAll('a[href$=".html"]').forEach(a => {
      a.addEventListener("click", (e) => {
        if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
        const href = a.getAttribute("href");
        if (!href || href.startsWith("#")) return;
        e.preventDefault();
        const overlay = document.createElement("div");
        overlay.className = "transition-overlay active";
        overlay.innerHTML = `<div class="transition-lines"></div><div class="transition-text">MODE SWITCHING...</div>`;
        document.body.appendChild(overlay);
        setTimeout(() => window.location.href = href, 330);
      });
    });
  });
})();
