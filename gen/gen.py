# -*- coding: utf-8 -*-
"""
Static site generator for USTaxDeductionFinder.com
Reads articles_data.py, renders every page as plain, dependency-free
HTML/CSS/JS ready for zero-config deployment on Vercel.
"""
import os, re, shutil, math, json
from datetime import datetime
from articles_data import ARTICLES, TAGS

SITE_NAME = "USTaxDeductionFinder.com"
SITE_URL = "https://www.ustaxdeductionfinder.com"
OUT = os.path.join(os.path.dirname(__file__), "..")
BLOG_DIR = os.path.join(OUT, "blog")
LEGAL_DIR = os.path.join(OUT, "legal")

TAG_SLUGS = {t: re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-") for t in TAGS}

def word_count(html):
    text = re.sub(r"<[^>]+>", " ", html)
    return len(text.split())

for a in ARTICLES:
    a["word_count"] = word_count(a["content"])
    a.setdefault("read_minutes", max(4, round(a["word_count"] / 220)))
    a["primary_tag"] = a["tags"][0]

def articles_by_tag(tag):
    return [a for a in ARTICLES if tag in a["tags"]]

def related_articles(article, n=3):
    scored = []
    for other in ARTICLES:
        if other["slug"] == article["slug"]:
            continue
        overlap = len(set(other["tags"]) & set(article["tags"]))
        scored.append((overlap, other))
    scored.sort(key=lambda x: -x[0])
    return [o for _, o in scored[:n]]

def fmt_date(iso):
    d = datetime.strptime(iso, "%Y-%m-%d")
    return d.strftime("%B %-d, %Y") if os.name != "nt" else d.strftime("%B %d, %Y")

# ---------------------------------------------------------------- icons
ICONS = {
"x": '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M18.9 2H22l-7.6 8.7L23.3 22H16.9l-5-6.5L6 22H2.9l8.1-9.3L1.7 2h6.6l4.5 6z"/></svg>',
"reddit": '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M22 12c0-1.1-.9-2-2-2-.5 0-1 .2-1.3.5-1.3-.9-3-1.5-4.9-1.6l.8-3.9 2.7.6c0 .8.7 1.4 1.4 1.4.8 0 1.4-.6 1.4-1.4s-.6-1.4-1.4-1.4c-.6 0-1 .3-1.3.8l-3-.6c-.2 0-.3.1-.4.2l-1 4.4c-1.9.1-3.6.7-4.9 1.6-.3-.3-.8-.5-1.3-.5-1.1 0-2 .9-2 2 0 .8.5 1.5 1.1 1.8-.1.3-.1.6-.1.9 0 2.7 3.1 4.9 7 4.9s7-2.2 7-4.9c0-.3 0-.6-.1-.9.6-.3 1.1-1 1.1-1.8zM8.5 13.5c0-.6.5-1 1-1s1 .4 1 1-.5 1.1-1 1.1-1-.5-1-1.1zm6.9 2.6c-.7.7-1.9 1-3.4 1s-2.7-.3-3.4-1c-.2-.1-.2-.4 0-.5.1-.2.4-.2.5 0 .5.5 1.5.8 2.9.8s2.4-.3 2.9-.8c.1-.2.4-.2.5 0 .2.1.2.4 0 .5zm-.2-1.5c-.5 0-1-.5-1-1.1s.5-1 1-1 1 .4 1 1-.5 1.1-1 1.1z"/></svg>',
"facebook": '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M13.5 21v-8h2.7l.4-3.1h-3.1V8c0-.9.2-1.5 1.6-1.5H17V3.7c-.3 0-1.2-.1-2.4-.1-2.3 0-3.9 1.4-3.9 4V10H8v3.1h2.7v8h2.8z"/></svg>',
"whatsapp": '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2a10 10 0 0 0-8.6 15L2 22l5.2-1.4A10 10 0 1 0 12 2zm0 18.1a8 8 0 0 1-4.1-1.1l-.3-.2-3.1.8.8-3-.2-.3A8.1 8.1 0 1 1 12 20.1zm4.4-6c-.2-.1-1.4-.7-1.6-.8-.2-.1-.4-.1-.5.1s-.6.8-.7.9-.3.2-.5.1a6.6 6.6 0 0 1-3.3-2.9c-.2-.4.2-.4.6-1.2.1-.1 0-.3 0-.4L9.2 8.9c-.2-.4-.4-.4-.5-.4h-.5a.9.9 0 0 0-.7.3 2.7 2.7 0 0 0-.8 2 4.7 4.7 0 0 0 1 2.5 10.8 10.8 0 0 0 4.5 4c1.6.6 1.9.5 2.3.5a1.9 1.9 0 0 0 1.3-.9 1.6 1.6 0 0 0 .1-.9c-.1-.1-.2-.2-.5-.3z"/></svg>',
"email": '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M2 4h20v16H2V4zm2 2v.01L12 12l8-5.99V6H4zm16 12V8.4l-8 6-8-6V18h16z"/></svg>',
"instagram": '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2c2.7 0 3.1 0 4.1.1 1.1 0 1.8.2 2.5.4.7.3 1.2.6 1.8 1.2.6.6.9 1.1 1.2 1.8.2.7.4 1.4.4 2.5.1 1 .1 1.4.1 4.1s0 3.1-.1 4.1c0 1.1-.2 1.8-.4 2.5-.3.7-.6 1.2-1.2 1.8-.6.6-1.1.9-1.8 1.2-.7.2-1.4.4-2.5.4-1 .1-1.4.1-4.1.1s-3.1 0-4.1-.1c-1.1 0-1.8-.2-2.5-.4-.7-.3-1.2-.6-1.8-1.2-.6-.6-.9-1.1-1.2-1.8-.2-.7-.4-1.4-.4-2.5C2 15.1 2 14.7 2 12s0-3.1.1-4.1c0-1.1.2-1.8.4-2.5.3-.7.6-1.2 1.2-1.8.6-.6 1.1-.9 1.8-1.2.7-.2 1.4-.4 2.5-.4C8.9 2 9.3 2 12 2zm0 5a5 5 0 1 0 0 10 5 5 0 0 0 0-10zm0 8.2A3.2 3.2 0 1 1 12 8.8a3.2 3.2 0 0 1 0 6.4zm5.2-8.4a1.2 1.2 0 1 1 0-2.4 1.2 1.2 0 0 1 0 2.4z"/></svg>',
"copy": '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M16 1H4a2 2 0 0 0-2 2v14h2V3h12V1zm3 4H8a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h11a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2zm0 16H8V7h11v14z"/></svg>',
"check": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M20 6L9 17l-5-5"/></svg>',
"pin": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 21s-7-6.1-7-11a7 7 0 1 1 14 0c0 4.9-7 11-7 11z"/><circle cx="12" cy="10" r="2.5"/></svg>',
"mail": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m2 7 10 6 10-6"/></svg>',
"clock": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 3"/></svg>',
}

def share_row():
    return ('<div class="share-row">'
        '<a href="#" data-share="x" class="share-btn share-x" aria-label="Share on X">' + ICONS["x"] + '</a>'
        '<a href="#" data-share="reddit" class="share-btn share-reddit" aria-label="Share on Reddit">' + ICONS["reddit"] + '</a>'
        '<a href="#" data-share="facebook" class="share-btn share-facebook" aria-label="Share on Facebook">' + ICONS["facebook"] + '</a>'
        '<a href="#" data-share="whatsapp" class="share-btn share-whatsapp" aria-label="Share on WhatsApp">' + ICONS["whatsapp"] + '</a>'
        '<a href="#" data-share="instagram" class="share-btn share-instagram" aria-label="Share on Instagram">' + ICONS["instagram"] + '</a>'
        '<a href="#" data-share="email" class="share-btn share-email" aria-label="Share by email">' + ICONS["email"] + '</a>'
        '<button data-share="copy" class="share-btn share-copy" aria-label="Copy link">' + ICONS["copy"] + '</button>'
        '</div>')

# ---------------------------------------------------------------- shell
def head(title, description, canonical, extra_schema=""):
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canon}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{site}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{site_url}/images/og-cover.svg">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<link rel="icon" type="image/svg+xml" href="/images/favicon.svg">
<link rel="stylesheet" href="/css/styles.css">
<meta name="robots" content="index, follow">
<meta name="google-adsense-account" content="ca-pub-XXXXXXXXXXXXXXXX">
{schema}
</head>
""".format(title=title, desc=description, canon=canonical, site=SITE_NAME, site_url=SITE_URL, schema=extra_schema)

def header_html(active=""):
    def cls(name):
        return " class=\"active\"" if active == name else ""
    return """<a class="skip-link" href="#main">Skip to content</a>
<div class="utility-bar"><div class="container">
  <span>IRS-aligned estimates for the {tax_year} filing season · Freelancers · 1099 · Gig Economy</span>
  <span><a href="/blog/index.html">Read the Tax Blog →</a></span>
</div></div>
<header class="site-header">
  <div class="container nav-wrap">
    <a href="/index.html" class="brand"><span class="mark">1040</span><span>{site}<small>Standard vs. Itemized Estimator</small></span></a>
    <nav class="primary-nav" id="primary-nav">
      <a href="/index.html"{home}>Home</a>
      <a href="/index.html#calculator">1040 Deduction Calculator</a>
      <a href="/blog/index.html"{blog}>Tax Blog</a>
      <a href="/contact.html"{contact}>Contact</a>
      <a href="/index.html#calculator" class="cta">Start Free Estimate</a>
    </nav>
    <button class="menu-toggle" aria-label="Toggle menu" aria-expanded="false">☰ Menu</button>
  </div>
</header>
""".format(site=SITE_NAME, tax_year="2026", home=cls("home"), blog=cls("blog"), contact=cls("contact"))

def footer_html():
    tag_links = "".join('<li><a href="/blog/tag-{s}.html">{t}</a></li>'.format(s=TAG_SLUGS[t], t=t) for t in TAGS[:6])
    article_links = "".join('<li><a href="/blog/{s}.html">{t}</a></li>'.format(s=a["slug"], t=a["title"][:42] + ("…" if len(a["title"])>42 else "")) for a in ARTICLES[:6])
    return """<footer class="site-footer">
  <div class="container footer-grid">
    <div>
      <div class="footer-brand"><span class="mark" style="width:32px;height:32px;border-radius:8px;background:#0d8a63;display:flex;align-items:center;justify-content:center;font-family:var(--font-mono);font-size:.8rem;">1040</span>{site}</div>
      <p class="footer-disclaimer">DISCLAIMER: This tool estimates tax deductions based on general IRS codes and public standard filing thresholds for the current tax season. It does not constitute CPA, financial planning, or professional legal tax advice. Always cross-verify your final deductions with official IRS documentation before filing.</p>
    </div>
    <div><h5>Company</h5><ul>
      <li><a href="/index.html">Home</a></li>
      <li><a href="/blog/index.html">Tax Blog</a></li>
      <li><a href="/contact.html">Contact Us</a></li>
      <li><a href="/index.html#calculator">1040 Deduction Calculator</a></li>
    </ul></div>
    <div><h5>Legal</h5><ul>
      <li><a href="/legal/privacy-policy.html">Privacy Policy</a></li>
      <li><a href="/legal/terms-of-service.html">Terms of Service</a></li>
      <li><a href="/legal/disclaimer.html">Disclaimer</a></li>
      <li><a href="https://www.irs.gov" rel="noopener nofollow" target="_blank">IRS.gov ↗</a></li>
    </ul></div>
    <div><h5>Popular Topics</h5><ul>{tags}</ul></div>
  </div>
  <div class="container footer-bottom">
    <span>© <span id="year">2026</span> {site} · Tax Tools Media Group, New York, NY, USA</span>
    <span>Not affiliated with the IRS or U.S. Department of the Treasury.</span>
  </div>
</footer>
<script>document.getElementById('year').textContent = new Date().getFullYear();</script>
<script src="/js/main.js"></script>
""".format(site=SITE_NAME, tags=tag_links)

def page(title, description, canonical, body, active="", extra_schema="", extra_js=""):
    return head(title, description, canonical, extra_schema) + "<body>\n" + header_html(active) + "<main id=\"main\">\n" + body + "\n</main>\n" + footer_html() + extra_js + "\n</body>\n</html>\n"

# ---------------------------------------------------------------- ARTICLE CARD
def article_card(a):
    return """<article class="article-card">
  <div class="thumb"><span class="tag-icon">§</span></div>
  <div class="body">
    <span class="tag">{tag}</span>
    <h3><a href="/blog/{slug}.html">{title}</a></h3>
    <p>{dek}</p>
    <div class="meta"><span>{icon_clock} {mins} min read</span><span>{date}</span></div>
  </div>
</article>""".format(tag=a["primary_tag"], slug=a["slug"], title=a["title"], dek=a["dek"],
                      mins=a["read_minutes"], date=fmt_date(a["publish_date"]), icon_clock="⏱")

print("gen.py helpers loaded OK")

# ---------------------------------------------------------------- CALCULATOR BLOCK
def calculator_block():
    return """
<section id="calculator">
  <div class="container">
    <div class="section-head" style="max-width:720px;">
      <span class="eyebrow">Free · No Sign-Up · Nothing Ever Saved</span>
      <h2>The 1040 Deduction Calculator</h2>
      <p>Answer four short steps and instantly see whether the Standard Deduction or Itemized Deductions save you more this tax year — plus your estimated business mileage write-off.</p>
    </div>

    <div class="ad-slot leaderboard"><!-- ADSENSE CONTENT AD HERE --></div>

    <form id="deduction-calculator" class="calc-card" onsubmit="return false;">
      <div class="calc-steps">
        <button type="button" class="active"><span class="num">1</span>Profession &amp; Filing Status</button>
        <button type="button"><span class="num">2</span>Income &amp; Expenses</button>
        <button type="button"><span class="num">3</span>Vehicle Mileage</button>
        <button type="button"><span class="num">4</span>Your Results</button>
      </div>
      <div class="calc-body">

        <div class="calc-panel active">
          <div class="field-grid">
            <div class="field">
              <label for="profession">What best describes your work?</label>
              <select id="profession">
                <option>Freelancer / Independent Contractor</option>
                <option>Uber / Lyft / Rideshare Driver</option>
                <option>Real Estate Agent</option>
                <option>Content Creator</option>
                <option>Other Self-Employed</option>
              </select>
              <span class="hint">This helps tailor the article recommendations after your results.</span>
            </div>
            <div class="field">
              <label>Filing Status</label>
              <div class="pill-group">
                <label><input type="radio" name="filingStatus" value="single" checked><span>Single ($15,000 std.)</span></label>
                <label><input type="radio" name="filingStatus" value="mfj"><span>Married Filing Jointly ($30,000 std.)</span></label>
                <label><input type="radio" name="filingStatus" value="hoh"><span>Head of Household ($22,000 std.)</span></label>
              </div>
            </div>
          </div>
          <div class="calc-nav"><span></span><button type="button" class="btn btn-primary" data-next>Continue →</button></div>
        </div>

        <div class="calc-panel">
          <div class="field-grid">
            <div class="field"><label for="agi">Annual Gross Income (AGI)</label><input type="text" id="agi" placeholder="e.g. 68000" inputmode="numeric"></div>
            <div class="field"><label for="medical">Out-of-Pocket Medical Expenses</label><input type="text" id="medical" placeholder="e.g. 4200" inputmode="numeric"><span class="hint">Only the amount above 7.5% of AGI counts.</span></div>
            <div class="field"><label for="salt">State &amp; Local Taxes (SALT) Paid</label><input type="text" id="salt" placeholder="e.g. 8500" inputmode="numeric"><span class="hint">Capped at $10,000 by the IRS.</span></div>
            <div class="field"><label for="mortgage">Mortgage Interest Expenses</label><input type="text" id="mortgage" placeholder="e.g. 6200" inputmode="numeric"></div>
            <div class="field"><label for="charity">Charitable Cash Donations</label><input type="text" id="charity" placeholder="e.g. 1200" inputmode="numeric"></div>
          </div>
          <div class="calc-nav"><button type="button" class="btn btn-outline" data-prev>← Back</button><button type="button" class="btn btn-primary" data-next>Continue →</button></div>
        </div>

        <div class="calc-panel">
          <div class="field-grid">
            <div class="field"><label for="miles">Total Business Miles Driven</label><input type="text" id="miles" placeholder="e.g. 9500" inputmode="numeric"><span class="hint">Uses the current standard mileage rate for business use.</span></div>
          </div>
          <div class="ad-slot" style="min-height:100px;"><!-- ADSENSE CONTENT AD HERE --></div>
          <div class="calc-nav"><button type="button" class="btn btn-outline" data-prev>← Back</button><button type="button" class="btn btn-amber" id="calc-run">Calculate My Deductions →</button></div>
        </div>

        <div class="calc-panel">
          <div id="calc-spinner" class="spinner-wrap" style="display:none;">
            <div class="spinner"></div>
            <p>Analyzing IRS standard deduction guidelines for the current tax year…</p>
          </div>

          <div id="calc-results" style="display:none;">
            <div class="ad-slot rectangle" style="margin-bottom:24px;"><!-- ADSENSE AD REVENUE UNIT --></div>
            <div class="results-grid">
              <div>
                <h3 style="font-size:1.2rem;">Standard vs. Itemized Comparison</h3>
                <div class="compare-bars">
                  <div class="compare-bar-row">
                    <div class="lbl"><span>Standard Deduction</span><span id="res-standard-amt">$0</span></div>
                    <div class="compare-bar-track"><div class="compare-bar-fill" id="bar-standard" style="width:0%"></div></div>
                  </div>
                  <div class="compare-bar-row">
                    <div class="lbl"><span>Itemized Deductions</span><span id="res-itemized-amt">$0</span></div>
                    <div class="compare-bar-track"><div class="compare-bar-fill" id="bar-itemized" style="width:0%"></div></div>
                  </div>
                </div>
                <div class="alert-winner">
                  """ + ICONS["check"] + """
                  <div>
                    <strong>Recommended route: <span id="res-winner-label">—</span></strong>
                    Take a total deduction of <strong id="res-winner-amount">$0</strong> — that's <span id="res-savings-diff">$0</span> more than the other route.
                  </div>
                </div>
                <p class="small-note">Estimated business mileage deduction: <strong id="res-mileage-ded">$0</strong> (added to your Schedule C, separate from the comparison above).</p>
              </div>
              <div>
                <h3 style="font-size:1.2rem;">Itemized Breakdown</h3>
                <ul class="breakdown-list" id="breakdown-list"></ul>
                <p class="small-note">All figures are calculated in your browser and are never transmitted or stored. See our <a href="/legal/privacy-policy.html">Privacy Policy</a>.</p>
              </div>
            </div>
          </div>
          <div class="calc-nav"><button type="button" class="btn btn-outline" data-prev>← Back</button><span></span></div>
        </div>

      </div>
    </form>

    <div class="disclaimer-box">
      <strong>DISCLAIMER:</strong> This tool is engineered to estimate tax deductions based on general internal revenue codes (IRS) and public standard filing tax thresholds for the current tax season. It does not constitute certified public accounting (CPA), financial planning, or professional legal tax consulting advice. Tax regulations are subject to regular updates. Always cross-verify your final standard or itemized write-offs with official IRS documentation before submission.
    </div>
  </div>
</section>
<script src="/js/calculator.js"></script>
"""

# ---------------------------------------------------------------- HOME
def build_home():
    latest = sorted(ARTICLES, key=lambda a: a["publish_date"], reverse=True)[:6]
    cards = "\n".join(article_card(a) for a in latest)

    schema = """<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "WebApplication",
  "name": "US Tax Deduction Finder",
  "applicationCategory": "FinanceApplication",
  "operatingSystem": "Any",
  "url": "%s",
  "description": "Free calculator comparing Standard vs. Itemized IRS tax deductions for freelancers, gig workers, and independent contractors.",
  "offers": {"@type":"Offer","price":"0","priceCurrency":"USD"}
}
</script>
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {"@type":"Question","name":"Can I claim the home office deduction if I work remotely for a company?","acceptedAnswer":{"@type":"Answer","text":"No, under current laws, W-2 employees cannot claim the home office deduction. It is strictly reserved for self-employed individuals."}},
    {"@type":"Question","name":"What is the standard mileage rate deduction for this year?","acceptedAnswer":{"@type":"Answer","text":"The IRS adjusts it annually; users can input total business miles driven to calculate the dollar deduction instantly."}},
    {"@type":"Question","name":"What happens if my itemized deductions are lower than the standard deduction?","acceptedAnswer":{"@type":"Answer","text":"The software will automatically advise you to take the standard deduction to secure the largest tax reduction."}},
    {"@type":"Question","name":"What receipts do I need to keep to back up my self-employed expenses?","acceptedAnswer":{"@type":"Answer","text":"Keep digital or physical logs of any purchase directly related to your business operation for at least 3 to 7 years."}}
  ]
}
</script>""" % SITE_URL

    hero = """
<section class="hero">
  <div class="container">
    <div>
      <span class="eyebrow">""" + ICONS["pin"] + """ Built for 1099 Filers &amp; Gig Workers</span>
      <h1>Find every deduction the IRS actually <em>owes</em> you.</h1>
      <p class="lede">USTaxDeductionFinder.com compares your Standard Deduction against a full Itemized breakdown in under sixty seconds — built specifically for freelancers, Uber &amp; Lyft drivers, real estate agents, and content creators filing a Schedule C.</p>
      <div class="hero-ctas">
        <a href="#calculator" class="btn btn-primary">Calculate My Deductions</a>
        <a href="/blog/index.html" class="btn btn-outline">Browse the Tax Blog</a>
      </div>
      <div class="hero-trust">
        <span>""" + ICONS["check"] + """ Nothing you enter is ever saved</span>
        <span>""" + ICONS["check"] + """ Updated for the current tax year</span>
        <span>""" + ICONS["check"] + """ 20+ in-depth guides included</span>
      </div>
    </div>
    <div class="receipt">
      <h4><span>ESTIMATE #0042</span><span>2026 TAX YEAR</span></h4>
      <div class="row"><span>Filing Status</span><span>Single</span></div>
      <div class="row"><span>Standard Deduction</span><span>$15,000</span></div>
      <div class="row"><span>Itemized (SALT+Mortgage+Charity)</span><span>$16,700</span></div>
      <div class="row"><span>Business Mileage (9,500 mi)</span><span>$6,365</span></div>
      <div class="row total"><span>Recommended Route</span><span>Itemized</span></div>
      <div class="badge">✓ Saves an estimated $1,700 vs. standard</div>
    </div>
  </div>
</section>
"""

    trust_bar = """
<section class="bg-panel" style="padding:32px 0;">
  <div class="container badge-list" style="justify-content:center;">
    <span class="trust-badge">""" + ICONS["check"] + """ SALT $10,000 cap enforced</span>
    <span class="trust-badge">""" + ICONS["check"] + """ 7.5% AGI medical threshold</span>
    <span class="trust-badge">""" + ICONS["check"] + """ Freelancer, Uber/Lyft &amp; Real Estate ready</span>
    <span class="trust-badge">""" + ICONS["check"] + """ 100% calculated in your browser</span>
  </div>
</section>
"""

    who = """
<section>
  <div class="container">
    <div class="section-head">
      <span class="eyebrow">Who This Tool Is Built For</span>
      <h2>One calculator, four very different tax pictures</h2>
      <p>Every profession below has its own blind spots in the tax code. Our blog covers each in depth — start with the calculator, then read the guide that matches your work.</p>
    </div>
    <div class="article-grid">
      <div class="article-card"><div class="thumb"><span class="tag-icon">✦</span></div><div class="body">
        <span class="tag">Self-Employed &amp; Freelance</span><h3><a href="/blog/home-office-deduction-freelancers-guide.html">Freelancers &amp; Contractors</a></h3>
        <p>Home office math, quarterly taxes, and the self-employment tax nobody warns you about.</p></div></div>
      <div class="article-card"><div class="thumb"><span class="tag-icon">✦</span></div><div class="body">
        <span class="tag">Gig Economy</span><h3><a href="/blog/uber-lyft-driver-tax-deductions-checklist.html">Uber &amp; Lyft Drivers</a></h3>
        <p>Mileage is your biggest write-off — here's exactly how to track and claim every trip.</p></div></div>
      <div class="article-card"><div class="thumb"><span class="tag-icon">✦</span></div><div class="body">
        <span class="tag">Real Estate Pros</span><h3><a href="/blog/real-estate-agent-tax-deductions.html">Real Estate Agents</a></h3>
        <p>MLS fees, marketing spend, and showings mileage add up fast — don't leave them unclaimed.</p></div></div>
      <div class="article-card"><div class="thumb"><span class="tag-icon">✦</span></div><div class="body">
        <span class="tag">Gig Economy</span><h3><a href="/blog/content-creator-tax-deductions.html">Content Creators</a></h3>
        <p>Cameras, software, and home studios — what production gear is actually deductible.</p></div></div>
    </div>
  </div>
</section>
"""

    latest_section = """
<section class="bg-panel">
  <div class="container">
    <div class="section-head">
      <span class="eyebrow">From the Tax Blog</span>
      <h2>Long-form guides, built to save you real money</h2>
      <p>Twenty in-depth articles at launch, all cross-linked so you can go deeper on exactly the deduction category that applies to you.</p>
    </div>
    <div class="article-grid">
      %s
    </div>
    <div style="text-align:center; margin-top:34px;"><a href="/blog/index.html" class="btn btn-outline">View All Articles →</a></div>
  </div>
</section>
""" % cards

    faq_section = """
<section>
  <div class="container" style="max-width:820px;">
    <div class="section-head">
      <span class="eyebrow">Frequently Asked Questions</span>
      <h2>Before you run the numbers</h2>
    </div>
    <details class="faq-item" open><summary>Can I claim the home office deduction if I work remotely for a company?</summary><p>No, under current laws, W-2 employees cannot claim the home office deduction. It is strictly reserved for self-employed individuals. Read the full breakdown in our <a href="/blog/home-office-deduction-freelancers-guide.html">Home Office Deduction Guide</a>.</p></details>
    <details class="faq-item"><summary>What is the standard mileage rate deduction for this year?</summary><p>The IRS adjusts it annually. Enter your total business miles driven into the calculator above to see the current-year dollar deduction instantly, or read <a href="/blog/standard-mileage-rate-vs-actual-expenses.html">Standard Mileage Rate vs. Actual Expenses</a> for the full comparison against tracking actual costs.</p></details>
    <details class="faq-item"><summary>What happens if my itemized deductions are lower than the standard deduction?</summary><p>The calculator will automatically recommend the Standard Deduction to secure the largest tax reduction — there is never a scenario where a smaller itemized total is the better choice.</p></details>
    <details class="faq-item"><summary>What receipts do I need to keep to back up my self-employed expenses?</summary><p>Keep digital or physical logs of any purchase directly related to your business operation for at least three to seven years. See our full system in <a href="/blog/recordkeeping-for-freelancers-receipts.html">Record Keeping for Freelancers</a>.</p></details>
  </div>
</section>
"""

    cta = """
<section class="bg-forest">
  <div class="container" style="text-align:center; max-width:640px;">
    <h2>Stop guessing which route saves more.</h2>
    <p style="margin-bottom:26px;">Run your real numbers through the calculator — it takes less than a minute and nothing you enter ever leaves your browser.</p>
    <a href="#calculator" class="btn btn-amber">Calculate My Deductions →</a>
  </div>
</section>
"""

    body = hero + trust_bar + calculator_block() + who + latest_section + faq_section + cta
    html = page(
        "US Tax Deduction Finder & Calculator: Maximize Your IRS Refund | " + SITE_NAME,
        "Free Standard vs. Itemized deduction calculator for freelancers, 1099 contractors, and gig workers. Instantly compare deductions and find every write-off you qualify for.",
        SITE_URL + "/index.html", body, active="home", extra_schema=schema
    )
    with open(os.path.join(OUT, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)

build_home()
print("home built")

# ---------------------------------------------------------------- SIDEBAR
def sidebar(active_tag=None):
    tag_items = ""
    for t in TAGS:
        count = len(articles_by_tag(t))
        active_cls = " active" if active_tag == t else ""
        tag_items += '<a href="/blog/tag-{s}.html" class="{cls}">{t}<span class="count">{c}</span></a>'.format(
            s=TAG_SLUGS[t], cls=active_cls.strip(), t=t, c=count)
    popular = sorted(ARTICLES, key=lambda a: a["read_minutes"])[:5]
    pop_items = "".join('<li><a href="/blog/{s}.html"><span class="n">{n:02d}</span><span>{t}</span></a></li>'.format(
        s=a["slug"], n=i+1, t=a["title"]) for i, a in enumerate(popular))
    return """
<aside>
  <div class="sidebar-box">
    <h4>Search Articles</h4>
    <div class="search-box"><input type="text" id="blog-search" placeholder="e.g. mileage, SALT cap…"><button type="button" aria-label="Search">""" + ICONS["check"] + """</button></div>
  </div>
  <div class="sidebar-box">
    <h4>Browse by Topic</h4>
    <nav class="tag-list">""" + tag_items + """</nav>
  </div>
  <div class="sidebar-box">
    <h4>Reader Favorites</h4>
    <ul class="popular-list">""" + pop_items + """</ul>
  </div>
  <div class="sidebar-box newsletter-box">
    <h4>Tax Season Reminders</h4>
    <p>Get one email before each quarterly deadline. No spam, unsubscribe anytime.</p>
    <form><input type="email" required placeholder="you@email.com"><button type="submit" class="btn btn-amber btn-sm">Notify Me</button></form>
  </div>
</aside>"""

# ---------------------------------------------------------------- BLOG INDEX
def build_blog_index():
    ordered = sorted(ARTICLES, key=lambda a: a["publish_date"], reverse=True)
    items = ""
    for i, a in enumerate(ordered):
        search_blob = " ".join([a["title"], a["dek"], " ".join(a["tags"]), " ".join(a["keywords"])]).lower()
        items += """<div class="blog-list-item" data-search-item="{blob}">
      <div class="num">{n:02d}</div>
      <div>
        <span class="tag" style="font-family:var(--font-mono);font-size:.68rem;text-transform:uppercase;letter-spacing:.06em;color:var(--amber-dark);font-weight:600;">{tag}</span>
        <h3><a href="/blog/{slug}.html">{title}</a></h3>
        <p>{dek}</p>
        <div class="meta"><span>{icon} {mins} min read</span><span>{date}</span></div>
      </div>
    </div>""".format(blob=search_blob, n=i+1, tag=a["primary_tag"], slug=a["slug"], title=a["title"],
                      dek=a["dek"], mins=a["read_minutes"], date=fmt_date(a["publish_date"]), icon="⏱")

    body = """
<section style="padding-top:44px;">
  <div class="container">
    <div class="section-head">
      <span class="eyebrow">The Tax Blog</span>
      <h1 style="font-size:clamp(1.8rem,3vw,2.6rem);">Long-Tail Tax Guides for the Self-Employed</h1>
      <p>%d articles and counting — every one of them cross-linked so you can build a complete picture of your deductions, not just one write-off at a time.</p>
    </div>
    <div class="blog-layout">
      <div>%s</div>
      %s
    </div>
  </div>
</section>
""" % (len(ARTICLES), items, sidebar())

    html = page("Tax Deduction Blog: Freelancer & Gig Economy Tax Guides | " + SITE_NAME,
        "Twenty in-depth, cross-linked tax guides for freelancers, 1099 contractors, Uber/Lyft drivers, real estate agents, and content creators.",
        SITE_URL + "/blog/index.html", body, active="blog")
    with open(os.path.join(BLOG_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)

build_blog_index()
print("blog index built")

# ---------------------------------------------------------------- TAG PAGES
def build_tag_pages():
    for t in TAGS:
        arts = sorted(articles_by_tag(t), key=lambda a: a["publish_date"], reverse=True)
        items = ""
        for i, a in enumerate(arts):
            items += """<div class="blog-list-item">
      <div class="num">{n:02d}</div>
      <div>
        <h3><a href="/blog/{slug}.html">{title}</a></h3>
        <p>{dek}</p>
        <div class="meta"><span>{mins} min read</span><span>{date}</span></div>
      </div>
    </div>""".format(n=i+1, slug=a["slug"], title=a["title"], dek=a["dek"], mins=a["read_minutes"], date=fmt_date(a["publish_date"]))
        body = """
<section style="padding-top:44px;">
  <div class="container">
    <div class="breadcrumbs"><a href="/index.html">Home</a> / <a href="/blog/index.html">Blog</a> / {t}</div>
    <div class="section-head">
      <span class="eyebrow">Topic</span>
      <h1 style="font-size:clamp(1.8rem,3vw,2.4rem);">{t}</h1>
      <p>{n} article{s} tagged &ldquo;{t}&rdquo;.</p>
    </div>
    <div class="blog-layout">
      <div>{items}</div>
      {sb}
    </div>
  </div>
</section>
""".format(t=t, n=len(arts), s="" if len(arts) == 1 else "s", items=items, sb=sidebar(active_tag=t))
        html = page(t + " Articles | Tax Blog | " + SITE_NAME,
            "Browse every " + SITE_NAME + " article tagged " + t + ".",
            SITE_URL + "/blog/tag-" + TAG_SLUGS[t] + ".html", body, active="blog")
        with open(os.path.join(BLOG_DIR, "tag-" + TAG_SLUGS[t] + ".html"), "w", encoding="utf-8") as f:
            f.write(html)

build_tag_pages()
print("tag pages built:", len(TAGS))

# ---------------------------------------------------------------- ARTICLE PAGES
def slugify(text):
    text = re.sub(r"<[^>]+>", "", text)
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s

def inject_toc_ids(html):
    toc = []
    def repl(m):
        inner = m.group(1)
        sid = slugify(inner)
        toc.append((sid, inner))
        return '<h2 id="{}">{}</h2>'.format(sid, inner)
    new_html = re.sub(r"<h2>(.*?)</h2>", repl, html)
    return new_html, toc

def extract_faqs(html):
    pairs = re.findall(r'<summary>(.*?)</summary><p>(.*?)</p>', html, flags=re.S)
    return pairs

def faq_schema(pairs):
    if not pairs:
        return ""
    entities = []
    for q, a in pairs:
        clean_a = re.sub(r"<[^>]+>", "", a).replace('"', '\\"').strip()
        clean_q = re.sub(r"<[^>]+>", "", q).replace('"', '\\"').strip()
        entities.append('{"@type":"Question","name":"%s","acceptedAnswer":{"@type":"Answer","text":"%s"}}' % (clean_q, clean_a))
    return '<script type="application/ld+json">\n{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[%s]}\n</script>' % ",".join(entities)

def article_schema(a):
    return """<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": %s,
  "description": %s,
  "datePublished": "%s",
  "author": {"@type":"Organization","name":"%s"},
  "publisher": {"@type":"Organization","name":"%s"},
  "mainEntityOfPage": "%s/blog/%s.html"
}
</script>""" % (json.dumps(a["title"]), json.dumps(a["meta_description"]), a["publish_date"], SITE_NAME, SITE_NAME, SITE_URL, a["slug"])

def build_article_pages():
    for a in ARTICLES:
        content_with_ids, toc = inject_toc_ids(a["content"])
        pairs = extract_faqs(a["content"])
        schema = article_schema(a) + "\n" + faq_schema(pairs)
        toc_html = "".join('<li><a href="#{id}">{t}</a></li>'.format(id=i, t=t) for i, t in toc)
        related = related_articles(a)
        related_cards = "\n".join(article_card(r) for r in related)

        toolbar = """
    <div class="article-toolbar">
      <div class="toolbar-group">
        <button type="button" class="tool-btn" id="tts-btn"><span aria-hidden="true">🔊</span><span id="tts-label">Listen to this article</span></button>
        <div class="font-ctrl" role="group" aria-label="Adjust text size">
          <button type="button" id="font-dec" aria-label="Decrease text size">A−</button>
          <button type="button" id="font-reset" aria-label="Reset text size">Aa</button>
          <button type="button" id="font-inc" aria-label="Increase text size">A+</button>
        </div>
      </div>
      <div class="toolbar-group">
        <span style="font-family:var(--font-mono);font-size:.76rem;color:var(--ink-faint);">Share:</span>
        """ + share_row() + """
      </div>
    </div>"""

        toc_box = ('<div class="sidebar-box toc-box"><h4>In This Article</h4><ol>' + toc_html + '</ol></div>') if toc else ""

        body = """
<div class="reading-progress"></div>
<section class="article-hero">
  <div class="container">
    <div class="breadcrumbs"><a href="/index.html">Home</a> / <a href="/blog/index.html">Blog</a> / <a href="/blog/tag-{tag_slug}.html">{tag}</a></div>
    <h1>{title}</h1>
    <p class="dek">{dek}</p>
    <div class="article-meta-row">
      <span class="avatar">TT</span>
      <span>Tax Tools Editorial Team</span>
      <span>·</span>
      <span>{date}</span>
      <span>·</span>
      <span>{mins} min read</span>
      <span>·</span>
      <span>{words} words</span>
    </div>
    {toolbar}
  </div>
</section>

<section class="article-layout container">
  <div class="article-body">
    <div class="ad-slot leaderboard"><!-- ADSENSE CONTENT AD HERE --></div>
    {content}
    <div class="disclaimer-box">
      <strong>DISCLAIMER:</strong> This article is for general informational purposes and does not constitute CPA, financial planning, or professional legal tax consulting advice. Tax regulations are subject to regular updates — always cross-verify your final deductions with official IRS documentation or a licensed tax professional before filing.
    </div>
    <div class="author-box">
      <div class="avatar">TT</div>
      <div><h4>Tax Tools Editorial Team</h4><p>We research current IRS guidance and translate it into plain-language, cross-linked guides for freelancers and self-employed filers. Have a correction or a topic request? <a href="/contact.html">Contact us</a>.</p></div>
    </div>

    <hr class="divider-dashed">
    <h3 style="font-size:1.3rem;">Related Reading</h3>
    <div class="related-grid">{related}</div>
  </div>
  <div>
    {toc_box}
    <div class="ad-slot skyscraper" style="margin-top:22px;"><!-- ADSENSE AD REVENUE UNIT --></div>
  </div>
</section>
""".format(tag_slug=TAG_SLUGS[a["primary_tag"]], tag=a["primary_tag"], title=a["title"], dek=a["dek"],
           date=fmt_date(a["publish_date"]), mins=a["read_minutes"], words=a["word_count"],
           toolbar=toolbar, content=content_with_ids, related=related_cards, toc_box=toc_box)

        html = page(a["title"] + " | " + SITE_NAME, a["meta_description"], SITE_URL + "/blog/" + a["slug"] + ".html",
                     body, active="blog", extra_schema=schema)
        with open(os.path.join(BLOG_DIR, a["slug"] + ".html"), "w", encoding="utf-8") as f:
            f.write(html)

build_article_pages()
print("article pages built:", len(ARTICLES))

# ---------------------------------------------------------------- LEGAL PAGES
def build_legal_pages():
    privacy_body = """
<section style="padding-top:44px;">
  <div class="container legal-body">
    <div class="breadcrumbs"><a href="/index.html">Home</a> / Privacy Policy</div>
    <h1>Privacy Policy</h1>
    <p><em>Last updated: August 2026</em></p>
    <h2>1. Data Confidentiality</h2>
    <p>Financial numbers, income data, and tax tracking parameters entered into the 1040 Deduction Calculator on this site remain completely confidential. All calculations are processed locally in your browser — nothing you type into the calculator is transmitted to a server, stored in a database, or logged by us in any form.</p>
    <h2>2. AdSense and Monetization</h2>
    <p>This site is monetized in part through Google AdSense and other third-party advertising vendors. These vendors may use cookies and similar technologies to display ads tailored to your interests based on your visit to this and other websites. You can manage, limit, or disable these cookies at any time in your browser settings, or through Google's Ads Settings.</p>
    <h2>3. Analytics</h2>
    <p>We may use standard web analytics tools to understand aggregate traffic patterns — which pages are read, how long visitors stay, and general geographic and device information. This data is used to improve site content and is not linked to the financial information entered into the calculator, which is never transmitted in the first place.</p>
    <h2>4. Third-Party Links</h2>
    <p>Our site may contain helpful outbound hyperlinks to IRS.gov and other official government or reference resources. We are not responsible for the content, accuracy, or privacy practices of external pages linked from this site.</p>
    <h2>5. Cookies</h2>
    <p>Beyond advertising cookies described above, this site may use minimal functional cookies or local browser storage to remember display preferences you set, such as font size. No personally identifiable financial information is ever stored this way.</p>
    <h2>6. Children's Privacy</h2>
    <p>This site is not directed at children under 13, and we do not knowingly collect personal information from children.</p>
    <h2>7. Changes to This Policy</h2>
    <p>We may update this Privacy Policy periodically to reflect changes in our practices or for legal and regulatory reasons. The "Last updated" date above reflects the most recent revision.</p>
    <h2>8. Contact</h2>
    <p>Questions about this Privacy Policy can be directed to <a href="mailto:privacy@ustaxdeductionfinder.com">privacy@ustaxdeductionfinder.com</a>.</p>
  </div>
</section>"""

    terms_body = """
<section style="padding-top:44px;">
  <div class="container legal-body">
    <div class="breadcrumbs"><a href="/index.html">Home</a> / Terms of Service</div>
    <h1>Terms of Service</h1>
    <p><em>Last updated: August 2026</em></p>
    <h2>1. Platform Overview</h2>
    <p>USTaxDeductionFinder.com offers a free interactive questionnaire and calculator to help taxpayers estimate and audit potential expense deductions, alongside an educational blog covering U.S. tax topics relevant to freelancers, independent contractors, and gig-economy workers.</p>
    <h2>2. Non-Reliance Clause</h2>
    <p>The calculations provided by this engine, and the information published in our blog articles, are estimations and general educational content. They should not be used as the sole foundation for filing formal tax returns. Always cross-verify results with official IRS publications or a licensed tax professional.</p>
    <h2>3. No Liability</h2>
    <p>Under no legal theory — contract, tort, negligence, or otherwise — shall the creators, owners, or operators of this website and software be held responsible for any penalties, interest, audits, or other consequences issued by the IRS or any tax authority to users of this web tool arising from reliance on its output.</p>
    <h2>4. Intellectual Property</h2>
    <p>The user interface, design system, underlying code architecture, and original written content on this site are proprietary properties of USTaxDeductionFinder.com / Tax Tools Media Group. Reproduction or redistribution without permission is prohibited.</p>
    <h2>5. Acceptable Use</h2>
    <p>You agree not to misuse this site, including attempting to disrupt its normal operation, scraping content at scale without permission, or using the calculator to generate misleading results for redistribution as official tax advice.</p>
    <h2>6. Advertising</h2>
    <p>This site displays third-party advertising, including through Google AdSense. Advertisements are served by third parties and their presence does not constitute an endorsement by USTaxDeductionFinder.com of the advertised products or services.</p>
    <h2>7. Changes to These Terms</h2>
    <p>We may revise these Terms of Service at any time. Continued use of the site after changes are posted constitutes acceptance of the revised terms.</p>
    <h2>8. Governing Law</h2>
    <p>These terms are governed by the laws of the State of New York, without regard to conflict-of-law principles.</p>
    <h2>9. Contact</h2>
    <p>Questions about these Terms can be directed to <a href="mailto:info@ustaxdeductionfinder.com">info@ustaxdeductionfinder.com</a>.</p>
  </div>
</section>"""

    disclaimer_body = """
<section style="padding-top:44px;">
  <div class="container legal-body">
    <div class="breadcrumbs"><a href="/index.html">Home</a> / Disclaimer</div>
    <h1>Disclaimer</h1>
    <p><em>Last updated: August 2026</em></p>
    <div class="disclaimer-box" style="margin-top:20px;">
      <strong>DISCLAIMER:</strong> This tool is engineered to estimate tax deductions based on general internal revenue codes (IRS) and public standard filing tax thresholds for the current tax season. It does not constitute certified public accounting (CPA), financial planning, or professional legal tax consulting advice. Tax regulations are subject to regular updates. Always cross-verify your final standard or itemized write-offs with official IRS documentation before submission.
    </div>
    <h2>No Professional Relationship</h2>
    <p>Using this website, its calculator, or reading its blog content does not create a CPA-client, attorney-client, or financial-advisor relationship between you and USTaxDeductionFinder.com, its owners, or its contributors.</p>
    <h2>Estimates Only</h2>
    <p>The 1040 Deduction Calculator uses simplified, hardcoded standard-deduction baselines and general IRS thresholds (such as the $10,000 SALT cap and the 7.5% AGI medical expense floor) for the current tax season. It does not account for every possible credit, phase-out, state-specific rule, or unusual filing circumstance that could apply to your specific situation.</p>
    <h2>Accuracy of Blog Content</h2>
    <p>Our editorial team researches current IRS guidance carefully, but tax law changes frequently, sometimes with limited notice. Figures such as mileage rates, contribution limits, and income thresholds are adjusted periodically by the IRS — always confirm current-year figures directly with the IRS or a licensed tax professional before filing.</p>
    <h2>Your Financial Data</h2>
    <p>All calculator entries are processed locally in your browser and are never transmitted to or stored on our servers. See our full <a href="/legal/privacy-policy.html">Privacy Policy</a> for details.</p>
    <h2>Seek Professional Advice</h2>
    <p>For guidance specific to your situation, we strongly recommend consulting a Certified Public Accountant (CPA), Enrolled Agent, or tax attorney licensed in your state.</p>
  </div>
</section>"""

    pages = [
        ("privacy-policy.html", "Privacy Policy", "How USTaxDeductionFinder.com handles your data, cookies, and advertising.", privacy_body),
        ("terms-of-service.html", "Terms of Service", "The terms governing your use of USTaxDeductionFinder.com and its calculator.", terms_body),
        ("disclaimer.html", "Disclaimer", "Important disclaimers about the estimates provided by USTaxDeductionFinder.com.", disclaimer_body),
    ]
    for fname, title, desc, body in pages:
        html = page(title + " | " + SITE_NAME, desc, SITE_URL + "/legal/" + fname, body)
        with open(os.path.join(LEGAL_DIR, fname), "w", encoding="utf-8") as f:
            f.write(html)

build_legal_pages()
print("legal pages built")

# ---------------------------------------------------------------- CONTACT
def build_contact():
    body = """
<section style="padding-top:44px;">
  <div class="container">
    <div class="breadcrumbs"><a href="/index.html">Home</a> / Contact</div>
    <div class="section-head">
      <span class="eyebrow">Get in Touch</span>
      <h1 style="font-size:clamp(1.8rem,3vw,2.4rem);">Contact Us</h1>
      <p>Need technical support with our tax calculator, spotted an error in an article, or looking to purchase dedicated financial ad placement during the tax season peak? Reach out below.</p>
    </div>
    <div class="contact-grid">
      <form class="contact-form" onsubmit="return handleContactSubmit(event)">
        <div><label for="c-name">Name</label><input type="text" id="c-name" required></div>
        <div><label for="c-email">Email</label><input type="email" id="c-email" required></div>
        <div><label for="c-topic">Topic</label>
          <select id="c-topic">
            <option>General Support</option>
            <option>Calculator Bug Report</option>
            <option>Content Correction</option>
            <option>Advertising / Ad Sales</option>
            <option>Press / Media</option>
          </select>
        </div>
        <div><label for="c-message">Message</label><textarea id="c-message" required></textarea></div>
        <button type="submit" class="btn btn-primary">Send Message</button>
        <p class="small-note" id="contact-confirm" style="display:none;color:var(--forest-dark);font-weight:600;">Thanks — your message has been queued. We reply within 1–2 business days.</p>
        <p class="small-note">This form is a static demo. Connect it to Formspree, Resend, or your preferred form backend before going live — see the project README.</p>
      </form>
      <div class="contact-info-card">
        <h3>Direct Contact</h3>
        <div class="contact-info-row">""" + ICONS["mail"] + """<div><strong style="display:block;color:#fff;">General Support</strong><a href="mailto:info@ustaxdeductionfinder.com">info@ustaxdeductionfinder.com</a></div></div>
        <div class="contact-info-row">""" + ICONS["mail"] + """<div><strong style="display:block;color:#fff;">Ad Sales</strong><a href="mailto:corporate-ads@ustaxdeductionfinder.com">corporate-ads@ustaxdeductionfinder.com</a></div></div>
        <div class="contact-info-row">""" + ICONS["mail"] + """<div><strong style="display:block;color:#fff;">Privacy Inquiries</strong><a href="mailto:privacy@ustaxdeductionfinder.com">privacy@ustaxdeductionfinder.com</a></div></div>
        <div class="contact-info-row">""" + ICONS["pin"] + """<div><strong style="display:block;color:#fff;">Office</strong>Tax Tools Media Group<br>New York, NY, USA</div></div>
        <div class="contact-info-row">""" + ICONS["clock"] + """<div><strong style="display:block;color:#fff;">Response Time</strong>1–2 business days (faster during tax season)</div></div>
      </div>
    </div>
  </div>
</section>
<script>
function handleContactSubmit(e){
  e.preventDefault();
  document.getElementById('contact-confirm').style.display = 'block';
  e.target.reset();
  return false;
}
</script>
"""
    html = page("Contact Us | " + SITE_NAME, "Contact USTaxDeductionFinder.com for support, corrections, or advertising inquiries.",
                 SITE_URL + "/contact.html", body, active="contact")
    with open(os.path.join(OUT, "contact.html"), "w", encoding="utf-8") as f:
        f.write(html)

build_contact()
print("contact built")

# ---------------------------------------------------------------- 404
def build_404():
    body = """
<section style="padding: 90px 0; text-align:center;">
  <div class="container">
    <span class="eyebrow">Error 404</span>
    <h1 style="font-size:3rem;">This page got audited.</h1>
    <p style="color:var(--ink-muted); max-width:520px; margin:0 auto 26px;">We couldn't find the page you were looking for. It may have been moved, renamed, or never existed — much like an unsubstantiated deduction.</p>
    <div class="hero-ctas" style="justify-content:center;">
      <a href="/index.html" class="btn btn-primary">Back to Home</a>
      <a href="/blog/index.html" class="btn btn-outline">Browse the Blog</a>
    </div>
  </div>
</section>"""
    html = page("Page Not Found | " + SITE_NAME, "The page you requested could not be found.", SITE_URL + "/404.html", body)
    with open(os.path.join(OUT, "404.html"), "w", encoding="utf-8") as f:
        f.write(html)

build_404()
print("404 built")

# ---------------------------------------------------------------- SITEMAP & ROBOTS
def build_sitemap_robots():
    urls = ["/index.html", "/blog/index.html", "/contact.html",
            "/legal/privacy-policy.html", "/legal/terms-of-service.html", "/legal/disclaimer.html"]
    urls += ["/blog/" + a["slug"] + ".html" for a in ARTICLES]
    urls += ["/blog/tag-" + TAG_SLUGS[t] + ".html" for t in TAGS]
    body = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for u in urls:
        body += "  <url><loc>{}{}</loc></url>\n".format(SITE_URL, u)
    body += "</urlset>\n"
    with open(os.path.join(OUT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(body)

    robots = """User-agent: *
Allow: /

Sitemap: {url}/sitemap.xml
""".format(url=SITE_URL)
    with open(os.path.join(OUT, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(robots)

build_sitemap_robots()
print("sitemap + robots built. total urls:", 6 + len(ARTICLES) + len(TAGS))
