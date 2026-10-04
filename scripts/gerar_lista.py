from pathlib import Path
import re

BASE = Path(__file__).resolve().parent.parent
PLAYLISTS = BASE / "playlists"
SAIDA = BASE / "MinhaLista.m3u"

# Listas que entram na biblioteca final.
# Arquivos de backup/trabalho são ignorados.
fontes = [
    PLAYLISTS / "tv.m3u",
    PLAYLISTS / "ManoSF.m3u",
    PLAYLISTS / "Cinema.m3u",
    PLAYLISTS / "filmes.m3u",
    PLAYLISTS / "series.m3u",
]

linhas = ["#EXTM3U"]
urls_vistas = set()

filmes = 0
series = 0
tv = 0
duplicadas = 0
invalidas = 0


def classificar(extinf, arquivo):
    texto = extinf.lower()
    nome_arquivo = arquivo.name.lower()

    # Cinema.m3u é tratado como FILMES mesmo que a fonte
    # não tenha group-title adequado.
    if nome_arquivo == "cinema.m3u":
        return "movie"

    # Filmes
    if any(x in texto for x in [
        'group-title="filmes',
        'group-title="filme',
        'group-title="movie',
        'group-title="movies'
    ]):
        return "movie"

    # Séries
    if any(x in texto for x in [
        'group-title="série',
        'group-title="serie',
        'group-title="series',
        'group-title="dorama',
        'group-title="novela'
    ]):
        return "series"

    return None


def normalizar_extinf(extinf, tipo):
    global filmes, series

    # Remove atributos antigos que vamos controlar.
    extinf = re.sub(
        r'\s+tvg-type="[^"]*"',
        "",
        extinf,
        flags=re.IGNORECASE
    )

    extinf = re.sub(
        r'\s+group-title="[^"]*"',
        "",
        extinf,
        flags=re.IGNORECASE
    )

    # Limpa espaços excessivos.
    extinf = re.sub(r"[ \t]+", " ", extinf).strip()

    if tipo == "movie":
        categoria = "FILMES"
        filmes += 1
    elif tipo == "series":
        categoria = "SERIES"
        series += 1
    else:
        return extinf

    pos = extinf.find(",")

    if pos < 0:
        return extinf

    metadados = extinf[:pos]
    nome = extinf[pos:]

    metadados += (
        f' tvg-type="{tipo}"'
        f' group-title="{categoria}"'
    )

    return metadados + nome


for arquivo in fontes:
    if not arquivo.exists():
        print(f"Ignorado (não existe): {arquivo.name}")
        continue

    print(f"Processando: {arquivo.name}")

    conteudo = arquivo.read_text(
        encoding="utf-8-sig",
        errors="replace"
    ).splitlines()

    i = 0

    while i < len(conteudo):
        linha = conteudo[i].strip()

        if not linha:
            i += 1
            continue

        # Ignora qualquer cabeçalho adicional.
        if linha.upper().startswith("#EXTM3U"):
            i += 1
            continue

        if linha.startswith("#EXTINF:"):
            extinf = linha

            # A URL normalmente está na linha seguinte.
            url = ""
            if i + 1 < len(conteudo):
                url = conteudo[i + 1].strip()

            if not url or url.startswith("#"):
                invalidas += 1
                i += 1
                continue

            # Deduplicação por URL.
            chave = url.strip()

            if chave in urls_vistas:
                duplicadas += 1
                i += 2
                continue

            urls_vistas.add(chave)

            tipo = classificar(extinf, arquivo)

            if tipo:
                extinf = normalizar_extinf(extinf, tipo)
            else:
                tv += 1

            linhas.append(extinf)
            linhas.append(url)

            i += 2
            continue

        # Outras linhas válidas são preservadas.
        linhas.append(linha)
        i += 1


SAIDA.write_text(
    "\n".join(linhas) + "\n",
    encoding="utf-8",
    newline="\n"
)

print("")
print("========================================")
print("       MINHA LISTA GERADA")
print("========================================")
print(f"Total de linhas:       {len(linhas)}")
print(f"Filmes:                {filmes}")
print(f"Séries:                {series}")
print(f"TV/outros:             {tv}")
print(f"Duplicadas removidas:  {duplicadas}")
print(f"Entradas inválidas:    {invalidas}")
print(f"URLs únicas:           {len(urls_vistas)}")
print("========================================")
print(f"Arquivo: {SAIDA}")
