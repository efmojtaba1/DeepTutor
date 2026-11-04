# -*- coding: utf-8 -*-
"""Add dir=auto to the compact markdown renderer (59347) and module 137 spans."""
import os, shutil

R = "F:/deeptutor-home/data/user/runtime/web/.next/static/chunks/"
V = "F:/deeptutor-home/.venv/Lib/site-packages/deeptutor_web/.next/static/chunks/"
BK = "F:/deeptutor-home/fa-backup/"
res = []

DA = ('function _da(){let l=new Set(["p","h1","h2","h3","h4","h5","h6","ul","ol","li",'
      '"blockquote","th","td"]);return e=>(function e(t){if("element"===t.type&&t.tagName){'
      'let n=t.properties?.className,r=Array.isArray(n)?n:String(n??"").split(/\\s+/);'
      'if(["pre","code","math","svg"].includes(t.tagName)||r.some(e=>["katex","katex-display","mermaid"].includes(String(e)))){'
      'if(t.properties={...t.properties,dir:"ltr"},"pre"!==t.tagName)return}'
      'l.has(t.tagName)&&t.properties?.dir===void 0&&(t.properties={...t.properties,dir:"auto"})}'
      't.children?.forEach(e)})(e)}')

def patch(path, repls, label):
    if not os.path.exists(path):
        res.append(f"MISSING {label}")
        return
    s = open(path, encoding="utf-8").read()
    if "_da()" in s:
        res.append(f"ALREADY {label}")
        return
    for old, new, name in repls:
        n = s.count(old)
        if n != 1:
            res.append(f"FAIL[{label}/{name}] count={n}")
            return
        s = s.replace(old, new)
    b = BK + "rtl__" + os.path.basename(path)
    if not os.path.exists(b):
        shutil.copy2(path, b)
    open(path, "w", encoding="utf-8", newline="\n").write(s)
    res.append(f"OK {label}")

# 59347: compact renderer — inject plugin + use it
repl_9347 = [
    ("function i({content:e}){", DA + "function i({content:e}){", "fn-def"),
    ("rehypePlugins:u,", "rehypePlugins:[_da(),...u],", "plugin-use"),
]
for base in (R, V):
    patch(base + "9347.ef125ab74f4fc87d.js", repl_9347, "9347@" + ("runtime" if base is R else "venv"))

# 5454 module 137: dir=auto on the two span wrappers
repl_5454 = [
    ('(0,r.jsx)("span",{className:t,children:n})', '(0,r.jsx)("span",{dir:"auto",className:t,children:n})', "span-plain"),
    ('(0,r.jsx)("span",{className:t,children:a})', '(0,r.jsx)("span",{dir:"auto",className:t,children:a})', "span-md"),
]
for base in (R, V):
    patch(base + "5454-de53825b1fa4dbd3.js", repl_5454, "5454@" + ("runtime" if base is R else "venv"))

print("\n".join(res))
