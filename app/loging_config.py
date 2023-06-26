import os
from logging.config import dictConfig

logger_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"default": {"format": "%(asctime)s - %(levelname)s - %(module)s - %(message)s"}},
    "handlers": {
        "default": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        }
    },
    "loggers": {"": {"handlers": ["default"], "level": os.getenv("LOGLEVEL", "INFO").upper()}},
}

dictConfig(logger_config)
