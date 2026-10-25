#!/usr/bin/env python3
"""Monta o documento de resultados do Painel de histórias.

Junta o painel-status.json publicado pelo GitHub Actions (repositório
público FARMAI-GIT/farmai-testes-status) com as histórias exportadas do
painel e gera um único documento com, para cada história:
  - ct: os critérios de aceite (Hxx-CA01, Hxx-CA02...) e quantos passaram;
  - ia: os casos de referência da IA ligados à história e quantos passaram.

Uso:
  python3 -I sincroniza-painel.py --status painel-status.json \
      --historias <pasta com H01.json, H02.json...> --saida ultimo.json

Status de um CT (critério):
  sem teste  nenhum teste tem a tag do critério
  falhou     algum teste do critério falhou
  passou     todos os testes do critério passaram
  pendente   os testes existem, mas foram pulados ou ainda não foram escritos
"""
import argparse
import datetime as dt
import glob
import json
import os
import re


def status_de(lista):
    if not lista:
        return "sem teste"
    if "falhou" in lista:
        return "falhou"
    if all(s == "passou" for s in lista):
        return "passou"
    return "pendente"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--status", required=True)
    ap.add_argument("--historias", required=True)
    ap.add_argument("--saida", required=True)
    a = ap.parse_args()

    st = json.load(open(a.status, encoding="utf-8"))
    if st.get("formato") != 2:
        raise SystemExit("Formato de status desconhecido")
    run = st.get("run") or {}
    tags = {k: v for k, v in (st.get("tags") or {}).items() if re.fullmatch(r"H\d+-CA\d+", k)}
    golden = {k: v for k, v in (st.get("golden") or {}).items() if re.fullmatch(r"GD-[A-Z]+-\d+", k)}

    historias = {}
    for f in sorted(glob.glob(os.path.join(a.historias, "*.json"))):
        s = json.load(open(f, encoding="utf-8"))
        sid = s.get("id")
        if not isinstance(sid, str) or not re.fullmatch(r"H\d+", sid):
            continue
        itens = []
        for i, _c in enumerate(s.get("criterios") or []):
            codigo = f"{sid}-CA{i + 1:02d}"
            lst = tags.get(codigo, [])
            itens.append({"codigo": codigo, "status": status_de(lst), "testes": len(lst)})
        ia = [
            {"id": gid, "status": g.get("status")}
            for gid, g in sorted(golden.items())
            if sid in (g.get("historias") or [])
        ]
        historias[sid] = {
            "ct": {
                "passou": sum(1 for x in itens if x["status"] == "passou"),
                "falhou": sum(1 for x in itens if x["status"] == "falhou"),
                "total": len(itens),
                "itens": itens,
            },
            "ia": {
                "passou": sum(1 for x in ia if x["status"] == "passou"),
                "falhou": sum(1 for x in ia if x["status"] == "falhou"),
                "total": len(ia),
                "itens": ia,
            },
        }

    tot = st.get("totais") or {}
    doc = {
        "runId": str(run.get("id")),
        "runNumero": run.get("numero"),
        "url": run.get("url"),
        "branch": run.get("branch"),
        "commit": run.get("commit"),
        "evento": run.get("evento"),
        "conclusao": run.get("conclusao"),
        "concluidoEm": run.get("concluidoEm"),
        "sincronizadoEm": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "totais": {
            "passou": tot.get("passou", 0),
            "falhou": tot.get("falhou", 0),
            "pulado": tot.get("pulado", 0),
            "pendente": tot.get("pendente", 0),
            "ctPassou": sum(h["ct"]["passou"] for h in historias.values()),
            "ctTotal": sum(h["ct"]["total"] for h in historias.values()),
            "iaPassou": sum(1 for g in golden.values() if g.get("status") == "passou"),
            "iaTotal": len(golden),
        },
        "historias": historias,
    }
    json.dump(doc, open(a.saida, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    t = doc["totais"]
    print(
        f"Rodada #{doc['runNumero']} ({doc['conclusao']}): "
        f"{t['ctPassou']}/{t['ctTotal']} CTs passed, IA {t['iaPassou']}/{t['iaTotal']}"
    )


if __name__ == "__main__":
    main()
