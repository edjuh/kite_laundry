# -*- coding: utf-8 -*-
"""
Stub helpers for simple projects: small preview, labeled preview,
and now Bol gore tiling (Easy Bol & Bol).
"""
import math
import os

import matplotlib.patches as patches
import matplotlib.pyplot as plt
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas


def simple_preview(out_dir, title="Preview", color="#888"):
    previews = os.path.join(out_dir, "previews")
    os.makedirs(previews, exist_ok=True)
    fig, ax = plt.subplots(figsize=(4, 6))
    ax.set_xlim(-1, 1)
    ax.set_ylim(0, 1.5)
    ax.axis("off")
    ax.add_patch(
        patches.Ellipse((0, 0.7), 0.8, 1.2, facecolor=color, edgecolor="black")
    )
    ax.text(0, 1.38, title, ha="center", fontsize=10)
    out = os.path.join(previews, f"{title.lower().replace(' ', '_')}.png")
    fig.savefig(out, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return out


def simple_labeled_preview(out_dir, title="Preview", labels=None):
    previews = os.path.join(out_dir, "previews")
    os.makedirs(previews, exist_ok=True)
    fig, ax = plt.subplots(figsize=(5, 7))
    ax.set_xlim(-1, 1)
    ax.set_ylim(0, 1.4)
    ax.axis("off")
    ax.add_patch(patches.Ellipse((0, 0.65), 0.8, 1.1, facecolor="#222"))
    if labels:
        for name, (lx, ly, px, py, color, txt) in labels.items():
            ax.annotate(
                "",
                xy=(px, py),
                xytext=(lx, ly),
                arrowprops=dict(arrowstyle="-", lw=1.0, color=color),
            )
            ax.text(
                lx,
                ly,
                f"{name} — {txt}",
                ha="center",
                va="center",
                fontsize=7,
                color="white",
                bbox=dict(
                    facecolor=color,
                    edgecolor="black",
                    boxstyle="round,pad=0.3",
                ),
            )
    out = os.path.join(previews, f"{title.lower().replace(' ', '_')}_labeled.png")
    fig.savefig(out, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return out


def bol_tiling(project, out_dir, settings, num_gores=12):
    """
    Draw a gore panel for a Bol (or Easy Bol) with crop marks, scale bar, seam allowance.
    """
    dims = project.get("scaled_dimensions", {})
    diameter = dims.get("diameter", 2.0) * 100  # cm
    depth = dims.get("depth", 0.6) * 100  # cm

    page_w, page_h = settings["page_size"]
    templates_dir = os.path.join(out_dir, "templates")
    os.makedirs(templates_dir, exist_ok=True)
    pdf_path = os.path.join(
        templates_dir, f"{project['name'].replace(' ', '_')}_Tiled.pdf"
    )

    gore_width = 2 * math.pi * (diameter / 2) / num_gores  # arc length cm
    gore_height = depth

    c = canvas.Canvas(pdf_path, pagesize=settings["page_size"])

    cols = math.ceil(gore_width / (page_w / cm))
    rows = math.ceil(gore_height / (page_h / cm))

    for r in range(rows):
        for col in range(cols):
            # crop marks
            c.setLineWidth(0.5)
            c.line(0, 10, 0, 30)
            c.line(0, page_h - 30, 0, page_h - 10)
            c.line(page_w - 0, 10, page_w - 0, 30)
            c.line(page_w - 0, page_h - 30, page_w - 0, page_h - 10)
            c.line(10, 0, 30, 0)
            c.line(page_w - 30, 0, page_w - 10, 0)
            c.line(10, page_h - 0, 30, page_h - 0)
            c.line(page_w - 30, page_h - 0, page_w - 10, page_h - 0)

            # scale bar
            c.setLineWidth(1)
            c.line(50, 50, 50 + 10 * cm, 50)
            c.drawString(50, 60, "10 cm")

            # gore outline
            x0, y0 = 100, 100
            c.roundRect(x0, y0, gore_width, gore_height, 30, stroke=1, fill=0)

            # seam allowance
            c.setDash(3, 2)
            c.roundRect(
                x0 - 10,
                y0 - 10,
                gore_width + 20,
                gore_height + 20,
                30,
                stroke=1,
                fill=0,
            )
            c.setDash()

            c.showPage()

    c.save()
    return pdf_path
