#!/usr/bin/env python3
"""JSON invoice to PDF: seller, buyer, lines, and subtotal. No tax and no YAML."""

from __future__ import annotations

import argparse
import json
import sys
from decimal import Decimal, ROUND_HALF_UP
from io import BytesIO
from pathlib import Path


CENT = Decimal("0.01")


class UsageError(ValueError):
    """The invoice file cannot be used."""


def money(value: Decimal) -> Decimal:
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


def as_decimal(value: object, label: str) -> Decimal:
    if isinstance(value, bool) or value is None:
        raise UsageError("%s must be a number" % label)
    if isinstance(value, int):
        return Decimal(value)
    if isinstance(value, float):
        return Decimal(str(value))
    if isinstance(value, str):
        return Decimal(value.strip())
    raise UsageError("%s must be a number" % label)


def load_invoice(path: Path) -> tuple[dict, list[tuple[str, Decimal, Decimal, Decimal]], Decimal]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise UsageError("invalid json: %s" % exc) from exc
    if not isinstance(data, dict):
        raise UsageError("root must be a mapping")
    number = data.get("invoice_number")
    seller = (data.get("seller") or {}).get("name") if isinstance(data.get("seller"), dict) else None
    buyer = (data.get("buyer") or {}).get("name") if isinstance(data.get("buyer"), dict) else None
    if not isinstance(number, str) or not number.strip():
        raise UsageError("invoice_number is required")
    if not isinstance(seller, str) or not seller.strip():
        raise UsageError("seller.name is required")
    if not isinstance(buyer, str) or not buyer.strip():
        raise UsageError("buyer.name is required")
    raw_lines = data.get("lines")
    if not isinstance(raw_lines, list) or not raw_lines:
        raise UsageError("lines must be a non-empty list")
    lines = []
    subtotal = Decimal("0")
    for index, raw in enumerate(raw_lines, start=1):
        if not isinstance(raw, dict):
            raise UsageError("line %s must be a mapping" % index)
        description = raw.get("description")
        if not isinstance(description, str) or not description.strip():
            raise UsageError("line %s description is required" % index)
        quantity = as_decimal(raw.get("quantity"), "quantity")
        price = money(as_decimal(raw.get("unit_price"), "unit_price"))
        if quantity <= 0 or price < 0:
            raise UsageError("line %s has a bad quantity or price" % index)
        amount = money(quantity * price)
        subtotal += amount
        lines.append((description.strip(), quantity, price, amount))
    return (
        {"number": number.strip(), "seller": seller.strip(), "buyer": buyer.strip()},
        lines,
        money(subtotal),
    )


def render_pdf(header: dict, lines: list[tuple[str, Decimal, Decimal, Decimal]], subtotal: Decimal) -> bytes:
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
    except ImportError as exc:
        raise UsageError(
            "reportlab is required (import name reportlab). Check upstream docs for the install name."
        ) from exc
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4, pageCompression=0)
    pdf.setTitle(header["number"])
    y = A4[1] - 56
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(48, y, "INVOICE")
    y -= 28
    pdf.setFont("Helvetica", 12)
    for text in (
        "Number: %s" % header["number"],
        "SELLER",
        header["seller"],
        "BUYER",
        header["buyer"],
    ):
        pdf.drawString(48, y, text)
        y -= 16
    y -= 8
    for description, quantity, price, amount in lines:
        pdf.drawString(
            48,
            y,
            "%s  qty %s  unit %s  amount %s" % (description, quantity, format(price, "f"), format(amount, "f")),
        )
        y -= 16
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(48, y - 8, "TOTAL USD %s" % format(subtotal, "f"))
    pdf.save()
    return buffer.getvalue()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Write a PDF invoice from JSON. No tax line.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    try:
        args = parser.parse_args(argv)
        header, lines, subtotal = load_invoice(Path(args.input))
        payload = render_pdf(header, lines, subtotal)
        dest = Path(args.output)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(payload)
    except UsageError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 2
    except OSError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 2
    print("wrote: %s" % dest)
    print("bytes: %s" % len(payload))
    print("invoice: %s" % header["number"])
    print("total: %s" % format(subtotal, "f"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
