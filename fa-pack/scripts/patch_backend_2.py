# -*- coding: utf-8 -*-
"""Backend fa patches, part 2: dict blocks (i18n messages)."""
import io

SP = "F:/deeptutor-home/.venv/Lib/site-packages/deeptutor/"
res = []

def insert_after(rel, anchor, block, name):
    p = SP + rel
    s = io.open(p, encoding="utf-8").read()
    n = s.count(anchor)
    if n != 1:
        res.append(f"FAIL[{name}] anchor count={n}")
        return
    io.open(p, "w", encoding="utf-8", newline="\n").write(s.replace(anchor, anchor + block))
    res.append(f"ok[{name}]")

# ---- i18n.py: fa messages after tr block ----
s = io.open(SP + "services/i18n.py", encoding="utf-8").read()
i = s.index('    "tr": {')
j = s.index("\n    },", i)
anchor = s[i:j + len("\n    },")]
fa = '''
    "fa": {
        "api.content_required": "محتوا الزامی است",
        "api.invalid_channels_config": "پیکربندی کانال‌ها نامعتبر است",
        "api.partner_already_exists": "هم‌مطالعه‌ای با نام '{name}' از قبل وجود دارد",
        "api.partner_not_found": "هم‌مطالعه پیدا نشد",
        "api.partner_not_found_or_not_running": "هم‌مطالعه پیدا نشد یا در حال اجرا نیست",
        "api.partner_not_running": "هم‌مطالعه در حال اجرا نیست",
        "api.partner_stopped_start_required": "هم‌مطالعه متوقف شده. قبل از شروع گفت‌وگو آن را اجرا کنید.",
        "api.persona_already_exists": "شخصیتی با نام {name} از قبل وجود دارد",
        "api.persona_name_required": "نام شخصیت الزامی است",
        "api.persona_not_found": "شخصیت پیدا نشد: {name}",
        "api.soul_already_exists": "شخصیتی با نام '{name}' از قبل وجود دارد",
        "api.soul_content_empty": "محتوای شخصیت سفارشی خالی است",
        "api.soul_library_not_found": "'{name}' در کتابخانه شخصیت‌ها پیدا نشد",
        "api.soul_not_found": "شخصیت پیدا نشد",
        "api.tool_not_found": "ابزار '{name}' پیدا نشد",
        "cli_apps.abi_mismatch": "برنامه CLI {app!r} برای {installed} ساخته شده اما این زمان‌اجر از {current} استفاده می‌کند. یک مدیر باید برنامه را دوباره نصب کند.",
        "cli_apps.args_required": "{tool} به آرایه 'args' نیاز دارد — در هر عضو باید یک آرگومان خط فرمان باشد.",
        "cli_apps.entry_admin_only": "برنامه‌های CLI را یک مدیر نصب می‌کند؛ از مدیر خود بخواهید این برنامه را اضافه کند.",
        "cli_apps.install_in_progress": "این برنامه از قبل در حال نصب است.",
        "cli_apps.not_in_catalog": "برنامه CLI با شناسه {id!r} در کاتالوگ وجود ندارد.",
        "cli_apps.not_installed": "برنامه CLI {app!r} دیگر در این استقرار نصب نیست.",
        "cli_apps.still_running": "{app} هنوز در حال اجراست ({seconds} ثانیه)",
        "mcp.configure_command_or_url": "سرور {name!r}: یک دستور (stdio) یا URL پیکربندی کنید.",
        "mcp.configure_before_testing": "قبل از آزمایش، یک دستور (stdio) یا URL پیکربندی کنید.",
        "mcp.server_error": "سرور {name!r}: {error}",
        "mcp.server_missing": "سروری با نام {name!r} در فهرست شما وجود ندارد.",
        "mcp.not_oauth": "این سرور از OAuth استفاده نمی‌کند؛ به‌جای آن اطلاعات ورود را وارد کنید.",
        "mcp.oauth_callback_incomplete": "پاسخ مجوزدهی ناقص بود.",
        "mcp.oauth_callback_unknown": "این مجوزدهی منقضی شده یا از قبل کامل شده. دوباره شروع کنید.",
        "mcp.oauth_done": "مجوزدهی کامل شد. می‌توانید این زبانه را ببندید.",
        "mcp.oauth_failed": "مجوزدهی ناموفق بود.",
        "mcp.catalog_entry_missing": "خدمت MCP با شناسه {id!r} در کاتالوگ وجود ندارد.",
        "mcp.entry_admin_only": "این خدمت به‌صورت دستور محلی اجرا می‌شود و فقط یک مدیر می‌تواند آن را اضافه کند.",
        "mcp.tool_not_available": "این ابزار در این گفت‌وگو در دسترس نیست. فقط ابزارهای فهرست‌شده در پرامپت قابل فراخوانی‌اند.",
        "sandbox.command_blocked": "خطا: دستور توسط بررسی امنیتی مسدود شد (الگوی خطرناک).",
        "sandbox.disabled_for_account": "اجرای کد برای حساب شما غیرفعال است.",
        "sandbox.no_backend": "هیچ بکاند سندباکس در دسترس نیست",
    },'''
s2 = s.replace(anchor, anchor + fa, 1)
io.open(SP + "services/i18n.py", "w", encoding="utf-8", newline="\n").write(s2)
res.append("ok[i18n_messages]")

# ---- overview_copy.py: fa block after tr block ----
s = io.open(SP + "book/overview_copy.py", encoding="utf-8").read()
i = s.index('    "tr": {')
j = s.index("\n    },", i)
anchor = s[i:j + len("\n    },")]
fa = '''
    "fa": {
        "chapter_title": "چگونه این کتاب را بخوانیم",
        "chapter_summary": (
            "خلاصه خودکارِ نقشه مفاهیم و فهرست فصل‌های کتاب."
        ),
        "objectives": [
            "نقشه کامل فصل‌ها را در یک نگاه ببینید",
            "بفهمید مفاهیم چگونه به هم وابسته‌اند",
            "مسیر مطالعه مناسب اهداف خود را انتخاب کنید",
        ],
        "intro_title": "چگونه این کتاب را بخوانیم",
        "intro_body": (
            "نمودار زیر {concepts} مفهوم کلیدی این کتاب و وابستگی‌های آن‌ها به یکدیگر "
            "را نشان می‌دهد. فهرست فصل‌های بعدی همه {chapters} فصل را برمی‌شمارد؛ "
            "برای دنبال کردن مسیر پیشنهادی از بالا به پایین بخوانید یا مستقیم به "
            "موضوعی که بیش از همه کنجکاوی‌اید بروید."
        ),
        "untitled_book": "این کتاب",
        "concept_map_title": "نقشه مفاهیم",
        "chapter_index_title": "فهرست فصل‌ها",
        "chapter_index_heading": "## فهرست فصل‌ها",
    },'''
io.open(SP + "book/overview_copy.py", "w", encoding="utf-8", newline="\n").write(s.replace(anchor, anchor + fa, 1))
res.append("ok[overview_copy]")

# ---- export.py: fa block after tr block ----
s = io.open(SP + "book/export.py", encoding="utf-8").read()
i = s.index('    "tr": {')
j = s.index("\n    },", i)
anchor = s[i:j + len("\n    },")]
fa = '''
    "fa": {
        "takeaway": "نکته کلیدی",
        "answer": "پاسخ",
        "front": "روی کارت",
        "back": "پشت کارت",
        "sources": "منابع",
        "chapters": "فصل‌ها",
        "note": "یادداشت",
        "untitled_book": "کتاب بی‌نام",
        "untitled_chapter": "فصل بی‌نام",
        "not_generated": "(این فصل هنوز تولید نشده است.)",
        "omitted": "({kind} حذف شد — معادل متنی ندارد.)",
    },'''
io.open(SP + "book/export.py", "w", encoding="utf-8", newline="\n").write(s.replace(anchor, anchor + fa, 1))
res.append("ok[export]")

# ---- quiz_judge.py: fa prompt before closing brace ----
s = io.open(SP + "api/routers/quiz_judge.py", encoding="utf-8").read()
anchor = '"- Yanıtı ve geri bildirimi Türkçe yazın.",\n}'
fa = '''"- Yanıtı ve geri bildirimi Türkçe yazın.",
    "fa": (
        "تو دستیار آموزشی دقیق اما تشویق‌کننده‌ای هستی و پاسخ یک یادگیرنده به سؤال آزمون را "
        "ارزیابی می‌کنی. بر اساس پرسش، پاسخ مرجع و توضیح، بازخورد هدفمند بده.\\n\\n"
        "الزامات پاسخ:\\n"
        "- با یک خط که نتیجه را نشان می‌دهد شروع کن: ✅ درست / ⚠️ تا حدی درست / ❌ نادرست "
        "و دلیل اصلی را کوتاه بنویس.\\n"
        "- سپس بندبند بنویس: یادگیرنده چه چیزهایی را درست گفته، چه چیزهایی نادرست یا ناقص است "
        "و چگونه اصلاح شود.\\n"
        "- اگر چند پاسخ موجه ممکن است، نقاط قوت یادگیرنده را بپذیر.\\n"
        "- مستقیم به همین پاسخ بپرداز؛ توصیه کلی و کلیشه‌ای نده.\\n"
        "- با یادگیرنده صمیمی و با «تو» صحبت کن.\\n"
        "- پاسخ و بازخورد را فارسی بنویس."
    ),
}'''
n = s.count(anchor)
if n == 1:
    io.open(SP + "api/routers/quiz_judge.py", "w", encoding="utf-8", newline="\n").write(s.replace(anchor, fa))
    res.append("ok[quiz_judge]")
else:
    res.append(f"FAIL[quiz_judge] count={n}")

print("\n".join(res))
