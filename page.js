(() => {
  /* =========================================================
     HELPERS
     ========================================================= */

  function getSubject() {
    return (window.CURRENT_SUBJECT || "").toUpperCase();
  }

  function isConfigured(url) {
    return (
      typeof url === "string" &&
      url.trim() !== "" &&
      !url.includes("_URL")
    );
  }

  function sleep(ms) {
    return new Promise((resolve) => {
      setTimeout(resolve, ms);
    });
  }

  function randomHex(length = 6) {
    const chars = "0123456789ABCDEF";

    return Array.from(
      { length },
      () => chars[Math.floor(Math.random() * chars.length)]
    ).join("");
  }

  /* =========================================================
     RESOURCE LOADING + CYBERPUNK TRANSITION
     ========================================================= */

  async function secureRedirect(url, subject, kind) {
    const overlay =
      document.getElementById("resource-transition");

    const label =
      document.getElementById("resource-transition-text");

    /* -------------------------------------------------------
       Validate URL first
       ------------------------------------------------------- */

    if (!isConfigured(url)) {
      if (overlay && label) {
        overlay.classList.add("active");
        overlay.setAttribute("aria-hidden", "false");

        label.textContent =
          "URL PLACEHOLDER // CONFIG REQUIRED";

        await sleep(400);

        overlay.classList.remove("active");
        overlay.setAttribute("aria-hidden", "true");
      }

      const urlName =
        `${subject}_${
          kind === "practice"
            ? "QUESTION_PRACTICE"
            : "NOTES"
        }_URL`;

      window.alert(
        `No real URL is configured yet.\n\n` +
        `Set ${urlName} in config.js.`
      );

      return;
    }

    /* -------------------------------------------------------
       OPEN THE TARGET IMMEDIATELY
       
       This starts loading the external website as soon as
       the user clicks, while our animation plays.
       ------------------------------------------------------- */

    let targetWindow = null;

    try {
      targetWindow = window.open(
        url,
        "_blank",
        "noopener,noreferrer"
      );
    } catch (error) {
      targetWindow = null;
    }

    const popupBlocked = !targetWindow;

    /* -------------------------------------------------------
       Fallback if transition HTML does not exist
       ------------------------------------------------------- */

    if (!overlay || !label) {
      if (popupBlocked) {
        window.location.assign(url);
      } else {
        try {
          targetWindow.focus();
        } catch (_) {}
      }

      return;
    }

    /* -------------------------------------------------------
       SHOW CONNECTION SCREEN
       ------------------------------------------------------- */

    overlay.classList.add("active");
    overlay.setAttribute("aria-hidden", "false");

    /* -------------------------------------------------------
       PHASE 1
       ------------------------------------------------------- */

    label.textContent =
      "ESTABLISHING SECURE CONNECTION...";

    await sleep(350);

    /* -------------------------------------------------------
       PHASE 2
       ------------------------------------------------------- */

    label.textContent =
      `SCANNING NODE // 0x${randomHex(6)}`;

    await sleep(300);

    /* -------------------------------------------------------
       PHASE 3
       ------------------------------------------------------- */

    label.textContent =
      "RESOURCE LOCATED";

    await sleep(300);

    /* -------------------------------------------------------
       PHASE 4
       ------------------------------------------------------- */

    label.textContent =
      "SECURE CHANNEL ESTABLISHED";

    await sleep(300);

    /* -------------------------------------------------------
       PHASE 5
       ------------------------------------------------------- */

    label.textContent =
      "ACCESSING DATABASE...";

    await sleep(350);

    /* -------------------------------------------------------
       FINAL PHASE
       ------------------------------------------------------- */

    label.textContent =
      "ACCESS GRANTED";

    await sleep(300);

    /* -------------------------------------------------------
       POPUP BLOCKED FALLBACK
       ------------------------------------------------------- */

    if (popupBlocked) {
      window.location.assign(url);
      return;
    }

    /* -------------------------------------------------------
       TRY TO FOCUS THE NEW TAB
       ------------------------------------------------------- */

    try {
      targetWindow.focus();
    } catch (_) {
      /*
       * Some browsers prevent scripts from changing focus.
       * The target page is still already loading.
       */
    }

    /* -------------------------------------------------------
       REMOVE TRANSITION
       ------------------------------------------------------- */

    overlay.classList.remove("active");
    overlay.setAttribute("aria-hidden", "true");
  }

  /* =========================================================
     DOM READY
     ========================================================= */

  document.addEventListener("DOMContentLoaded", () => {

    /* =======================================================
       CYBER EFFECTS
       ======================================================= */

    CyberEffects?.orientationGate?.();
    CyberEffects?.attachGlitchPulse?.();
    CyberEffects?.attachMagneticCards?.();
    CyberEffects?.attachButtonNoise?.();

    /* =======================================================
       SUBJECT RESOURCE BUTTONS
       ======================================================= */

    const subject = getSubject();

    if (
      subject &&
      window.CYBER_RESOURCES?.[subject]
    ) {

      document
        .querySelectorAll("[data-resource]")
        .forEach((btn) => {

          btn.addEventListener("click", () => {

            const kind =
              btn.dataset.resource;

            const url =
              window.CYBER_RESOURCES[subject][kind];

            secureRedirect(
              url,
              subject,
              kind
            );

          });

        });
    }

    /* =======================================================
       MASTER ADMIN BUTTON
       ======================================================= */

    const adminButton =
      document.getElementById("admin-button");

    if (adminButton) {

      if (
        window.ADMIN_URL &&
        !String(window.ADMIN_URL).includes("_URL")
      ) {

        adminButton.href =
          window.ADMIN_URL;

      } else {

        adminButton.addEventListener(
          "click",
          (event) => {

            event.preventDefault();

            window.alert(
              "Replace ADMIN_URL in config.js with your admin website URL."
            );

          }
        );
      }
    }

    /* =======================================================
       INTERNAL HTML PAGE TRANSITIONS
       ======================================================= */

    document
      .querySelectorAll('a[href$=".html"]')
      .forEach((link) => {

        link.addEventListener("click", (event) => {

          /*
           * Allow normal browser behavior for:
           * Ctrl + Click
           * Cmd + Click
           * Shift + Click
           * Alt + Click
           */

          if (
            event.metaKey ||
            event.ctrlKey ||
            event.shiftKey ||
            event.altKey
          ) {
            return;
          }

          const href =
            link.getAttribute("href");

          if (
            !href ||
            href.startsWith("#")
          ) {
            return;
          }

          event.preventDefault();

          /* -------------------------------------------------
             Create transition overlay
             ------------------------------------------------- */

          const transition =
            document.createElement("div");

          transition.className =
            "transition-overlay active";

          transition.innerHTML = `
            <div class="transition-lines"></div>

            <div class="transition-text">
              MODE SWITCHING...
            </div>
          `;

          document.body.appendChild(
            transition
          );

          /* -------------------------------------------------
             Navigate after short cinematic transition
             ------------------------------------------------- */

          setTimeout(() => {

            window.location.href =
              href;

          }, 330);

        });

      });

  });

})();
