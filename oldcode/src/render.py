# Navigate to project directory and replace src/render.py
cd /Users/ed/kite_laundry
cat << 'EOF' > src/render.py
import io
import svgwrite
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors as rl_colors
from reportlab.pdfgen import canvas
import math

def generate_svg(design_type, dimensions, colors):
    """
    Generate SVG for kite laundry design with scalable viewBox.
    Args: design_type (str), dimensions (dict), colors (list)
    Returns: io.BytesIO with SVG content
    """
    gore = dimensions.get('gore', 8 if design_type == 'spinner' else 6)
    base_length = dimensions.get('length', 100)
    base_width = dimensions.get('width', dimensions.get('entry_diameter', 10))
    scale = 20  # Increased multiplier for large, visible designs
    viewbox_width = base_length * scale
    viewbox_height = base_width * scale
    dwg = svgwrite.Drawing(size=('100%', '100%'), viewBox=(0, 0, viewbox_width, viewbox_height))
    primary = colors[0] if colors else 'red'
    secondary = colors[1] if len(colors) > 1 else 'black'
    tertiary = colors[2] if len(colors) > 2 else secondary
    if design_type == 'tail':
        length = dimensions['length'] * scale
        width = dimensions['width'] * scale
        dwg.add(dwg.rect(insert=(10, 10), size=(length, width), rx=width/2, ry=width/2, fill=primary, stroke=secondary))
    elif design_type == 'drogue':
        entry_dia = dimensions['entry_diameter'] * scale
        outlet_dia = dimensions['outlet_diameter'] * scale
        length = dimensions['length'] * scale
        dwg.add(dwg.polygon(points=[(10, 10), (10 + length, 10 + (entry_dia - outlet_dia)/2), (10 + length, 10 + (entry_dia + outlet_dia)/2), (10, 10 + entry_dia)], fill=primary, stroke=secondary))
        for i in range(1, gore):
            gore_x = 10 + i * (length / gore)
            gore_height = entry_dia - (entry_dia - outlet_dia) * (gore_x - 10) / length
            dwg.add(dwg.line(start=(gore_x, 10 + (entry_dia - gore_height) / 2), end=(gore_x, 10 + (entry_dia - gore_height) / 2 + gore_height), stroke='black', stroke_width=1))
    elif design_type == 'spinner':
        entry_dia = dimensions['entry_diameter'] * scale
        length = dimensions['length'] * scale
        outlet_dia = 0
        for i in range(gore):
            start_x = 10 + i * (length / gore)
            end_x = 10 + (i + 1) * (length / gore)
            start_height = entry_dia - (entry_dia * i / gore)
            end_height = entry_dia - (entry_dia * (i + 1) / gore)
            color = colors[i % len(colors)]
            dwg.add(dwg.polygon(points=[(start_x, 10 + (entry_dia - start_height)/2), (end_x, 10 + (entry_dia - end_height)/2), (end_x, 10 + (entry_dia + end_height)/2), (start_x, 10 + (entry_dia + start_height)/2)], fill=color, stroke=secondary))
        dwg.add(dwg.circle(center=(10, 10 + entry_dia/2), r=entry_dia/2, fill='none', stroke=secondary, stroke_width=5))
    elif design_type == 'graded_tail':
        length = dimensions['length'] * scale
        width = dimensions['width'] * scale
        for i in range(gore):
            start_x = 10 + i * (length / gore)
            end_x = 10 + (i + 1) * (length / gore)
            start_width = width - (width * 0.75 * i / gore)
            end_width = width - (width * 0.75 * (i + 1) / gore)
            color = colors[i % len(colors)]
            dwg.add(dwg.polygon(points=[(start_x, 10), (end_x, 10), (end_x, 10 + end_width), (start_x, 10 + start_width)], fill=color, stroke=secondary))
    svg_str_io = io.StringIO()
    dwg.write(svg_str_io)
    svg_bytes = svg_str_io.getvalue().encode('utf-8')
    svg_io = io.BytesIO(svg_bytes)
    return svg_io

def generate_pdf(name, design_type, dimensions, colors, rod, date, unit_label):
    """
    Generate PDF for kite laundry design using ReportLab.
    Args: name (str), design_type (str), dimensions (dict), colors (list), rod (str), date (str), unit_label (str)
    Returns: io.BytesIO with PDF content
    """
    pdf_io = io.BytesIO()
    c = canvas.Canvas(pdf_io, pagesize=letter)
    width, height = letter
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, height - 50, f"Kite Laundry Design: {name}")
    c.setFont("Helvetica", 12)
    y = height - 80
    c.drawString(100, y, f"Type: {design_type.capitalize()}")
    y -= 20
    dims_str = ', '.join([f"{k}: {v} {unit_label}" if k != 'gore' else f"{k}: {v}" for k, v in dimensions.items()])
    c.drawString(100, y, f"Dimensions: {dims_str}")
    y -= 20
    colors_str = ', '.join(colors)  # Match colors list structure
    c.drawString(100, y, f"Colors: {colors_str} (Icarex Ripstop)")
    y -= 20
    c.drawString(100, y, f"Rod: {rod.capitalize()}")
    y -= 20
    c.drawString(100, y, f"Created: {date}")
    y -= 50
    c.drawString(100, y, "Preview:")
    y -= 200
    primary = colors[0] if colors else 'red'
    secondary = colors[1] if len(colors) > 1 else 'black'
    tertiary = colors[2] if len(colors) > 2 else secondary
    scale = min(5, 400 / dimensions.get('length', 100), 400 / dimensions.get('width', dimensions.get('entry_diameter', 10)))
    x_start = 100
    y_start = y
    if design_type == 'tail':
        length = dimensions['length'] * scale
        width = dimensions['width'] * scale
        c.setFillColor(primary)
        c.setStrokeColor(secondary)
        c.rect(x_start, y_start, length, width, fill=1)
    elif design_type == 'drogue':
        entry_dia = dimensions['entry_diameter'] * scale
        outlet_dia = dimensions['outlet_diameter'] * scale
        length = dimensions['length'] * scale
        c.setFillColor(primary)
        c.setStrokeColor(secondary)
        points = [(x_start, y_start), (x_start + length, y_start + (entry_dia - outlet_dia)/2), (x_start + length, y_start + (entry_dia + outlet_dia)/2), (x_start, y_start + entry_dia)]
        path = c.beginPath()
        path.moveTo(*points[0])
        for p in points[1:]:
            path.lineTo(*p)
        path.close()
        c.drawPath(path, fill=1, stroke=1)
        gore = dimensions.get('gore', 6)
        for i in range(1, gore):
            gore_x = x_start + i * (length / gore)
            gore_height = entry_dia - (entry_dia - outlet_dia) * (gore_x - x_start) / length
            c.line(gore_x, y_start + (entry_dia - gore_height) / 2, gore_x, y_start + (entry_dia - gore_height) / 2 + gore_height)
    elif design_type == 'spinner':
        entry_dia = dimensions['entry_diameter'] * scale
        length = dimensions['length'] * scale
        gore = dimensions.get('gore', 8)
        for i in range(gore):
            start_x = x_start + i * (length / gore)
            end_x = x_start + (i + 1) * (length / gore)
            start_height = entry_dia - (entry_dia * i / gore)
            end_height = entry_dia - (entry_dia * (i + 1) / gore)
            color = colors[i % len(colors)]
            c.setFillColor(color)
            c.setStrokeColor(secondary)
            path = c.beginPath()
            path.moveTo(start_x, y_start + (entry_dia - start_height)/2)
            path.lineTo(end_x, y_start + (entry_dia - end_height)/2)
            path.lineTo(end_x, y_start + (entry_dia + end_height)/2)
            path.lineTo(start_x, y_start + (entry_dia + start_height)/2)
            path.close()
            c.drawPath(path, fill=1, stroke=1)
        c.setStrokeColor(secondary)
        c.setStrokeWidth(5)  # Set stroke width before drawing circle
        c.circle(x_start, y_start + entry_dia/2, entry_dia/2, fill=0, stroke=1)
    elif design_type == 'graded_tail':
        length = dimensions['length'] * scale
        width = dimensions['width'] * scale
        gore = dimensions.get('gore', 6)
        for i in range(gore):
            start_x = x_start + i * (length / gore)
            end_x = x_start + (i + 1) * (length / gore)
            start_width = width - (width * 0.75 * i / gore)
            end_width = width - (width * 0.75 * (i + 1) / gore)
            color = colors[i % len(colors)]
            c.setFillColor(color)
            c.setStrokeColor(secondary)
            path = c.beginPath()
            path.moveTo(start_x, y_start)
            path.lineTo(end_x, y_start)
            path.lineTo(end_x, y_start + end_width)
            path.lineTo(start_x, y_start + start_width)
            path.close()
            c.drawPath(path, fill=1, stroke=1)
    c.save()
    return pdf_io
