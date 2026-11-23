"""Gera README.md a partir de carreira.yaml. Só entram projetos com status: publico."""
import sys
from pathlib import Path

import yaml

MESES = "jan fev mar abr mai jun jul ago set out nov dez".split()
ROTULOS = {"dados_ia": "Dados, IA e automação", "operacoes": "Operações", "cliente": "Cliente", "financeiro": "Mercado financeiro"}


def mes(v):
    if not v:
        return "hoje"
    ano, m = str(v).split("-")[:2]
    return f"{MESES[int(m) - 1]}/{ano}"


def render(d):
    p = d["pessoa"]
    user = p["github"].rstrip("/").rsplit("/", 1)[-1]
    out = [
        f"# {p['nome']}",
        "",
        f"**{p['titulo']}**  ",
        f"{p['local']}",
        "",
        p["resumo"].strip(),
        "",
        f"[LinkedIn]({p['linkedin']}) · [E-mail](mailto:{p['email']})"
        + (f" · [Site](https://{p['dominio']})" if p.get("dominio") and p["dominio"] != "TODO" else ""),
        "",
        '<div align="center">',
        f'  <img src="https://github-readme-stats.vercel.app/api?username={user}&show_icons=true" alt="Estatísticas do GitHub" />',
        f'  <img src="https://github-readme-stats.vercel.app/api/top-langs/?username={user}&layout=compact" alt="Linguagens mais usadas" />',
        "</div>",
        "",
        "## Experiência",
        "",
    ]
    for e in d["experiencia"]:
        out.append(f"**{e['cargo']}** · {e['empresa']} · {mes(e['inicio'])} – {mes(e['fim'])}")
        out += [f"- {x}" for x in e["destaques"]]
        out.append("")
    projetos = [x for x in d["projetos"] if x.get("status") == "publico"]
    if projetos:
        out += ["## Projetos", ""]
        for x in sorted(projetos, key=lambda x: (x.get("ordem", 99), str(x["data"])), reverse=False):
            link = x["links"][0] if x.get("links") else None
            nome = f"[{x['titulo']}]({link})" if link else x["titulo"]
            out.append(f"- **{nome}** ({mes(x['data'])}): {x['resumo']}")
        out.append("")
    out += ["## Formação", ""]
    out += [f"- {f['curso']}, {f['instituicao']} ({f['periodo']})" for f in d["formacao"]]
    out += ["", "## Certificações", ""] + [f"- {c}" for c in d["certificacoes"]]
    out += ["", "## Skills", ""]
    out += [f"- **{ROTULOS.get(k, k)}:** {', '.join(v)}" for k, v in d["skills"].items()]
    out += ["", f"_Idiomas: {', '.join(d['idiomas'])}_", ""]
    return "
".join(out)


if __name__ == "__main__":
    src, dst = (sys.argv[1:] + ["carreira.yaml", "README.md"])[:2]
    Path(dst).write_text(render(yaml.safe_load(Path(src).read_text(encoding="utf-8"))), encoding="utf-8")
