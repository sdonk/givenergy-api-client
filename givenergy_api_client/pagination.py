from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class PaginationMeta(BaseModel):
    """Pagination metadata returned alongside paginated data lists."""

    model_config = ConfigDict(frozen=True)

    current_page: int
    last_page: int
    per_page: int
    total: int


class PaginatedResult[T](BaseModel):
    """Generic typed wrapper for paginated API responses."""

    model_config = ConfigDict(frozen=True)

    data: list[T]
    meta: PaginationMeta
