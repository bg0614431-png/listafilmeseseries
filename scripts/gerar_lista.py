from pathlib import Path
import re

BASE = Path(__file__).resolve().parent.parent
PLAYLISTS = BASE / "playlists"
SAIDA = BASE / "MinhaLista.m3u"

fontes = [
    PLAYLISTS / "tv.m3u",
    PLAYLISTS / "ManoSF.m3u",
    PLAYLISTS / "Cinema.m3u",
    PLAYLISTS / "filmes.m3u",
    PLAYLISTS / "series.m3u",
]

linhas = ["#EXTM3U"]
filmes = 0
series = 0

def classificar(extinf):
    texto = extinf.lower()

    if any(x in texto for x in [
        'group-title="filmes',
        'group-title="filme',
        'group-title="movie',
        'group-title="movies'
    ]):
        return "movie"

    if any(x in texto for x in [
        'group-title="série',
        'group-title="serie',
        'group-title="series',
        'group-title="dorama',
        'group-title="novela'
    ]):
        return "series"

    return None

def alterar_categoria(extinf, tipo):
    global filmes, series

    extinf = re.sub(r'\s+tvg-type="[^"]*"', "", extinf, flags=re.IGNORECASE)
    extinf = re.sub(r'\s+group-title="[^"]*"', "", extinf, flags=re.IGNORECASE)

    if tipo == "movie":
        categoria = "FILMES"
        filmes += 1
    else:
        categoria = "SERIES"
        series += 1

    pos = extinf.find(",")
    if pos >= 0:
        metadados = extinf[:pos]
        nome = extinf[pos:]
        metadados += f' tvg-type="{tipo}" group-title="{categoria}"'
        extinf = metadados + nome

    return extinf

for arquivo in fontes:
    if not arquivo.exists():
        continue

    conteudo = arquivo.read_text(
        encoding="utf-8-sig",
        errors="ignore"
    ).splitlines()

    for linha in conteudo:
        linha = linha.strip()

        if not linha or linha.startswith("#EXTM3U"):
            continue

        if linha.startswith("#EXTINF:"):
            tipo = classificar(linha)

            if tipo:
                linha = alterar_categoria(linha, tipo)

        linhas.append(linha)

SAIDA.write_text(
    "\n".join(linhas) + "\n",
    encoding="utf-8"
)

print(f"Lista gerada: {SAIDA}")
print(f"Total de linhas: {len(linhas)}")
print(f"Filmes classificados: {filmes}")
print(f"Séries classificadas: {series}")
