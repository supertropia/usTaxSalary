/* =========================================================
   USTaxDeductionFinder.com — global site behavior
   ========================================================= */
(function () {
  "use strict";

  /* ---------- Mobile menu ---------- */
  var toggle = document.querySelector(".menu-toggle");
  var nav = document.querySelector(".primary-nav");
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  /* ---------- Reading progress bar (article pages) ---------- */
  var progressBar = document.querySelector(".reading-progress");
  var articleBody = document.querySelector(".article-body");
  if (progressBar && articleBody) {
    window.addEventListener("scroll", function () {
      var rect = articleBody.getBoundingClientRect();
      var total = articleBody.offsetHeight - window.innerHeight;
      var scrolled = Math.min(Math.max(-rect.top, 0), total);
      var pct = total > 0 ? (scrolled / total) * 100 : 0;
      progressBar.style.width = pct + "%";
    });
  }

  /* ---------- Font size control (persisted) ---------- */
  var FONT_KEY = "utdf-font-size";
  var htmlEl = document.documentElement;
  function applyFont(size) {
    htmlEl.classList.remove("font-lg", "font-xl");
    if (size === "lg") htmlEl.classList.add("font-lg");
    if (size === "xl") htmlEl.classList.add("font-xl");
  }
  try {
    var saved = localStorage.getItem(FONT_KEY);
    if (saved) applyFont(saved);
  } catch (e) {}

  var incBtn = document.getElementById("font-inc");
  var decBtn = document.getElementById("font-dec");
  var resetBtn = document.getElementById("font-reset");
  var sizes = ["base", "lg", "xl"];
  function currentIndex() {
    if (htmlEl.classList.contains("font-xl")) return 2;
    if (htmlEl.classList.contains("font-lg")) return 1;
    return 0;
  }
  function setFont(idx) {
    idx = Math.min(Math.max(idx, 0), sizes.length - 1);
    var size = sizes[idx];
    applyFont(size);
    try { localStorage.setItem(FONT_KEY, size); } catch (e) {}
  }
  if (incBtn) incBtn.addEventListener("click", function () { setFont(currentIndex() + 1); });
  if (decBtn) decBtn.addEventListener("click", function () { setFont(currentIndex() - 1); });
  if (resetBtn) resetBtn.addEventListener("click", function () { setFont(0); });

  /* ---------- Text-to-Speech: "Listen to this article" ----------
     Uses the browser's built-in, free SpeechSynthesis Web API.
     No API key or paid service required. */
  var ttsBtn = document.getElementById("tts-btn");
  var ttsLabel = document.getElementById("tts-label");
  if (ttsBtn && articleBody && "speechSynthesis" in window) {
    var utterance = null;
    var speaking = false;
    var paused = false;

    function getArticleText() {
      var clone = articleBody.cloneNode(true);
      var kill = clone.querySelectorAll(".ad-slot, .callout, script, style");
      kill.forEach(function (n) { n.remove(); });
      return clone.textContent.replace(/\s+/g, " ").trim();
    }

    function stopSpeech() {
      window.speechSynthesis.cancel();
      speaking = false;
      paused = false;
      ttsBtn.classList.remove("playing");
      ttsLabel.textContent = "Listen to this article";
    }

    ttsBtn.addEventListener("click", function () {
      if (!speaking) {
        var text = getArticleText();
        utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 0.98;
        utterance.pitch = 1;
        utterance.lang = "en-US";
        utterance.onend = stopSpeech;
        utterance.onerror = stopSpeech;
        window.speechSynthesis.cancel();
        window.speechSynthesis.speak(utterance);
        speaking = true;
        ttsBtn.classList.add("playing");
        ttsLabel.textContent = "Pause listening";
      } else if (!paused) {
        window.speechSynthesis.pause();
        paused = true;
        ttsLabel.textContent = "Resume listening";
      } else {
        window.speechSynthesis.resume();
        paused = false;
        ttsLabel.textContent = "Pause listening";
      }
    });

    window.addEventListener("beforeunload", function () {
      window.speechSynthesis.cancel();
    });
  } else if (ttsBtn) {
    ttsBtn.style.display = "none";
  }

  /* ---------- Share buttons ---------- */
  document.querySelectorAll("[data-share]").forEach(function (btn) {
    btn.addEventListener("click", function (e) {
      var network = btn.getAttribute("data-share");
      var url = encodeURIComponent(window.location.href);
      var title = encodeURIComponent(document.title);
      var shareUrls = {
        x: "https://twitter.com/intent/tweet?url=" + url + "&text=" + title,
        reddit: "https://www.reddit.com/submit?url=" + url + "&title=" + title,
        facebook: "https://www.facebook.com/sharer/sharer.php?u=" + url,
        whatsapp: "https://api.whatsapp.com/send?text=" + title + "%20" + url,
        email: "mailto:?subject=" + title + "&body=" + url
      };
      if (network === "copy") {
        e.preventDefault();
        navigator.clipboard && navigator.clipboard.writeText(window.location.href).then(function () {
          var original = btn.getAttribute("aria-label");
          btn.setAttribute("aria-label", "Link copied!");
          btn.classList.add("playing");
          setTimeout(function () {
            btn.setAttribute("aria-label", original);
            btn.classList.remove("playing");
          }, 1600);
        });
        return;
      }
      if (network === "instagram") {
        e.preventDefault();
        navigator.clipboard && navigator.clipboard.writeText(window.location.href);
        alert("Instagram doesn't support direct web sharing. The article link has been copied — paste it into your Instagram bio or story.");
        return;
      }
      if (shareUrls[network]) {
        e.preventDefault();
        window.open(shareUrls[network], "_blank", "noopener,noreferrer,width=600,height=600");
      }
    });
  });

  /* ---------- Blog tag / search filter (blog index page) ---------- */
  var searchInput = document.getElementById("blog-search");
  if (searchInput) {
    searchInput.addEventListener("input", function () {
      var q = searchInput.value.toLowerCase();
      document.querySelectorAll("[data-search-item]").forEach(function (item) {
        var haystack = item.getAttribute("data-search-item").toLowerCase();
        item.style.display = haystack.indexOf(q) !== -1 ? "" : "none";
      });
    });
  }

  /* ---------- FAQ schema toggler is native <details>, no JS needed ---------- */

  /* ---------- Newsletter form (static demo, no backend wired) ---------- */
  document.querySelectorAll(".newsletter-box form").forEach(function (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var btn = form.querySelector("button");
      var original = btn.textContent;
      btn.textContent = "Subscribed! ✓";
      form.reset();
      setTimeout(function () { btn.textContent = original; }, 2500);
    });
  });
})();
