# -*- coding: utf-8 -*-
"""Backend fa patches, part 1: simple anchors."""
import io

SP = "F:/deeptutor-home/.venv/Lib/site-packages/deeptutor/"
res = []

def apply(rel, old, new, name):
    p = SP + rel
    s = io.open(p, encoding="utf-8").read()
    n = s.count(old)
    if n != 1:
        res.append(f"FAIL[{name}] count={n}")
        return
    io.open(p, "w", encoding="utf-8", newline="\n").write(s.replace(old, new))
    res.append(f"ok[{name}]")

apply("core/response_languages.py", '"tr",', '"tr",\n    "fa",', "response_languages")
apply("services/prompt/language.py", '"tr": "Türkçe",', '"tr": "Türkçe",\n        "fa": "فارسی",', "prompt_labels")
apply("services/settings/interface_settings.py",
      'UiLanguage = Literal["en", "zh", "fr", "de", "uk", "pl", "pt", "vi", "ja", "tr"]',
      'UiLanguage = Literal["en", "zh", "fr", "de", "uk", "pl", "pt", "vi", "ja", "tr", "fa"]',
      "ui_literal")
apply("services/settings/interface_settings.py",
      '    "türkçe": "tr",',
      '    "türkçe": "tr",\n    "farsi": "fa",\n    "persian": "fa",\n    "فارسی": "fa",',
      "ui_aliases")
apply("services/settings/interface_settings.py",
      '        if s in {"turkish", "türkçe"} or base == "tr":\n            return "tr"',
      '        if s in {"turkish", "türkçe"} or base == "tr":\n            return "tr"\n        if s in {"farsi", "persian", "فارسی"} or base == "fa":\n            return "fa"',
      "ui_norm")
apply("services/config/launch_settings.py",
      '    if language in {"turkish", "türkçe"} or base == "tr":\n        return "tr"',
      '    if language in {"turkish", "türkçe"} or base == "tr":\n        return "tr"\n    if language in {"farsi", "persian", "فارسی"} or base == "fa":\n        return "fa"',
      "launch_norm")
apply("services/config/settings_spec.py",
      '    ("tr", "Türkçe", "Interface and replies in Turkish."),',
      '    ("tr", "Türkçe", "Interface and replies in Turkish."),\n    ("fa", "فارسی", "Interface and replies in Persian."),',
      "spec_ui")
apply("services/config/settings_spec.py",
      '    ("tr", "Türkçe", "Replies in Turkish."),',
      '    ("tr", "Türkçe", "Replies in Turkish."),\n    ("fa", "فارسی", "Replies in Persian."),',
      "spec_resp")
apply("services/i18n.py",
      '    if raw.replace("_", "-").split("-", 1)[0] == "tr" or raw in {"turkish", "türkçe"}:\n        return "tr"',
      '    if raw.replace("_", "-").split("-", 1)[0] == "tr" or raw in {"turkish", "türkçe"}:\n        return "tr"\n    if raw.startswith("fa") or raw in {"farsi", "persian", "فارسی"}:\n        return "fa"',
      "i18n_parse")
apply("book/language.py",
      '    ("tr", r"(?:türkçe\\s+olarak|türkçe\\s+yaz(?:ın)?\\b|in\\s+turkish|用土耳其(?:语|文))"),',
      '    ("tr", r"(?:türkçe\\s+olarak|türkçe\\s+yaz(?:ın)?\\b|in\\s+turkish|用土耳其(?:语|文))"),\n    ("fa", r"(?:به\\s+فارسی|فارسی\\s+بنویس|به\\s+زبان\\s+فارسی|in\\s+(?:persian|farsi)|用波斯(?:语|文))"),',
      "book_cues")
apply("services/partners/runtime.py",
      '    "tr": "🤔 Düşünüyorum…",',
      '    "tr": "🤔 Düşünüyorum…",\n    "fa": "🤔 دارم فکر می‌کنم…",',
      "partner_notice")
apply("runtime/banner.py",
      '    if code in {"tr", "tr-tr", "turkish", "türkçe"}:\n        return "tr"',
      '    if code in {"tr", "tr-tr", "turkish", "türkçe"}:\n        return "tr"\n    if code in {"fa", "fa-ir", "farsi", "persian", "فارسی"}:\n        return "fa"',
      "banner_pick")

print("\n".join(res))
