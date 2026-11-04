# -*- coding: utf-8 -*-
"""
verify_fa.py — تأیید نهایی فارسی‌سازی DeepTutor بعد از reapply_fa.py
====================================================================
بعد از هر اجرای reapply_fa.py و deeptutor stop/start یک‌بار اجرا کن:

    python verify_fa.py              # بررسی فایل‌ها + تست زندهٔ سرور (اگر روشن باشد)
    python verify_fa.py --no-live    # فقط بررسی فایل‌ها
    python verify_fa.py --url http://127.0.0.1:3782

خروجی: جدول OK/FAIL برای هر قابلیت + کد خروج (0 = همه‌چیز درست، 1 = حداقل یک FAIL).
FAIL یعنی آن قابلیت روی این نصب فعال نیست — اول reapply_fa.py را دوباره اجرا کن؛
اگر دوباره FAIL بود، خروجی همین اسکریپت را برای نگهدارندهٔ بسته بفرست.
"""
import glob, os, re, sys, urllib.request

HOME = os.environ.get("DEEPTUTOR_HOME", "F:/deeptutor-home")
PACK = os.path.dirname(os.path.abspath(__file__))
URL = "http://127.0.0.1:3782"
if "--url" in sys.argv:
    URL = sys.argv[sys.argv.index("--url") + 1]
LIVE = "--no-live" not in sys.argv

res = []
def check(name, ok, detail=""):
    """ok: True/False/None (None = SKIP، در جمع FAIL نمی‌آید)."""
    res.append((name, ok, detail))
    tag = "[  OK ]" if ok else ("[ SKIP ]" if ok is None else "[ FAIL ]")
    print(tag, name + (f" — {detail}" if detail else ""))

def rd(p):
    try:
        return open(p, encoding="utf-8", errors="replace").read()
    except OSError:
        return None

def find_sp():
    cands = [HOME + "/.venv/Lib/site-packages/"]
    cands += sorted(glob.glob(HOME + "/.venv/lib/python*/site-packages/"))
    for c in cands:
        if os.path.isdir(c + "deeptutor"):
            return c
    return HOME + "/.venv/Lib/site-packages/"
SP = find_sp()

def web_roots():
    roots = [SP + "deeptutor_web/.next/"]
    rt = HOME + "/data/user/runtime/web/.next/"
    if os.path.isdir(rt):
        roots.append(rt)
    return roots

def any_file_has(root, pattern, globs, regex=False):
    """اولین فایل از الگوهای glob که pattern را دارد؛ (نام فایل، None/متن)."""
    for g in globs:
        for f in glob.glob(root + g, recursive=True):
            s = rd(f)
            if s is None:
                continue
            hit = re.search(pattern, s) if regex else (pattern in s)
            if hit:
                return os.path.basename(f)
    return None

FA_LABEL = "فارسی"
# the catalog embeds JSON inside a JS string literal, so unicode escapes are
# doubled on disk (\\u0641) — match that shape, not raw Persian.
ESC_FA = "\\\\u0641\\\\u0627\\\\u0631\\\\u0633\\\\u06cc"

# --------------------------------------------------------------- backend
print("== بک‌اند (site-packages) ==")
b = {
    "response_languages": (SP + "deeptutor/core/response_languages.py", '"fa",'),
    "ui_literal":         (SP + "deeptutor/services/settings/interface_settings.py", '"ja", "tr", "fa"]'),
    "ui_aliases":         (SP + "deeptutor/services/settings/interface_settings.py", '"farsi": "fa",'),
    "i18n_parse":         (SP + "deeptutor/services/i18n.py", 'raw.startswith("fa")'),
    "i18n_messages":      (SP + "deeptutor/services/i18n.py", '"fa": {'),
    "overview_copy":      (SP + "deeptutor/book/overview_copy.py", '"fa": {'),
    "export":             (SP + "deeptutor/book/export.py", '"fa": {'),
    "book_cues":          (SP + "deeptutor/book/language.py", '("fa", r"'),
}
for name, (p, pat) in b.items():
    s = rd(p)
    check("backend: " + name, s is not None and pat in s,
          "" if s is not None else "فایل نیست — DEEPTUTOR_HOME درست است؟")
s = rd(SP + "deeptutor/services/config/settings_spec.py")
check("backend: settings_spec", s is not None and s.count('("fa",') >= 2)

# --------------------------------------------------------------- frontend
print("== فرانت (هر دو ریشه: قالب + runtime) ==")
for root in web_roots():
    tag = "runtime" if "runtime" in root else "template"
    cat = root + "static/chunks/7777.fa.js"
    cs = rd(cat)
    check(f"{tag}: کاتالوگ fa",
          cs is not None and (FA_LABEL in cs or ESC_FA in cs) and len(cs) > 50000,
          "" if cs is not None else "7777.fa.js ساخته نشده")
    check(f"{tag}: resolver وب‌پک",
          any_file_has(root, r'7777===\w+\?"static/chunks/7777\.fa\.js"',
                       ["static/chunks/*.js"], regex=True) is not None)
    check(f"{tag}: فهرست زبان‌ها",
          any_file_has(root, r'\{code:"fa",labelKey:"language\.persian"\}',
                       ["static/chunks/*.js", "server/chunks/*.js"], regex=True) is not None)
    check(f"{tag}: فونت وزیرمتن",
          any_file_has(root, "/* fa-font: Vazirmatn variable (data URI) */",
                       ["static/css/*.css", "static/chunks/*.css", "static/chunks/*.js"]) is not None)
    check(f"{tag}: انهنسر جلالی",
          any_file_has(root, "__faJalaliEnhancer", ["static/chunks/app/layout-*.js"]) is not None)
    check(f"{tag}: اعداد جلالی تقویم",
          any_file_has(root, "__faDayNumV2",
                       ["static/chunks/app/**/calendar/page-*.js"], regex=False) is not None)
    check(f"{tag}: صفحهٔ خطای فارسی",
          any_file_has(root, "این صفحه بارگذاری نشد",
                       ["static/chunks/*.js", "server/chunks/*.js"]) is not None)

# ------------------------------------------------------------------ live
if LIVE:
    print("== تست زنده (سرور) ==")
    def get(path):
        try:
            with urllib.request.urlopen(URL + path, timeout=8) as r:
                return r.status, r.read(400000).decode("utf-8", "replace")
        except Exception as e:
            return None, str(e)
    st, html = get("/")
    if st is None:
        check("live: سرور", None, "سرور در دسترس نیست (" + html[:80] + ") — deeptutor start کن یا --no-live بزن")
    else:
        # SSR shell is English by design — fa kicks in client-side (i18n +
        # enhancer), so here we only prove the shell and assets are served.
        check("live: صفحهٔ اصلی", st == 200 and "<html" in html)
        st2, html2 = get("/calendar")
        check("live: /calendar", st2 == 200 and "application error" not in html2.lower())
        st3, _ = get("/_next/static/chunks/7777.fa.js")
        check("live: کاتالوگ fa سرو می‌شود", st3 == 200)

# --------------------------------------------------------------- verdict
print()
fails = [r for r in res if r[1] is False]
skips = [r for r in res if r[1] is None]
print(f"VERIFY: {len(res)} چک | OK: {len(res) - len(fails) - len(skips)} | SKIP: {len(skips)} | FAIL: {len(fails)}")
for name, _, detail in fails:
    print("  FAIL:", name, "—", detail)
if fails:
    print("→ اول reapply_fa.py را دوباره اجرا کن؛ اگر FAIL ماند، خروجی بالا را برای نگهدارندهٔ بسته بفرست.")
    sys.exit(1)
print("→ همه‌چیز آماده است. اگر تازه reapply کرده‌ای: deeptutor stop/start و Ctrl+Shift+R.")
sys.exit(0)
