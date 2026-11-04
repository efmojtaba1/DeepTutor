# -*- coding: utf-8 -*-
"""
restore_fa.py — بازگرداندن فایل‌های اصلی DeepTutor از بکاپ fa-pack
==================================================================
هر اجرای reapply_fa.py قبل از بازنویسی هر فایل، نسخهٔ اصلی آن را زیر
fa-pack/backup/<زمان>/ نگه می‌دارد. این اسکریپت همان نسخه‌ها را برمی‌گرداند:

    python restore_fa.py --list          # فهرست بکاپ‌ها (زمان + تعداد فایل)
    python restore_fa.py                 # بازگرداندن از آخرین بکاپ
    python restore_fa.py 20261105-012345 # بازگرداندن از یک بکاپ مشخص

بعد از بازگرداندن: deeptutor stop/start و در مرورگر Ctrl+Shift+R.
نکته: بکاپ‌ها را خودت هم می‌توانی پاک کنی (پوشهٔ fa-pack/backup) — هر بکاپ
کامل و مستقل است و به بکاپ‌های قبلی وابسته نیست.
"""
import os, shutil, sys

HOME = os.environ.get("DEEPTUTOR_HOME", "F:/deeptutor-home")
PACK = os.path.dirname(os.path.abspath(__file__))
BK = PACK + "/backup"


def restore(stamp):
    src = BK + "/" + stamp
    if not os.path.isdir(src):
        print("این بکاپ وجود ندارد:", stamp)
        return 1
    files = []
    for root, _, names in os.walk(src):
        for n in names:
            files.append(os.path.join(root, n))
    if not files:
        print("بکاپ خالی است:", stamp)
        return 1
    n = 0
    for f in sorted(files):
        rel = os.path.relpath(f, src).replace("\\", "/")
        if rel.startswith("pack/"):
            print("  رد شد (فایل بسته، نه نصب):", rel)
            continue
        dst = HOME + "/" + rel
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(f, dst)
        n += 1
        print("  بازگشت:", rel)
    print(f"RESTORED: {n} فایل از {stamp}")
    print("→ حالا deeptutor stop/start کن و در مرورگر Ctrl+Shift+R بزن.")
    return 0


def main():
    if not os.path.isdir(BK):
        print("هیچ بکاپی نیست — پک هنوز چیزی بازنویسی نکرده است.")
        return 1
    stamps = sorted(d for d in os.listdir(BK) if os.path.isdir(BK + "/" + d))
    if "--list" in sys.argv:
        if not stamps:
            print("هیچ بکاپی نیست.")
            return 0
        for s in stamps:
            cnt = sum(len(f) for _, _, f in os.walk(BK + "/" + s))
            print(s, f"({cnt} فایل)")
        return 0
    target = next((a for a in sys.argv[1:] if not a.startswith("-")),
                  stamps[-1] if stamps else None)
    if not target:
        print("هیچ بکاپی نیست.")
        return 1
    return restore(target)


if __name__ == "__main__":
    sys.exit(main())
