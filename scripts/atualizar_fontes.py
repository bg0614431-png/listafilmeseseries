from pathlib import Path
from urllib.request import Request, urlopen

BASE = Path(__file__).resolve().parent.parent
FONTES = BASE / "fontes" / "urls.txt"

for linha in FONTES.read_text(encoding="utf-8-sig").splitlines():
    linha = linha.strip()

    if not linha or linha.startswith("#"):
        continue

    destino, url = linha.split("|", 1)
    destino = BASE / destino

    destino.parent.mkdir(parents=True, exist_ok=True)

    print(f"Baixando: {destino}")

    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})

    with urlopen(req, timeout=120) as resposta:
        destino.write_bytes(resposta.read())

print("Fontes atualizadas com sucesso.")
