"""
run_pipeline.py

Orquestador del pipeline de datos completo:
  1. ETL    — descarga datos crudos de Rickettsia y CONAGUA (make_dataset.py)
  2. Proceso — imputa, transforma y corrige fechas (make_processed_dataset.py)

Uso:
    uv run python src/data/run_pipeline.py

Para correr solo una etapa:
    uv run python src/data/make_dataset.py
    uv run python src/data/make_processed_dataset.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from make_dataset import main as etl
from make_processed_dataset import main as procesar


def main() -> None:
    print('=' * 60)
    print('ETAPA 1/2 — ETL (descarga de datos)')
    print('=' * 60)
    etl()

    print()
    print('=' * 60)
    print('ETAPA 2/2 — Procesamiento y feature engineering')
    print('=' * 60)
    procesar()

    print()
    print('Pipeline completado.')


if __name__ == '__main__':
    main()
