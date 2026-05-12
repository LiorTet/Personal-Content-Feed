import time
from typing import Any

from core.logger_format import logger


class TrackInference:
    def __enter__(self) -> "TrackInference":
        self.start_time = time.perf_counter()
        self.duration = 0.0
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.duration = time.perf_counter() - self.start_time
        if exc_type is None:
            logger.info("Agent Scout Inference Complete", extra={"latency": self.duration})
