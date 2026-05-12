import logging
import sys


class StructuredFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "module": record.module,
            "message": record.getMessage(),
        }
        if hasattr(record, "latency"):
            log_data["latency_sec"] = f"{record.latency:.4f}s"
        return str(log_data)


def setup_logging() -> logging.Logger:
    logger = logging.getLogger("content_feed")
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(StructuredFormatter())
    logger.addHandler(handler)
    return logger


logger = setup_logging()
