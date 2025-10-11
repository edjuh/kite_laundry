# -*- coding: utf-8 -*-
"""Simple PDF writer – draws the rectangle as a single page."""

from __future__ import annotations

from pathlib import Path

from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas

from .geometry import Geometry


def render_pdf(geom: Geometry, out_path: Path, src_yaml: Path) -> None:
    """
    Write a one‑page PDF that shows the rectangle.
    Adds a comment in the PDF metadata for provenance.
    """
    # Set up a landscape A4 canvas
    c = canvas.Canvas(str(out_path), pagesize=landscape(A4))
    # Metadata – this is the “comment” that some PDF viewers display
    c.setAuthor("kite‑laundry pipeline")
    c.setTitle(f"Design – {src_yaml.name}")
    c.setSubject(f"Generated from {src_yaml.resolve()}")
    # Convert mm to points (1 point = 1/72 inch, 1 mm = 2.8346 pt)
    mm_to_pt = 2.8346456692913386
    width_pt = geom.width * mm_to_pt
    height_pt = geom.length * mm_to_pt  # note: length becomes height in landscape
    # Draw the rectangle in the middle of the page
    x = (c._pagesize[0] - width_pt) / 2
    y = (c._pagesize[1] - height_pt) / 2
    c.setStrokeColor("black")
    c.setFillColor(geom.colour)
    c.rect(x, y, width_pt, height_pt, fill=1)
    c.showPage()
    c.save()
