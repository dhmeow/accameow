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
     RESET RESOURCE TRANSITION
     
     IMPORTANT:
     This fixes the browser Back-button problem.
     
     Chrome/Edge/Firefox may restore the previous page from
     the BFCache with the loading overlay still visible.
     ========================================================= */

  function resetResourceTransition() {
    const overlay =
      document.getElementById("resource-transition");

    if (!overlay) {
      return;
    }

    overlay.classList.remove("active");

    overlay.setAttribute(
      "aria-hidden",
      "true"
    );

    /*
     * Remove inline styles that were added while the
     * connection animation was running.
     */

    overlay.style.opacity = "";
    overlay.style.visibility = "";
    overlay.style.pointerEvents = "";
    overlay.style.animation = "";

    const label =
      document.getElementById(
        "resource-transition-text"
      );

    if (label) {
      label.textContent =
        "ESTABLISHING SECURE CONNECTION...";
    }
  }

  /* =========================================================
     RESOURCE CONNECTION ANIMATION
     ========================================================= */

  async function secureRedirect(
    url,
    subject,
    kind
  ) {
    const overlay =
      document.getElementById(
        "resource-transition"
      );

    const label =
      document.getElementById(
        "resource-transition-text"
      );

    /* -------------------------------------------------------
       Validate URL
       ------------------------------------------------------- */

    if (!isConfigured(url)) {
      const resourceName =
        `${subject}_${
          kind === "practice"
            ? "QUESTION_PRACTICE"
            : "NOTES"
        }_URL`;

      if (overlay && label) {
        overlay.classList.add("active");

        overlay.setAttribute(
          "aria-hidden",
          "false"
        );

        overlay.style.opacity = "1";
        overlay.style.visibility = "visible";
        overlay.style.pointerEvents = "all";
        overlay.style.animation = "none";

        label.textContent =
          "URL PLACEHOLDER // CONFIG REQUIRED";

        await sleep(900);

        resetResourceTransition();
      }

      window.alert(
        `No real URL is configured yet.\n\n` +
        `Set ${resourceName} in config.js.`
      );

      return;
    }

    /* -------------------------------------------------------
       Fallback if transition doesn't exist
       ------------------------------------------------------- */

    if (!overlay || !label) {
      window.location.assign(url);
      return;
    }

    /* -------------------------------------------------------
       START CONNECTION ANIMATION
       ------------------------------------------------------- */

    overlay.classList.add("active");

    overlay.setAttribute(
      "aria-hidden",
      "false"
    );

    /*
     * Prevent CSS transition-out from hiding the overlay
     * before our sequence finishes.
     */

    overlay.style.opacity = "1";
    overlay.style.visibility = "visible";
    overlay.style.pointerEvents = "all";
    overlay.style.animation = "none";

    /* -------------------------------------------------------
       PHASE 1
       ------------------------------------------------------- */

    label.textContent =
      "ESTABLISHING SECURE CONNECTION...";

    await sleep(450);

    /* -------------------------------------------------------
       PHASE 2
       ------------------------------------------------------- */

    label.textContent =
      `SCANNING NODE // 0x${randomHex(6)}`;

    await sleep(400);

    /* -------------------------------------------------------
       PHASE 3
       ------------------------------------------------------- */

    label.textContent =
      "RESOURCE LOCATED";

    await sleep(350);

    /* -------------------------------------------------------
       PHASE 4
       ------------------------------------------------------- */

    label.textContent =
      "SECURE CHANNEL ESTABLISHED";

    await sleep(400);

    /* -------------------------------------------------------
       PHASE 5
       ------------------------------------------------------- */

    label.textContent =
      "ACCESSING DATABASE...";

    await sleep(450);

    /* -------------------------------------------------------
       FINAL
       ------------------------------------------------------- */

    label.textContent =
      "ACCESS GRANTED";

    await sleep(250);

    /*
     * Navigate in the SAME TAB.
     */

    window.location.assign(url);
  }

  /* =========================================================
     DOM READY
     ========================================================= */

  document.addEventListener(
    "DOMContentLoaded",
    () => {

      /*
       * Always start with a clean transition state.
       */

      resetResourceTransition();

      /* =====================================================
         CYBER EFFECTS
         ===================================================== */

      CyberEffects?.orientationGate?.();
      CyberEffects?.attachGlitchPulse?.();
      CyberEffects?.attachMagneticCards?.();
      CyberEffects?.attachButtonNoise?.();

      /* =====================================================
         SUBJECT RESOURCE BUTTONS
         ===================================================== */

      const subject =
        getSubject();

      if (
        subject &&
        window.CYBER_RESOURCES?.[subject]
      ) {

        document
          .querySelectorAll(
            "[data-resource]"
          )
          .forEach((button) => {

            button.addEventListener(
              "click",
              () => {

                const kind =
                  button.dataset.resource;

                const url =
                  window.CYBER_RESOURCES[
                    subject
                  ][kind];

                secureRedirect(
                  url,
                  subject,
                  kind
                );

              }
            );

          });
      }

      /* =====================================================
         MASTER ADMIN BUTTON
         ===================================================== */

      const adminButton =
        document.getElementById(
          "admin-button"
        );

      if (adminButton) {

        if (
          window.ADMIN_URL &&
          !String(
            window.ADMIN_URL
          ).includes("_URL")
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

      /* =====================================================
         INTERNAL HTML PAGE TRANSITIONS
         ===================================================== */

      document
        .querySelectorAll(
          'a[href$=".html"]'
        )
        .forEach((link) => {

          link.addEventListener(
            "click",
            (event) => {

              /*
               * Allow modifier-clicks to work normally.
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

              const transition =
                document.createElement(
                  "div"
                );

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

              setTimeout(() => {

                window.location.href =
                  href;

              }, 350);

            }
          );
        });

    }
  );

  /* =========================================================
     BROWSER BACK / FORWARD / BFCache FIX
     ========================================================= */

  window.addEventListener(
    "pageshow",
    () => {

      /*
       * This fires when the page is:
       *
       * - normally loaded
       * - restored from BFCache
       * - returned to using the browser Back button
       *
       * Therefore the resource overlay is always reset.
       */

      resetResourceTransition();

    }
  );

  /* =========================================================
     PAGE VISIBILITY FIX
     ========================================================= */

  document.addEventListener(
    "visibilitychange",
    () => {

      /*
       * When returning to this page from another tab/page,
       * make sure the temporary transition isn't stuck.
       */

      if (
        document.visibilityState === "visible"
      ) {

        resetResourceTransition();

      }

    }
  );

})();
