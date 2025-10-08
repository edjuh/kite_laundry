#!/usr/bin/env python3
"""
Central Base Module for Kite Laundry Builder
kite_laundry/base.py
"""

import math
from pathlib import Path
from typing import Dict, List, Tuple, Any
from datetime import datetime
import logging

# === External utilities ===
from utils.physics import calculate_drag, calculate_difficulty  # 👈 new physics link

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ========= Geometry Helpers =========

class GeometryLib:
    @staticmethod
    def add_seam_allowance(points: List[Tuple[float, float]], allowance: float = 10) -> List[Tuple[float, float]]:
        """Expand polygon by approximate radial offset (mm)."""
        cx = sum(x for x, _ in points) / len(points)
        cy = sum(y for _, y in points) / len(points)
        out = []
        for x, y in points:
            dx, dy = x - cx, y - cy
            d = math.hypot(dx, dy)
            if d == 0:
                out.append((x, y))
            else:
                s = (d + allowance) / d
                out.append((cx + dx * s, cy + dy * s))
        return out

# ========= Geometry Functions =========

def generate_cone_geometry(project, length_mm, settings):
    """Generate cone geometry (drogue/spinner)"""
    base_length = project["base_length"]
    scale = length_mm / base_length
    
    diameter = project["parameters"]["diameter"] * scale
    length = project["parameters"]["length"] * scale
    num_gores = project["parameters"]["num_gores"]
    opening_size = project["parameters"].get("opening_size", 0.3)
    
    # Calculate panel dimensions
    top_circ = math.pi * diameter * opening_size
    bottom_circ = math.pi * diameter
    top_width = top_circ / num_gores * 0.9
    bottom_width = bottom_circ / num_gores * 0.9
    height = length
    
    # Generate single gore panel
    gore_points = [
        (0, 0),
        (top_width, 0),
        (bottom_width, height),
        (0, height)
    ]
    
    # Apply seam allowance
    gore_points = GeometryLib.add_seam_allowance(gore_points, allowance=10)
    
    panels = []
    for i in range(num_gores):
        panels.append({
            "name": f"Gore_{i+1}",
            "points": gore_points,
            "color": project.get("colors", {}).get("main", "#FFB6C1")
        })
    
    return panels


def generate_cylinder_geometry(project, length_mm, settings):
    """Generate cylinder geometry (spinner tube)"""
    base_length = project["base_length"]
    scale = length_mm / base_length
    
    diameter = project["parameters"]["diameter"] * scale
    length = project["parameters"]["length"] * scale
    num_segments = project["parameters"].get("num_segments", 8)
    
    circumference = math.pi * diameter
    panel_width = circumference / num_segments * 0.9
    height = length
    
    segment_points = [
        (0, 0),
        (panel_width, 0),
        (panel_width, height),
        (0, height)
    ]
    
    segment_points = GeometryLib.add_seam_allowance(segment_points, allowance=10)
    
    panels = []
    for i in range(num_segments):
        panels.append({
            "name": f"Segment_{i+1}",
            "points": segment_points,
            "color": project.get("colors", {}).get("main", "#00CED1")
        })
    
    return panels


def generate_flat_geometry(project, length_mm, settings):
    """Generate flat geometry (strips/flags)"""
    base_length = project["base_length"]
    scale = length_mm / base_length
    
    length = project["parameters"]["length"] * scale
    width = project["parameters"]["width"] * scale
    num_items = project["parameters"].get("num_items", 1)
    item_height = length / num_items
    
    panels = []
    for i in range(num_items):
        y_offset = i * item_height
        points = [
            (0, y_offset),
            (width, y_offset),
            (width, y_offset + item_height),
            (0, y_offset + item_height)
        ]
        
        panels.append({
            "name": f"Item_{i+1}",
            "points": points,
            "color": project.get("colors", {}).get("main", "#FF69B4")
        })
    
    return panels

# YAML checker and validation

from typing import Optional, Tuple
import re

def normalize_project_dict(project: Dict[str, Any], filename: Optional[str] = None) -> Tuple[Dict[str, Any], List[str]]:
    """
    Normalize a project dict to the new schema expected by utils/base and laundry_builder.
    - Ensures: name, complexity, base_length, geometry.type, parameters dict, colors, materials.
    - Does NOT insert Python callables (like function objects) so YAML remains serializable.
    Returns (normalized_project, warnings_list).
    """
    warnings: List[str] = []
    proj = dict(project) if project is not None else {}

    # --- Name ---
    if not proj.get("name"):
        if filename:
            proj["name"] = filename
            warnings.append("Filled missing 'name' from filename")
        else:
            proj["name"] = "Unnamed Project"
            warnings.append("Added default name 'Unnamed Project'")

    # --- Complexity ---
    if "complexity" not in proj:
        proj["complexity"] = 2
        warnings.append("Added default 'complexity'=2")

    # --- Base length ---
    if "base_length" not in proj:
        # try to infer from top-level length or parameters length
        bl = proj.get("length") or (proj.get("parameters") or {}).get("length")
        if bl:
            proj["base_length"] = float(bl)
            warnings.append("Inferred 'base_length' from 'length'")
        else:
            proj["base_length"] = 1000
            warnings.append("Added default 'base_length'=1000 mm")

    # --- Parameters (core normalized block) ---
    if not isinstance(proj.get("parameters"), dict):
        parameters: Dict[str, Any] = {}

        # 1) From existing 'parameters' if present and is mapping, keep it
        if isinstance(project.get("parameters"), dict):
            parameters.update(project.get("parameters"))

        # 2) From 'geometry' block if it has numeric keys
        geom_block = project.get("geometry") if isinstance(project.get("geometry"), dict) else {}
        for key, val in geom_block.items():
            if key in ("type",):
                continue
            parameters.setdefault(key, val)

        # 3) From 'dimensions' block (legacy)
        dims = project.get("dimensions")
        if isinstance(dims, dict):
            for k, v in dims.items():
                # common renames
                if k in ("diam", "diameter"):
                    parameters.setdefault("diameter", v)
                elif k in ("gores", "num_gores"):
                    parameters.setdefault("num_gores", v)
                elif k in ("length", "height"):
                    parameters.setdefault("length", v)
                else:
                    parameters.setdefault(k, v)

        # 4) From top-level legacy keys
        legacy_keys = {
            "diam": "diameter", "diameter": "diameter", "base_diameter": "base_diameter",
            "top_diameter": "top_diameter", "length": "length", "gores": "num_gores",
            "num_gores": "num_gores", "width": "width", "height": "length"
        }
        for lk, dest in legacy_keys.items():
            if lk in project and dest not in parameters:
                parameters[dest] = project[lk]

        # 5) Fallback defaults if we found nothing
        if not parameters:
            parameters = {"diameter": 600, "length": 1000, "num_gores": 8}
            warnings.append("No geometry parameters found; applied defaults")

        proj["parameters"] = parameters
        warnings.append("Created 'parameters' block (normalized legacy fields)")

    # --- Geometry type detection ---
    geom = proj.get("geometry") if isinstance(proj.get("geometry"), dict) else {}
    geom_type = geom.get("type") if geom.get("type") else None

    # try from geometry_fn string if present
    gf = project.get("geometry_fn") if isinstance(project.get("geometry_fn"), str) else None
    if not geom_type and gf:
        gf_l = gf.lower()
        if "bol" in gf_l or "cone" in gf_l or "drogue" in gf_l or "chute" in gf_l or "parachute" in gf_l:
            geom_type = "cone"
        elif "spinner" in gf_l or "tube" in gf_l or "cylinder" in gf_l or "blimp" in gf_l:
            geom_type = "cylinder"
        elif "windsock" in gf_l or "stream" in gf_l or "tail" in gf_l or "flag" in gf_l:
            geom_type = "flat"
        else:
            # keep searching
            geom_type = None

    # try filename clues
    if not geom_type and filename:
        f = filename.lower()
        if any(k in f for k in ("drogue", "chute", "parachute", "bol", "cone")):
            geom_type = "cone"
        elif any(k in f for k in ("spinner", "tube", "blimp", "long_blimp", "rocket")):
            geom_type = "cylinder"
        elif any(k in f for k in ("windsock", "streamer", "tail", "flag")):
            geom_type = "flat"

    # final fallback
    if not geom_type:
        geom_type = "cone"
        warnings.append("Could not infer geometry.type; defaulted to 'cone'")

    proj["geometry"] = proj.get("geometry", {})
    proj["geometry"]["type"] = geom_type

    # --- Colors ---
    if not isinstance(proj.get("colors"), dict):
        # try color_pattern legacy field (list)
        cp = project.get("color_pattern") or project.get("colors") or project.get("palette")
        if isinstance(cp, list) and cp:
            main = cp[0]
            accent = cp[1] if len(cp) > 1 else "#FFFFFF"
            proj["colors"] = {"main": main, "accent": accent}
            warnings.append("Mapped 'color_pattern' to 'colors'")
        elif isinstance(cp, dict):
            proj["colors"] = cp
        else:
            # default neutral palette
            proj["colors"] = {"main": "#FFB347", "accent": "#FFFFFF"}

    # --- Materials normalize ---
    m = project.get("materials")
    if isinstance(m, list):
        normalized_materials = []
        for item in m:
            if isinstance(item, str):
                normalized_materials.append({"item": item, "qty": "?"})
            elif isinstance(item, dict):
                normalized_materials.append(item)
        if normalized_materials:
            proj["materials"] = normalized_materials
            warnings.append("Normalized 'materials' list")
    elif isinstance(m, dict):
        proj["materials"] = m

    # --- Meta fallback fields ---
    if "description" not in proj and "description" in project:
        proj["description"] = project["description"]
    if "author" not in proj and "author" in project:
        proj["author"] = project["author"]
    proj.setdefault("version", project.get("version", 1.0))

    # mark conversion (useful for auditing)
    proj["_converted"] = True
    if warnings:
        proj["_conversion_warnings"] = warnings

    return proj, warnings


# ========= Geometry Registry =========

GEOMETRY_FUNCTIONS = {
    'cone': generate_cone_geometry,
    'cylinder': generate_cylinder_geometry,
    'flat': generate_flat_geometry,
    'sphere': None,  # Not implemented yet
}

def get_geometry_function(geometry_type: str):
    """Get geometry function by type"""
    func = GEOMETRY_FUNCTIONS.get(geometry_type)
    if func is None:
        logger.error(f"Geometry function '{geometry_type}' not found")
        logger.error(f"Available functions: {list(GEOMETRY_FUNCTIONS.keys())}")
    return func

def get_available_geometry_functions() -> List[str]:
    """Get list of available geometry functions"""
    available = [k for k, v in GEOMETRY_FUNCTIONS.items() if v is not None]
    logger.info(f"Available geometry functions: {available}")
    return available

# ========= Project Validation =========

class ProjectValidator:
    REQUIRED_KEYS = ['name', 'complexity', 'base_length', 'parameters']
    
    @classmethod
    def validate(cls, project: Dict) -> Tuple[bool, List[str]]:
        errors = []
        for key in cls.REQUIRED_KEYS:
            if key not in project:
                errors.append(f"Missing key: {key}")
        if 'base_length' in project and project['base_length'] <= 0:
            errors.append("base_length must be positive")
        if errors:
            logger.warning(f"Validation errors: {errors}")
        else:
            logger.info(f"✅ {project['name']} validated")
        return len(errors) == 0, errors

# ========= Tiling System =========

class TilingSystem:
    PAGE_SIZES = {'A4': (210, 297), 'A3': (297, 420)}

    def __init__(self, page_size: str = 'A4', overlap: float = 20, margin: float = 10):
        self.page_size = self.PAGE_SIZES.get(page_size.upper(), self.PAGE_SIZES['A4'])
        self.overlap = overlap
        self.margin = margin

    def calculate_tiles(self, width: float, height: float) -> Dict:
        pw, ph = self.page_size
        usable_w = pw - 2 * self.margin
        usable_h = ph - 2 * self.margin
        eff_w = usable_w - self.overlap
        eff_h = usable_h - self.overlap
        tiles_x = math.ceil(width / eff_w)
        tiles_y = math.ceil(height / eff_h)
        total = tiles_x * tiles_y
        return {'grid': (tiles_x, tiles_y), 'total_pages': total}

# ========= Material Calculator =========

class MaterialCalculator:
    def __init__(self, fabric_width: float = 1500):
        self.fabric_width = fabric_width

    def calculate_requirements(self, panels: List[Dict], project: Dict = None) -> Dict:
        total_area = 0
        complexity_sum = 0
        
        for p in panels:
            pts = p.get("points", [])
            if pts:
                total_area += self._poly_area(pts)
                complexity_sum += p.get("complexity", 1)
        
        complexity_waste = complexity_sum * 0.02
        total_with_waste = total_area * (1 + 0.15 + complexity_waste)
        
        fabric_length = total_with_waste / self.fabric_width
        efficiency = (total_area / (self.fabric_width * fabric_length)) * 100
        
        material_type = "Unknown"
        if project and "materials" in project:
            materials = project["materials"]
            if isinstance(materials, dict):
                material_type = materials.get("fabric", materials.get("thread", "Unknown"))
            elif isinstance(materials, list) and materials:
                first_item = materials[0].get("item", "Unknown")
                material_type = first_item
        
        return {
            "fabric_width_mm": self.fabric_width,
            "fabric_length_m": fabric_length / 1000,
            "total_area_cm2": total_area / 100,
            "efficiency": f"{efficiency:.1f}%",
            "estimated_waste_m": (total_with_waste - total_area) / 1000,
            "material_type": material_type
        }

    def _poly_area(self, pts):
        return abs(sum(pts[i][0]*pts[i-1][1]-pts[i-1][0]*pts[i][1] for i in range(len(pts)))) / 2

# ========= Preview Generator =========

class PreviewGenerator:
    @staticmethod
    def generate_preview(project: Dict, panels: List[Dict], out_dir: str) -> str:
        svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="800" height="600">']
        
        title_color = project.get("colors", {}).get("main", "#333333")
        svg.append(f'<text x="400" y="30" text-anchor="middle" font-size="18" fill="{title_color}">{project["name"]}</text>')
        
        bg_color = project.get("colors", {}).get("accent", "#f0f0f0")
        svg.append(f'<rect width="100%" height="100%" fill="{bg_color}"/>')
        
        default_colors = ["#FFB347", "#77DD77", "#AEC6CF", "#CFCFC4", "#FF6961"]
        for i, p in enumerate(panels):
            pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in p.get("points", []))
            color = p.get("color", default_colors[i % len(default_colors)])
            svg.append(f'<polygon points="{pts}" fill="{color}" stroke="black" opacity="0.6"/>')
        
        svg.append("</svg>")
        path = Path(out_dir) / "preview.svg"
        path.write_text("\n".join(svg))
        return str(path)

# ========= HTML Documentation Generator =========

class HTMLDocGenerator:
    @staticmethod
    def generate_documentation(project, panels, materials, out_dir):
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{project['name']} Documentation</title>
    <style>
        body {{ font-family: sans-serif; max-width: 900px; margin: auto; line-height: 1.6; }}
        h1, h2 {{ color: #2c3e50; }}
        .warning {{ background: #fff3cd; padding: 15px; border-left: 5px solid #ffc107; margin: 20px 0; }}
        .materials {{ background: #f8f9fa; padding: 15px; border-radius: 5px; }}
    </style>
</head>
<body>
<h1>🪁 {project['name']}</h1>
<p>{project.get('description','No description')}</p>

<h2>Overview</h2>
<p><strong>Base length:</strong> {project.get('base_length')} mm | 
   <strong>Complexity:</strong> {project.get('complexity')} | 
   <strong>Version:</strong> {project.get('version', '1.0')}</p>
<p><strong>Author:</strong> {project.get('author', 'Unknown')}</p>

<h2>Performance</h2>
<ul>
<li><strong>Estimated drag:</strong> {project.get('drag_estimate', 'N/A')} N @ 6 m/s</li>
<li><strong>Difficulty rating:</strong> {project.get('difficulty_rating', {}).get('score', 'N/A')}/10 ({project.get('difficulty_rating', {}).get('level', 'N/A')})</li>
</ul>

{HTMLDocGenerator._generate_materials_section(materials, project)}
{HTMLDocGenerator._generate_assembly_notes(project)}
{HTMLDocGenerator._generate_cut_layout_section(materials, project)}

<p><em>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</em></p>
</body></html>"""
        path = Path(out_dir) / "documentation.html"
        path.write_text(html)
        return str(path)

    @staticmethod
    def _generate_materials_section(materials: Dict, project: Dict) -> str:
        materials_info = ""
        if "materials" in project:
            project_materials = project["materials"]
            if isinstance(project_materials, dict):
                materials_info = f"""
<li><strong>Fabric:</strong> {project_materials.get('fabric', 'Unknown')}</li>
<li><strong>Thread:</: {project_materials.get('thread', 'Unknown')}</li>
"""
            elif isinstance(project_materials, list):
                materials_info = "<li><strong>Materials:</strong><ul>"
                for item in project_materials:
                    if isinstance(item, dict):
                        name = item.get("item", "Unknown")
                        qty = item.get("qty", "Unknown")
                        materials_info += f"<li>{name}: {qty}</li>"
                materials_info += "</ul></li>"
        
        return f"""
<h2>Materials Summary</h2>
<div class="materials">
<ul>
{materials_info}
<li><strong>Fabric width:</strong> {materials['fabric_width_mm']/1000:.2f} m</li>
<li><strong>Fabric length:</strong> {materials['fabric_length_m']:.2f} m</li>
<li><strong>Efficiency:</strong> {materials['efficiency']}</li>
</ul>
</div>"""

    @staticmethod
    def _generate_assembly_notes(project: Dict) -> str:
        assembly = project.get("assembly", [])
        if assembly:
            html = '<h2>Assembly Instructions</h2><ol>'
            for step in assembly:
                html += f'<li>{step}</li>'
            html += '</ol>'
            return html
        return "<h2>Assembly</h2><p>No assembly instructions provided.</p>"

    @staticmethod
    def _generate_cut_layout_section(materials: Dict, project: Dict) -> str:
        fabric_width = materials.get("fabric_width_mm", 1500)
        fabric_length = materials.get("fabric_length_m", 1.0)
        efficiency = materials.get("efficiency", "80%")
        
        return f"""
<h2>Cut Layout</h2>
<p><strong>Fabric width:</strong> {fabric_width/1000:.2f} m, <strong>required length:</strong> {fabric_length:.2f} m.</p>
<p><strong>Estimated cutting efficiency:</strong> {efficiency}.</p>
"""

# ========= Pipeline Runner =========

class PipelineError(Exception):
    def __init__(self, message, project_name=None):
        self.project_name = project_name
        self.message = message
        super().__init__(self.message)
    
    def __str__(self):
        if self.project_name:
            return f"Pipeline error in {self.project_name}: {self.message}"
        return self.message

def run_pipeline(project: Dict, length_mm: float, out_dir: str, settings: Dict) -> Dict:
    try:
        logger.info(f"🚀 Running pipeline for {project['name']}")

        # Validate
        valid, errors = ProjectValidator.validate(project)
        if not valid:
            raise ValueError(f"Invalid project: {errors}")

        # Generate panels
        panels = project["geometry_fn"](project, length_mm, settings)
        logger.info(f"🧩 Generated {len(panels)} panels")

        # Physics & difficulty
        drag_est = calculate_drag(project)
        difficulty = calculate_difficulty(project)
        project["drag_estimate"] = drag_est
        project["difficulty_rating"] = difficulty

        # Materials
        materials = MaterialCalculator().calculate_requirements(panels, project)
        logger.info(f"📐 Material efficiency: {materials['efficiency']}")

        # Outputs
        preview_path = PreviewGenerator.generate_preview(project, panels, out_dir)
        doc_path = HTMLDocGenerator.generate_documentation(project, panels, materials, out_dir)

        logger.info(f"✅ {project['name']} pipeline complete")
        return {
            "panels": panels,
            "materials": materials,
            "preview_path": preview_path,
            "doc_path": doc_path,
            "drag_estimate": drag_est,
            "difficulty_rating": difficulty
        }

    except Exception as e:
        logger.error(f"❌ Pipeline failed for {project['name']}: {str(e)}")
        raise PipelineError(f"Pipeline failed: {str(e)}", project.get('name'))

# Normalization Function

def normalize_project_dict(project_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize project dictionary to new schema"""
    normalized = project_dict.copy()
    
    # Convert geometry_fn to geometry_type
    if 'geometry_fn' in normalized and 'geometry_type' not in normalized:
        normalized['geometry_type'] = normalized.pop('geometry_fn')
        logger.info("Converted geometry_fn to geometry_type")
    
    # Convert dimensions to parameters
    if 'dimensions' in normalized and 'parameters' not in normalized:
        normalized['parameters'] = normalized.pop('dimensions')
        logger.info("Converted dimensions to parameters")
    
    # Convert nested materials to flat format
    if 'materials' in normalized and isinstance(normalized['materials'], list):
        # Convert list format to dict format
        materials_dict = {}
        for item in normalized['materials']:
            if isinstance(item, dict) and 'item' in item:
                key = item['item'].lower().replace(' ', '_').replace('(', '').replace(')', '')
                materials_dict[key] = item.get('qty', 'Unknown')
        normalized['materials'] = materials_dict
        logger.info("Converted materials list to dictionary")
    
    return normalized


