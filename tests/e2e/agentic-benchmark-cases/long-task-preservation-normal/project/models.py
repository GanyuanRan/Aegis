"""Inventory item model."""

from dataclasses import dataclass


@dataclass
class Item:
    sku: str
    name: str
    qty: int
    unit_price: float
