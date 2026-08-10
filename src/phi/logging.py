"""Structured, deterministic logging for PHI.

Phase 1-2 observability is intentionally lightweight (SYSTEM_ARCHITECTURE §28):
structured logs via the standard library, no external log infrastructure. Logs are
JSON lines so that ingestion/validation/backtest runs are machine-auditable after
the fact without a live dashboard.

Timestamps are emitted in UTC and log records never include secret values
(PRD-SEC-001).
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import UTC, datetime
from typing import Any

_CONFIGURED = False


class JsonFormatter(logging.Formatter):
    """Render log records as single-line JSON for auditable, parseable output."""

    _RESERVED = frozenset(
        {
            "name", "msg", "args", "levelname", "levelno", "pathname", "filename",
            "module", "exc_info", "exc_text", "stack_info", "lineno", "funcName",
            "created", "msecs", "relativeCreated", "thread", "threadName",
            "processName", "process", "taskName",
        }
    )

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        # Merge structured extras passed via logger.info(..., extra={...}).
        for key, value in record.__dict__.items():
            if key not in self._RESERVED and not key.startswith("_"):
                payload[key] = value
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str, sort_keys=True)


def configure_logging(level: int | str = logging.INFO, *, stream: Any = None) -> None:
    """Configure the root ``phi`` logger once, idempotently.

    Args:
        level: Logging level (name or numeric).
        stream: Output stream; defaults to stderr so stdout stays clean for data.
    """
    global _CONFIGURED
    handler = logging.StreamHandler(stream or sys.stderr)
    handler.setFormatter(JsonFormatter())

    root = logging.getLogger("phi")
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)
    root.propagate = False
    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    """Return a namespaced child of the ``phi`` logger, configuring defaults once."""
    if not _CONFIGURED:
        configure_logging()
    if not name.startswith("phi"):
        name = f"phi.{name}"
    return logging.getLogger(name)
