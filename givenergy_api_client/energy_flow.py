from __future__ import annotations

from enum import IntEnum


class EnergyDataFlowGrouping(IntEnum):
    """Time grouping for energy flow data queries."""

    HALF_HOURLY = 0
    DAILY = 1
    MONTHLY = 2
    YEARLY = 3
    TOTAL = 4


class EnergyDataFlowType(IntEnum):
    """Direction of energy flow between components."""

    PV_TO_HOME = 0
    PV_TO_BATTERY = 1
    PV_TO_GRID = 2
    GRID_TO_HOME = 3
    GRID_TO_BATTERY = 4
    BATTERY_TO_HOME = 5
    BATTERY_TO_GRID = 6
