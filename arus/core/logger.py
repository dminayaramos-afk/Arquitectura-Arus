"""
ARUS - Artificial Reasoning Unified System
------------------------------------------

Sistema centralizado de registro (logging).

Todos los módulos de ARUS deberán utilizar este logger.
"""

from __future__ import annotations

import logging

from arus.core.paths import LOGS_DIR, LOG_FILE

# Crear el directorio de logs si no existe
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Configuración global del logger
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)-8s %(name)s : %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)


def get_logger(name: str) -> logging.Logger:
    """
    Devuelve un logger configurado.

    Args:
        name: Nombre del módulo.

    Returns:
        logging.Logger
    """
    return logging.getLogger(name)
