# -*- coding: utf-8 -*-
"""Inject Vazirmatn font (data-URI) + lang=fa overrides into the global CSS."""
import base64, shutil, os

FONT = "F:/deeptutor-home/data/user/runtime/web/public/fonts/Vazirmatn-var.woff2"
TARGETS = [
    "F:/deeptutor-home/data/user/runtime/web/.next/static/css/0df3933f59c98172.css",
    "F:/deeptutor-home/.venv/Lib/site-packages/deeptutor_web/.next/static/css/0df3933f59c98172.css",
]
BK = "F:/deeptutor-home/fa-backup/"
res = []

b64 = base64.b64encode(open(FONT, "rb").read()).decode()
block = (
    "/* fa-font: Vazirmatn variable (data URI, no server fetch) */"
    "@font-face{font-family:'Vazirmatn';"
    f"src:url(data:font/woff2;base64,{b64}) format('woff2');"
    "font-weight:100 900;font-style:normal;font-display:swap}"
    'html[lang="fa"]{--font-sans:\'Vazirmatn\';--font-serif:\'Vazirmatn\'}'
)
print("block size:", len(block))

for t in TARGETS:
    if not os.path.exists(t):
        res.append(f"MISSING: {t}")
        continue
    s = open(t, encoding="utf-8").read()
    if "Vazirmatn" in s:
        res.append(f"ALREADY: {t}")
        continue
    b = BK + "css__" + os.path.basename(t)
    if not os.path.exists(b):
        shutil.copy2(t, b)
    open(t, "w", encoding="utf-8", newline="\n").write(s + block)
    res.append(f"OK: {t} (+{len(block)} bytes)")

print("\n".join(res))
