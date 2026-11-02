#!/usr/bin/env python3
"""Build the Risk Governance Group static site.

Run from the repo root:  python3 tools/build.py
Writes the HTML pages into the repo root (what Vercel serves) and a .html-linked copy into _preview/.
styles.css and assets/ are the source of truth at the repo root; the build does not touch them.
"""
import os, re, shutil, html, json

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)            # repo root = site root (Vercel serves this)
SITE = ROOT
PREVIEW = os.path.join(ROOT, "_preview")  # .html links, for the Claude artifact preview; gitignored

BASE = "https://riskgg.com/"
EMAIL = "info@riskgg.com"
PHONE_DISPLAY = "203-442-4114"
PHONE_TEL = "+12034424114"
LINKEDIN = "https://www.linkedin.com/in/brian-allen-esq-93a1545/"
BOOKING = "https://calendar.app.google/1QkTQTcaoQQRDGSk6"

NAV = [
    ("ai-oversight.html", "AI oversight"),
    ("cyber-operational-risk.html", "Cyber and operational risk"),
    ("team.html", "Team"),
    ("body-of-work.html", "Body of work"),
    ("perspectives.html", "Perspectives"),
]

FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600;700;800&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400&display=swap" rel="stylesheet">'

FAVICON = '<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">\n<link rel="apple-touch-icon" href="assets/apple-touch-icon.png">\n<meta name="theme-color" content="#11144B">'

HOME_DESC = "Risk Governance Group helps boards and executives build and mature AI oversight and risk governance programs they can defend."

HOME_JSON_LD = json.dumps({
    "@context": "https://schema.org",
    "@type": "ProfessionalService",
    "name": "Risk Governance Group",
    "legalName": "Risk Governance Group, LLC",
    "url": "https://riskgg.com/",
    "email": "info@riskgg.com",
    "telephone": "+1-203-442-4114",
    "address": {
        "@type": "PostalAddress",
        "addressRegion": "CT",
        "addressCountry": "US"
    },
    "areaServed": "US",
    "description": HOME_DESC,
    "founder": {
        "@type": "Person",
        "name": "Brian J. Allen",
        "jobTitle": "Chief Executive Officer",
        "url": "https://riskgg.com/team",
        "sameAs": [
            "https://www.linkedin.com/in/brian-allen-esq-93a1545/"
        ]
    }
})

def wordmark(white=False):
    cls = "wordmark wordmark-white" if white else "wordmark"
    return (f'<a href="index.html" class="{cls}" aria-label="Risk Governance Group home">'
            f'<span class="wm-top"><span class="wm-risk">RISK</span><span class="wm-gg">GG</span></span>'
            f'<span class="wm-sub">Risk Governance Group</span></a>')

def header(active):
    links = "".join(
        f'<a href="{href}"{" class=\"active\" aria-current=\"page\"" if href == active else ""}>{label}</a>'
        for href, label in NAV)
    return f'''<header class="site-header">
  <div class="wrap header-inner">
    {wordmark()}
    <nav class="nav nav-desktop" aria-label="Primary">
      {links}
      <a href="contact.html" class="btn btn-solid btn-nav">Talk to us</a>
    </nav>
    <details class="menu">
      <summary aria-label="Menu">Menu</summary>
      <nav class="nav nav-mobile" aria-label="Mobile Primary">
        {links}
        <a href="contact.html" class="btn btn-solid btn-nav">Talk to us</a>
      </nav>
    </details>
  </div>
</header>'''

FOOTER = f'''<footer class="site-footer">
  <div class="wrap footer-grid">
    <div class="footer-brand">
      {wordmark(white=True)}
      <p>We help boards and executives build and mature AI oversight and risk governance programs they can defend.</p>
    </div>
    <div>
      <h2>What we do</h2>
      <a href="ai-oversight.html">AI oversight and risk governance</a>
      <a href="cyber-operational-risk.html">Cyber and operational risk programs</a>
    </div>
    <div>
      <h2>Firm</h2>
      <a href="team.html">Team</a>
      <a href="body-of-work.html">Body of work</a>
      <a href="perspectives.html">Perspectives</a>
      <a href="contact.html">Contact</a>
    </div>
    <div>
      <h2>Reach us</h2>
      <a href="mailto:{EMAIL}">{EMAIL}</a>
      <a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a>
      <a href="{LINKEDIN}" rel="noopener">Brian Allen on LinkedIn</a>
    </div>
    <div class="footer-legal">
      <span>Brian Allen also founded the <a href="https://cfaio.org" rel="noopener">Center for AI Oversight</a>, an independent 501(c)(3) research organization. The Center is a separate entity and does not endorse Risk Governance Group services.</span>
      <div class="footer-copy"><span>Copyright 2026 Risk Governance Group, LLC. All rights reserved.</span><a href="privacy.html">Privacy policy</a><a href="terms.html">Terms of use</a></div>
    </div>
  </div>
</footer>'''

def clean_slug(path):
    if path == "index.html":
        return ""
    if path.endswith("/index.html"):
        return path[:-11]
    if path.endswith(".html"):
        return path[:-5]
    return path

def head(title, description, path):
    t = html.escape(title); d = html.escape(description)
    slug = clean_slug(path)
    url = BASE + slug
    is_404 = (path == "404.html")
    robots = '\n<meta name="robots" content="noindex">' if is_404 else ""
    canon = "" if is_404 else f'\n<link rel="canonical" href="{url}">'
    og_url = "" if is_404 else f'\n<meta property="og:url" content="{url}">'
    ld_script = f'\n<script type="application/ld+json">{HOME_JSON_LD}</script>' if path == "index.html" else ""
    return f'''<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{t}</title>
<meta name="description" content="{d}">{robots}{canon}
<meta property="og:type" content="website">
<meta property="og:site_name" content="Risk Governance Group">
<meta property="og:title" content="{t}">
<meta property="og:description" content="{d}">{og_url}
<meta property="og:image" content="{BASE}assets/og-image.png">
<meta name="twitter:card" content="summary_large_image">
{FONTS}
<link rel="stylesheet" href="styles.css">
{FAVICON}{ld_script}'''

def page(path, title, description, body, active=None):
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
{head(title, description, path)}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
{header(active)}
<main id="main">
{body}
</main>
{FOOTER}
</body>
</html>
'''

# ---------------------------------------------------------------- shared bits

def cta(heading="If your board is asking what it should be asking about AI, start here.",
        text="A first conversation is 30 minutes with a senior member of our team. We listen to where you are and tell you plainly what we would look at first."):
    return f'''<section class="band band-navy cta">
  <div class="wrap cta-inner">
    <h2>{heading}</h2>
    <p>{text}</p>
    <div class="btn-row"><a href="{BOOKING}" rel="noopener" class="btn btn-blue">Book 30 minutes</a><a href="contact.html" class="btn btn-ghost-light">Talk to us</a></div>
  </div>
</section>'''

LAYERS_HTML = '''<figure class="layers" aria-label="The three layers of AI governance">
  <div class="layers-body">
    <div class="layers-rail" aria-hidden="true">
      <span class="layers-rail-text">Direction cascades down</span>
      <span class="layers-rail-arrow">&#8595;</span>
    </div>
    <ol class="layers-list">
      <li class="layer-card layer-oversight">
        <div class="layer-top">
          <span class="layer-label">Oversight governance</span>
          <span class="layer-start">Where we start</span>
        </div>
        <p class="layer-line">What is governed. Who is accountable.</p>
        <p class="layer-detail">Charter, named accountability, tolerance, authority to operate, the record.</p>
      </li>
      <li class="layer-card layer-management">
        <div class="layer-top">
          <span class="layer-label">Management</span>
        </div>
        <p class="layer-line">The activity, not the rank.</p>
        <p class="layer-detail">Objectives, policy, risk assessment and treatment, vendors, training, response.</p>
      </li>
      <li class="layer-card layer-technical">
        <div class="layer-top">
          <span class="layer-label">Technical controls</span>
        </div>
        <p class="layer-line">What the system does.</p>
        <p class="layer-detail">Security, data, model validation, guardrails, access, logging, fail safe logic.</p>
      </li>
    </ol>
  </div>
  <figcaption class="layers-caption">We work at all three layers. Oversight first, because the layers below cannot supply it.</figcaption>
</figure>'''

def card_research():
    return f'''<section class="band band-light">
  <div class="wrap">
    <div class="section-head">
      <div>
        <div class="eyebrow">Research we cite</div>
        <h2>Published research on board-level AI oversight</h2>
        <p>Brian Allen's research on AI oversight is published by the Center for AI Oversight, an independent 501(c)(3) he founded. We cite it the way we cite any published source. These links open on the Center's site.</p>
      </div>
      <a href="https://cfaio.org/insights" rel="noopener" class="link-strong">All research at cfaio.org/insights &#8599;</a>
    </div>
    <div class="cards-3">
      <a href="https://cfaio.org/is-ai-mission-critical" rel="noopener" class="card">
        <span class="card-kicker">Center paper</span>
        <span class="card-title">Is AI Mission Critical?</span>
        <span class="card-text">Which uses of AI create a board oversight duty, and what the board's record should show.</span>
        <span class="card-link">Read at cfaio.org &#8599;</span>
      </a>
      <a href="https://cfaio.org/the-ai-oversight-governance-layer" rel="noopener" class="card">
        <span class="card-kicker">Center paper</span>
        <span class="card-title">The AI Oversight Governance Layer</span>
        <span class="card-text">Three layers of governance operate in any organization deploying AI. The oversight layer, which decides what is governed, at what granularity, and who is accountable, is usually missing.</span>
        <span class="card-link">Read at cfaio.org &#8599;</span>
      </a>
      <a href="https://cfaio.org/committee-fallacy-anatomy" rel="noopener" class="card">
        <span class="card-kicker">Center paper</span>
        <span class="card-title">The Committee Fallacy</span>
        <span class="card-text">Assigning AI risk to a committee is not governing it. Why the Delaware doctrine demands a program, not just a venue.</span>
        <span class="card-link">Read at cfaio.org &#8599;</span>
      </a>
    </div>
  </div>
</section>'''

# ---------------------------------------------------------------- pages

INDEX = f'''<section class="hero">
  <div class="wrap hero-grid">
    <div class="hero-copy">
      <h1>Move fast on AI, with oversight you can defend.</h1>
      <p class="lede">Risk Governance Group helps boards and executives build and mature the oversight and risk governance programs that let them take risk on AI with confidence.</p>
      <div class="btn-row"><a href="#how-we-work" class="btn btn-solid">How we work</a><a href="{BOOKING}" rel="noopener" class="btn btn-outline">Book 30 minutes</a></div>
    </div>
    <aside class="hero-aside">
      <p class="aside-title">Who we work with</p>
      <span>Boards, audit and risk committees</span>
      <span>CEOs and general counsel</span>
      <span>Chief risk and chief audit executives</span>
      <span>Financial services, insurance, healthcare, critical infrastructure</span>
      <span>Companies that sell AI into regulated markets</span>
    </aside>
  </div>
  <div class="wrap">{LAYERS_HTML}</div>
</section>

<section class="band">
  <div class="wrap">
    <h2 class="h2-narrow">The gap regulators, courts, and shareholders are now looking at</h2>
    <p class="measure muted">AI is moving faster than the governance around it. Most organizations have policies, committees, and technical controls. Few can show, at the board and executive level, who is accountable for what, how decisions get made, and why those decisions were informed. We close that gap.</p>
  </div>
</section>

<section id="how-we-work" class="band band-tight">
  <div class="wrap">
    <div class="eyebrow">How we work</div>
    <h2>Three engagements. One program.</h2>
    <p class="measure muted">Every engagement is scoped to one of these, led by Brian Allen, and delivered by senior practitioners assembled for it. Each one states which layer of governance it addresses.</p>
    <div class="steps">
      <div class="step"><span class="step-n">1</span><div class="eng-head"><h3>Assess</h3><span class="layer-tag">Oversight layer</span></div><p>We measure where your oversight program stands today against what regulators, case law, and standards now expect of boards and executives. You get a plain statement of what exists, what is missing, and what matters most.</p></div>
      <div class="step"><span class="step-n">2</span><div class="eng-head"><h3>Build</h3><span class="layer-tag">Oversight and management layers</span></div><p>We help you stand up the program: the charter, the accountable roles, the reporting cadence, the risk tolerances, and the escalation paths that turn oversight from a committee into a working system.</p></div>
      <div class="step"><span class="step-n">3</span><div class="eng-head"><h3>Mature</h3><span class="layer-tag">Oversight layer</span></div><p>We stay with you as the program grows, so oversight keeps pace with how fast your organization is adopting AI, and your board can show it made informed decisions at every step.</p></div>
    </div>
    <div class="btn-row"><a href="ai-oversight.html" class="btn btn-outline">AI oversight and risk governance</a><a href="cyber-operational-risk.html" class="btn btn-outline">Cyber and operational risk programs</a></div>
  </div>
</section>

<section class="band">
  <div class="wrap split">
    <div>
      <div class="eyebrow">Why it matters</div>
      <h2>Mature oversight is how you move faster</h2>
      <p class="muted">Most organizations are putting AI on top of the governance processes they built for cyber: built for protection, slow to approve, focused on what can go wrong. That cannot keep pace with AI. When governance is only compliance and downside, the business routes around it, or it stalls. Moving slowly is a risk too. A competitor that moves faster can take your place.</p>
    </div>
    <div class="list-grid">
      <div><h3>Tolerances are decision points</h3><p>A tolerance set by the board tells your people how far they can go without asking. Clear tolerances let decisions happen faster.</p></div>
      <div><h3>Escalation by design</h3><p>A risk outside tolerance should reach the right person before it becomes an incident, through a defined path rather than through relationships.</p></div>
      <div><h3>Decision-making AI needs this most</h3><p>As agents begin acting without approval of every step, the question shifts from whether a human touched the decision to whether the process around it was adequate.</p></div>
      <div><h3>The program outlasts the technology</h3><p>Ad hoc controls turn every new use case into a scramble. A chartered program, built from the oversight layer down, holds steady as the technology changes.</p></div>
    </div>
  </div>
</section>

<section class="band band-navy statement">
  <div class="wrap statement-inner">
    <p class="statement-big">The goal is not the right decision every time. The goal is an informed decision, made through a process you can defend at the scale of the risk.</p>
    <p class="statement-small">We call this the Informed Decision Standard. Every engagement is built to meet it.</p>
  </div>
</section>

<section class="band">
  <div class="wrap split">
    <div>
      <div class="eyebrow">Who we are</div>
      <h2>A firm built from people who have held your roles</h2>
      <p>Risk Governance Group is deliberately small and deliberately senior. Every engagement is led by Brian Allen, former Fortune 100 Chief Security Officer and former head of emerging technology risk at the Bank Policy Institute, and delivered by practitioners who have served as chief risk officers, chief information security officers, chief audit executives, regulators, and policy leaders.</p>
      <p>We assemble the team to fit the engagement and we name it in every proposal. Clients work with people who have done the work, not a bench of analysts.</p>
      <div class="btn-row"><a href="team.html" class="btn btn-outline">Meet the team</a></div>
    </div>
    <div class="roles">
      <div><b>Chief Risk Officers</b><span>Enterprise risk appetite, tolerances, and board reporting</span></div>
      <div><b>Chief Information Security Officers</b><span>Cyber and technology risk programs in regulated institutions</span></div>
      <div><b>Chief Audit Executives</b><span>Assurance, controls testing, and audit committee practice</span></div>
      <div><b>Former regulators</b><span>How supervisors and examiners read an oversight program</span></div>
      <div><b>Policy leaders</b><span>Where AI regulation and standards are heading</span></div>
    </div>
  </div>
</section>

{card_research()}

<section class="band">
  <div class="wrap split">
    <h2>Where the discipline came from</h2>
    <div>
      <p>We built our practice on cyber and operational risk programs for regulated institutions. That work continues. The oversight lessons from cyber carry over to AI: named accountability, a tolerance the board sets, and a reporting line that does not wait for an incident. The cyber operating model, built to protect and slow to approve, does not. AI needs those lessons on a much shorter clock.</p>
      <div class="btn-row"><a href="cyber-operational-risk.html" class="btn btn-outline">Cyber and operational risk programs</a></div>
    </div>
  </div>
</section>

{cta()}'''

AI_OVERSIGHT = f'''<section class="page-hero">
  <div class="wrap">
    <div class="eyebrow">Layer: oversight governance, with the management-layer build the program needs</div>
    <h1>AI oversight and risk governance</h1>
    <p class="lede">What is governed, who is accountable, and the record that shows the board made an informed decision. We build the program that answers those questions and keeps answering them as AI adoption accelerates.</p>
  </div>
</section>

<section class="band">
  <div class="wrap">
    <h2>What we do</h2>
    <div class="engagements">
      <div class="engagement">
        <div class="eng-head"><h3>Oversight assessment</h3><span class="layer-tag">Oversight layer</span></div>
        <p>About a dozen senior interviews over three to four weeks. No technical testing. You get a plain statement of what exists, what is missing, and what matters most, measured against what regulators, case law, and standards now expect of boards and executives.</p>
        <p class="muted small">Output: current state of the oversight program, findings, target state, a roadmap at 90 days, 6 months and 12 months, and a board reporting framework.</p>
      </div>
      <div class="engagement">
        <div class="eng-head"><h3>Program build</h3><span class="layer-tag">Oversight and management layers</span></div>
        <p>We stand up the program with you. At the oversight layer: the charter, named accountability at the committee and officer level, risk tolerance ratified where it belongs, a bounded and expiring authority to operate for any system that acts without a person in the loop, the reporting and escalation line, independent assurance, and the competency to interrogate what gets reported.</p>
        <p>At the management layer: the policies, tolerance statements, indicators, and board dashboard that operate it day to day.</p>
      </div>
      <div class="engagement">
        <div class="eng-head"><h3>Annual re-assessment and the watch</h3><span class="layer-tag">Oversight layer</span></div>
        <p>The program is re-examined each year so board oversight disclosures stay defensible. Between assessments we track the case law, regulation, and standards that change what defensible means, by geography and by industry, and tell you what has changed and what it requires of you.</p>
      </div>
    </div>
  </div>
</section>

<section class="band band-light">
  <div class="wrap split">
    <div>
      <div class="eyebrow">What the board should be able to answer</div>
      <h2>Six questions only the oversight layer answers</h2>
      <p class="muted">Every control in the layers beneath can be in place and none of them answers these, because each is a decision about accountability, not a control. Drawn from <a href="https://cfaio.org/the-ai-oversight-governance-layer" rel="noopener">The AI Oversight Governance Layer</a>, published by the Center for AI Oversight.</p>
    </div>
    <ol class="questions">
      <li><b>The program.</b> Have we chartered an AI oversight program, and does the record show which standards we elected to apply, how far, and who decided?</li>
      <li><b>The accountability.</b> Which committee holds oversight by charter, which officer answers to it by name, and what have we allowed to sit outside it, accepted by whom?</li>
      <li><b>The tolerance.</b> Did we set the boundaries of acceptable AI risk in advance, on a stated basis, and ratify them, or were they set by default?</li>
      <li><b>The authority.</b> What operates without a person in the loop, under what limits, until when, and who can withdraw it?</li>
      <li><b>The line.</b> Do escalation and disclosure reach us on triggers fixed in advance, by at least one path that does not depend on management's discretion?</li>
      <li><b>The record.</b> When a regulator, court, or auditor asks, can we show the informed decision, the report we received, what we did with it, and that someone independent confirmed the program did what it said?</li>
    </ol>
  </div>
</section>

<section class="band">
  <div class="wrap split">
    <div>
      <h2>How a finding reads</h2>
      <p class="muted">Every finding we deliver has the same five parts. A board member can read it in a minute and know what to do with it.</p>
    </div>
    <div class="finding">
      <div><b>Observation</b><span>What we saw, stated plainly.</span></div>
      <div><b>Evidence</b><span>The document, interview, or record it rests on.</span></div>
      <div><b>Why it matters</b><span>The regulatory, legal, or operational consequence.</span></div>
      <div><b>Recommendation</b><span>What to do, sized to the risk.</span></div>
      <div><b>Owner and timing</b><span>Who does it and by when.</span></div>
    </div>
  </div>
</section>

<section class="band band-tight">
  <div class="wrap split">
    <h2>Most organizations buy AI. The duty is the same.</h2>
    <div>
      <p>A few organizations build models. Most put AI to work embedded in products, platforms, and vendors they already use. The oversight duty is the same in kind: who authorized it, under what limits, and who answers when it is examined. We build programs for both, and we are clear about which one you are.</p>
    </div>
  </div>
</section>

{cta()}'''

CYBER = f'''<section class="page-hero">
  <div class="wrap">
    <div class="eyebrow">Layers: oversight governance and management</div>
    <h1>Cyber and operational risk programs</h1>
    <p class="lede">The programs that made cyber governance defensible, built for boards that answer for it. This is where our practice started and the work continues.</p>
  </div>
</section>

<section class="band">
  <div class="wrap">
    <h2>What we do</h2>
    <div class="engagements">
      <div class="engagement">
        <div class="eng-head"><h3>Cyber risk management program</h3><span class="layer-tag">Oversight and management layers</span></div>
        <p>A defined, documented program that puts cyber risk where regulators, courts, and disclosure rules now expect it: owned at the top, measured against a tolerance the board set, and reported on a cadence that does not depend on an incident. Built on the approach set out in <em>Building a Cyber Risk Management Program</em> (O'Reilly Media, 2023).</p>
      </div>
      <div class="engagement">
        <div class="eng-head"><h3>Enterprise security risk management</h3><span class="layer-tag">Management layer</span></div>
        <p>Security run as a risk discipline rather than a set of tasks. Physical, cyber, and continuity risk managed in one life cycle, with business owners deciding what risk to accept and security showing them what it costs. Based on <em>Enterprise Security Risk Management: Concepts and Applications</em> (Rothstein Publishing, 2017).</p>
      </div>
      <div class="engagement">
        <div class="eng-head"><h3>Operational resilience</h3><span class="layer-tag">Oversight and management layers</span></div>
        <p>The services that matter most, the tolerances for their disruption, the dependencies that can break them, and the evidence that you have tested the plan. Scoped for institutions that answer to a supervisor for it.</p>
      </div>
      <div class="engagement">
        <div class="eng-head"><h3>Board reporting on cyber and technology risk</h3><span class="layer-tag">Oversight layer</span></div>
        <p>What the board receives, how often, and what it does with it. We design the reporting line so directors can show they oversaw the risk and so management's disclosures rest on a program rather than a narrative.</p>
      </div>
    </div>
  </div>
</section>

<section class="band band-light">
  <div class="wrap split">
    <h2>Where it came from</h2>
    <div>
      <p>Brian Allen ran security and enterprise risk at Time Warner Cable, a Fortune 100 company, and later worked with the largest U.S. banks on technology risk at the Bank Policy Institute. He was appointed by the Chairman of the Federal Communications Commission to work with NIST on the development of the Cybersecurity Framework and has served in the Communications Information Sharing and Analysis Center and the Communications Sector Coordinating Council.</p>
      <p>The lesson from cyber is the one AI is repeating. The control frameworks matured first, the oversight layer went unbuilt, and it took a decade for regulators and courts to close the gap. We built our cyber practice closing it. We built our AI practice so clients do not wait a decade.</p>
      <div class="btn-row"><a href="ai-oversight.html" class="btn btn-outline">AI oversight and risk governance</a></div>
    </div>
  </div>
</section>

{cta("If your cyber program is a set of controls and a slide, start here.", "A first conversation is 30 minutes with a senior member of our team. We listen to where you are and tell you plainly what we would look at first.")}'''

TEAM = f'''<section class="page-hero">
  <div class="wrap">
    <h1>Team</h1>
    <p class="lede">Every engagement is led by Brian Allen and delivered by senior practitioners assembled for it. We name the team in every proposal.</p>
  </div>
</section>

<section class="band">
  <div class="wrap split">
    <div>
      <h2>How we staff an engagement</h2>
      <p class="muted">We are deliberately small. That is a choice about who sits in the room with your board, not a limit on what we can take on.</p>
    </div>
    <div class="list-grid">
      <div><h3>Led by a principal</h3><p>Brian Allen leads every engagement and is in every working session. There is no handoff to a delivery team you have not met.</p></div>
      <div><h3>Built to fit</h3><p>We assemble two to four practitioners for each engagement from a group who have run risk, security, audit, and supervisory functions inside regulated institutions.</p></div>
      <div><h3>Named in the proposal</h3><p>Every proposal names the people who will do the work, what each has done, and what each will do for you.</p></div>
      <div><h3>No bench</h3><p>Nobody on an engagement is learning the job on your time. If a question needs a specialist we do not have, we say so and we find one.</p></div>
    </div>
  </div>
</section>

<section class="band band-tight">
  <div class="wrap">
    <h2>Who you work with</h2>
    <p class="muted measure">Our practitioners have served as:</p>
    <div class="roles roles-wide">
      <div><b>Chief Risk Officers</b><span>They set enterprise risk appetite and tolerances and report to boards on whether the organization is operating within them.</span></div>
      <div><b>Chief Information Security Officers</b><span>They built and ran cyber and technology risk programs under regulatory scrutiny.</span></div>
      <div><b>Chief Audit Executives</b><span>They provided independent assurance to audit committees and know what evidence holds up.</span></div>
      <div><b>Former regulators</b><span>They examined institutions and know how supervisors read an oversight program.</span></div>
      <div><b>Policy leaders</b><span>They have worked on AI and technology policy with industry groups, standards bodies, and government.</span></div>
    </div>
  </div>
</section>

<section class="band band-light">
  <div class="wrap">
    <div class="eyebrow">Leadership</div>
    <div class="bio-grid">
      <div class="portrait"><img src="assets/brian-allen.jpg" alt="Brian J. Allen" width="800" height="1000"></div>
      <div>
        <h2>Brian J. Allen, Esq.</h2>
        <div class="bio-title">Chief Executive Officer, Risk Governance Group</div>
        <p>Brian Allen has spent his career on the side of the table where risk decisions get made. He served as Chief Security Officer and led Enterprise Risk Management at Time Warner Cable, a Fortune 100 company, and later as Senior Vice President of Emerging Technology Risk Management at the Bank Policy Institute, where he worked with the largest U.S. banks on the governance of AI and other emerging technologies. He founded the Center for AI Oversight, an independent nonprofit research and education organization that defines oversight governance for AI in regulated industries.</p>
        <p>He is the author of <em>Building a Cyber Risk Management Program</em> (O'Reilly Media, 2023), co-author with Rachelle Loyear of <em>Enterprise Security Risk Management: Concepts and Applications</em> (Rothstein Publishing, 2017), and lead author of the forthcoming <em>The AI Risk Compendium</em>. He has delivered keynote addresses and speaks globally on risk governance.</p>
        <div class="cred-grid">
          <div><b>Bank Policy Institute</b>SVP, Emerging Technology Risk Management</div>
          <div><b>Time Warner Cable</b>Chief Security Officer; Enterprise Risk Management</div>
          <div><b>NIST</b>AI Safety Institute Consortium member</div>
          <div><b>University of Connecticut</b>Adjunct Professor, MBA Financial Risk Management</div>
          <div><b>Ampliwork</b>Chief Trust Advisor</div>
          <div><b>New York State Bar</b>Admitted 2003</div>
        </div>
        <div class="btn-row"><a href="{LINKEDIN}" rel="noopener" class="btn btn-outline">Brian on LinkedIn</a><a href="body-of-work.html" class="btn btn-outline">Body of work</a></div>
      </div>
    </div>
  </div>
</section>

{cta()}'''

BODY_OF_WORK = f'''<section class="page-hero">
  <div class="wrap">
    <h1>Body of work</h1>
    <p class="lede">Books, public work, and research that set out how we think about risk governance. All of it is in print or on the record.</p>
  </div>
</section>

<section class="band">
  <div class="wrap">
    <h2>Books</h2>
    <div class="books">
      <a href="https://www.oreilly.com/library/view/-/9781098147785/" rel="noopener" class="book">
        <span class="card-kicker">O'Reilly Media, 2023</span>
        <span class="card-title">Building a Cyber Risk Management Program: Evolving Security for the Digital Age</span>
        <span class="card-text">Brian Allen, Brandon Bapst, and Terry Allan Hicks. A detailed framework for designing, developing, and implementing a cyber risk management program, written for directors, senior executives, risk practitioners, and auditors.</span>
        <span class="card-link">At O'Reilly &#8599;</span>
      </a>
      <a href="https://www.asisonline.org/publications/enterprise-security-risk-management/" rel="noopener" class="book">
        <span class="card-kicker">Rothstein Publishing, 2017</span>
        <span class="card-title">Enterprise Security Risk Management: Concepts and Applications</span>
        <span class="card-text">Brian Allen and Rachelle Loyear. The step by step guide to managing every security risk, physical, cyber, and continuity, through one risk discipline with business owners making the decisions.</span>
        <span class="card-link">At ASIS International &#8599;</span>
      </a>
      <div class="book book-static">
        <span class="card-kicker">Forthcoming</span>
        <span class="card-title">The AI Risk Compendium</span>
        <span class="card-text">Brian Allen, lead author, with five co-authors. A reference on the risks that come with putting AI to work and the governance that answers for them.</span>
      </div>
    </div>
  </div>
</section>

<section class="band band-light">
  <div class="wrap split">
    <h2>Public and industry work</h2>
    <div class="list-grid">
      <div><h3>NIST Cybersecurity Framework</h3><p>Appointed by the Chairman of the Federal Communications Commission to work with NIST on the development of the Cybersecurity Framework.</p></div>
      <div><h3>NIST AI Safety Institute Consortium</h3><p>Member of the consortium convened by NIST to develop measurement and evaluation practice for AI.</p></div>
      <div><h3>Communications sector</h3><p>Communications Information Sharing and Analysis Center and the Communications Sector Coordinating Council.</p></div>
      <div><h3>Bank Policy Institute</h3><p>Worked with the largest U.S. banks on the governance of AI and other emerging technologies, and represented the industry before regulators and legislators.</p></div>
      <div><h3>University of Connecticut</h3><p>Adjunct Professor in the MBA Financial Risk Management program, teaching cyber risk and enterprise risk management.</p></div>
      <div><h3>Speaking</h3><p>Brian Allen has delivered keynote addresses and speaks globally on risk governance. For speaking inquiries, <a href="contact.html">contact us</a>.</p></div>
    </div>
  </div>
</section>

{card_research()}

{cta()}'''

PDF = "assets/pdf/"
ARTICLES = [
    ("Book", "Building a Cyber Risk Management Program: Evolving Security for the Digital Age", "https://www.oreilly.com/library/view/-/9781098147785/", "O'Reilly Media, 2023. A detailed framework for designing, developing, and implementing a cyber risk management program."),
    ("Book", "Enterprise Security Risk Management: Concepts and Applications", "https://www.asisonline.org/publications/enterprise-security-risk-management/", "Rothstein Publishing, 2017. Why security and business interests drift apart, and how a risk discipline brings them back together."),
    ("Bank Policy Institute, 2024", "Navigating Artificial Intelligence in Banking", "https://bpi.com/navigating-artificial-intelligence-in-banking/", "How banking organizations deploy new technologies while continuing to operate in a safe and sound manner. Written while Brian Allen was SVP of Emerging Technology Risk Management at BPI; published under the BPI staff byline."),
    ("CSO Online", "New risk management framework helps with SEC mandate compliance", "https://www.csoonline.com/article/1284801/new-risk-management-framework-helps-with-sec-mandate-compliance.html", "The authors of the Cyber Risk Management Program framework on meeting SEC and other disclosure and reporting rules."),
    ("Security Management", "A Professional Path", PDF + "A-Professional-Path-Security-Management-2017.pdf", "Enterprise security risk management raises security from a task-bound trade to a business driver in the C-suite. PDF, September 2017."),
]

def article_rows():
    out = []
    for cat, title, href, blurb in ARTICLES:
        rel = ' rel="noopener"' if href.startswith("http") else ""
        out.append(f'<a href="{href}"{rel} class="article"><span class="art-cat">{cat}</span><span class="art-body"><span class="art-title">{title}</span><span class="art-blurb">{blurb}</span></span><span class="art-arrow">&#8599;</span></a>')
    return "\n".join(out)

PERSPECTIVES = f'''<section class="page-hero">
  <div class="wrap">
    <h1>Perspectives</h1>
    <p class="lede">Articles and papers on AI governance, cyber risk, and security risk management.</p>
  </div>
</section>

<section class="band">
  <div class="wrap">
    <div class="center-block">
      <div class="section-head">
        <h2>From the Center for AI Oversight</h2>
        <a href="https://cfaio.org/insights" rel="noopener" class="link-strong">cfaio.org/insights &#8599;</a>
      </div>
      <p class="muted">Research by Brian Allen published through the Center, an independent 501(c)(3). These links open on the Center's site.</p>
      <div class="list-rows">
        <a href="https://cfaio.org/is-ai-mission-critical" rel="noopener" class="article"><span class="art-cat">Center paper</span><span class="art-body"><span class="art-title">Is AI Mission Critical?</span><span class="art-blurb">Which uses of AI create a board oversight duty, and what the board's record should show.</span></span><span class="art-arrow">&#8599;</span></a>
        <a href="https://cfaio.org/the-ai-oversight-governance-layer" rel="noopener" class="article"><span class="art-cat">Center paper</span><span class="art-body"><span class="art-title">The AI Oversight Governance Layer</span><span class="art-blurb">The decisions that establish what an enterprise governs, who answers, and what record the program must produce.</span></span><span class="art-arrow">&#8599;</span></a>
        <a href="https://cfaio.org/committee-fallacy-anatomy" rel="noopener" class="article"><span class="art-cat">Center paper</span><span class="art-body"><span class="art-title">The Committee Fallacy</span><span class="art-blurb">Assigning AI risk to a committee is not governing it.</span></span><span class="art-arrow">&#8599;</span></a>
        <a href="https://cfaio.org/builders-and-buyers" rel="noopener" class="article"><span class="art-cat">Center paper</span><span class="art-body"><span class="art-title">Builders and Buyers</span><span class="art-blurb">Decision rights and accountability for institutions that build AI and those that put it to work.</span></span><span class="art-arrow">&#8599;</span></a>
      </div>
    </div>
  </div>
</section>

<section class="band band-tight">
  <div class="wrap">
    <h2>Articles and books</h2>
    <div class="list-rows">
      {article_rows()}
    </div>
  </div>
</section>

{cta()}'''

CONTACT = f'''<section class="page-hero">
  <div class="wrap">
    <h1>Talk to us</h1>
    <p class="lede">A first conversation is 30 minutes with a senior member of our team. We listen to where you are and tell you plainly what we would look at first. No deck, no pitch.</p>
  </div>
</section>

<section class="band">
  <div class="wrap split">
    <div class="contact-card">
      <h2>Reach us</h2>
      <div class="contact-rows">
        <div><span class="contact-label">Email</span><a href="mailto:{EMAIL}?subject=First%20conversation" class="contact-value">{EMAIL}</a></div>
        <div><span class="contact-label">Phone</span><a href="tel:{PHONE_TEL}" class="contact-value">{PHONE_DISPLAY}</a></div>
        <div><span class="contact-label">Book</span><a href="{BOOKING}" rel="noopener" class="contact-value">30 minute first conversation</a></div>
        <div><span class="contact-label">LinkedIn</span><a href="{LINKEDIN}" rel="noopener" class="contact-value">Brian Allen</a></div>
      </div>
      <div class="btn-row"><a href="{BOOKING}" rel="noopener" class="btn btn-solid">Book 30 minutes</a><a href="mailto:{EMAIL}?subject=First%20conversation" class="btn btn-outline">Email us instead</a></div>
    </div>
    <div class="list-grid">
      <div><h3>Engagements</h3><p>Oversight assessment, program build, annual re-assessment, and cyber and operational risk programs. Tell us what your board is asking and we will tell you where we would start.</p></div>
      <div><h3>Speaking</h3><p>Keynotes, board briefings, and executive sessions on AI oversight and risk governance. Email with the date, audience, and format.</p></div>
      <div><h3>Press and analysts</h3><p>Email with your deadline. We respond the same business day.</p></div>
      <div><h3>Where we are</h3><p>Connecticut, and wherever the engagement is. Most first conversations happen by video.</p></div>
    </div>
  </div>
</section>'''

PRIVACY = f'''<section class="page-hero page-hero-tight">
  <div class="wrap">
    <h1>Privacy policy</h1>
    <p class="lede">Effective date: April 9, 2025. Last reviewed: October 2026.</p>
  </div>
</section>
<section class="band legal">
  <div class="wrap measure">
    <h2>1. Introduction</h2>
    <p>Risk Governance Group, LLC ("RGG," "we," "us," or "our") is committed to protecting the privacy of visitors to our website, www.riskgg.com (the "Site"). This Privacy Policy explains what personal information we collect, how we use and share that information, and your choices concerning our data practices.</p>
    <h2>2. Information we collect</h2>
    <p>We collect personal information that you voluntarily provide to us when you interact with the Site. The types of personal information we may collect include:</p>
    <ul>
      <li><b>Contact information:</b> name, email address, telephone number.</li>
      <li><b>Professional information:</b> your company or business name, job title, business address.</li>
    </ul>
    <p>We collect this information when you email us, call us, or request information about our services.</p>
    <h2>3. Cookies and analytics</h2>
    <p>The Site does not use analytics, advertising or tracking cookies. Our hosting provider processes technical information such as IP addresses and request logs to deliver the Site and protect it from misuse. If we add analytics in the future, we will update this section before we do.</p>
    <h2>4. How we use your information</h2>
    <p>We use the personal information we collect for the following purposes:</p>
    <ul>
      <li>To respond to your inquiries and fulfill your requests for information.</li>
      <li>To send you communications and other information you have requested or consented to receive.</li>
      <li>To provide you with information about our services.</li>
      <li>To operate, maintain, and improve the Site and our services.</li>
      <li>To comply with legal obligations and protect our legal rights.</li>
    </ul>
    <h2>5. Sharing your information</h2>
    <p>We do not sell your personal information. We do not share your personal information with third parties for their own marketing purposes.</p>
    <p>We may share information in the following circumstances:</p>
    <ul>
      <li><b>Service providers:</b> we use third-party service providers to perform functions on our behalf, such as website hosting. These providers only have access to the information needed to perform their functions and are obligated to maintain confidentiality and security.</li>
      <li><b>Legal requirements:</b> we may disclose your information if required by law, subpoena, or other legal process, or if we believe in good faith that disclosure is necessary to protect our rights, protect your safety or the safety of others, investigate fraud, or respond to a government request.</li>
      <li><b>Business transfers:</b> in the event of a merger, acquisition, reorganization, bankruptcy, or other similar event, your personal information may be transferred as part of the transaction, subject to standard confidentiality arrangements.</li>
    </ul>
    <h2>6. Data security</h2>
    <p>We implement reasonable administrative, technical, and physical security measures designed to protect the personal information we collect from loss, misuse, unauthorized access, disclosure, alteration, and destruction. However, no internet transmission or electronic storage is 100% secure. While we strive to protect your information, we cannot guarantee its absolute security.</p>
    <h2>7. Data retention</h2>
    <p>We retain your personal information for as long as necessary to fulfill the purposes for which it was collected, including for the purposes of satisfying any legal, accounting, or reporting requirements, or as long as needed to resolve disputes or enforce our agreements.</p>
    <h2>8. Your privacy rights</h2>
    <p>Depending on your location, you may have certain rights regarding your personal information. You may request to:</p>
    <ul>
      <li>Access the personal information we hold about you.</li>
      <li>Correct inaccurate personal information.</li>
      <li>Delete your personal information.</li>
    </ul>
    <p>To exercise these rights, please contact us at <a href="mailto:{EMAIL}">{EMAIL}</a>. We will respond to your request in accordance with applicable law.</p>
    <h2>9. Children's privacy</h2>
    <p>The Site is not directed to children under 13, and we do not knowingly collect personal information from children. If you believe a child has provided us with personal information, contact us and we will delete it.</p>
    <h2>10. Changes to this privacy policy</h2>
    <p>We may update this Privacy Policy from time to time. We will notify you of any material changes by posting the new Privacy Policy on the Site and updating the effective date at the top. We encourage you to review this Privacy Policy periodically.</p>
    <h2>11. Contact us</h2>
    <p>If you have any questions about this Privacy Policy or our data practices, please contact us at: Risk Governance Group, LLC, <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>
  </div>
</section>'''

TERMS = f'''<section class="page-hero page-hero-tight">
  <div class="wrap">
    <h1>Terms of use</h1>
    <p class="lede">Effective date: April 9, 2025. Last reviewed: October 2026.</p>
  </div>
</section>
<section class="band legal">
  <div class="wrap measure">
    <h2>Acceptance of terms</h2>
    <p>Welcome to the Risk Governance Group, LLC ("RGG," "we," "us," or "our") website, located at www.riskgg.com (the "Site"). By accessing or using this Site, you agree to be bound by these Terms of Use ("Terms") and our Privacy Policy. If you do not agree to these Terms, please do not use the Site.</p>
    <h2>Use of the Site</h2>
    <p>The Site provides information about Risk Governance Group and its services. You agree to use the Site only for lawful purposes and in a manner that does not infringe the rights of, restrict, or inhibit anyone else's use and enjoyment of the Site. Prohibited behavior includes harassing or causing distress or inconvenience to any person, transmitting obscene or offensive content, or disrupting the normal flow of dialogue within the Site.</p>
    <h2>Intellectual property</h2>
    <p>All content included on the Site, such as text, graphics, logos, images, as well as the compilation thereof, and any software used on the Site, is the property of RGG or its suppliers and protected by copyright and other laws that protect intellectual property and proprietary rights. You agree to observe and abide by all copyright and other proprietary notices, legends, or other restrictions contained in any such content and will not make any changes thereto. You are granted a non-exclusive, non-transferable, revocable license to access and use the Site strictly in accordance with these Terms. You may not modify, publish, transmit, reverse engineer, participate in the transfer or sale, create derivative works, or in any way exploit any of the content, in whole or in part, found on the Site. RGG content is not for resale.</p>
    <h2>No user-generated content</h2>
    <p>This Site does not permit users to create accounts, post comments, or submit any form of user-generated content.</p>
    <h2>Not professional advice</h2>
    <p>Content on the Site is general information about risk governance. It is not legal, financial, or professional advice and does not create an engagement or an attorney-client relationship. Engagements are governed by a separate written agreement.</p>
    <h2>Disclaimer of warranties</h2>
    <p>The information and materials on the Site are provided "as is" and "as available" without warranties of any kind, either express or implied. RGG disclaims all warranties, express or implied, including, but not limited to, implied warranties of merchantability, fitness for a particular purpose, title, and non-infringement. RGG does not warrant that the functions contained in the Site will be uninterrupted or error-free, that defects will be corrected, or that the Site or the server that makes it available are free of viruses or other harmful components. RGG does not warrant or make any representations regarding the use or the results of the use of the material on the Site in terms of its correctness, accuracy, reliability, or otherwise.</p>
    <h2>Limitation of liability</h2>
    <p>To the fullest extent permitted by law, RGG and its officers, directors, employees, and agents will not be liable for any indirect, incidental, special, consequential, or punitive damages, or any loss of profits, revenue, data, or goodwill, arising out of or relating to your use of or inability to use the Site, whether based on warranty, contract, tort, or any other legal theory, and whether or not RGG has been advised of the possibility of such damages. RGG's total liability for any claim relating to the Site will not exceed one hundred U.S. dollars.</p>
    <h2>Indemnification</h2>
    <p>You agree to indemnify, defend, and hold harmless RGG, its officers, directors, employees, agents, and third parties, for any losses, costs, liabilities, and expenses (including reasonable attorney's fees) relating to or arising out of your use of or inability to use the Site, your violation of any terms of this Agreement or your violation of any rights of a third party, or your violation of any applicable laws, rules or regulations.</p>
    <h2>Governing law and jurisdiction</h2>
    <p>These Terms shall be governed by and construed in accordance with the laws of the State of Connecticut, United States, without regard to its conflict of law provisions. You agree that any legal action or proceeding between RGG and you for any purpose concerning these Terms or the parties' obligations hereunder shall be brought exclusively in a federal or state court of competent jurisdiction sitting in the State of Connecticut.</p>
    <h2>Changes to terms</h2>
    <p>RGG reserves the right, in its sole discretion, to change the Terms under which the Site is offered. The most current version of the Terms will supersede all previous versions. RGG encourages you to periodically review the Terms posted on the Site to stay informed of our updates. Your continued use of the Site following the posting of revised Terms means that you accept and agree to the changes.</p>
    <h2>Contact us</h2>
    <p>If you have any questions about these Terms, please contact us at: Risk Governance Group, LLC, <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>
  </div>
</section>'''

NOT_FOUND = f'''<section class="page-hero page-hero-tight">
  <div class="wrap">
    <h1>Page not found</h1>
    <p class="lede">The page you are looking for has moved or no longer exists.</p>
    <div class="btn-row">
      <a href="index.html" class="btn btn-solid">Home</a>
      <a href="ai-oversight.html" class="btn btn-outline">AI oversight and risk governance</a>
      <a href="contact.html" class="btn btn-outline">Talk to us</a>
    </div>
  </div>
</section>

{cta()}'''

PAGES = [
    ("index.html", "Risk Governance Group", HOME_DESC, INDEX, None),
    ("ai-oversight.html", "AI Oversight and Risk Governance | Risk Governance Group", "Oversight assessment, program build, and annual re-assessment for boards and executives accountable for AI.", AI_OVERSIGHT, "ai-oversight.html"),
    ("cyber-operational-risk.html", "Cyber and Operational Risk Programs | Risk Governance Group", "Cyber risk management programs, enterprise security risk management, operational resilience, and board reporting on technology risk.", CYBER, "cyber-operational-risk.html"),
    ("team.html", "Team | Risk Governance Group", "Every engagement is led by Brian Allen and delivered by senior practitioners assembled for it. We name the team in every proposal.", TEAM, "team.html"),
    ("body-of-work.html", "Body of Work | Risk Governance Group", "Books, public work, and research by Brian Allen on cyber risk, enterprise security risk management, and AI oversight.", BODY_OF_WORK, "body-of-work.html"),
    ("perspectives.html", "Perspectives | Risk Governance Group", "Articles, papers, and books by Brian Allen on AI oversight, cyber risk management, and enterprise security risk management.", PERSPECTIVES, "perspectives.html"),
    ("contact.html", "Talk to us | Risk Governance Group", "A first conversation is 30 minutes with a senior member of our team. Email info@riskgg.com or call 203-442-4114.", CONTACT, None),
    ("privacy.html", "Privacy Policy | Risk Governance Group", "How Risk Governance Group collects, uses, shares, and protects personal information, and the choices and rights you have.", PRIVACY, None),
    ("terms.html", "Terms of Use | Risk Governance Group", "Terms of use for the Risk Governance Group website, covering permitted use, intellectual property, disclaimers, liability, and governing law.", TERMS, None),
    ("404.html", "Page not found | Risk Governance Group", "The page you are looking for has moved or no longer exists.", NOT_FOUND, None),
]

def clean_links(doc):
    """Vercel cleanUrls: link to /team instead of team.html. Anchors on index stay."""
    doc = re.sub(r'href="index\.html"', 'href="/"', doc)
    doc = re.sub(r'href="(?:\.\./)?([a-z0-9\-/]+)\.html(#[a-z0-9\-]+)?"', lambda m: f'href="/{m.group(1)}{m.group(2) or ""}"', doc)
    doc = re.sub(r'(src|href)="(?:\.\./)?(assets/|styles\.css)', r'\1="/\2', doc)
    return doc

def relativize(doc, depth):
    """For the preview copy (plain files): fix paths for pages in a subfolder."""
    if depth == 0: return doc
    up = "../" * depth
    doc = re.sub(r'(href|src)="(?!https?:|mailto:|tel:|#|\.\./)([a-z0-9\-/]+\.(?:html|css|svg|png|jpg|pdf)(?:#[a-z0-9\-]+)?)"', lambda m: f'{m.group(1)}="{up}{m.group(2)}"', doc)
    doc = re.sub(r'href="(assets/pdf/[^"]+)"', lambda m: f'href="{up}{m.group(1)}"', doc)
    return doc

def build():
    if os.path.exists(PREVIEW): shutil.rmtree(PREVIEW)
    os.makedirs(os.path.join(PREVIEW, "assets"), exist_ok=True)
    shutil.copy(os.path.join(ROOT, "styles.css"), PREVIEW)
    for f in os.listdir(os.path.join(ROOT, "assets")):
        src = os.path.join(ROOT, "assets", f)
        if os.path.isfile(src): shutil.copy(src, os.path.join(PREVIEW, "assets", f))
    urls = []
    for path, title, desc, body, active in PAGES:
        doc = page(path, title, desc, body, active)
        depth = path.count("/")
        # repo copy: clean URLs, root-relative assets
        with open(os.path.join(SITE, path), "w", encoding="utf-8") as fh: fh.write(clean_links(doc))
        if path != "404.html":
            urls.append(BASE + clean_slug(path))
        # preview copy: plain .html links
        pdoc = relativize(doc, depth)
        if path == "index.html":
            inner = pdoc.split("<body>",1)[1].rsplit("</body>",1)[0]
            pdoc = f'<title>{html.escape(title)}</title>\n<meta name="description" content="{html.escape(desc)}">\n{FONTS}\n<link rel="stylesheet" href="styles.css">\n{FAVICON}\n' + inner
        with open(os.path.join(PREVIEW, path), "w", encoding="utf-8") as fh: fh.write(pdoc)
    # sitemap and robots
    today = __import__("datetime").date.today().isoformat()
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for u in urls:
        u = u if u.endswith("/") or u != BASE.rstrip("/") else u + "/"
        sm += f"  <url><loc>{u}</loc><lastmod>{today}</lastmod></url>\n"
    sm += "</urlset>\n"
    with open(os.path.join(SITE, "sitemap.xml"), "w", encoding="utf-8") as fh: fh.write(sm)
    with open(os.path.join(SITE, "robots.txt"), "w", encoding="utf-8") as fh: fh.write(f"User-agent: *\nAllow: /\nSitemap: {BASE}sitemap.xml\n")
    print("built", len(PAGES), "pages into", SITE, "and preview into", PREVIEW)

if __name__ == "__main__":
    build()
