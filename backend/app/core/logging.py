import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from app.core.config_registry import ConfigRegistry


def setup_logging() -> logging.Logger:
    settings = ConfigRegistry.get_settings()
    log_dir = Path(settings.LOG_DIR)
    log_dir.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("voice_studio")
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
    logger.handlers.clear()

    try:
        from pythonjsonlogger import jsonlogger
        formatter = jsonlogger.JsonFormatter(
            '%(asctime)s %(levelname)s %(name)s %(message)s',
            rename_fields={"levelname": "level", "asctime": "timestamp"}
        )
    except ImportError:
        # Fallback if not installed yet
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s:%(lineno)d]: %(message)s"
        )

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    logger.addHandler(console_handler)

    # API Log Handler (rotating 10MB x 5 files)
    api_log_path = log_dir / "api.log"
    api_file_handler = RotatingFileHandler(
        api_log_path, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    api_file_handler.setFormatter(formatter)
    api_file_handler.setLevel(logging.INFO)
    logger.addHandler(api_file_handler)

    # Errors Log Handler
    errors_log_path = log_dir / "errors.log"
    error_file_handler = RotatingFileHandler(
        errors_log_path, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    error_file_handler.setFormatter(formatter)
    error_file_handler.setLevel(logging.ERROR)
    logger.addHandler(error_file_handler)

    return logger


logger = setup_logging()
