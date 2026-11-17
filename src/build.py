"""src/ からサイトを生成する。使い方: python3 src/build.py（リポジトリのルートで）

アプリを足すとき: src/apps/<slug>/app.json を作り、ポリシーがあれば src/apps/<slug>/privacy.md を置く。
privacy.md の {{CONTACT}} は site.json の contact に置き換わる。
"""
import html, json, pathlib, shutil
import markdown

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
site = json.loads((SRC / "site.json").read_text(encoding="utf-8"))
contact = site.get("contact") or ""
contact_html = f'<a href="mailto:{html.escape(contact)}">{html.escape(contact)}</a>' if contact else "（準備中）"

CSS = """
:root{--bg:#f7f8fa;--card:#fff;--fg:#1b1f24;--muted:#5b6470;--line:#d8dde3;--accent:#2f5bd3}
@media (prefers-color-scheme:dark){:root{--bg:#0d1828;--card:#11213a;--fg:#eef2f8;--muted:#b4c0d3;--line:#2c3d5a;--accent:#8fb0ff}}
*{box-sizing:border-box}
body{background:var(--bg);color:var(--fg);font-family:system-ui,-apple-system,"Hiragino Sans","Noto Sans JP",sans-serif;line-height:1.75;margin:0;padding:24px 16px 48px}
main{max-width:760px;margin:0 auto}
a{color:var(--accent)}
header.site{margin-bottom:28px} header.site a{color:inherit;text-decoration:none}
h1{font-size:1.6rem;line-height:1.4;margin:.2em 0} h2{font-size:1.15rem;margin-top:2em;border-bottom:1px solid var(--line);padding-bottom:.3em}
.lead,.muted{color:var(--muted)}
.cards{display:grid;gap:14px}
.card{display:flex;gap:14px;align-items:center;background:var(--card);border:1px solid var(--line);border-radius:16px;padding:14px;color:inherit;text-decoration:none}
.card img,.icon{width:64px;height:64px;border-radius:16px;flex:none;background:var(--line)}
.card .name{font-weight:700;font-size:1.05rem}
.badge{display:inline-block;font-size:.75rem;border:1px solid var(--line);border-radius:999px;padding:0 .6em;margin-left:.4em;color:var(--muted);vertical-align:middle}
.apphead{display:flex;gap:16px;align-items:center}
.apphead img,.apphead .icon{width:88px;height:88px;border-radius:22px}
table{border-collapse:collapse;width:100%;font-size:.92rem;display:block;overflow-x:auto}
th,td{border:1px solid var(--line);padding:.5em .6em;text-align:left;vertical-align:top}
footer{margin-top:48px;font-size:.85rem;color:var(--muted)}
"""

def page(title, body, depth):
    up = "../" * depth
    return f"""<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title><link rel="stylesheet" href="{up}style.css"></head>
<body><main>
<header class="site"><a href="{up}">{html.escape(site['title'])}</a></header>
{body}
<footer>© {html.escape(site['author'])}</footer>
</main></body></html>
"""

def write(rel, text):
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")

apps = []
for d in sorted((SRC / "apps").iterdir()):
    if (d / "app.json").exists():
        a = json.loads((d / "app.json").read_text(encoding="utf-8"))
        a["slug"] = d.name
        a["has_privacy"] = (d / "privacy.md").exists()
        apps.append(a)
apps.sort(key=lambda a: a.get("order", 99))

if (ROOT / "assets").exists():
    shutil.rmtree(ROOT / "assets")
shutil.copytree(SRC / "assets", ROOT / "assets")
write("style.css", CSS.strip() + "\n")
write(".nojekyll", "")

def icon(a, up):
    return f'<img src="{up}{a["icon"]}" alt="">' if a.get("icon") else '<div class="icon"></div>'

def badge(a):
    return f'<span class="badge">{html.escape(a["status"])}</span>' if a.get("status") else ""

cards = "\n".join(
    f'<a class="card" href="{a["slug"]}/">{icon(a, "")}<div><div class="name">{html.escape(a["name"])}{badge(a)}</div>'
    f'<div class="muted">{html.escape(a["platform"])} · {html.escape(a["tagline"])}</div></div></a>'
    for a in apps
)
write("index.html", page(site["title"], f'<h1>{html.escape(site["title"])}</h1><p class="lead">{html.escape(site["lead"])}</p><div class="cards">{cards}</div>', 0))

for a in apps:
    feats = "".join(f"<li>{html.escape(f)}</li>" for f in a.get("features", []))
    links = []
    if a.get("store_url"):
        links.append(f'<a href="{html.escape(a["store_url"])}">Google Play で見る</a>')
    if a["has_privacy"]:
        links.append('<a href="privacy/">プライバシーポリシー</a>')
    body = (
        f'<div class="apphead">{icon(a, "../")}<div><h1>{html.escape(a["name"])}{badge(a)}</h1>'
        f'<div class="muted">{html.escape(a["platform"])}</div></div></div>'
        f'<p>{html.escape(a["tagline"])}</p>'
        + (f"<ul>{feats}</ul>" if feats else "")
        + (f'<p>{" · ".join(links)}</p>' if links else "")
    )
    write(f'{a["slug"]}/index.html', page(a["name"], body, 1))
    if a["has_privacy"]:
        md = (SRC / "apps" / a["slug"] / "privacy.md").read_text(encoding="utf-8").replace("{{CONTACT}}", contact_html)
        write(f'{a["slug"]}/privacy/index.html', page(f'{a["name"]} プライバシーポリシー', markdown.markdown(md, extensions=["tables"]), 2))

print("built:", ", ".join(a["slug"] for a in apps))
