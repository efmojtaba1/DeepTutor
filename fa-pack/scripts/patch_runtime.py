# -*- coding: utf-8 -*-
"""Patch the LIVE runtime .next (data/user/runtime/web/.next) with fa support."""
import os, glob, shutil, hashlib

V = "F:/deeptutor-home/.venv/Lib/site-packages/deeptutor_web/.next/"
R = "F:/deeptutor-home/data/user/runtime/web/.next/"
BK = "F:/deeptutor-home/fa-backup/runtime-web/"
os.makedirs(BK, exist_ok=True)

FA_OPT = ',{value:"fa",label:"\\u0641\\u0627\\u0631\\u0633\\u06cc"}'
res = []

def patch(rel, repls, label):
    p = R + rel
    s = open(p, encoding='utf-8').read()
    orig = s
    log = []
    for old, new, name in repls:
        n = s.count(old)
        if n == 0: log.append(f"MISS[{name}]"); continue
        s = s.replace(old, new)
        log.append(f"ok[{name}]x{n}")
    if s != orig:
        b = BK + rel.replace("/", "__")
        if not os.path.exists(b): shutil.copy2(p, b)
        open(p, "w", encoding='utf-8', newline='\n').write(s)
    res.append(f"{label}: " + " ".join(log))

# server 8844
patch("server/chunks/8844.js", [
 ('{code:"tr",labelKey:"language.turkish"}]', '{code:"tr",labelKey:"language.turkish"},{code:"fa",labelKey:"language.persian"}]', 'APP_LANG'),
 ('"tr"===c||"turkish"===b||"t\\xfcrk\\xe7e"===b?"tr":"en"', '"tr"===c||"turkish"===b||"t\\xfcrk\\xe7e"===b?"tr":"fa"===c||"farsi"===b||"persian"===b?"fa":"en"', 'NORM'),
 ('if("tr"===a){let a=(await c.e(996).then(c.t.bind(c,70996,19))).default;d.default.addResourceBundle("tr","app",a,!0,!0)}}}',
  'if("tr"===a){let a=(await c.e(996).then(c.t.bind(c,70996,19))).default;d.default.addResourceBundle("tr","app",a,!0,!0)}if("fa"===a){let a=(await c.e(7777).then(c.t.bind(c,77770,19))).default;d.default.addResourceBundle("fa","app",a,!0,!0)}}}', 'ENSURE'),
 ('["language.turkish","T\\xfcrk\\xe7e"]])', '["language.turkish","T\\xfcrk\\xe7e"],["language.persian","Persian"]])', 'EN_CAT'),
], "8844")

# server 8844 ResponseLanguage (array + map) — detect dynamically
s = open(R + "server/chunks/8844.js", encoding='utf-8').read()
i = s.find('"zh-tw"')
if i >= 0:
    seg = s[max(0,i-300):i+1500]
    import re
    m = re.search(r'let ([a-z])=\["en","zh","zh-tw"(.*?)\]', seg)
    if m:
        arr_old = m.group(0); arr_new = arr_old[:-1] + ',"fa"]'
        n = s.count(arr_old)
        if n == 1:
            b = BK + "server__chunks__8844.js"
            if not os.path.exists(b): shutil.copy2(R + "server/chunks/8844.js", b)
            s = s.replace(arr_old, arr_new)
            open(R + "server/chunks/8844.js", "w", encoding='utf-8', newline='\n').write(s)
            res.append("8844 RESP_ARR ok")
        else: res.append(f"8844 RESP_ARR count={n}")
    m2 = re.search(r'let ([a-z])=\{([^{}]*"bahasa melayu"[^{}]*)\}', s)
    if m2:
        map_old = m2.group(0); map_new = map_old[:-1] + ',farsi:"fa",persian:"fa"}'
        n = s.count(map_old)
        if n == 1:
            s = s.replace(map_old, map_new)
            open(R + "server/chunks/8844.js", "w", encoding='utf-8', newline='\n').write(s)
            res.append("8844 RESP_MAP ok")
        else: res.append(f"8844 RESP_MAP count={n}")
    else: res.append("8844 RESP_MAP not found")
else: res.append("8844 zh-tw not found")

# server RESP chunks
for f in ["4453.js","4945.js","678.js"]:
    patch("server/chunks/" + f, [('{value:"tr",label:"T\\xfcrk\\xe7e"}]', '{value:"tr",label:"T\\xfcrk\\xe7e"}' + FA_OPT + ']', 'RESP_OPT')], f)

# client 2769
patch("static/chunks/2769-3fe92318fe709266.js", [
 ('{code:"tr",labelKey:"language.turkish"}]', '{code:"tr",labelKey:"language.turkish"},{code:"fa",labelKey:"language.persian"}]', 'APP_LANG'),
 ('"tr"===r||"turkish"===t||"t\\xfcrk\\xe7e"===t?"tr":"en"', '"tr"===r||"turkish"===t||"t\\xfcrk\\xe7e"===t?"tr":"fa"===r||"farsi"===t||"persian"===t?"fa":"en"', 'NORM'),
 ('"ms","vi","tr"]', '"ms","vi","tr","fa"]', 'RESP_ARR'),
 ('"bahasa melayu":"ms",vietnamese:"vi"', '"bahasa melayu":"ms",farsi:"fa",persian:"fa",vietnamese:"vi"', 'RESP_MAP'),
], "2769")

# client 9428
patch("static/chunks/9428-5e8818c3f7789245.js", [
 ('if("tr"===e){let e=(await o.e(3201).then(o.t.bind(o,3201,19))).default;a.default.addResourceBundle("tr","app",e,!0,!0)}}}',
  'if("tr"===e){let e=(await o.e(3201).then(o.t.bind(o,3201,19))).default;a.default.addResourceBundle("tr","app",e,!0,!0)}if("fa"===e){let e=(await o.e(7777).then(o.t.bind(o,77770,19))).default;a.default.addResourceBundle("fa","app",e,!0,!0)}}}', 'ENSURE'),
 ('["language.turkish","T\\xfcrk\\xe7e"]])', '["language.turkish","T\\xfcrk\\xe7e"],["language.persian","Persian"]])', 'EN_CAT'),
], "9428")

# client RESP chunks
for f in ["3525-a4aa63006c41c3c4.js","4010-ea473dea21db231d.js","5995-31bf4e819574c5d5.js"]:
    patch("static/chunks/" + f, [('{value:"tr",label:"T\\xfcrk\\xe7e"}]', '{value:"tr",label:"T\\xfcrk\\xe7e"}' + FA_OPT + ']', 'RESP_OPT')], f.split('-')[0])

# webpack resolver
patch("static/chunks/webpack-d094ab3f26be167a.js", [('.u=e=>6709===e?', '.u=e=>7777===e?"static/chunks/7777.fa.js":6709===e?', 'RESOLVER')], "webpack")

# layout RTL
patch("static/chunks/app/layout-ea57c06fdc2f3b68.js", [('document.documentElement.lang=a,c(a)', 'document.documentElement.lang=a,document.documentElement.dir="fa"===a?"rtl":"ltr",c(a)', 'RTL_HOOK')], "layout")

# copy new 7777 chunks
for rel in ["static/chunks/7777.fa.js", "server/chunks/7777.js"]:
    shutil.copy2(V + rel, R + rel)
    res.append(f"copied {rel}")

# catalog labels: server + client
INS = ',"language.persian":"\\u0641\\u0627\\u0631\\u0633\\u06cc"'
def add_label(path):
    t = open(path, encoding='utf-8').read()
    idx = t.rfind("'")
    if idx < 1 or t[idx-1] != '}': return "SKIP"
    b = BK + os.path.basename(path)
    if not os.path.exists(b): shutil.copy2(path, b)
    open(path, "w", encoding='utf-8', newline='\n').write(t[:idx-1] + INS + t[idx-1:])
    return "OK"
for sid in ['3276','1618','9233','6754','9918','7158','8335','2651','996']:
    p = R + f"server/chunks/{sid}.js"
    res.append(f"srv-cat {sid}: " + (add_label(p) if os.path.exists(p) else "MISSING"))
for cid in ['329','8067','9068','7763','7495','63','1262','3906','3201']:
    fs = glob.glob(R + f"static/chunks/{cid}.*.js")
    res.append(f"cli-cat {cid}: " + (add_label(fs[0]) if fs else "MISSING"))

print("\n".join(res))
