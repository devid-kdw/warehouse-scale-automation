"""UOM catalog service — open-entry unit-of-measure persistence."""
from ..extensions import db
from ..models.uom_catalog import UomCatalog


def get_or_create_uom(code: str) -> UomCatalog:
    """Normalize UOM code to uppercase, find or insert into catalog.

    Args:
        code: Raw UOM code string (e.g. 'kg', 'L', 'KOM').

    Returns:
        UomCatalog instance (existing or newly created).
    """
    normalized = code.strip().upper()
    if not normalized:
        raise ValueError("UOM code must not be empty")

    uom = UomCatalog.query.filter_by(code=normalized).first()
    if uom:
        return uom

    uom = UomCatalog(code=normalized)
    db.session.add(uom)
    db.session.flush()
    return uom


def list_uom() -> list:
    """Return all UOM catalog entries, ordered by code."""
    return UomCatalog.query.order_by(UomCatalog.code).all()
