from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
PLAYLISTS = BASE / "playlists"
SAIDA = BASE / "MinhaLista.m3u"

fontes = [
    PLAYLISTS / "tv.m3u",
    PLAYLISTS / "filmes.m3u",
    PLAYLISTS / "series.m3u",
]

linhas = ["#EXTM3U"]

for arquivo in fontes:
    if not arquivo.exists():
        continue

    conteudo = arquivo.read_text(encoding="utf-8-sig", errors="ignore").splitlines()

    for linha in conteudo:
        linha = linha.strip()

        if not linha or linha == "#EXTM3U":
            continue

        linhas.append(linha)

SAIDA.write_text("\n".join(linhas) + "\n", encoding="utf-8")

print(f"Lista gerada: {SAIDA}")
print(f"Total de linhas: {len(linhas)}")
