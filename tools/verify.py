# tools/verify.py  Run from the repo root after building: python tools/verify.py
import json, re, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
SKIP = {"_preview", ".git", "node_modules", ".vercel"}
pages = [p for p in ROOT.rglob("*.html") if not SKIP & set(p.relative_to(ROOT).parts)]
fails = []
fail = fails.append
BANNED = re.compile(r"\b(robust|leverag\w*|holistic|seamless\w*|empower\w*|stakeholder\w*|unlock\w*|unprecedented|journey|transform\w*|navigat\w*|delve|cutting-edge|best-in-class|regrisk|north star)\b", re.I)
GONE = ["AI-Governance-For-Wealth-Management-Executives.pdf", "BPI-Practitioners-Guide-to-Explainability.pdf"]
ESRM = ["articles/introducing-esrm", "articles/esrm-and-erm"]

def resolve(path):
    t = path.strip("/")
    cands = [ROOT / "index.html"] if t == "" else [ROOT / t, ROOT / (t + ".html"), ROOT / t / "index.html"]
    return any(c.is_file() for c in cands)

def text_of(h):
    h = re.sub(r"(?is)<(script|style|svg)\b.*?</\1>", " ", h)
    return re.sub(r"(?s)<[^>]+>", " ", h)

def attr(h, marker, name):
    m = re.search(r"<(?:link|meta)\b[^>]*" + marker + r"[^>]*>", h, re.I)
    if not m:
        return None
    a = re.search(name + r'="([^"]*)"', m.group(0))
    return a.group(1) if a else None

esrm_present = all(resolve("/" + e) for e in ESRM)
if not esrm_present:
    print("NOTE: ESRM article pages not found; ESRM checks skipped")

textfiles = [*pages, *ROOT.glob("*.css"), *ROOT.glob("tools/*.py"), ROOT / "vercel.json", ROOT / "sitemap.xml"]
for f in textfiles:
    s = f.read_text(encoding="utf-8")
    rel = f.relative_to(ROOT).as_posix()
    if re.search("[\u2013\u2014]", s):
        fail(f"em or en dash in {rel}")
    if f.name != "verify.py" and re.search(r"(?i)regrisk", s):
        fail(f"RegRisk text in {rel}")
    if f.name not in ("verify.py", "vercel.json") and any(g in s for g in GONE):
        fail(f"removed PDF still referenced in {rel}")

for g in GONE:
    if (ROOT / "assets" / "pdf" / g).exists():
        fail(f"removed PDF still on disk: {g}")

for p in pages:
    rel = p.relative_to(ROOT).as_posix()
    h = p.read_text(encoding="utf-8")
    if not rel.startswith("articles/"):
        visible = text_of(h).replace("Navigating Artificial Intelligence", "")  # published BPI title
        hits = sorted({m.group(0).lower() for m in BANNED.finditer(visible)})
        if hits:
            fail(f"banned words in {rel}: {hits}")
    for href in re.findall(r'(?:href|src)="(/[^"#?]*)', h):
        if not href.startswith("//") and not resolve(href):
            fail(f"{rel}: broken internal link {href}")
    levels = [int(x) for x in re.findall(r"<h([1-6])\b", h, re.I)]
    if levels.count(1) != 1:
        fail(f"{rel}: expected one h1, found {levels.count(1)}")
    for a, b in zip(levels, levels[1:]):
        if b > a + 1:
            fail(f"{rel}: heading jumps from h{a} to h{b}")
            break
    if 'rel="apple-touch-icon"' not in h or 'name="theme-color"' not in h:
        fail(f"{rel}: missing apple-touch-icon or theme-color")
    if rel == "404.html":
        if 'content="noindex' not in h:
            fail("404.html missing noindex")
        continue
    slug = "" if rel == "index.html" else (rel[:-11] if rel.endswith("/index.html") else rel[:-5])
    expected = "https://riskgg.com/" + slug
    canon = attr(h, 'rel="canonical"', "href")
    ogurl = attr(h, 'property="og:url"', "content")
    if canon != expected:
        fail(f"{rel}: canonical {canon} should be {expected}")
    if ogurl != expected:
        fail(f"{rel}: og:url {ogurl} should be {expected}")
    desc = attr(h, 'name="description"', "content") or ""
    if len(desc) < 100:
        fail(f"{rel}: meta description is {len(desc)} characters, needs 100 or more")
    if "Research paper" in h:
        fail(f"{rel}: still says Research paper")

if not (ROOT / "404.html").is_file():
    fail("404.html missing")

idx = (ROOT / "index.html").read_text(encoding="utf-8")
no_svg = re.sub(r"(?is)<svg\b.*?</svg>", " ", idx)
for line in ["What is governed. Who is accountable.", "The activity, not the rank.", "What the system does."]:
    if line not in no_svg:
        fail(f"homepage layer text not in HTML: {line}")
if "Oversight and management layers" not in idx:
    fail("homepage engagement cards missing layer tags")
if "The same approach that made cyber governance defensible" in idx:
    fail("homepage contradiction sentence still present")
if "The cyber operating model" not in idx:
    fail("homepage replacement sentence missing")
m = re.search(r'(?is)<script type="application/ld\+json">(.*?)</script>', idx)
if not m:
    fail("homepage JSON-LD missing")
else:
    try:
        ld = json.loads(m.group(1))
        if ld.get("@type") != "ProfessionalService" or "Center" in m.group(1):
            fail("JSON-LD type wrong or mentions the Center")
    except ValueError as e:
        fail(f"JSON-LD does not parse: {e}")

contact = (ROOT / "contact.html").read_text(encoding="utf-8")
if "<title>Talk to us | Risk Governance Group</title>" not in contact:
    fail("contact title not 'Talk to us | Risk Governance Group'")

privacy = (ROOT / "privacy.html").read_text(encoding="utf-8")
if "Google Analytics" in privacy:
    fail("privacy policy still mentions Google Analytics")
if "does not use analytics, advertising or tracking cookies" not in privacy:
    fail("privacy section 3 replacement text missing")

per = (ROOT / "perspectives.html").read_text(encoding="utf-8")
if "published under the BPI staff byline" not in per:
    fail("BPI card line missing")
if "bpi.com/navigating-artificial-intelligence-in-banking" not in per:
    fail("BPI banking link missing")
if esrm_present:
    for e in ESRM:
        if "/" + e not in per:
            fail(f"Perspectives does not link /{e}")

vj = json.loads((ROOT / "vercel.json").read_text(encoding="utf-8"))
reds = vj.get("redirects", [])
srcs = {r["source"]: r["destination"] for r in reds}
for g in GONE:
    if srcs.get("/assets/pdf/" + g) != "/perspectives":
        fail(f"no redirect from /assets/pdf/{g} to /perspectives")
for r in reds:
    d = r["destination"]
    if d.startswith("/") and not d.startswith("/_") and not resolve(d.split("#")[0].split("?")[0]):
        fail(f"redirect {r['source']} points to missing page {d}")
    if esrm_present and r["source"].startswith("/articles/"):
        if r["source"] in ("/" + ESRM[0], "/" + ESRM[1]) or any(w in r["source"] for w in (":path", "*", "(.*)")):
            fail(f"redirect {r['source']} shadows the ESRM pages")
csp = [x for blk in vj.get("headers", []) for x in blk.get("headers", []) if x.get("key", "").lower() == "content-security-policy"]
if not csp:
    fail("no Content-Security-Policy header in vercel.json")
elif "'unsafe-inline'" in csp[0]["value"].split("script-src")[-1].split(";")[0]:
    fail("script-src allows unsafe-inline")

sm = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
for loc in re.findall(r"<loc>([^<]+)</loc>", sm):
    path = loc.replace("https://riskgg.com", "")
    if loc.endswith(".html") or "404" in loc or not resolve(path):
        fail(f"bad sitemap entry {loc}")
if esrm_present:
    for e in ESRM:
        if "https://riskgg.com/" + e + "<" not in sm:
            fail(f"sitemap missing /{e}")

if fails:
    print(f"{len(fails)} CHECK(S) FAILED")
    for f in fails:
        print(" -", f)
    sys.exit(1)
print(f"ALL CHECKS PASSED ({len(pages)} pages)")
