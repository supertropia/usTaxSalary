/* =========================================================
   USTaxDeductionFinder.com — Standard vs. Itemized Engine
   All math runs client-side in memory. Nothing is transmitted
   or stored on any server. See /legal/privacy-policy.html
   ========================================================= */
(function () {
  "use strict";
  var form = document.getElementById("deduction-calculator");
  if (!form) return;

  var STANDARD = { single: 15000, mfj: 30000, hoh: 22000 };
  var SALT_CAP = 10000;
  var MEDICAL_AGI_THRESHOLD = 0.075;

  var steps = Array.prototype.slice.call(form.querySelectorAll(".calc-panel"));
  var stepBtns = Array.prototype.slice.call(form.querySelectorAll(".calc-steps button"));
  var currentStep = 0;

  function fmt(n) {
    return "$" + Math.round(n).toLocaleString("en-US");
  }

  function goToStep(idx) {
    currentStep = idx;
    steps.forEach(function (s, i) { s.classList.toggle("active", i === idx); });
    stepBtns.forEach(function (b, i) { b.classList.toggle("active", i === idx); });
    window.scrollTo({ top: form.offsetTop - 100, behavior: "smooth" });
  }

  stepBtns.forEach(function (btn, i) {
    btn.addEventListener("click", function () { goToStep(i); });
  });

  form.querySelectorAll("[data-next]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      if (currentStep < steps.length - 1) goToStep(currentStep + 1);
    });
  });
  form.querySelectorAll("[data-prev]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      if (currentStep > 0) goToStep(currentStep - 1);
    });
  });

  var calculateBtn = document.getElementById("calc-run");
  var spinnerWrap = document.getElementById("calc-spinner");
  var resultsPanel = document.getElementById("calc-results");

  calculateBtn.addEventListener("click", function () {
    goToStep(steps.length - 1);
    resultsPanel.style.display = "none";
    spinnerWrap.style.display = "block";
    setTimeout(runCalculation, 1400);
  });

  function num(id) {
    var el = document.getElementById(id);
    var v = parseFloat((el.value || "0").replace(/,/g, ""));
    return isNaN(v) ? 0 : v;
  }

  function runCalculation() {
    var filingStatus = form.querySelector('input[name="filingStatus"]:checked').value;
    var agi = num("agi");
    var medical = num("medical");
    var salt = num("salt");
    var mortgage = num("mortgage");
    var charity = num("charity");
    var miles = num("miles");
    var mileageRate = 0.67; // current-year standard mileage rate for business use (verify annually with the IRS)

    var standardDeduction = STANDARD[filingStatus];
    var allowedMedical = Math.max(0, medical - agi * MEDICAL_AGI_THRESHOLD);
    var cappedSalt = Math.min(salt, SALT_CAP);
    var totalItemized = allowedMedical + cappedSalt + mortgage + charity;
    var mileageDeduction = miles * mileageRate;
    var winner = totalItemized > standardDeduction ? "itemized" : "standard";
    var winnerAmount = Math.max(totalItemized, standardDeduction);
    var savingsVsOther = Math.abs(totalItemized - standardDeduction);

    spinnerWrap.style.display = "none";
    resultsPanel.style.display = "block";

    document.getElementById("res-standard-amt").textContent = fmt(standardDeduction);
    document.getElementById("res-itemized-amt").textContent = fmt(totalItemized);
    document.getElementById("res-winner-label").textContent =
      winner === "itemized" ? "Itemized Deductions" : "Standard Deduction";
    document.getElementById("res-winner-amount").textContent = fmt(winnerAmount);
    document.getElementById("res-savings-diff").textContent = fmt(savingsVsOther);
    document.getElementById("res-mileage-ded").textContent = fmt(mileageDeduction);

    var stdBar = document.getElementById("bar-standard");
    var itmBar = document.getElementById("bar-itemized");
    var maxVal = Math.max(standardDeduction, totalItemized, 1);
    stdBar.style.width = (standardDeduction / maxVal * 100) + "%";
    itmBar.style.width = (totalItemized / maxVal * 100) + "%";
    stdBar.classList.toggle("winner", winner === "standard");
    itmBar.classList.toggle("winner", winner === "itemized");

    var list = document.getElementById("breakdown-list");
    list.innerHTML =
      "<li><span>Allowed Medical (over 7.5% AGI)</span><span>" + fmt(allowedMedical) + "</span></li>" +
      "<li><span>SALT (capped at $10,000)</span><span>" + fmt(cappedSalt) + "</span></li>" +
      "<li><span>Mortgage Interest</span><span>" + fmt(mortgage) + "</span></li>" +
      "<li><span>Charitable Donations</span><span>" + fmt(charity) + "</span></li>" +
      "<li class=\"total\"><span>Total Itemized</span><span>" + fmt(totalItemized) + "</span></li>";
  }
})();
