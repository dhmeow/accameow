(() => {
  const prefersReducedMotion = window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;

  function randomHex(len = 6) {
    const chars = "0123456789ABCDEF";
    return Array.from({ length: len }, () => chars[Math.floor(Math.random() * chars.length)]).join("");
  }

  function attachGlitchPulse() {
    document.querySelectorAll(".glitch-title,.gameover-you,.gameover-big").forEach((el) => {
      const loop = () => {
        const delay = prefersReducedMotion ? 999999 : 1400 + Math.random() * 3900;
        window.setTimeout(() => {
          el.classList.add("glitch-pulse");
          window.setTimeout(() => el.classList.remove("glitch-pulse"), 260);
          loop();
        }, delay);
      };
      loop();
    });
  }

  function attachMagneticCards() {
    if (prefersReducedMotion || !window.matchMedia?.("(pointer: fine)").matches) return;
    document.querySelectorAll(".interactive-panel").forEach((el) => {
      el.addEventListener("pointermove", (event) => {
        const r = el.getBoundingClientRect();
        const x = (event.clientX - r.left) / r.width - 0.5;
        const y = (event.clientY - r.top) / r.height - 0.5;
        el.style.transform = `perspective(900px) rotateY(${x * 2}deg) rotateX(${y * -2}deg) translateY(-2px)`;
      });
      el.addEventListener("pointerleave", () => {
        el.style.transform = "";
      });
    });
  }

  function attachButtonNoise() {
    if (prefersReducedMotion) return;
    document.querySelectorAll(".cyber-btn,.resource-card,.subject-card").forEach((el) => {
      el.addEventListener("mouseenter", () => {
        el.dataset.noise = randomHex(8);
      });
    });
  }

  function updateHudClock() {
    const clock = document.getElementById("boot-clock");
    if (!clock) return;
    const d = new Date();
    clock.textContent = d.toTimeString().slice(0, 8);
    setTimeout(updateHudClock, 1000);
  }

  function orientationGate() {
    const layer = document.getElementById("orientation-layer");
    if (!layer) return;
    const shouldShow = window.innerWidth < 700 && window.matchMedia("(orientation: portrait)").matches;
    layer.classList.toggle("active", shouldShow);
    layer.setAttribute("aria-hidden", String(!shouldShow));
  }

  window.CyberEffects = { attachGlitchPulse, attachMagneticCards, attachButtonNoise, updateHudClock, orientationGate };

  document.addEventListener("DOMContentLoaded", () => {
    attachGlitchPulse();
    attachMagneticCards();
    attachButtonNoise();
    updateHudClock();
    orientationGate();
  });
  window.addEventListener("resize", orientationGate);
  window.addEventListener("orientationchange", orientationGate);
})();
