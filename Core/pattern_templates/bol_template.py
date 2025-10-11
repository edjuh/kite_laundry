# -*- coding: utf-8 -*-
import math

import svgwrite


class BolPatternTemplate:
    """Generate SVG templates for Bol rotor patterns"""

    def __init__(self, parameters):
        self.parameters = parameters
        self.diameter = parameters.get("diameter", 1000)
        self.num_gores = parameters.get("num_gores", 8)
        self.seam_allowance = parameters.get("seam_allowance", 10)

        # Bol specific calculations
        self.radius = self.diameter / 2
        self.bol_height = self.diameter * 0.7  # Ideal rotation ratio
        self.circumference = math.pi * self.diameter

        # Gore dimensions
        self.gore_base_width = self.circumference / self.num_gores
        self.gore_height = self.bol_height
        self.angle_per_gore = (2 * math.pi) / self.num_gores

        # With seam allowance
        self.gore_width_with_seam = self.gore_base_width + (2 * self.seam_allowance)
        self.gore_height_with_seam = self.gore_height + (2 * self.seam_allowance)

    def generate_template(self, output_path):
        """Generate SVG template for Bol gore pattern"""
        margin = 20
        drawing_width = self.gore_width_with_seam + (2 * margin)
        drawing_height = self.gore_height_with_seam + (2 * margin)

        dwg = svgwrite.Drawing(
            output_path, size=(f"{drawing_width}mm", f"{drawing_height}mm")
        )
        dwg.viewbox(0, 0, drawing_width, drawing_height)

        # Background
        dwg.add(
            dwg.rect(
                insert=(0, 0),
                size=(drawing_width, drawing_height),
                fill="white",
                stroke="none",
            )
        )

        # Draw gore shape with curvature
        self._draw_bol_gore(dwg, margin)

        # Add dimensions and labels
        self._add_dimensions(dwg, margin)
        self._add_labels(dwg, margin)

        dwg.save()

    def _draw_bol_gore(self, dwg, margin):
        """Draw the curved triangular gore shape for Bol"""
        # Base points
        base_y = margin + self.gore_height_with_seam - self.seam_allowance

        # Calculate curved sides (approximated with Bezier curves)
        control_point_offset = self.gore_base_width * 0.2  # Curvature amount

        # Path for the gore shape
        path_data = [
            f"M {margin + self.seam_allowance},{base_y}",  # Start at bottom left
            f"L {margin + self.gore_width_with_seam - self.seam_allowance},{base_y}",  # Base line
            f"Q {margin + self.gore_width_with_seam - self.seam_allowance + control_point_offset},{margin + self.seam_allowance + self.gore_height/2}",
            f" {margin + self.gore_width_with_seam/2},{margin + self.seam_allowance}",  # Right curve to top
            f"Q {margin + self.seam_allowance - control_point_offset},{margin + self.seam_allowance + self.gore_height/2}",
            f" {margin + self.seam_allowance},{base_y}",  # Left curve back to start
        ]

        gore_path = dwg.path(d=path_data, fill="none", stroke="black", stroke_width=0.5)
        dwg.add(gore_path)

        # Add seam allowance guidelines
        self._add_seam_allowance(dwg, margin, base_y)

    def _add_seam_allowance(self, dwg, margin, base_y):
        """Add seam allowance guidelines"""
        # Base seam line
        dwg.add(
            dwg.line(
                start=(margin, base_y),
                end=(margin + self.gore_width_with_seam, base_y),
                stroke="red",
                stroke_width=0.3,
                stroke_dasharray="5,5",
            )
        )

        # Top seam line
        dwg.add(
            dwg.line(
                start=(margin + self.seam_allowance, margin + self.seam_allowance),
                end=(
                    margin + self.gore_width_with_seam - self.seam_allowance,
                    margin + self.seam_allowance,
                ),
                stroke="red",
                stroke_width=0.3,
                stroke_dasharray="5,5",
            )
        )

    def _add_dimensions(self, dwg, margin):
        """Add dimension lines"""
        # Width dimension
        dwg.add(
            dwg.line(
                start=(margin, margin + self.gore_height_with_seam + 5),
                end=(
                    margin + self.gore_width_with_seam,
                    margin + self.gore_height_with_seam + 5,
                ),
                stroke="black",
                stroke_width=0.2,
            )
        )

        dwg.add(
            dwg.text(
                f"{self.gore_width_with_seam:.1f}mm",
                insert=(
                    margin + self.gore_width_with_seam / 2,
                    margin + self.gore_height_with_seam + 8,
                ),
                text_anchor="middle",
                font_size="3mm",
            )
        )

        # Height dimension
        dwg.add(
            dwg.line(
                start=(margin - 5, margin),
                end=(margin - 5, margin + self.gore_height_with_seam),
                stroke="black",
                stroke_width=0.2,
            )
        )

        dwg.add(
            dwg.text(
                f"{self.gore_height_with_seam:.1f}mm",
                insert=(margin - 8, margin + self.gore_height_with_seam / 2),
                text_anchor="middle",
                font_size="3mm",
                transform=f"rotate(-90,{margin-8},{margin + self.gore_height_with_seam/2})",
            )
        )

    def _add_labels(self, dwg, margin):
        """Add labels and information"""
        # Title
        dwg.add(
            dwg.text(
                f"Bol Rotor Gore - {self.num_gores} panels",
                insert=(margin + self.gore_width_with_seam / 2, margin - 10),
                text_anchor="middle",
                font_size="4mm",
                font_weight="bold",
            )
        )

        # Dimensions
        dwg.add(
            dwg.text(
                f"Diameter: {self.diameter}mm, Height: {self.bol_height:.0f}mm",
                insert=(margin + self.gore_width_with_seam / 2, margin - 5),
                text_anchor="middle",
                font_size="3mm",
            )
        )

        # Cutting instructions
        dwg.add(
            dwg.text(
                f"Cut {self.num_gores} identical gores",
                insert=(
                    margin + self.gore_width_with_seam / 2,
                    margin + self.gore_height_with_seam + 15,
                ),
                text_anchor="middle",
                font_size="3mm",
            )
        )

        # Rotation info
        dwg.add(
            dwg.text(
                f"Rotation ratio: {self.bol_height/self.diameter:.2f}",
                insert=(
                    margin + self.gore_width_with_seam / 2,
                    margin + self.gore_height_with_seam + 20,
                ),
                text_anchor="middle",
                font_size="3mm",
            )
        )
