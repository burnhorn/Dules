import logging
import sys
import structlog
from typing import Any

def setup_logging(json_logs: bool = True, log_level: str = "INFO"):
    """
    애플리케이션 전체 로깅 설정
    """

    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
    ]

    structlog.configure(
        processors=shared_processors + [
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer() if json_logs else structlog.dev.ConsoleRenderer(),
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        processor=structlog.processors.JSONRenderer() if json_logs else structlog.dev.ConsoleRenderer(),
        foreign_pre_chain=shared_processors,
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(log_level.upper())

    for _log in ["uvicorn", "uvicorn.error", "uvicorn.access"]:
        logging.getLogger(_log).handlers = [handler]
        logging.getLogger(_log).propagate = False