# -*- coding: utf-8 -*-
import math

import svgwrite


class TubePatternTemplate:
    """Generate SVG templates for tube patterns with proper mathematical calculations"""

    def __init__(self, parameters):
        self.parameters = parameters
        self.diameter = parameters.get("diameter", 600)
        self.length = parameters.get("length", 1000)
        self.num_gores = parameters.get("num_gores", 1)
        self.seam_allowance = parameters.get("seam_allowance", 10)

        # Calculate dimensions
        self.circumference = math.pi * self.diameter
        self.pattern_width = self.circumference + (2 * self.seam_allowance)
        self.pattern_height = self.length + (2 * self.seam_allowance)

    def generate_template(self, output_path):
        """Generate SVG template for tube pattern"""
        # Create SVG drawing with margins
        margin = 20
        drawing_width = self.pattern_width + (2 * margin)
        drawing_height = self.pattern_height + (2 * margin)

        dwg = svgwrite.Drawing(
            output_path, size=(f"{drawing_width}mm", f"{drawing_height}mm")
        )

        # Set viewbox for proper scaling
        dwg.viewbox(0, 0, drawing_width, drawing_height)

        # Add background
        dwg.add(
            dwg.rect(
                insert=(0, 0),
                size=(drawing_width, drawing_height),
                fill="white",
                stroke="none",
            )
        )

        # Main pattern rectangle
        pattern_rect = dwg.rect(
            insert=(margin, margin),
            size=(self.pattern_width, self.pattern_height),
            fill="none",
            stroke="black",
            stroke_width=0.5,
        )
        dwg.add(pattern_rect)

        # Add seam allowance lines
        seam_line_left = dwg.line(
            start=(margin + self.seam_allowance, margin),
            end=(margin + self.seam_allowance, margin + self.pattern_height),
            stroke="red",
            stroke_width=0.3,
            stroke_dasharray="5,5",
        )
        dwg.add(seam_line_left)

        seam_line_right = dwg.line(
            start=(margin + self.pattern_width - self.seam_allowance, margin),
            end=(
                margin + self.pattern_width - self.seam_allowance,
                margin + self.pattern_height,
            ),
            stroke="red",
            stroke_width=0.3,
            stroke_dasharray="5,5",
        )
        dwg.add(seam_line_right)

        # Add dimensions
        self._add_dimensions(dwg, margin)

        # Add labels and annotations
        self._add_labels(dwg, margin)

        dwg.save()

    def _add_dimensions(self, dwg, margin):
        """Add dimension lines and text"""
        # Width dimension
        dwg.add(
            dwg.line(
                start=(margin, margin - 5),
                end=(margin + self.pattern_width, margin - 5),
                stroke="black",
                stroke_width=0.2,
            )
        )

        dwg.add(
            dwg.text(
                f"{self.pattern_width:.1f}mm",
                insert=(margin + self.pattern_width / 2, margin - 8),
                text_anchor="middle",
                font_size="3mm",
            )
        )

        # Height dimension
        dwg.add(
            dwg.line(
                start=(margin - 5, margin),
                end=(margin - 5, margin + self.pattern_height),
                stroke="black",
                stroke_width=0.2,
            )
        )

        dwg.add(
            dwg.text(
                f"{self.pattern_height:.1f}mm",
                insert=(margin - 8, margin + self.pattern_height / 2),
                text_anchor="middle",
                font_size="3mm",
                transform=f"rotate(-90,{margin-8},{margin + self.pattern_height/2})",
            )
        )

    def _add_labels(self, dwg, margin):
        """Add labels and annotations"""
        # Title
        dwg.add(
            dwg.text(
                f"Tube Pattern - {self.diameter}mm × {self.length}mm",
                insert=(margin + self.pattern_width / 2, margin - 15),
                text_anchor="middle",
                font_size="4mm",
                font_weight="bold",
            )
        )

        # Seam allowance labels
        dwg.add(
            dwg.text(
                f"Seam Allowance: {self.seam_allowance}mm",
                insert=(
                    margin + self.pattern_width / 2,
                    margin + self.pattern_height + 10,
                ),
                text_anchor="middle",
                font_size="3mm",
            )
        )

        # Gore information if multi-gore
        if self.num_gores > 1:
            gore_width = self.circumference / self.num_gores
            dwg.add(
                dwg.text(
                    f"Multi-gore: {self.num_gores} panels, each {gore_width:.1f}mm wide",
                    insert=(
                        margin + self.pattern_width / 2,
                        margin + self.pattern_height + 15,
                    ),
                    text_anchor="middle",
                    font_size="3mm",
                )
            )

            # Add gore division lines
            for i in range(1, self.num_gores):
                x_pos = margin + (i * gore_width) + self.seam_allowance
                dwg.add(
                    dwg.line(
                        start=(x_pos, margin),
                        end=(x_pos, margin + self.pattern_height),
                        stroke="blue",
                        stroke_width=0.2,
                        stroke_dasharray="3,3",
                    )
                )
