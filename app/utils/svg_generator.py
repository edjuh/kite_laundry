import svgwrite
import json

def generate_svg(design):
    # Parse dimensions
    dims = json.loads(design.dimensions)
    unit = design.unit_label
    colors = design.colors.split(',') if design.colors else ['#000000']

    # Scale for larger preview
    scale = 10

    # Basic SVG for demonstration - adjust based on type
    dwg = svgwrite.Drawing(size=(dims.get('length', 100) * scale, dims.get('width', 50) * scale), viewBox=f"0 0 {dims.get('length', 100)} {dims.get('width', 50)}")

    # Example rectangle for tail
    if design.type == 'tail':
        dwg.add(dwg.rect(insert=(0, 0), size=(dims['length'], dims['width']), fill=colors[0]))

    # For gore-based, draw segments
    if 'num_gores' in dims:
        gore_width = dims.get('length', 100) / dims['num_gores']
        for i in range(dims['num_gores']):
            color = colors[i % len(colors)]
            dwg.add(dwg.rect(insert=(i * gore_width, 0), size=(gore_width, dims.get('width', 50)), fill=color))

    # Save to string or file - return as data URI for HTML
    svg_data = dwg.tostring()
    return f"data:image/svg+xml;base64,{svg_data.encode('utf-8').hex()}"  # Simplified base64 for inline

