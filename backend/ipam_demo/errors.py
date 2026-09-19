"""Safe errors shared by the CLI and HTTP boundary."""

import sqlite3


class AppError(Exception):
    def __init__(self, code: str, message: str, status: int = 503, details=None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status = status
        self.details = details or {}

    def body(self, request_id: str) -> dict:
        return {"error": {"code": self.code, "message": self.message,
                          "details": self.details, "request_id": request_id}}


def store_error(error: sqlite3.Error) -> AppError:
    # Extended result codes retain the primary result in the low byte.
    code = getattr(error, "sqlite_errorcode", 0) & 0xFF
    if code in (sqlite3.SQLITE_BUSY, sqlite3.SQLITE_LOCKED):
        return AppError("STORE_BUSY", "The inventory store is busy. Retry the request.")
    return AppError("STORE_ERROR", "The inventory store could not complete the operation. See server logs.")
