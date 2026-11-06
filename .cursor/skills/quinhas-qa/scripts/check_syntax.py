"""Confere a sintaxe do JavaScript de index.html sem rodar o jogo.

Extrai cada <script> sem src, grava num arquivo temporario e roda `node --check`.
Uso (da raiz do projeto): python .cursor/skills/quinhas-qa/scripts/check_syntax.py [index.html]
Sai com 0 se tudo certo, 1 se houver erro de sintaxe. Nao instala nada; precisa de node no PATH.
"""
import os
import re
import subprocess
import sys
import tempfile


def main() -> int:
    path = sys.argv[1] if len(sys.argv) > 1 else "index.html"
    try:
        html = open(path, encoding="utf-8").read()
    except OSError as e:
        print(f"ERRO: nao consegui ler {path}: {e}")
        return 1

    scripts = [
        m.group(2)
        for m in re.finditer(r"<script([^>]*)>(.*?)</script>", html, re.S)
        if "src=" not in m.group(1)
    ]
    if not scripts:
        print("ERRO: nenhum <script> inline encontrado")
        return 1

    bad = 0
    for i, code in enumerate(scripts, 1):
        with tempfile.NamedTemporaryFile(
            "w", suffix=".js", delete=False, encoding="utf-8"
        ) as tmp:
            tmp.write(code)
            name = tmp.name
        try:
            r = subprocess.run(
                ["node", "--check", name], capture_output=True, text=True
            )
        except FileNotFoundError:
            print("ERRO: node nao encontrado no PATH")
            return 1
        finally:
            os.unlink(name)
        if r.returncode:
            bad += 1
            print(f"script {i}: ERRO de sintaxe\n{r.stderr.strip()}")
        else:
            print(f"script {i}: ok ({len(code.splitlines())} linhas)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
