# Deploy: GitHub to Vercel

Every step below is a click or a one line paste. Do them in order.

## 1. Put the repo on GitHub

Option A, from this folder in PowerShell (Git must be installed):

```
cd <this folder>
git init -b main
git add -A
git commit -m "Risk Governance Group site: initial static build"
gh repo create riskgg-site --public --source=. --remote=origin --push
```

If `gh` is not installed, create an empty repo named `riskgg-site` at https://github.com/new (no README, no .gitignore), then:

```
git remote add origin https://github.com/brianjallenesq/riskgg-site.git
git push -u origin main
```

Option B: open this folder in Antigravity and tell it: "Initialize a git repo on branch main, commit everything, create a public GitHub repo named riskgg-site under brianjallenesq, and push."

## 2. Connect Vercel

1. Go to https://vercel.com/new
2. Click Import next to `riskgg-site`.
3. Framework Preset: leave as Other. Build Command: leave empty. Output Directory: leave empty. Root Directory: leave as `./`.
4. Click Deploy. Vercel gives you a `*.vercel.app` address in about 30 seconds.

## 3. Check the preview address before touching DNS

Open the `*.vercel.app` address and click through:

- Every nav item and every "Book 30 minutes" button.
- `/ai-readiness` should land on `/ai-oversight` (old WordPress redirect).
- `/articles/esrm-and-erm` should show the article.
- `/assets/pdf/A-Professional-Path-Security-Management-2017.pdf` should open, if the PDFs have been added (see assets/pdf/README.md).

## 4. Point riskgg.com at Vercel

1. In the Vercel project click Settings, then Domains.
2. Type `riskgg.com`, click Add. Do the same for `www.riskgg.com`. Set `riskgg.com` as the primary and let `www` redirect to it.
3. Vercel shows the exact DNS records to set. At your DNS provider (wherever riskgg.com's nameservers live today) replace the current A record for `@` and the CNAME for `www` with the values Vercel shows.
4. Wait for Vercel to show a green check on both domains. Usually under an hour.

## 5. Switch off WordPress

Only after step 4 shows green:

1. Take a final backup from the WordPress host (Tools, Export, All content) and keep it.
2. Cancel or downgrade the WordPress hosting. Keep the domain registration.

The old AI RegRisk page, the broken Work menu link, the misspelled team member page, and the duplicated legal clauses all disappear with WordPress. The redirects in vercel.json catch every old address.

## Verification commands (run from the repo root)

```
python3 tools/build.py
python3 - <<'EOF2'
import glob,re
bad=[]
for f in glob.glob('*.html')+glob.glob('articles/*.html'):
    s=open(f,encoding='utf-8').read()
    if '—' in s or '–' in s: bad.append(f+': dash')
    if 'href="#"' in s: bad.append(f+': dead link')
    for w in ['robust','leverage','holistic','seamless','empower','stakeholder','unlock','unprecedented','journey','regrisk','north star','delve','cutting-edge','best-in-class']:
        if re.search(w, re.sub(r'<[^>]+>',' ',s), re.I): bad.append(f+': '+w)
print('\n'.join(bad) if bad else 'PASS: no dashes, no dead links, no banned words')
EOF2
```

Expected output: `PASS: no dashes, no dead links, no banned words`.
