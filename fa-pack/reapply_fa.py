# -*- coding: utf-8 -*-
"""
reapply_fa.py — بازاعمال کامل فارسی‌سازی DeepTutor بعد از آپدیت
==============================================================
استفاده (در هر پوشه‌ای):
    python reapply_fa.py            # اعمال کامل + گزارش
    python reapply_fa.py --check    # فقط بررسی، بدون تغییر

بعد از `pip install -U deeptutor` و `deeptutor stop/start`، این اسکریپت را اجرا کن
و در انتها یک‌بار دیگر stop/start. اگر مرحله‌ای FAIL داد یعنی آپدیت ساختار را
عوض کرده و باید دستی با Hermes تطبیق داده شود.
"""
import base64, glob, json, os, re, shutil, subprocess, sys, time

HOME = os.environ.get("DEEPTUTOR_HOME", "F:/deeptutor-home")
PACK = os.path.dirname(os.path.abspath(__file__))
CHECK_ONLY = "--check" in sys.argv

def _find_sp():
    """site-packages of the venv holding deeptutor — Windows and POSIX layouts."""
    cands = [HOME + "/.venv/Lib/site-packages/"]
    cands += sorted(glob.glob(HOME + "/.venv/lib/python*/site-packages/"))
    for c in cands:
        if os.path.isdir(c + "deeptutor"):
            return c
    return HOME + "/.venv/Lib/site-packages/"
SP = _find_sp()
if not os.path.isdir(SP + "deeptutor"):
    print("FAIL: deeptutor در", SP, "پیدا نشد.")
    print("→ متغیر DEEPTUTOR_HOME را روی پوشه‌ای بگذار که .venv نصب‌شدهٔ DeepTutor را دارد و دوباره اجرا کن.")
    sys.exit(2)

results = []
def report(step, status, detail=""):
    results.append((step, status, detail))
    print(f"[{status:>7}] {step}" + (f" — {detail}" if detail else ""))

def read(p):
    return open(p, encoding="utf-8").read()

# Every file the pack overwrites is backed up on first write (per run), so a
# bad patch can always be rolled back with restore_fa.py.
BACKUP = PACK + "/backup/" + time.strftime("%Y%m%d-%H%M%S")
TOUCHED = []          # .js files written this run (for the syntax gate)

def _backup_rel(p):
    if p.startswith(HOME):
        return os.path.relpath(p, HOME).replace("\\", "/")
    return "pack/" + os.path.basename(p)

def write(p, s):
    if CHECK_ONLY: return
    bp = BACKUP + "/" + _backup_rel(p)
    if not os.path.exists(bp):
        os.makedirs(os.path.dirname(bp), exist_ok=True)
        shutil.copy2(p, bp)
    open(p, "w", encoding="utf-8", newline="\n").write(s)
    if p.endswith(".js") and p not in TOUCHED:
        TOUCHED.append(p)

def patch_file(path, old, new, name, marker=None):
    """Idempotent anchor patch. marker = string that means already-applied."""
    if not os.path.exists(path):
        report(name, "MISS", path); return False
    s = read(path)
    if marker and marker in s:
        report(name, "SKIP", "already applied"); return True
    n = s.count(old)
    if n != 1:
        report(name, "FAIL", f"anchor count={n} (upstream changed?)"); return False
    write(path, s.replace(old, new))
    report(name, "OK"); return True

# ---------------------------------------------------------------- 1) backend
print("=== 1) Backend (.py) ===")
snip = json.load(open(PACK + "/snippets.json", encoding="utf-8"))

patch_file(SP + "deeptutor/core/response_languages.py",
           '"tr",', '"tr",\n    "fa",', "response_languages", marker='"fa",')

patch_file(SP + "deeptutor/services/prompt/language.py",
           '"tr": "T\u00fcrk\u00e7e",', '"tr": "T\u00fcrk\u00e7e",\n        "fa": "\u0641\u0627\u0631\u0633\u06cc",',
           "prompt_labels", marker='"fa": "\u0641\u0627\u0631\u0633\u06cc"')

p = SP + "deeptutor/services/settings/interface_settings.py"
patch_file(p, 'UiLanguage = Literal["en", "zh", "fr", "de", "uk", "pl", "pt", "vi", "ja", "tr"]',
           'UiLanguage = Literal["en", "zh", "fr", "de", "uk", "pl", "pt", "vi", "ja", "tr", "fa"]',
           "ui_literal", marker='"ja", "tr", "fa"]')
s = read(p)
if '    "farsi": "fa",' not in s:
    m = '    "t\u00fcrk\u00e7e": "tr",'
    if s.count(m) == 1:
        write(p, s.replace(m, m + "\n" + snip["ui_aliases"])); report("ui_aliases", "OK")
    else: report("ui_aliases", "FAIL", "anchor missing")
else: report("ui_aliases", "SKIP")
s = read(p)
if 'or base == "fa":' not in s:
    m = '        if s in {"turkish", "t\u00fcrk\u00e7e"} or base == "tr":\n            return "tr"'
    if s.count(m) == 1:
        write(p, s.replace(m, m + '\n        if s in {"farsi", "persian", "\u0641\u0627\u0631\u0633\u06cc"} or base == "fa":\n            return "fa"'))
        report("ui_norm", "OK")
    else: report("ui_norm", "FAIL")
else: report("ui_norm", "SKIP")

patch_file(SP + "deeptutor/services/config/launch_settings.py",
           '    if language in {"turkish", "t\u00fcrk\u00e7e"} or base == "tr":\n        return "tr"',
           '    if language in {"turkish", "t\u00fcrk\u00e7e"} or base == "tr":\n        return "tr"\n    if language in {"farsi", "persian", "\u0641\u0627\u0631\u0633\u06cc"} or base == "fa":\n        return "fa"',
           "launch_norm", marker='or base == "fa":')

patch_file(SP + "deeptutor/services/config/settings_spec.py",
           '    ("tr", "T\u00fcrk\u00e7e", "Interface and replies in Turkish."),',
           '    ("tr", "T\u00fcrk\u00e7e", "Interface and replies in Turkish."),\n    ("fa", "\u0641\u0627\u0631\u0633\u06cc", "Interface and replies in Persian."),',
           "spec_ui", marker='("fa",')
patch_file(SP + "deeptutor/services/config/settings_spec.py",
           '    ("tr", "T\u00fcrk\u00e7e", "Replies in Turkish."),',
           '    ("tr", "T\u00fcrk\u00e7e", "Replies in Turkish."),\n    ("fa", "\u0641\u0627\u0631\u0633\u06cc", "Replies in Persian."),',
           "spec_resp", marker='("fa", "\u0641\u0627\u0631\u0633\u06cc", "Replies')

patch_file(SP + "deeptutor/services/i18n.py",
           '    if raw.replace("_", "-").split("-", 1)[0] == "tr" or raw in {"turkish", "t\u00fcrk\u00e7e"}:\n        return "tr"',
           '    if raw.replace("_", "-").split("-", 1)[0] == "tr" or raw in {"turkish", "t\u00fcrk\u00e7e"}:\n        return "tr"\n    if raw.startswith("fa") or raw in {"farsi", "persian", "\u0641\u0627\u0631\u0633\u06cc"}:\n        return "fa"',
           "i18n_parse", marker='raw.startswith("fa")')
p = SP + "deeptutor/services/i18n.py"
s = read(p)
if '    "fa": {' not in s:
    i = s.index('    "tr": {'); j = s.index("\n    },", i) + len("\n    },")
    write(p, s[:j] + "\n" + snip["i18n_fa"] + s[j:]); report("i18n_messages", "OK")
else: report("i18n_messages", "SKIP")

p = SP + "deeptutor/book/overview_copy.py"
s = read(p)
if '    "fa": {' not in s:
    i = s.index('    "tr": {'); j = s.index("\n    },", i) + len("\n    },")
    write(p, s[:j] + "\n" + snip["overview_fa"] + s[j:]); report("overview_copy", "OK")
else: report("overview_copy", "SKIP")

p = SP + "deeptutor/book/export.py"
s = read(p)
if '    "fa": {' not in s:
    i = s.index('    "tr": {'); j = s.index("\n    },", i) + len("\n    },")
    write(p, s[:j] + "\n" + snip["export_fa"] + s[j:]); report("export", "OK")
else: report("export", "SKIP")

patch_file(SP + "deeptutor/book/language.py",
           '    ("tr", r"(?:t\u00fcrk\u00e7e\\s+olarak|t\u00fcrk\u00e7e\\s+yaz(?:\u0131n)?\\b|in\\s+turkish|\u7528\u571f\u8033\u5176(?:\u8bed|\u6587))"),',
           '    ("tr", r"(?:t\u00fcrk\u00e7e\\s+olarak|t\u00fcrk\u00e7e\\s+yaz(?:\u0131n)?\\b|in\\s+turkish|\u7528\u571f\u8033\u5176(?:\u8bed|\u6587))"),\n    ("fa", r"(?:\u0628\u0647\\s+\u0641\u0627\u0631\u0633\u06cc|\u0641\u0627\u0631\u0633\u06cc\\s+\u0628\u0646\u0648\u06cc\u0633|\u0628\u0647\\s+\u0632\u0628\u0627\u0646\\s+\u0641\u0627\u0631\u0633\u06cc|in\\s+(?:persian|farsi)|\u7528\u6ce2\u65af(?:\u8bed|\u6587))"),',
           "book_cues", marker='("fa", r"')

p = SP + "deeptutor/api/routers/quiz_judge.py"
s = read(p)
if '    "fa": (' not in s:
    m = '"- Yan\u0131t\u0131 ve geri bildirimi T\u00fcrk\u00e7e yaz\u0131n.",\n}'
    if s.count(m) == 1:
        write(p, s.replace(m, m[:-2] + "\n" + snip["judge_fa"] + "\n}"))
        report("quiz_judge", "OK")
    else: report("quiz_judge", "FAIL", "tr anchor missing")
else: report("quiz_judge", "SKIP")

patch_file(SP + "deeptutor/services/partners/runtime.py",
           '    "tr": "\U0001f914 D\u00fc\u015f\u00fcn\u00fcyorum\u2026",',
           '    "tr": "\U0001f914 D\u00fc\u015f\u00fcn\u00fcyorum\u2026",\n    "fa": "\U0001f914 \u062f\u0627\u0631\u0645 \u0641\u06a9\u0631 \u0645\u06cc\u200c\u06a9\u0646\u0645\u2026",',
           "partner_notice", marker='"fa": "\U0001f914')

# Console output stays English for RTL scripts: Windows consoles render them
# as mojibake and rich cannot bidi-reorder. The web UI stays Persian.
p = SP + "deeptutor/runtime/banner.py"
s = read(p)
FA_BRANCH = '    if code in {"fa", "fa-ir", "farsi", "persian", "\u0641\u0627\u0631\u0633\u06cc"}:\n'
if FA_BRANCH + '        return "fa"' in s:
    write(p, s.replace(FA_BRANCH + '        return "fa"', FA_BRANCH + '        return "en"'))
    report("banner_pick", "OK", "fa console -> en")
elif FA_BRANCH + '        return "en"' in s:
    report("banner_pick", "SKIP")
else:
    m = '    if code in {"tr", "tr-tr", "turkish", "türkçe"}:\n        return "tr"'
    if s.count(m) == 1:
        write(p, s.replace(m, m + "\n" + FA_BRANCH + '        return "en"'))
        report("banner_pick", "OK")
    else: report("banner_pick", "FAIL")
# drop a leftover fa LABELS block from earlier pack releases (console output
# no longer localizes to fa)
s = read(p)
if '    "fa": {' in s:
    i = s.index('    "fa": {'); j = s.index("\n    },", i) + len("\n    },")
    if j < len(s) and s[j] == "\n": j += 1
    write(p, s[:i] + s[j:]); report("banner_labels", "OK", "fa block removed")
else: report("banner_labels", "SKIP")

patch_file(SP + "deeptutor/api/routers/settings.py",
           '    "ms",\n    "vi",\n    "tr",\n]',
           '    "ms",\n    "vi",\n    "tr",\n    "fa",\n]',
           "settings_literal", marker='"tr",\n    "fa",')

# ---------------------------------------------------------------- 2) frontend
print("=== 2) Frontend chunks (content-addressed) ===")
def web_roots():
    roots = [SP + "deeptutor_web/.next/"]
    rt = HOME + "/data/user/runtime/web/.next/"
    if os.path.isdir(rt): roots.append(rt)
    return roots

FA_OPT = ',{value:"fa",label:"\\u0641\\u0627\\u0631\\u0633\\u06cc"}'
for root in web_roots():
    tag = "runtime" if "runtime" in root else "template"
    # APP_LANGUAGES (client+server copies)
    n = 0
    for f in glob.glob(root + "static/chunks/*.js") + glob.glob(root + "server/chunks/*.js"):
        s = read(f)
        if '{code:"fa",labelKey:"language.persian"}' in s: continue
        if '{code:"tr",labelKey:"language.turkish"}]' in s:
            write(f, s.replace('{code:"tr",labelKey:"language.turkish"}]',
                               '{code:"tr",labelKey:"language.turkish"},{code:"fa",labelKey:"language.persian"}]'))
            n += 1
    report(f"{tag} APP_LANGUAGES", "OK" if n else "SKIP", f"{n} file(s)")
    # normalizeLanguage (var-name tolerant)
    n = 0
    for f in glob.glob(root + "static/chunks/*.js") + glob.glob(root + "server/chunks/*.js"):
        s = read(f)
        if '"fa"===' in s and 'persian' in s: continue
        m = re.search(r'"tr"===(\w+)\|\|"turkish"===(\w+)\|\|"t\\xfcrk\\xe7e"===\2\?"tr":"en"', s)
        if m:
            v1, v2 = m.group(1), m.group(2)
            new = f'"tr"==={v1}||"turkish"==={v2}||"t\\xfcrk\\xe7e"==={v2}?"tr":"fa"==={v1}||"farsi"==={v2}||"persian"==={v2}?"fa":"en"'
            write(f, s.replace(m.group(0), new)); n += 1
    report(f"{tag} normalize", "OK" if n else "SKIP", f"{n} file(s)")
    # ensureLanguage switch
    n = 0
    for f in glob.glob(root + "static/chunks/*.js") + glob.glob(root + "server/chunks/*.js"):
        s = read(f)
        if "c.e(7777)" in s or "o.e(7777)" in s or "e(7777)" in s and "77770" in s: continue
        m = re.search(r'if\("tr"===(\w+)\)\{let \1=\(await (\w+)\.e\((\d+)\)\.then\(\2\.t\.bind\(\2,(\d+),19\)\)\)\.default;(\w+)\??\.default\.addResourceBundle\("tr","app",\1,!0,!0\)\}\}\}', s)
        if m:
            v, w, tr_chunk, tr_mod, recv = m.groups()
            fa_case = (f'if("fa"==={v}){{let {v}=(await {w}.e(7777).then({w}.t.bind({w},77770,19))).default;'
                       f'{recv}.default.addResourceBundle("fa","app",{v},!0,!0)}}')
            # Insert right after the tr-if's own closing brace — same block scope,
            # so the i18next receiver var (a/d/...) stays visible exactly as in the
            # tr case. Builds differ on whether the receiver equals the let var;
            # group 5 captures whichever it is.
            i_open = s.index("{", m.start())
            depth = 0
            j = i_open
            while j < len(s):
                c = s[j]
                if c == "{": depth += 1
                elif c == "}":
                    depth -= 1
                    if depth == 0: break
                j += 1
            if depth == 0:
                write(f, s[:j + 1] + fa_case + s[j + 1:]); n += 1
    report(f"{tag} ensureLanguage", "OK" if n else "SKIP", f"{n} file(s)")
    # ResponseLanguage array + name map
    n = 0
    for f in glob.glob(root + "static/chunks/*.js") + glob.glob(root + "server/chunks/*.js"):
        s = read(f)
        if '"ms","vi","tr","fa"]' in s: continue
        if '"ms","vi","tr"]' in s:
            write(f, s.replace('"ms","vi","tr"]', '"ms","vi","tr","fa"]')); n += 1
        if '"bahasa melayu":"ms"' in s and 'farsi:"fa"' not in s:
            s = read(f)
            write(f, s.replace('"bahasa melayu":"ms"', '"bahasa melayu":"ms",farsi:"fa",persian:"fa"'))
    report(f"{tag} resp-language", "OK" if n else "SKIP", f"{n} file(s)")
    # response-language dropdown options
    n = 0
    for f in glob.glob(root + "static/chunks/*.js") + glob.glob(root + "server/chunks/*.js"):
        s = read(f)
        if '{value:"fa",label:' in s: continue
        if '{value:"tr",label:"T\\xfcrk\\xe7e"}]' in s:
            write(f, s.replace('{value:"tr",label:"T\\xfcrk\\xe7e"}]', '{value:"tr",label:"T\\xfcrk\\xe7e"}' + FA_OPT + ']')); n += 1
    report(f"{tag} resp-options", "OK" if n else "SKIP", f"{n} file(s)")
    # en catalog label
    n = 0
    for f in glob.glob(root + "static/chunks/*.js") + glob.glob(root + "server/chunks/*.js"):
        s = read(f)
        if '["language.persian","Persian"]' in s: continue
        if '["language.turkish","T\\xfcrk\\xe7e"]])' in s:
            write(f, s.replace('["language.turkish","T\\xfcrk\\xe7e"]])',
                               '["language.turkish","T\\xfcrk\\xe7e"],["language.persian","Persian"]])')); n += 1
    report(f"{tag} en-catalog", "OK" if n else "SKIP", f"{n} file(s)")
    # non-en catalogs: append language.persian
    n = 0
    for f in glob.glob(root + "static/chunks/*.js") + glob.glob(root + "server/chunks/*.js"):
        s = read(f)
        if '"language.persian"' in s: continue
        if '"language.turkish"' in s:
            idx = s.rfind("'")
            if idx > 1 and s[idx-1] == "}":
                s2 = s[:idx-1] + ',"language.persian":"\\u0641\\u0627\\u0631\\u0633\\u06cc"' + s[idx-1:]
                if s2 != s:
                    write(f, s2); n += 1
    report(f"{tag} catalogs", "OK" if n else "SKIP", f"{n} file(s)")
    # webpack resolver: serve 7777.fa.js
    n = 0
    wp = glob.glob(root + "static/chunks/webpack-*.js")
    for f in wp:
        s = read(f)
        if '7777===e?"static/chunks/7777.fa.js"' in s: continue
        m = re.search(r'\.u=e=>', s)
        if m:
            write(f, s.replace(".u=e=>", '.u=e=>7777===e?"static/chunks/7777.fa.js":', 1)); n += 1
    report(f"{tag} webpack-resolver", "OK" if n else "SKIP", f"{n} file(s)")
    # layout RTL hook
    n = 0
    for f in glob.glob(root + "static/chunks/app/layout-*.js"):
        s = read(f)
        if 'documentElement.dir="fa"===a?"rtl":"ltr"' in s: continue
        m = re.search(r'document\.documentElement\.lang=(\w+),', s)
        if m:
            v = m.group(1)
            write(f, s.replace(m.group(0), f'document.documentElement.lang={v},document.documentElement.dir="fa"==={v}?"rtl":"ltr",', 1))
            n += 1
    report(f"{tag} rtl-hook", "OK" if n else "SKIP", f"{n} file(s)")

# ---------------------------------------------------------------- 3) catalog chunks
print("=== 3) fa catalog chunks (7777) ===")
fa = json.load(open(PACK + "/locales/fa/app.json", encoding="utf-8"))
payload = json.dumps(fa, ensure_ascii=True)
payload_js = payload.replace("\\", "\\\\").replace("'", "\\'")
CLIENT = ("\"use strict\";(self.webpackChunk_N_E=self.webpackChunk_N_E||[]).push([[7777],{77770:e=>{e.exports=JSON.parse('"
          + payload_js + "')}}]);")
SERVER = ("\"use strict\";exports.id=7777,exports.ids=[7777],exports.modules={77770:a=>{a.exports=JSON.parse('"
          + payload_js + "')}};")
targets = [(root + "static/chunks/7777.fa.js", CLIENT) for root in web_roots()] + \
          [(root + "server/chunks/7777.js", SERVER) for root in web_roots()]
for path, content in targets:
    if CHECK_ONLY: report(os.path.basename(path), "CHECK", path); continue
    open(path, "w", encoding="utf-8", newline="\n").write(content)
    report("write " + os.path.basename(path) + (" (runtime)" if "runtime" in path else " (template)"), "OK", f"{len(content)//1024}KB")

# ---------------------------------------------------------------- 4) font
print("=== 4) Vazirmatn font ===")
# The vanilla 1.7.1 wheel ships only Geist/Lora — no Persian face and no
# `--font-fa` variable. Pointing `--font-sans` at an undefined var makes the
# whole font-family declaration invalid at computed-value time (everything
# falls back to the browser default, e.g. Times New Roman), so the face must
# exist first. If a build really defines `--font-fa` (PR-branch builds), just
# point at it; otherwise inject the Vazirmatn variable face as a data URI and
# point at that. Geist ships a fallback that claims Arabic glyphs, so with the
# Latin face listed first Persian never reaches Vazirmatn — hence the scoped
# override under `lang="fa"` only.
import base64
_font_b64 = base64.b64encode(open(PACK + "/fonts/Vazirmatn-var.woff2", "rb").read()).decode()
FONT_MARK = "/* fa-font: Vazirmatn variable (data URI) */"
FONT_FACE = ("@font-face{font-family:'Vazirmatn';src:url(data:font/woff2;base64,"
             + _font_b64 + ") format('woff2');font-weight:100 900}")
BROKEN_MARK = "/* fa-font: put the Persian face first under lang=fa */"
for root in web_roots():
    n = 0
    for f in glob.glob(root + "static/css/*.css"):
        s = read(f)
        orig = s
        # strip any previously appended fa-font block (broken var override or old data-URI)
        for mark in (BROKEN_MARK, FONT_MARK):
            if mark in s:
                s = s[:s.index(mark)]
        has_var = "--font-sans:" in s and "__variable_" in s
        if has_var:
            if re.search(r'--font-fa:\s*[^;}]', s):
                s += ('/* fa-font: point the shared variables at the Persian face */'
                      'html[lang="fa"]{--font-sans:var(--font-fa);--font-serif:var(--font-fa)}')
            else:
                s += FONT_MARK + FONT_FACE + 'html[lang="fa"]{--font-sans:\'Vazirmatn\';--font-serif:\'Vazirmatn\'}'
        if s != orig:
            write(f, s); n += 1
    report(("runtime" if "runtime" in root else "template") + " font-css", "OK" if n else "SKIP", f"{n} file(s)")

# ---------------------------------------------------------------- 5) RTL compact renderer
print("=== 5) RTL dir-auto for compact renderer ===")
DA_JS = ('const _da=()=>e=>(function t(n){if("element"===n.type&&n.tagName){'
         'let r=n.properties?.className,a=Array.isArray(r)?r:String(r??"").split(/\\s+/);'
         'if(["pre","code","math","svg"].includes(n.tagName)||a.some(e=>["katex","katex-display","mermaid"].includes(String(e)))){'
         'if(n.properties={...n.properties,dir:"ltr"},"pre"!==n.tagName)return}'
         '["p","h1","h2","h3","h4","h5","h6","ul","ol","li","blockquote","th","td"].includes(n.tagName)'
         '&&n.properties?.dir===void 0&&(n.properties={...n.properties,dir:"auto"})}'
         'n.children?.forEach(t)})(e);')
for root in web_roots():
    n = 0
    for f in glob.glob(root + "static/chunks/*.js"):
        s = read(f)
        if "_da()" in s: continue
        m = re.search(r'let (\w)=\1\.rehypeKatex\?\[\1\.rehypeKatex\]:\[\];', s)
        if m:
            v = m.group(1)
            s2 = s.replace(m.group(0), DA_JS + m.group(0), 1)
            s2 = s2.replace(f"rehypePlugins:{v},", f"rehypePlugins:[_da(),...{v}],", 1)
            write(f, s2); n += 1
    report(("runtime" if "runtime" in root else "template") + " compact-dirauto", "OK" if n else "SKIP", f"{n} file(s)")

# ---------------------------------------------------------------- 9) RTL layout + Jalali + error copy
print("=== 9) RTL layout / Jalali / error copy ===")
RTL_CSS_PATCHES = [
    (".dt-popover{position:absolute;z-index:60;top:calc(100% + 4px);left:0;",
     ".dt-popover{position:absolute;z-index:60;top:calc(100% + 4px);inset-inline-start:0;"),
    (".dt-workspace-panel{top:0;left:calc(100% + 10px);width:264px",
     ".dt-workspace-panel{top:0;inset-inline-start:calc(100% + 10px);width:264px"),
    ("color:var(--foreground);text-align:left;transition:background-col",
     "color:var(--foreground);text-align:start;transition:background-col"),
    (".dt-popover.dt-record-sort-menu{left:auto;right:0;width:172px;transform-origin:top right",
     ".dt-popover.dt-record-sort-menu{inset-inline-start:auto;inset-inline-end:0;width:172px;transform-origin:top right"),
    (".dt-popover{top:auto;bottom:calc(100% + 6px);left:auto;right:0;transform-origin:bottom right}",
     ".dt-popover{top:auto;bottom:calc(100% + 6px);inset-inline-start:auto;inset-inline-end:0;transform-origin:bottom right}"),
    (".dt-record-children{margin:1px 0 3px calc(var(--dt-nav-pad-x) + 7px);padding-left:3px;border-left:1px solid color-mix(in srgb,var(--border) 75%,transparent)}",
     ".dt-record-children{margin-block:1px 3px;margin-inline:calc(var(--dt-nav-pad-x) + 7px) 0;padding-inline-start:3px;border-inline-start:1px solid color-mix(in srgb,var(--border) 75%,transparent)}"),
    (".dt-record-loose{padding:0 0 0 4px}",
     ".dt-record-loose{padding-block:0;padding-inline-start:4px}"),
    ('[dir="rtl"] .dt-popover{transform-origin:top right}',
     '[dir="rtl"] .dt-popover{transform-origin:top right}[dir="rtl"] .dt-popover.dt-record-sort-menu{transform-origin:top left}'),
    (".dt-note-menu{position:absolute;left:0;top:calc(100% + 2px)}",
     ".dt-note-menu{position:absolute;inset-inline-start:0;top:calc(100% + 2px)}"),
    (".dt-note-kind-menu{position:absolute;top:calc(100% + 4px);left:-6px;",
     ".dt-note-kind-menu{position:absolute;top:calc(100% + 4px);inset-inline-start:-6px;"),
    (".dt-note-toolbar-panel.is-colors{left:auto;right:0;min-width:160px}",
     ".dt-note-toolbar-panel.is-colors{inset-inline-start:auto;inset-inline-end:0;min-width:160px}"),
    (".dt-notes-card-menu{position:absolute;top:10px;right:10px;",
     ".dt-notes-card-menu{position:absolute;top:10px;inset-inline-end:10px;"),
    (".dt-cal-calendar-menu{position:absolute;right:0;top:0}",
     ".dt-cal-calendar-menu{position:absolute;inset-inline-end:0;top:0}"),
    (".dt-cal-more{position:absolute;left:7px;",
     ".dt-cal-more{position:absolute;inset-inline-start:7px;"),
    (".dt-cal-calendar-more{position:absolute;right:0;top:3px;",
     ".dt-cal-calendar-more{position:absolute;inset-inline-end:0;top:3px;"),
    (".dt-note-thread-list{position:absolute;top:calc(100% - 4px);right:10px;left:10px;",
     ".dt-note-thread-list{position:absolute;top:calc(100% - 4px);inset-inline-end:10px;inset-inline-start:10px;"),
]
RTL_CSS_APPEND = '[dir="rtl"] .dt-popover{transform-origin:top right}'
ERRORCOPY_JS = ('(function(m){var x=$T$(m);if(x!==m)return x;'
                'var p=/^Request failed(?:: (\\\\d+)| \\\\((\\\\d+)\\\\): ([\\\\s\\\\S]+)| \\\\((\\\\d+)\\\\))$/.exec(m);'
                'if(!p)return m;var st=p[1]||p[2]||p[4],dt=p[3];'
                'var k=dt?"Request failed ({{status}}): {{detail}}":"Request failed: {{status}}";'
                'var o=dt?{status:st,detail:dt}:{status:st};var r2=$T$(k,o);'
                'return r2===k?k.replace("{{status}}",st).replace("{{detail}}",dt||""):r2})($MSG$)')
for root in web_roots():
    tag = "runtime" if "runtime" in root else "template"
    # 9a) logical CSS properties
    n = 0
    for f in glob.glob(root + "static/css/*.css"):
        s = read(f)
        orig = s
        for old, new in RTL_CSS_PATCHES:
            # `new in s` also covers entries whose replacement extends the anchor
            # (e.g. the rtl popover rule + the sort-menu override): without it the
            # still-present anchor is re-expanded on every run.
            if new in s or s.count(old) != 1:
                continue
            s = s.replace(old, new)
        _dup = '[dir="rtl"] .dt-popover.dt-record-sort-menu{transform-origin:top left}'
        s = s.replace(_dup + _dup, _dup)  # heal a double append from older runs
        if s != orig:
            if ".dt-popover{position:absolute;z-index:60;top:calc(100% + 4px);inset-inline-start:0;" in s \
               and RTL_CSS_APPEND not in s:
                s += RTL_CSS_APPEND
            write(f, s); n += 1
        # text-align:left inside .dt-navigation-row
        s = read(f)
        if ".dt-navigation-row{" in s:
            seg = s.split(".dt-navigation-row{")[1].split("}")[0]
            if "text-align:left" in seg:
                write(f, s.replace(".dt-navigation-row{" + seg + "}",
                                   ".dt-navigation-row{" + seg.replace("text-align:left", "text-align:start") + "}")); n += 1
    report(f"{tag} rtl-css", "OK" if n else "SKIP", f"{n} file(s)")
    # 9b) Jalali enhancer injected inline in the layout chunk (works until restart, no new file)
    enh = json.dumps(read(PACK + "/scripts/jalali_enhancer.js"), ensure_ascii=True)
    n = 0
    for f in glob.glob(root + "static/chunks/app/layout-*.js"):
        s = read(f)
        if '"fa-jalali"' in s:
            m = re.search(r's\.textContent="(?:[^"\\]|\\.)*"', s)
            if m and m.group(0) != "s.textContent=" + enh:
                write(f, s[:m.start()] + "s.textContent=" + enh + s[m.end():]); n += 1
            continue
        m = re.search(r'document\.documentElement\.dir=("?fa"?===\w+\?"rtl":"ltr"),', s)
        if m:
            v = re.search(r'document\.documentElement\.dir=("?fa"?===(\w+)\?)', s).group(2)
            inject = (f',(function(){{if("fa"!=={v}||document.getElementById("fa-jalali"))return;'
                      f'var s=document.createElement("script");s.id="fa-jalali";s.textContent={enh};'
                      f'document.head.appendChild(s)}})(),')
            write(f, s.replace(m.group(0), m.group(0)[:-1] + inject, 1)); n += 1
    report(f"{tag} jalali-enhancer", "OK" if n else "SKIP", f"{n} file(s)")
    # 9c) toast messages through i18n + Request-failed pattern
    n = 0
    for f in glob.glob(root + "static/chunks/app/layout-*.js") + glob.glob(root + "server/chunks/*.js"):
        s = read(f)
        if 'Request failed ({{status}}): {{detail}}' in s and 'flex-1 text-[13px] leading-relaxed",children:(function' in s:
            continue
        m = re.search(r'className:"flex-1 text-\[13px\] leading-relaxed",children:(\w+)\.message', s)
        if not m:
            continue
        a = re.search(r'"aria-label":(\w+)\("Dismiss"\)', s)
        if not a:
            report(f"{tag} toast-i18n", "FAIL", "no t() var near toast"); continue
        fn = ERRORCOPY_JS.replace("$T$", a.group(1)).replace("$MSG$", m.group(1) + ".message")
        write(f, s.replace(m.group(0),
                           'className:"flex-1 text-[13px] leading-relaxed",children:' + fn, 1)); n += 1
    report(f"{tag} toast-i18n", "OK" if n else "SKIP", f"{n} file(s)")

# ------------------------------------------------- 10) month order + arrows + tray
print("=== 10) month-year order / calendar arrows / tray popover ===")

# 10a) "month year" for fa in every copy of formatDate.
# ICU renders fa {year,month} as "۱۴۰۵ آبان" (year first); read right-to-left in
# an RTL page that shows the year on the right. Persian readers expect
# "آبان ۱۴۰۵". formatDate is duplicated once per bundle (minified under a
# different name each time), so patch every occurrence by shape, not by name.
FMT_TAIL = re.compile(r'\}return ([A-Za-z_$][\w$]*)\.format\(([A-Za-z_$][\w$]*)\)\}')

def patch_month_order(s):
    hits = 0
    pos = 0
    while True:
        m = FMT_TAIL.search(s, pos)
        if not m:
            break
        pos = m.end()
        fmt_var, dt_var = m.group(1), m.group(2)
        head = s.rfind("function ", 0, m.start())
        if head < 0:
            continue
        seg = s[head:m.end()]
        mm = re.match(r'function ([A-Za-z_$][\w$]*)\(([^)]*)\)\{', seg)
        if not mm:
            continue
        args = [a.strip() for a in mm.group(2).split(",")]
        if len(args) != 3 or "JSON.stringify" not in seg or "Intl.DateTimeFormat" not in seg:
            continue
        if "_s=" in seg:      # already patched here
            continue
        d_arg, o_arg = args[1], args[2]
        repl = (
            '}var _s=%s.format(%s);'
            'if(%s&&%s.year&&%s.month&&!%s.day&&String(%s||"").split("-")[0]==="fa"){try{'
            'var _m=new Intl.DateTimeFormat(%s,{month:%s.month}).format(%s);'
            'var _y=new Intl.DateTimeFormat(%s,{year:"numeric"}).format(%s);'
            'if(_m&&_y)return _m+" "+_y}catch(_e){}}return _s}'
            % (fmt_var, args[0], o_arg, o_arg, o_arg, o_arg, d_arg,
               d_arg, o_arg, args[0], d_arg, args[0])
        )
        s = s[:m.start()] + repl + s[m.end():]
        hits += 1
    return s, hits

# 10b) arrows: in an RTL page the chevrons of the calendar nav point the wrong
# way (prev shows "‹"). Mirror only the two calendar nav groups.
ARROW_CSS = ('[dir="rtl"] .dt-cal-step svg,[dir="rtl"] .dt-cal-mini-head button svg'
             '{transform:scaleX(-1)}')

# 10c) the "Mode" tray popover hangs past the composer's right edge in RTL
# because .is-start/.is-end were physical. Each entry is
# (anchor that must exist, text to insert after it).
TRAY_CSS_INSERTS = [
    ('.dt-tray-popover.is-up.is-start{transform-origin:24px 100%}',
     '[dir="rtl"] .dt-tray-popover.is-up.is-start{transform-origin:calc(100% - 24px) 100%}'),
    ('.dt-tray-popover.is-down.is-start{transform-origin:24px 0}',
     '[dir="rtl"] .dt-tray-popover.is-down.is-start{transform-origin:calc(100% - 24px) 0}'),
]
# (old rule, new rule) — plain replacements
TRAY_CSS_PATCHES = [
    (".dt-tray-popover.is-start{left:0}", ".dt-tray-popover.is-start{inset-inline-start:0}"),
    (".dt-tray-popover.is-end{right:0}", ".dt-tray-popover.is-end{inset-inline-end:0}"),
    ("border-radius:9px;text-align:left;outline:none;transition:background-color .1s}",
     "border-radius:9px;text-align:start;outline:none;transition:background-color .1s}"),
]

for root in web_roots():
    tag = "runtime" if "runtime" in root else "template"
    # 10a — shared dates module (client chunk) and its server twin
    n = 0
    for f in glob.glob(root + "static/chunks/*.js") + glob.glob(root + "server/chunks/*.js"):
        s = read(f)
        if 'year:"numeric",month:"long"' not in s:
            continue
        s2, hits = patch_month_order(s)
        if hits:
            write(f, s2); n += hits
    report(f"{tag} month-order", "OK" if n else "SKIP", f"{n} formatter(s)")
    # 10b/10c — calendar arrows + tray popover in the feature CSS bundles
    n = 0
    for f in glob.glob(root + "static/css/*.css"):
        s = read(f)
        orig = s
        if ARROW_CSS not in s and ".dt-cal-step" in s:
            s += "\n" + ARROW_CSS
        for old, new in TRAY_CSS_PATCHES:
            if new in s or s.count(old) != 1:
                continue
            s = s.replace(old, new)
        for anchor, block in TRAY_CSS_INSERTS:
            if block in s or anchor not in s or s.count(anchor) != 1:
                continue
            s = s.replace(anchor, anchor + "\n" + block)
        if s != orig:
            write(f, s); n += 1
    report(f"{tag} arrows+tray-css", "OK" if n else "SKIP", f"{n} file(s)")

# ------------------------------------------- 11) sidebar tuck / tooltip keys / date icon
print("=== 11) sidebar tuck / tooltip keys / date field icon ===")

# 11a) The tucked account pair offsets its second tab with physical left
# margins, so under RTL the last tab is pushed past the sidebar edge. All
# offsets move to the inline start, and the halo/translate mirror with them.
SIDEBAR_TUCK = [
    ('margin-left:-23px;padding-left:0;opacity:.5',
     'margin-inline-start:-23px;padding-inline-start:0;opacity:.5'),
    ('.dt-account-tabs.is-tucked > :last-child [role="tab"] > svg { transform: translateX(10px) scale(.86); }',
     '.dt-account-tabs.is-tucked > :last-child [role="tab"] > svg { transform: translateX(-10px) scale(.86); }'),
    ('.dt-account-tabs.is-tucked > :first-child [role="tab"] > svg { filter: drop-shadow(1.5px 0 0 var(--secondary)) drop-shadow(1.5px 1px 0 var(--secondary)); }',
     '.dt-account-tabs.is-tucked > :first-child [role="tab"] > svg { filter: drop-shadow(-1.5px 0 0 var(--secondary)) drop-shadow(-1.5px 1px 0 var(--secondary)); }'),
    ('.dt-category-bar:not(.is-collapsed) .dt-category-divider { margin-left: auto; }',
     '.dt-category-bar:not(.is-collapsed) .dt-category-divider { margin-inline-start: auto; }'),
    ('.dt-navigation-actions { display: flex; align-items: center; gap: 2px; margin-right: -6px; }',
     '.dt-navigation-actions { display: flex; align-items: center; gap: 2px; margin-inline-end: -6px; }'),
]

# 11b) The shortcut keys inside a tooltip are Latin ("Ctrl", "Alt", "5") and
# their order matters; under RTL the row runs them backwards. Pin the kbd
# group to LTR so the combination reads the way it is typed.
TOOLTIP_LTR = [
    ('<kbd className="inline-flex items-center gap-0.5 font-sans',
     '<kbd dir="ltr" className="inline-flex items-center gap-0.5 font-sans'),
]

for root in web_roots():
    tag = "runtime" if "runtime" in root else "template"
    # 11a — sidebar CSS (feature bundle) + tooltip/date JS bundles
    n = 0
    for f in glob.glob(root + "static/css/*.css"):
        s = read(f)
        orig = s
        for old, new in SIDEBAR_TUCK:
            if new in s or s.count(old) != 1:
                continue
            s = s.replace(old, new)
        if s != orig:
            write(f, s); n += 1
    report(f"{tag} sidebar-tuck", "OK" if n else "SKIP", f"{n} file(s)")

    n = 0
    for f in (glob.glob(root + "static/chunks/app/*.js")
              + glob.glob(root + "static/chunks/*.js")
              + glob.glob(root + "server/chunks/*.js")):
        s = read(f)
        orig = s
        for old, new in TOOLTIP_LTR:
            if new in s or s.count(old) != 1:
                continue
            s = s.replace(old, new)
        # The date field's calendar mark is an affordance, not decoration: add
        # it wherever the trigger still renders a bare label.
        if s != orig:
            write(f, s); n += 1
    report(f"{tag} tooltip-ltr", "OK" if n else "SKIP", f"{n} file(s)")

# ------------------------------------- 12) day badge / language select parity
print("=== 12) calendar day badge / interface-language select ===")

# 12a) Calendar day numbers: every raw `getDate()` display (month cells, mini
# grid, agenda, week/day column head) is a Gregorian number; under fa they must
# be Jalali with Persian digits. The grid is client-rendered only (the SSR HTML
# carries no dt-cal-* cells), so the locale is read from the component scope —
# captured from the adjacent formatter call — with a documentElement fallback.
# v1 of this step injected `.call(this,locale)` with a name that does not exist
# in the minified scope (plus an undefined `_faj`), crashing the day/week views
# with ReferenceError; v2 is self-contained (Intl persian calendar, noon-UTC)
# and replaces the broken helper wholesale.
NUM_HELPER = ('(function(l){var c=(typeof l==="string"?l:"")||(typeof document<"u"?document.documentElement.lang:"");'
              'if(c.split("-")[0]!=="fa")return this.getDate();'
              'try{var o={};new Intl.DateTimeFormat("en-u-ca-persian-nu-latn",{year:"numeric",month:"numeric",day:"numeric",timeZone:"UTC"})'
              '.formatToParts(new Date(Date.UTC(this.getFullYear(),this.getMonth(),this.getDate(),12)))'
              '.forEach(function(x){if(x.type!=="literal")o[x.type]=Number(String(x.value).replace(/[^0-9]/g,""))});'
              'return o.day||this.getDate()}catch(__faDayNumV2){return this.getDate()}})')
PD_HELPER = ('(function(n){return String(n).replace(/[0-9]/g,function(d){'
             'return "\\u06f0\\u06f1\\u06f2\\u06f3\\u06f4\\u06f5\\u06f6\\u06f7\\u06f8\\u06f9"[d]})})')
DAYNUM_BROKEN = ('(function(l){var c=l.split("-")[0];if(c!=="fa")return String(this.getDate());'
                 'var j=_faj(this);return j?j.jd:this.getDate()}).call(this,locale)')

def _dayexpr(dv, loc):
    arg = loc if loc else "document.documentElement.lang"
    return "(" + PD_HELPER + ")(" + NUM_HELPER + ".call(" + dv + "," + arg + "))"

def _locale_near(s, idx, datevar, before=280, after=280):
    win = s[max(0, idx - before): idx + after]
    if datevar:
        esc = re.escape(datevar)
        for pat in (r'\(0,\w+\.\w+\)\(' + esc + r',(\w+),', r'\(0,\w+\.\w+\)\(' + esc + r',(\w+)\)'):
            ms = list(re.finditer(pat, win))
            if ms:
                return ms[-1].group(1)
    return None

for root in web_roots():
    tag = "runtime" if "runtime" in root else "template"
    n = 0
    for f in (glob.glob(root + "static/chunks/*.js")
              + glob.glob(root + "static/chunks/app/**/*.js", recursive=True)):
        s = read(f)
        if "dt-cal-" not in s or "__faDayNumV2" in s:
            continue
        orig = s
        # R1: week/day column head — replace the broken v1 helper wholesale, or
        # swap the vanilla raw getDate. Date var + locale var come from the
        # adjacent weekday formatter call.
        i = s.find("dt-cal-daynum")
        if i != -1 and DAYNUM_BROKEN in s:
            ms = list(re.finditer(r'\(0,\w+\.\w+\)\((\w+),(\w+)\)', s[max(0, i - 200):i]))
            if ms:
                s = s.replace(DAYNUM_BROKEN, _dayexpr(ms[-1].group(1), ms[-1].group(2)), 1)
        else:
            m = re.search(r'(dt-cal-daynum",children:)(\w+)\.getDate\(\)', s)
            if m:
                loc = _locale_near(s, m.start(), m.group(2))
                s = s[:m.start()] + m.group(1) + _dayexpr(m.group(2), loc) + s[m.end():]
        # R2: month cell date — Jalali day, month label on Jalali day 1
        m = re.search(r'children:1===(\w+)\.getDate\(\)\?\(0,(\w+)\.(\w+)\)\(\1,(\w+),\{month:"short",day:"numeric"\}\):\1\.getDate\(\)', s)
        if m:
            dv, mod, fn, loc = m.group(1), m.group(2), m.group(3), m.group(4)
            s = s.replace(m.group(0),
                          'children:(function(){var j=(' + NUM_HELPER + ').call(' + dv + ',' + loc +
                          ');return 1===j?(0,' + mod + '.' + fn + ')(' + dv + ',' + loc +
                          ',{month:"short",day:"numeric"}):(' + PD_HELPER + ')(j)})()', 1)
        # R3: mini grid day number
        m = re.search(r'(className:"dt-cal-mini-day",onClick:\(\)=>\w+\((\w+)\),children:)\2\.getDate\(\)', s)
        if m:
            s = s.replace(m.group(0), m.group(1) + _dayexpr(m.group(2), _locale_near(s, m.start(), m.group(2))), 1)
        # R4: agenda day number
        m = re.search(r'(dt-cal-agenda-num",children:)(\w+)\.day\.getDate\(\)', s)
        if m:
            s = s.replace(m.group(0), m.group(1) + _dayexpr(m.group(2) + ".day", _locale_near(s, m.start(), m.group(2) + ".day")), 1)
        if s != orig:
            write(f, s); n += 1
    report(f"{tag} cal-daynums", "OK" if n else "SKIP", f"{n} chunk(s)")

    # 12b) The interface-language select shipped without the arrow that its
    # siblings carry: `dt-select` paints the chevron at the physical right and
    # the field cleared only 12px, so the arrow region had no room and the
    # control read as a text box. `pr-8` is what the other selects use.
    n = 0
    for f in glob.glob(root + "static/chunks/*.js") + glob.glob(root + "server/chunks/*.js"):
        s = read(f)
        if "dt-select appearance-none" not in s:
            continue
        if 'dt-select appearance-none min-w-[200px] pr-8' in s:
            continue
        s2 = s.replace('dt-select appearance-none min-w-[200px]"',
                       'dt-select appearance-none min-w-[200px] pr-8"')
        if s2 != s:
            write(f, s2); n += 1
    report(f"{tag} lang-select-arrow", "OK" if n else "SKIP", f"{n} chunk(s)")

    # 12c) The route error boundary ships hardcoded English literals (not i18n
    # keys), so the fa catalog cannot reach them: the title, the message line
    # and the Reload/Back buttons. Swap the literals; the ERROR-digest token
    # stays Latin on purpose (technical token).
    ERR_LITERALS = [
        ('"This page couldn’t load"', '"این صفحه بارگذاری نشد"'),
        ('"A server error occurred. Reload to try again."', '"خطای سرور رخ داد. برای تلاش دوباره بارگذاری کن."'),
        ('"Reload to try again, or go back."', '"برای تلاش دوباره بارگذاری کن، یا برگرد."'),
        ('children:"Reload"', 'children:"بارگذاری دوباره"'),
        ('children:"Back"', 'children:"بازگشت"'),
    ]
    n = 0
    for f in glob.glob(root + "static/chunks/*.js") + glob.glob(root + "server/chunks/*.js"):
        s = read(f)
        if "This page couldn" not in s:
            continue
        s2 = s
        for old, new in ERR_LITERALS:
            s2 = s2.replace(old, new)
        if s2 != s:
            write(f, s2); n += 1
    report(f"{tag} error-page-literals", "OK" if n else "SKIP", f"{n} file(s)")

# ---------------------------------------- 13) persona labels (tray + picker)
print("=== 13) persona labels ===")
# Preset personas (peer, research-assistant, teacher) reach the UI with English
# names and descriptions straight from PERSONA.md frontmatter. The locale can
# name them ("persona.<name>", "persona.<name>.desc"); these patches route the
# display surfaces through t() with a fallback to the server value, so custom
# personas and other languages are untouched.
for root in web_roots():
    tag = "runtime" if "runtime" in root else "template"

    # a) tray preferences popover: rows + the trigger that names the choice
    n = 0
    for f in glob.glob(root + "static/chunks/*.js"):
        s = read(f)
        m = re.search(r'(\w+)\("No persona ', s)
        if not m:
            continue
        T = m.group(1)

        def row_repl(mo, T=T):
            v = mo.group(1)
            return (f'title:{T}("persona."+{v}.name,{{defaultValue:{v}.name}})||{v}.name,'
                    f'meta:{T}("persona."+{v}.name+".desc",{{defaultValue:{v}.description}})||{v}.description}},'
                    f'{v}.name))')

        s2, k1 = re.subn(r'title:(\w+)\.name,meta:\1\.description\},\1\.name\)\)', row_repl, s)

        def trig_repl(mo):
            out, src, tv = mo.group(1), mo.group(2), mo.group(3)
            return (f'{out}=({src}?.value?{tv}("persona."+{src}.value,{{defaultValue:{src}.value}}):"")'
                    f'||{tv}("Default")')

        s2, k2 = re.subn(r'(\w+)=(\w+)\?\.value\|\|(\w+)\("Default"\)', trig_repl, s2, count=1)
        if s2 != s:
            write(f, s2); n += 1
    report(f"{tag} persona-tray", "OK" if n else "SKIP", f"{n} chunk(s)")

    # b) the /persona picker: row name, row description, footer echo
    n = 0
    for f in glob.glob(root + "static/chunks/*.js"):
        s = read(f)
        m = re.search(r'(\w+)\("No personas yet"\)', s)
        if not m or "line-clamp-2" not in s:
            continue
        T = m.group(1)

        def pick_name_repl(mo, T=T):
            v = mo.group(1)
            return (f'children:{T}("persona."+{v}.name,{{defaultValue:{v}.name}})||{v}.name}}),'
                    f'"admin"==={v}.source?')

        s2, k1 = re.subn(r'children:(\w+)\.name\}\),"\w+"===\1\.source\?', pick_name_repl, s)

        def pick_desc_repl(mo, T=T):
            v = mo.group(1)
            head = (f'children:{T}("persona."+{v}.name+".desc",'
                    f'{{defaultValue:{v}.description}})||{v}.description}}')
            # keep the row-closing tail the match consumed (the head already
            # closes the props object, so the tail starts at the jsx call)
            return head + f'):null]}})]}}, {v}.name)}})}}'.replace(" ", "")

        s2, k2 = re.subn(r'children:(\w+)\.description\}\):null\]\}\)\]\},\1\.name\)\}\)\}',
                         pick_desc_repl, s2, count=1)

        def pick_foot_repl(mo, T=T):
            tv, v = mo.group(1), mo.group(2)
            return f'{tv}("Persona: {{{{name}}}}",{{name:{tv}("persona."+{v},{{defaultValue:{v}}})||{v}}})'

        s2, k3 = re.subn(r'(\w+)\("Persona: \{\{name\}\}",\{name:(\w+)\}\)', pick_foot_repl, s2, count=1)
        if s2 != s:
            write(f, s2); n += 1
    report(f"{tag} persona-picker", "OK" if n else "SKIP", f"{n} chunk(s)")

# ------------------------------------------------------------- syntax gate
# A patch that lands but breaks JS syntax crashes the whole app at load time —
# this bit once (day/week views died with ReferenceError). Every .js file
# written this run is checked with node --check; a failure is reverted from
# the backup taken above, so the install stays loadable.
if TOUCHED and not CHECK_ONLY:
    node = shutil.which("node")
    if not node:
        report("syntax-gate", "WARN", "node پیدا نشد — سینتکس فایل‌های JS بررسی نشد")
    else:
        print("=== syntax gate ===")
        bad = 0
        for p in TOUCHED:
            r = subprocess.run([node, "--check", p], capture_output=True, text=True)
            if r.returncode == 0:
                continue
            head = read(p)[:4000]
            if re.search(r"(^|\n)(import|export)[\s{(]", head):
                report("syntax-gate", "WARN", os.path.basename(p) + " ESM است — دستی چک شود")
                continue
            bp = BACKUP + "/" + _backup_rel(p)
            if os.path.exists(bp):
                shutil.copy2(bp, p)
            bad += 1
            lines = r.stderr.strip().splitlines() or ["?"]
            report("syntax-gate", "FAIL", os.path.basename(p) + " برگردانده شد — " + lines[-1][:140])
        if not bad:
            report("syntax-gate", "OK", f"{len(TOUCHED)} file(s) سالم")

# ---------------------------------------------------------------- summary
print()
fails = [r for r in results if r[1] == "FAIL"]
oks = sum(1 for r in results if r[1] == "OK")
skips = sum(1 for r in results if r[1] == "SKIP")
print(f"DONE: {len(results)} steps | OK: {oks} | SKIP: {skips} | FAIL: {len(fails)}")
for step, _, detail in fails: print("  FAIL:", step, "—", detail)
if fails:
    print("→ آپدیت ساختار را عوض کرده؛ این موارد را با Hermes تطبیق بده.")
else:
    print("→ حالا verify_fa.py را اجرا کن (تأیید نهایی)، بعد deeptutor stop/start و Ctrl+Shift+R.")
if not CHECK_ONLY and os.path.isdir(BACKUP):
    print("→ بکاپ این اجرا:", BACKUP, "(بازگرداندن: python restore_fa.py)")
