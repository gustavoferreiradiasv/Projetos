
import argparse
import json
import logging
import shutil
import sys
import time
from pathlib import Path

DEFAULT_CONFIG_PATH = Path(__file__).parent / "config.json"
OUTROS_CATEGORIA = "Outros"


def setup_logging(log_file: Path) -> None:
    """Configura o log para arquivo e para o terminal ao mesmo tempo."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )


def load_config(config_path: Path) -> dict:
    """Carrega o mapeamento de categorias -> extensões a partir do JSON."""
    if not config_path.exists():
        raise FileNotFoundError(f"Arquivo de configuração não encontrado: {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_extension_map(config: dict) -> dict:
    """Inverte o config para consulta rápida: extensão -> categoria."""
    extension_map = {}
    for categoria, extensoes in config.items():
        for ext in extensoes:
            extension_map[ext.lower()] = categoria
    return extension_map


def get_category(file_path: Path, extension_map: dict) -> str:
    """Retorna a categoria de um arquivo com base na extensão."""
    return extension_map.get(file_path.suffix.lower(), OUTROS_CATEGORIA)


def resolve_conflict(destino: Path) -> Path:
    """
    Evita sobrescrever arquivos com o mesmo nome, adicionando um
    sufixo numérico: exemplo.pdf -> exemplo (1).pdf
    """
    if not destino.exists():
        return destino

    contador = 1
    novo_destino = destino
    while novo_destino.exists():
        novo_destino = destino.with_name(f"{destino.stem} ({contador}){destino.suffix}")
        contador += 1
    return novo_destino


def organize(source: Path, extension_map: dict, dry_run: bool = False) -> dict:
    """
    Organiza os arquivos da pasta `source` em subpastas por categoria.
    Retorna um resumo com a contagem de arquivos movidos por categoria.
    """
    if not source.exists() or not source.is_dir():
        raise NotADirectoryError(f"A pasta informada não existe: {source}")

    resumo = {}

    arquivos = [f for f in source.iterdir() if f.is_file()]

    for arquivo in arquivos:
        categoria = get_category(arquivo, extension_map)
        pasta_destino = source / categoria
        destino = resolve_conflict(pasta_destino / arquivo.name)

        if dry_run:
            logging.info("[SIMULAÇÃO] %s -> %s/", arquivo.name, categoria)
        else:
            pasta_destino.mkdir(exist_ok=True)
            shutil.move(str(arquivo), str(destino))
            logging.info("Movido: %s -> %s/", arquivo.name, categoria)

        resumo[categoria] = resumo.get(categoria, 0) + 1

    return resumo


def watch(source: Path, extension_map: dict, interval: int = 5) -> None:
    """
    Monitora a pasta continuamente e organiza novos arquivos assim
    que aparecem. Usa polling simples (sem dependências externas).
    Pressione Ctrl+C para parar.
    """
    logging.info("Monitorando %s a cada %ss (Ctrl+C para sair)...", source, interval)
    try:
        while True:
            resumo = organize(source, extension_map, dry_run=False)
            if resumo:
                logging.info("Resumo desta rodada: %s", resumo)
            time.sleep(interval)
    except KeyboardInterrupt:
        logging.info("Monitoramento encerrado pelo usuário.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Organiza arquivos de uma pasta em subpastas por categoria."
    )
    parser.add_argument(
        "--source", "-s", required=True, help="Caminho da pasta a ser organizada"
    )
    parser.add_argument(
        "--config", "-c", default=str(DEFAULT_CONFIG_PATH), help="Caminho do config.json"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Simula a organização sem mover arquivos"
    )
    parser.add_argument(
        "--watch", "-w", action="store_true", help="Monitora a pasta continuamente"
    )
    parser.add_argument(
        "--interval", type=int, default=5, help="Intervalo (s) entre checagens no modo --watch"
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source = Path(args.source).expanduser().resolve()

    setup_logging(source.parent / "organizer.log" if source.exists() else Path("organizer.log"))

    config = load_config(Path(args.config))
    extension_map = build_extension_map(config)

    if args.watch:
        watch(source, extension_map, interval=args.interval)
        return

    resumo = organize(source, extension_map, dry_run=args.dry_run)

    if not resumo:
        logging.info("Nenhum arquivo encontrado para organizar em %s", source)
    else:
        logging.info("Concluído! Resumo: %s", resumo)


if __name__ == "__main__":
    main()
