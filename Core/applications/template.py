# -*- coding: utf-8 -*-
"""SVG generator – draws a rectangle in the specified colour."""

from __future__ import annotations

from pathlib import Path

import svgwrite

from .geometry import Geometry


def build_svg(geom: Geometry, out_path: Path, src_yaml: Path) -> None:
    """
    Create an SVG file at *out_path*.
    The file starts with a comment that points to *src_yaml*.
    """
    dwg = svgwrite.Drawing(filename=str(out_path), size=(geom.length, geom.width))
    # provenance comment
    dwg.add(svgwrite.base.Comment(f" Generated from: {src_yaml.resolve()} "))
    # rectangle
    dwg.add(
        dwg.rect(
            insert=(0, 0),
            size=(geom.length, geom.width),
            fill=geom.colour,
            stroke="black",
            stroke_width=2,
        )
    )
    dwg.save()
