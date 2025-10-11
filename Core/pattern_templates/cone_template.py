# -*- coding: utf-8 -*-
import math

import svgwrite


class ConePatternTemplate:
    """Generate SVG templates for cone/drogue patterns with proper mathematical calculations"""

    def __init__(self, parameters):
        self.parameters = parameters
        self.diameter = parameters.get("diameter", 600)  # Base diameter
        self.length = parameters.get("length", 1000)  # Height of cone
        self.tip_diameter = parameters.get(
            "tip_diameter", 0
        )  # Tip diameter (0 for pointed)
        self.num_gores = parameters.get("num_gores", 8)
        self.seam_allowance = parameters.get("seam_allowance", 10)

        # Calculate cone geometry
        self.base_radius = self.diameter / 2
        self.tip_radius = self.tip_diameter / 2
        self.slant_height = math.sqrt(
            self.length**2 + (self.base_radius - self.tip_radius) ** 2
        )

        # Calculate gore dimensions
        self.base_arc_length = (math.pi * self.diameter) / self.num_gores
        self.tip_arc_length = (
            (math.pi * self.tip_diameter) / self.num_gores
            if self.tip_diameter > 0
            else 0
        )

        # Pattern dimensions with seam allowance
        self.gore_height = self.slant_height + (2 * self.seam_allowance)
        self.gore_base_width = self.base_arc_length + (2 * self.seam_allowance)
        self.gore_tip_width = (
            (self.tip_arc_length + (2 * self.seam_allowance))
            if self.tip_diameter > 0
            else (2 * self.seam_allowance)
        )

    def generate_template(self, output_path):
        """Generate SVG template for cone pattern"""
        margin = 20
        drawing_width = self.gore_base_width + (2 * margin)
        drawing_height = self.gore_height + (2 * margin)

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

        # Draw gore shape
        gore_points = self._calculate_gore_points()
        shifted_points = [(x + margin, y + margin) for x, y in gore_points]

        # Main gore outline
        gore_path = dwg.polygon(
            points=shifted_points, fill="none", stroke="black", stroke_width=0.5
        )
        dwg.add(gore_path)

        # Seam allowance lines
        self._add_seam_allowance(dwg, margin, gore_points)

        # Dimensions and labels
        self._add_dimensions(dwg, margin)
        self._add_labels(dwg, margin)

        dwg.save()

    def _calculate_gore_points(self):
        """Calculate the points for a single gore with seam allowance"""
        points = []

        # Bottom left (with seam allowance)
        points.append((0, self.gore_height))

        # Bottom right
        points.append((self.gore_base_width, self.gore_height))

        if self.tip_diameter > 0:
            # Truncated cone - trapezoid shape
            tip_x_offset = (self.gore_base_width - self.gore_tip_width) / 2
            points.append((self.gore_base_width - tip_x_offset, self.seam_allowance))
            points.append((tip_x_offset, self.seam_allowance))
        else:
            # Pointed cone - triangle shape
            points.append((self.gore_base_width / 2, 0))

        return points

    def _add_seam_allowance(self, dwg, margin, gore_points):
        """Add seam allowance guidelines"""
        # Base seam allowance
        base_seam_y = margin + self.gore_height - self.seam_allowance
        dwg.add(
            dwg.line(
                start=(margin, base_seam_y),
                end=(margin + self.gore_base_width, base_seam_y),
                stroke="red",
                stroke_width=0.3,
                stroke_dasharray="5,5",
            )
        )

        # Side seam allowances (approximated)
        if self.tip_diameter > 0:
            # For truncated cone
            tip_x_offset = (self.gore_base_width - self.gore_tip_width) / 2
            left_seam_points = [
                (
                    margin + self.seam_allowance,
                    margin + self.gore_height - self.seam_allowance,
                ),
                (
                    margin + tip_x_offset + self.seam_allowance,
                    margin + self.seam_allowance,
                ),
            ]
            right_seam_points = [
                (
                    margin + self.gore_base_width - self.seam_allowance,
                    margin + self.gore_height - self.seam_allowance,
                ),
                (
                    margin + self.gore_base_width - tip_x_offset - self.seam_allowance,
                    margin + self.seam_allowance,
                ),
            ]
        else:
            # For pointed cone
            left_seam_points = [
                (
                    margin + self.seam_allowance,
                    margin + self.gore_height - self.seam_allowance,
                ),
                (margin + self.gore_base_width / 2, margin + self.seam_allowance),
            ]
            right_seam_points = [
                (
                    margin + self.gore_base_width - self.seam_allowance,
                    margin + self.gore_height - self.seam_allowance,
                ),
                (margin + self.gore_base_width / 2, margin + self.seam_allowance),
            ]

        dwg.add(
            dwg.polyline(
                points=left_seam_points,
                fill="none",
                stroke="red",
                stroke_width=0.3,
                stroke_dasharray="5,5",
            )
        )
        dwg.add(
            dwg.polyline(
                points=right_seam_points,
                fill="none",
                stroke="red",
                stroke_width=0.3,
                stroke_dasharray="5,5",
            )
        )

    def _add_dimensions(self, dwg, margin):
        """Add dimension lines and text"""
        # Base width dimension
        dwg.add(
            dwg.line(
                start=(margin, margin + self.gore_height + 5),
                end=(margin + self.gore_base_width, margin + self.gore_height + 5),
                stroke="black",
                stroke_width=0.2,
            )
        )

        dwg.add(
            dwg.text(
                f"{self.gore_base_width:.1f}mm",
                insert=(
                    margin + self.gore_base_width / 2,
                    margin + self.gore_height + 8,
                ),
                text_anchor="middle",
                font_size="3mm",
            )
        )

        # Height dimension
        dwg.add(
            dwg.line(
                start=(margin - 5, margin),
                end=(margin - 5, margin + self.gore_height),
                stroke="black",
                stroke_width=0.2,
            )
        )

        dwg.add(
            dwg.text(
                f"{self.gore_height:.1f}mm",
                insert=(margin - 8, margin + self.gore_height / 2),
                text_anchor="middle",
                font_size="3mm",
                transform=f"rotate(-90,{margin-8},{margin + self.gore_height/2})",
            )
        )

    def _add_labels(self, dwg, margin):
        """Add labels and annotations"""
        # Title
        cone_type = "Truncated Cone" if self.tip_diameter > 0 else "Pointed Cone"
        dwg.add(
            dwg.text(
                f"{cone_type} Gore - {self.num_gores} panels",
                insert=(margin + self.gore_base_width / 2, margin - 10),
                text_anchor="middle",
                font_size="4mm",
                font_weight="bold",
            )
        )

        # Dimensions
        dim_text = f"Base: Ø{self.diameter}mm, Height: {self.length}mm"
        if self.tip_diameter > 0:
            dim_text += f", Tip: Ø{self.tip_diameter}mm"

        dwg.add(
            dwg.text(
                dim_text,
                insert=(margin + self.gore_base_width / 2, margin - 5),
                text_anchor="middle",
                font_size="3mm",
            )
        )

        # Seam allowance
        dwg.add(
            dwg.text(
                f"Seam Allowance: {self.seam_allowance}mm",
                insert=(
                    margin + self.gore_base_width / 2,
                    margin + self.gore_height + 15,
                ),
                text_anchor="middle",
                font_size="3mm",
            )
        )

        # Cutting instructions
        dwg.add(
            dwg.text(
                f"Cut {self.num_gores} identical gores",
                insert=(
                    margin + self.gore_base_width / 2,
                    margin + self.gore_height + 20,
                ),
                text_anchor="middle",
                font_size="3mm",
            )
        )
