"""Gera a página bento (dist/index-<variante>.html) a partir de carreira.yaml.
Design system: Shared/ui-ux-pro-max/design-system/carreira/MASTER.md (Design Max + direção do dono).
Uso: python3 scripts/render_bento.py carreira.yaml a|b|c [dist/index.html]
Variações (MASTER.md): a=Sóbrio b=Apple-bento c=Compacto
"""
import html
import sys
from pathlib import Path

import yaml

MESES = "jan fev mar abr mai jun jul ago set out nov dez".split()
ROTULOS = {"dados_ia": "Dados, IA e automação", "operacoes": "Operações", "cliente": "Cliente", "financeiro": "Mercado financeiro"}

VARIANTS = {
    # raio, gap, padding, padding principal, brilho (0 = sem), pele
    "a": (16, 16, 24, 32, 0.06, "dev"),
    "b": (24, 20, 28, 36, 0.10, "dev"),
    "c": (16, 12, 20, 28, 0.0, "dev"),
    "d": (12, 16, 24, 32, 0.0, "mui"),
    "e": (12, 16, 24, 32, 0.0, "m3"),
}

SKINS = {
    # conceitos do Material UI (mui/material-ui): paper + elevação, claro, azul primary, Roboto
    "dev": dict(
        scheme="dark", font='-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif',
        bg="#161925", card="#1f2230", borderc="#2e3245",
        shadow="none", shadowh="none",
        text="#e7e9f0", muted="#a3a8ba", accent="#b49cfc", line="#8b5cf6",
        tagbg="rgba(139,92,246,.16)", tagborder="transparent", tagtext="#b49cfc",
        btnradius="10px", btnborder="#8b5cf6", btnhoverbg="rgba(139,92,246,.16)", btnhoverborder="#b49cfc",
        focus="#b49cfc", hairline="#2e3245", printcolors="", extra="",
    ),
    "mui": dict(
        scheme="light", font='Roboto,"Helvetica Neue",Arial,sans-serif',
        bg="#f5f5f5", card="#ffffff", borderc="transparent",
        shadow="0 2px 4px rgba(0,0,0,.08), 0 1px 2px rgba(0,0,0,.06)",
        shadowh="0 6px 12px rgba(0,0,0,.10), 0 2px 4px rgba(0,0,0,.08)",
        text="#212121", muted="#616161", accent="#1976d2", line="#1976d2",
        tagbg="rgba(25,118,210,.08)", tagborder="rgba(25,118,210,.35)", tagtext="#1976d2",
        btnradius="4px", btnborder="rgba(25,118,210,.5)", btnhoverbg="rgba(25,118,210,.04)", btnhoverborder="#1976d2",
        focus="#1976d2", hairline="rgba(0,0,0,.12)",
        printcolors="@media print{.card,.principal{box-shadow:none!important;border-color:#ccc}}",
        extra="",
    ),
    # Material You / MD3 (hiratazx/material-you-css, MIT): tokens vendados em scripts/m3-tokens.css;
    # a página segue claro/escuro do sistema (comportamento Material You)
    "m3": dict(
        scheme="light dark", font='Roboto,"Helvetica Neue",Arial,sans-serif',
        bg="var(--md-sys-color-background)", card="var(--md-sys-color-surface-container-low)", borderc="transparent",
        shadow="0px 1px 2px rgba(0,0,0,.3), 0px 1px 3px 1px rgba(0,0,0,.15)",
        shadowh="0px 1px 2px rgba(0,0,0,.3), 0px 2px 6px 2px rgba(0,0,0,.15)",
        text="var(--md-sys-color-on-surface)", muted="var(--md-sys-color-on-surface-variant)",
        accent="var(--md-sys-color-primary)", line="var(--md-sys-color-primary)",
        tagbg="transparent", tagborder="var(--md-sys-color-outline)", tagtext="var(--md-sys-color-on-surface)",
        btnradius="var(--md-sys-shape-corner-full)", btnborder="transparent", btnhoverbg="var(--md-sys-color-secondary-container)", btnhoverborder="transparent",
        focus="var(--md-sys-color-primary)", hairline="var(--md-sys-color-outline-variant)",
        printcolors="",
        extra="""
/* Componentes MD3 adaptados do material-you-css (MIT) para as classes do gerador */
.card{border-radius:var(--md-sys-shape-corner-medium);overflow:hidden;position:relative;
transition:box-shadow var(--md-sys-motion-duration-short4) var(--md-sys-motion-easing-standard)}
.btn{position:relative;height:40px;padding:0 24px;font-size:var(--md-sys-typescale-label-large-size);
font-weight:var(--md-sys-typescale-label-large-weight);letter-spacing:var(--md-sys-typescale-label-large-tracking)}
.btn:hover{box-shadow:0px 1px 2px rgba(0,0,0,.3),0px 1px 3px 1px rgba(0,0,0,.15)}
.btn::after,a.linkcard::after{content:'';position:absolute;inset:0;background:currentColor;opacity:0;
transition:opacity var(--md-sys-motion-duration-short4) var(--md-sys-motion-easing-standard);pointer-events:none}
.btn:hover::after,a.linkcard:hover::after{opacity:var(--md-sys-state-hover-opacity)}
.btn:focus-visible::after,a.linkcard:focus-visible::after{opacity:var(--md-sys-state-focus-opacity)}
.btn:focus-visible,a.linkcard:focus-visible{outline:none}
.tag{font-family:inherit;font-size:var(--md-sys-typescale-label-large-size);padding:0 16px;height:32px;
display:inline-flex;align-items:center;border-radius:var(--md-sys-shape-corner-small);white-space:nowrap}
@media (prefers-reduced-motion:reduce){.card,.btn{transition:none}}
""",
    ),
}

ICON = {
    "linkedin": '<svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"><circle cx="12" cy="8" r="3.4"/><path d="M5.5 19.5c.9-3.7 3.4-5.6 6.5-5.6s5.6 1.9 6.5 5.6"/></svg>',
    "mail": '<svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="5.5" width="18" height="13" rx="2"/><path d="m4 7 8 6 8-6"/></svg>',
    "github": '<svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"><line x1="6" y1="3" x2="6" y2="15"/><circle cx="6" cy="18" r="2.6"/><circle cx="18" cy="6" r="2.6"/><path d="M18 8.6c0 4.6-4.4 5-8.4 6.4"/></svg>',
    "bag": '<svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="8" width="18" height="12" rx="2"/><path d="M9 8V6a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v2"/></svg>',
    "cap": '<svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M12 4 2 9l10 5 10-5-10-5Z"/><path d="M6 12v4.5c3.4 2.4 8.6 2.4 12 0V12"/></svg>',
}

FAVICON = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='8' fill='%23161925'/%3E%3Cpath d='M12 11 9 16l3 5M20 11l3 5-3 5' stroke='%23b49cfc' stroke-width='2.4' fill='none' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E"


def mes(v):
    if not v:
        return "hoje"
    ano, m = str(v).split("-")[:2]
    return f"{MESES[int(m) - 1]}/{ano}"


def e(s):
    return html.escape(str(s))


def css(v):
    raio, gap, pad, padlg, brilho, skin_name = VARIANTS[v]
    s = SKINS[skin_name]
    glow = f"radial-gradient(150% 150% at 100% 0%, rgba(139,92,246,{brilho}) 0%, rgba(139,92,246,0) 55%), " if brilho else ""
    base = f"""
:root{{--bg:{s['bg']};--card:{s['card']};--borderc:{s['borderc']};--text:{s['text']};--muted:{s['muted']};
--accent:{s['accent']};--line:{s['line']};--tag:{s['tagbg']};--tagborder:{s['tagborder']};--tagtext:{s['tagtext']};
--focus:{s['focus']};--shadow:{s['shadow']};--shadowh:{s['shadowh']};--btnradius:{s['btnradius']};
--btnborder:{s['btnborder']};--btnhoverbg:{s['btnhoverbg']};--btnhoverborder:{s['btnhoverborder']};
--raio:{raio}px;--gap:{gap}px;--pad:{pad}px;--padlg:{padlg}px;--hairline:{s['hairline']};color-scheme:{s['scheme']}}}
*{{margin:0;padding:0;box-sizing:border-box}}
html{{-webkit-text-size-adjust:100%}}
body{{font:16px/1.5 {s['font']};
color:var(--text);background:var(--bg);max-width:1200px;margin:0 auto;padding:var(--gap) 16px 48px}}
.mono{{font-family:ui-monospace,"SF Mono",Menlo,Consolas,"Liberation Mono",monospace}}
.rot{{font-family:ui-monospace,"SF Mono",Menlo,Consolas,"Liberation Mono",monospace;
font-size:.8125rem;font-weight:500;letter-spacing:.02em;color:var(--accent);margin-bottom:12px}}
.grid{{display:grid;grid-template-columns:repeat(12,1fr);grid-auto-flow:dense;grid-auto-rows:auto;gap:var(--gap)}}
.card{{background:var(--card);border:1px solid var(--borderc);box-shadow:var(--shadow);border-radius:var(--raio);padding:var(--pad)}}
.span8{{grid-column:span 8}}.span4{{grid-column:span 4}}.span3{{grid-column:span 3}}.span6{{grid-column:span 6}}
.principal{{grid-column:span 8;grid-row:span 2;padding:var(--padlg);
background:{glow}var(--card)}}
h1{{font-size:clamp(2.2rem,5vw,3.5rem);font-weight:700;letter-spacing:-.02em;line-height:1.1;overflow-wrap:anywhere}}
.cargo{{font-size:1.25rem;font-weight:500;color:var(--accent);margin-top:8px}}
.resumo{{margin-top:16px;max-inline-size:65ch;color:var(--text)}}
.local{{margin-top:14px;font-size:.8125rem;color:var(--muted)}}
.botoes{{display:flex;flex-wrap:wrap;gap:10px;margin-top:6px}}
.btn{{display:inline-flex;align-items:center;gap:8px;padding:10px 14px;border-radius:var(--btnradius);
border:1px solid var(--btnborder);color:var(--text);text-decoration:none;cursor:pointer;
transition:border-color .15s,background-color .15s}}
.btn:hover{{background:var(--btnhoverbg);border-color:var(--btnhoverborder)}}
.btn:focus-visible{{outline:2px solid var(--focus);outline-offset:3px}}
.tags{{display:flex;flex-wrap:wrap;gap:8px}}
.tag{{font-family:ui-monospace,"SF Mono",Menlo,Consolas,"Liberation Mono",monospace;
font-size:.8125rem;padding:4px 10px;border-radius:999px;background:var(--tag);
border:1px solid var(--tagborder);color:var(--tagtext)}}
.projeto h3 a{{font-size:1.125rem;font-weight:600;color:var(--text);text-decoration:none;overflow-wrap:anywhere;cursor:pointer}}
.projeto h3 a:hover{{color:var(--accent)}}
.projeto h3 a:focus-visible{{outline:2px solid var(--focus);outline-offset:3px}}
a.linkcard{{display:block;text-decoration:none;color:inherit;cursor:pointer}}
a.linkcard:focus-visible{{outline:2px solid var(--focus);outline-offset:3px;border-radius:var(--raio)}}
a.linkcard:hover,.projeto:hover{{border-color:var(--line)}}
.projeto{{transition:border-color .18s ease-out,transform .18s ease-out,box-shadow .18s ease-out}}
a.linkcard:hover{{transform:translateY(-2px);box-shadow:var(--shadowh)}}
.data{{font-family:ui-monospace,"SF Mono",Menlo,Consolas,"Liberation Mono",monospace;
font-size:.8125rem;color:var(--muted);margin-top:6px}}
.desc{{margin-top:10px;color:var(--muted)}}
.stack-grupos{{display:grid;grid-template-columns:1fr 1fr;gap:18px 28px}}
.stack-grupos h4{{font-size:.8125rem;font-weight:500;color:var(--muted);margin-bottom:8px;font-family:ui-monospace,"SF Mono",Menlo,Consolas,"Liberation Mono",monospace}}
.timeline{{border-left:2px solid var(--line);margin:10px 0 0 7px;padding-left:24px;display:flex;flex-direction:column;gap:28px}}
.item h3{{font-size:1.125rem;font-weight:600;overflow-wrap:anywhere}}
.item .meta{{color:var(--muted);margin-top:2px;font-size:.95rem}}
.item .periodo{{font-family:ui-monospace,"SF Mono",Menlo,Consolas,"Liberation Mono",monospace;
font-size:.8125rem;color:var(--muted);margin-top:4px}}
.item ul{{list-style:none;margin-top:10px}}
.item li{{padding-left:18px;position:relative;margin-bottom:6px;color:var(--text)}}
.item li::before{{content:"";position:absolute;left:2px;top:.72em;width:7px;height:1.5px;background:var(--line)}}
h2.rot{{font-size:.8125rem}}
.rodape{{margin-top:48px;padding-top:24px;border-top:1px solid var(--hairline);
font-size:.9rem;color:var(--muted)}}
.rodape a{{color:var(--muted);text-decoration:none;border-bottom:1px solid var(--hairline)}}
.rodape a:hover{{color:var(--accent)}}
.rodape a:focus-visible{{outline:2px solid var(--focus);outline-offset:3px}}
@media (prefers-reduced-motion:reduce){{*,*::before,*::after{{transition:none!important;transform:none!important}}}}
@media (max-width:1023px){{
.grid{{grid-template-columns:repeat(6,1fr)}}
.principal,.span8,.span6{{grid-column:span 6}}
.span4,.span3{{grid-column:span 3}}
.stack-grupos{{grid-template-columns:1fr}}
}}
@media (max-width:767px){{
.grid{{grid-template-columns:1fr}}
.principal{{grid-row:auto}}
.principal,.span8,.span6,.span4,.span3{{grid-column:span 1}}
}}
@media print{{
body{{background:#fff;color:#111;max-width:none}}
.card,.principal{{background:#fff!important;border-color:#ccc;color:#111}}
h1,.item li,.resumo,.desc,.meta{{color:#111!important}}
.rot,.cargo{{color:#5b21b6!important}}
.btn,.rodape a{{border-color:#999}}
a{{text-decoration:underline}}
.timeline{{border-color:#999}}
}}
"""
    tokens = ""
    if skin_name == "m3":
        tokens = (Path(__file__).parent / "m3-tokens.css").read_text(encoding="utf-8") + "\n"
    return tokens + base + s["extra"]


def tags(itens):
    return "".join(f'<span class="tag">{e(x)}</span>' for x in itens)


def render(d, v):
    p = d["pessoa"]
    user = p["github"].rstrip("/").rsplit("/", 1)[-1]
    projs = [x for x in d["projetos"] if x.get("status") == "publico"]
    projs.sort(key=lambda x: (x.get("ordem", 99), str(x["data"])))

    cards = [f'<section class="card principal">']
    cards.append(f'<h1>{e(p["nome"])}</h1>')
    cards.append(f'<div class="cargo">{e(p["titulo"])}</div>')
    cards.append(f'<p class="resumo">{e(p["resumo"].strip())}</p>')
    cards.append(f'<div class="local">{e(p["local"])}</div>')
    cards.append("</section>")

    cards.append('<section class="card span4">')
    cards.append('<div class="rot">// contato</div>')
    cards.append('<div class="botoes">')
    cards.append(f'<a class="btn" href="{e(p["linkedin"])}">{ICON["linkedin"]}LinkedIn</a>')
    cards.append(f'<a class="btn" href="mailto:{e(p["email"])}">{ICON["mail"]}E-mail</a>')
    cards.append(f'<a class="btn" href="{e(p["github"])}">{ICON["github"]}GitHub</a>')
    cards.append("</div></section>")

    cards.append('<section class="card span4">')
    cards.append('<div class="rot">// certificações</div>')
    cards.append('<div class="tags">' + tags(d["certificacoes"] + d["idiomas"]) + "</div>")
    cards.append("</section>")

    for x in projs:
        link = x["links"][0] if x.get("links") else None
        cards.append('<section class="card projeto span8">' if (x.get("ordem") == 1 or projs.index(x) == 0) else '<section class="card projeto span4">')
        cards.append('<div class="rot">// projeto</div>')
        cards.append("<h3>")
        if link:
            cards.append(f'<a class="linkcard" href="{e(link)}">{e(x["titulo"])}</a>')
        else:
            cards.append(e(x["titulo"]))
        cards.append("</h3>")
        cards.append(f'<div class="data">{mes(x["data"])}</div>')
        cards.append(f'<p class="desc">{e(x["resumo"])}</p>')
        cards.append("</section>")

    cards.append('<section class="card span8">')
    cards.append('<div class="rot">// stack</div>')
    cards.append('<div class="stack-grupos">')
    for k, vals in d["skills"].items():
        cards.append(f'<div><h4>{e(ROTULOS.get(k, k))}</h4><div class="tags">{tags(vals)}</div></div>')
    cards.append("</div></section>")

    tl = ['<h2 class="rot">// experiência</h2>', '<div class="timeline">']
    for exp in d["experiencia"]:
        tl.append('<div class="item">')
        tl.append(f'<h3>{e(exp["cargo"])}</h3>')
        tl.append(f'<div class="meta">{e(exp["empresa"])} · {e(exp.get("local", ""))}</div>')
        tl.append(f'<div class="periodo">{mes(exp["inicio"])} – {mes(exp["fim"])}</div>')
        tl.append("<ul>" + "".join(f"<li>{e(x)}</li>" for x in exp["destaques"]) + "</ul>")
        tl.append("</div>")
    tl.append("</div>")

    tl += ['<h2 class="rot" style="margin-top:40px">// formação</h2>', '<div class="timeline">']
    for f in d["formacao"]:
        tl.append('<div class="item">')
        tl.append(f'<h3>{e(f["curso"])}</h3>')
        tl.append(f'<div class="meta">{e(f["instituicao"])}</div>')
        tl.append(f'<div class="periodo">{e(f["periodo"])}</div>')
        tl.append("</div>")
    tl.append("</div>")

    out = [
        "<!doctype html>",
        '<html lang="pt-BR">',
        "<meta charset=\"utf-8\">",
        f'<title>{e(p["nome"])}</title>',
        f'<meta name="description" content="{e(p["resumo"].strip())}">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        f'<link rel="icon" href="{FAVICON}">',
        f"<style>{css(v)}</style>",
        '<div class="grid">' + "".join(cards) + "</div>",
        *tl,
        f'<footer class="rodape">Código e registro: <a href="{e(p["github"])}">github.com/{e(user)}</a></footer>',
        "</html>",
    ]
    return "\n".join(out)


if __name__ == "__main__":
    src, v, dst = (sys.argv[1:] + ["carreira.yaml", "a", "dist/index.html"])[:3]
    assert v in VARIANTS, f"variante inválida: {v}"
    data = yaml.safe_load(Path(src).read_text(encoding="utf-8"))
    target = Path(dst)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render(data, v), encoding="utf-8")
