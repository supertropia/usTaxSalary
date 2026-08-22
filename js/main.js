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
     No API key or paid service required.

     Chrome-specific fixes applied here:
     1) Chrome loads its voice list asynchronously — speak() called before
        voices are ready can silently do nothing on the first click. We wait
        for the "voiceschanged" event (or a short poll) before enabling.
     2) Chrome has a long-standing bug where utterances longer than ~15
        seconds get cut off / go silent. We avoid it by splitting the
        article into sentence-sized chunks and queuing them as separate
        utterances that play back-to-back, instead of one giant utterance.
     3) We prefer a local/offline voice when available, since Chrome's
        network-based voices can fail silently with no error event if the
        request to Google's voice service is blocked or slow. */
  var ttsBtn = document.getElementById("tts-btn");
  var ttsLabel = document.getElementById("tts-label");
  if (ttsBtn && articleBody && "speechSynthesis" in window) {
    var synth = window.speechSynthesis;
    var chunks = [];
    var chunkIndex = 0;
    var speaking = false;
    var paused = false;
    var chosenVoice = null;
    var voicesReady = false;

    function pickVoice() {
      var voices = synth.getVoices() || [];
      if (!voices.length) return;
      voicesReady = true;
      var enVoices = voices.filter(function (v) { return /^en/i.test(v.lang); });
      var local = enVoices.filter(function (v) { return v.localService; });
      chosenVoice = local[0] || enVoices[0] || voices[0];
    }
    pickVoice();
    if (!voicesReady && "onvoiceschanged" in synth) {
      synth.addEventListener("voiceschanged", pickVoice, { once: true });
    }

    function getArticleText() {
      var clone = articleBody.cloneNode(true);
      var kill = clone.querySelectorAll(".ad-slot, .callout, script, style");
      kill.forEach(function (n) { n.remove(); });
      return clone.textContent.replace(/\s+/g, " ").trim();
    }

    function splitIntoChunks(text) {
      // Split on sentence boundaries, then regroup into ~200-character
      // chunks so Chrome never has to hold a single very long utterance.
      var sentences = text.match(/[^.!?]+[.!?]+(\s|$)|[^.!?]+$/g) || [text];
      var out = [];
      var buf = "";
      sentences.forEach(function (s) {
        if ((buf + s).length > 200 && buf) {
          out.push(buf.trim());
          buf = s;
        } else {
          buf += s;
        }
      });
      if (buf.trim()) out.push(buf.trim());
      return out;
    }

    function stopSpeech() {
      synth.cancel();
      speaking = false;
      paused = false;
      chunkIndex = 0;
      ttsBtn.classList.remove("playing");
      ttsLabel.textContent = "Listen to this article";
    }

    function speakNextChunk() {
      if (chunkIndex >= chunks.length) {
        stopSpeech();
        return;
      }
      var utterance = new SpeechSynthesisUtterance(chunks[chunkIndex]);
      utterance.rate = 0.98;
      utterance.pitch = 1;
      utterance.lang = "en-US";
      if (chosenVoice) utterance.voice = chosenVoice;
      utterance.onend = function () {
        chunkIndex++;
        speakNextChunk();
      };
      utterance.onerror = function () {
        // Skip a chunk that failed rather than killing the whole reading.
        chunkIndex++;
        if (chunkIndex < chunks.length) {
          speakNextChunk();
        } else {
          stopSpeech();
        }
      };
      synth.speak(utterance);
    }

    ttsBtn.addEventListener("click", function () {
      if (!speaking) {
        if (!voicesReady) pickVoice(); // last-chance sync attempt
        var text = getArticleText();
        chunks = splitIntoChunks(text);
        chunkIndex = 0;
        synth.cancel();
        speaking = true;
        paused = false;
        ttsBtn.classList.add("playing");
        ttsLabel.textContent = "Pause listening";
        speakNextChunk();
      } else if (!paused) {
        synth.pause();
        paused = true;
        ttsLabel.textContent = "Resume listening";
      } else {
        synth.resume();
        paused = false;
        ttsLabel.textContent = "Pause listening";
      }
    });

    window.addEventListener("beforeunload", function () {
      synth.cancel();
    });

    // Chrome occasionally goes idle and silently drops an in-progress
    // utterance queue. A harmless pause/resume "heartbeat" keeps it alive.
    setInterval(function () {
      if (speaking && !paused && synth.speaking) {
        synth.pause();
        synth.resume();
      }
    }, 10000);
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
