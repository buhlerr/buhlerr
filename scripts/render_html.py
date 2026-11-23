"""Gera o site estático (index.html) a partir de carreira.yaml — mesma fonte única do README.
Uso: python3 scripts/render_html.py carreira.yaml dist/index.html
Só entram projetos com status: publico. Sem dependências além do PyYAML.
"""
import html
import sys
from pathlib import Path

import yaml

MESES = "jan fev mar abr mai jun jul ago set out nov dez".split()
ROTULOS = {"dados_ia": "Dados, IA e automação", "operacoes": "Operações", "cliente": "Cliente", "financeiro": "Mercado financeiro"}

CSS = """
:root{--tinta:#1a1c20;--cinza:#5c6470;--linha:#e4e7eb;--fundo:#fafafa}
*{margin:0;padding:0;box-sizing:border-box}
body{font:16px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;color:var(--tinta);background:var(--fundo)}
main{max-width:720px;margin:0 auto;padding:64px 24px 96px}
header{margin-bottom:56px}
h1{font-size:2rem;letter-spacing:-.02em}
.titulo{color:var(--cinza);margin-top:6px;font-weight:600}
.local{color:var(--cinza);font-size:.95rem;margin-top:10px}
.contato{margin-top:16px;display:flex;flex-wrap:wrap;gap:8px 20px}
.contato a{color:var(--tinta);text-decoration:none;border-bottom:1px solid var(--linha)}
.contato a:hover{border-bottom-color:var(--tinta)}
.resumo{margin-top:24px;font-size:1.05rem;max-width:60ch}
h2{font-size:.8rem;text-transform:uppercase;letter-spacing:.08em;color:var(--cinza);margin:56px 0 20px}
.item{margin-bottom:28px}
.cab{display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap}
.cab b{font-size:1.05rem}
.cab span{color:var(--cinza);white-space:nowrap;font-size:.95rem}
.empresa{color:var(--cinza);margin-top:2px}
ul{list-style:none;margin-top:10px}
li{padding-left:18px;position:relative;margin-bottom:6px}
li::before{content:"";position:absolute;left:2px;top:.72em;width:6px;height:6px;border-radius:50%;background:var(--linha)}
a.proj{color:var(--tinta)
}
footer{margin-top:72px;padding-top:24px;border-top:1px solid var(--linha);color:var(--cinza);font-size:.9rem}
footer a{color:var(--cinza)}
"""


def mes(v):
    if not v:
        return "hoje"
    ano, m = str(v).split("-")[:2]
    return f"{MESES[int(m) - 1]}/{ano}"


def e(s):
    return html.escape(str(s))


def experiencia(d):
    out = ["<h2>Experiência</h2>"]
    for exp in d["experiencia"]:
        out.append('<div class="item">')
        out.append(f'<div class="cab"><b>{e(exp["cargo"])}</b><span>{mes(exp["inicio"])} – {mes(exp["fim"])}</span></div>')
        out.append(f'<div class="empresa">{e(exp["empresa"])} · {e(exp.get("local", ""))}</div>')
        out.append("<ul>" + "".join(f"<li>{e(x)}</li>" for x in exp["destaques"]) + "</ul>")
        out.append("</div>")
    return out


def projetos(d):
    itens = [x for x in d["projetos"] if x.get("status") == "publico"]
    itens.sort(key=lambda x: (x.get("ordem", 99), str(x["data"])))
    out = ["<h2>Projetos</h2>"]
    for x in itens:
        link = x["links"][0] if x.get("links") else None
        nome = f'<a href="{e(link)}">{e(x["titulo"])}</a>' if link else e(x["titulo"])
        out.append('<div class="item">')
        out.append(f'<div class="cab"><b class="proj">{nome}</b><span>{mes(x["data"])}</span></div>')
        out.append(f'<div class="empresa">{e(x["resumo"])}</div>')
        out.append("</div>")
    return out


def render(d):
    p = d["pessoa"]
    user = p["github"].rstrip("/").rsplit("/", 1)[-1]
    out = [
        "<!doctype html>",
        '<html lang="pt-BR">',
        "<meta charset=\"utf-8\">",
        f'<title>{e(p["nome"])}</title>',
        f'<meta name="description" content="{e(p["resumo"].strip())}">',
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">",
        f"<style>{CSS}</style>",
        "<main>",
        "<header>",
        f'<h1>{e(p["nome"])}</h1>',
        f'<div class="titulo">{e(p["titulo"])}</div>',
        f'<div class="local">{e(p["local"])}</div>',
        '<div class="contato">',
        f'<a href="{e(p["linkedin"])}">LinkedIn</a>',
        f'<a href="mailto:{e(p["email"])}">E-mail</a>',
        f'<a href="{e(p["github"])}">GitHub</a>',
        "</div>",
        f'<p class="resumo">{e(p["resumo"].strip())}</p>',
        "</header>",
        *experiencia(d),
        *projetos(d),
        "<h2>Formação</h2>",
        *[
            f'<div class="item"><div class="cab"><b>{e(f["curso"])}</b><span>{e(f["periodo"])}</span></div><div class="empresa">{e(f["instituicao"])}</div></div>'
            for f in d["formacao"]
        ],
        "<h2>Certificações</h2>",
        "<ul>" + "".join(f"<li>{e(c)}</li>" for c in d["certificacoes"]) + "</ul>",
        "<h2>Skills</h2>",
        "<ul>"
        + "".join(f"<li><b>{e(ROTULOS.get(k, k))}:</b> {e(', '.join(v))}</li>" for k, v in d["skills"].items())
        + "</ul>",
        "<h2>Idiomas</h2>",
        "<ul>" + "".join(f"<li>{e(i)}</li>" for i in d["idiomas"]) + "</ul>",
        f'<footer>Código e registro: <a href="{e(p["github"])}">{user}</a></footer>',
        "</main>",
        "</html>",
    ]
    return "\n".join(out)


if __name__ == "__main__":
    src, dst = (sys.argv[1:] + ["carreira.yaml", "dist/index.html"])[:2]
    data = yaml.safe_load(Path(src).read_text(encoding="utf-8"))
    target = Path(dst)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render(data), encoding="utf-8")
