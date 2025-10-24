import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, send_file
import io
import json
import logging
import svgwrite
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors as rl_colors
from reportlab.pdfgen import canvas
import yaml
import math

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
app.secret_key = 'super_secret_key'

def init_db():
    conn = sqlite3.connect('designs.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS designs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  type TEXT NOT NULL,
                  dimensions TEXT NOT NULL,
                  colors TEXT NOT NULL,
                  rod TEXT,
                  creation_date TEXT NOT NULL)''')
    conn.commit()
    conn.close()

init_db()

def convert_to_metric(value, is_imperial):
    return value * 2.54 if is_imperial else value

def convert_to_imperial(value, is_imperial):
    return value / 2.54 if is_imperial else value

design_principles = {
    'tail': {
        'description': 'Simple pipe tail for stability. Recommended length-to-width ratio: 10:1. Icarex ripstop material.',
        'dimensions': ['length', 'width'],
        'suggested_ratio': 10,
        'ratio_field': ('length', 'width'),
        'ratio_desc': 'length to width',
        'has_gore': False,
        'has_outlet': False
    },
    'drogue': {
        'description': 'Cone-shaped drogue for drag (tapered like bucket). Length ~3 times entry diameter, outlet ~1/4 entry, 6 gores default. Icarex ripstop material.',
        'dimensions': ['length', 'entry_diameter', 'outlet_diameter'],
        'suggested_ratio': 3,
        'ratio_field': ('length', 'entry_diameter'),
        'ratio_desc': 'length to entry diameter',
        'has_gore': True,
        'has_outlet': True
    },
    'graded_tail': {
        'description': 'Graded tapering tail (diagonal grading for color shift). Cut 12"x41" rectangles, diagonal taper to 4" strips, 6-10 gores/sections. Icarex ripstop, no rod.',
        'dimensions': ['length', 'width'],
        'suggested_ratio': 10,
        'ratio_field': ('length', 'width'),
        'ratio_desc': 'length to width',
        'has_gore': True,
        'has_outlet': False
    },
    'spinner': {
        'description': 'Helix Spinner (tapering cone with hoop). Length ~4 times entry diameter, 8 gores for taper, carbon hoop for spin. Icarex ripstop material.',
        'dimensions': ['length', 'entry_diameter'],
        'suggested_ratio': 4,
        'ratio_field': ('length', 'entry_diameter'),
        'ratio_desc': 'length to entry diameter',
        'has_gore': True,
        'has_outlet': False
    }
}

rod_types = ['none', 'carbon', 'fiberglass', 'bamboo']

@app.route('/', methods=['GET', 'POST'])
def start():
    if request.method == 'POST':
        units = request.form['units']
        return redirect(url_for('select_type', units=units))
    return render_template('start.html')

@app.route('/select', methods=['GET', 'POST'])
def select_type():
    units = request.args.get('units')
    if request.method == 'POST':
        design_type = request.form['type']
        return redirect(url_for('configure', units=units, type=design_type))
    return render_template('select.html', units=units, types=list(design_principles.keys()))

@app.route('/configure', methods=['GET', 'POST'])
def configure():
    units = request.args.get('units', 'metric')
    design_type = request.args.get('type')
    is_imperial = (units == 'imperial')
    unit_label = 'inches' if is_imperial else 'cm'

    if design_type not in design_principles:
        flash('Invalid design type.')
        return redirect(url_for('select_type', units=units))

    dims = design_principles[design_type]['dimensions']
    principle = design_principles[design_type]['description']
    suggested_ratio = design_principles[design_type]['suggested_ratio']
    ratio_field = design_principles[design_type]['ratio_field']
    ratio_desc = design_principles[design_type]['ratio_desc']
    has_gore = design_principles[design_type]['has_gore']
    has_outlet = design_principles[design_type]['has_outlet']

    if request.method == 'POST':
        name = request.form['name']
        colors = [request.form.get('color1', 'red'), request.form.get('color2', ''), request.form.get('color3', '')]
        colors = [c for c in colors if c]
        rod = request.form['rod']
        dimensions = {}
        try:
            for dim in dims:
                val = float(request.form[dim])
                if val <= 0:
                    raise ValueError
                dimensions[dim] = round(convert_to_metric(val, is_imperial), 0)
            if has_gore:
                dimensions['gore'] = int(request.form.get('gore', 8 if design_type == 'spinner' else 6))
            if has_outlet:
                entry_dia = float(request.form['entry_diameter'])
                val = float(request.form.get('outlet_diameter', entry_dia / 4))
                if val > entry_dia:
                    raise ValueError("Outlet must be smaller than entry.")
                dimensions['outlet_diameter'] = round(convert_to_metric(val, is_imperial), 0)
            ratio = dimensions[ratio_field[0]] / dimensions[ratio_field[1]]
            if abs(ratio - suggested_ratio) > suggested_ratio * 0.2:
                flash(f'Suggestion: Optimal {ratio_desc} ratio ~{suggested_ratio}:1. Yours is {ratio:.1f}:1.')
            conn = sqlite3.connect('designs.db')
            c = conn.cursor()
            c.execute('INSERT INTO designs (name, type, dimensions, colors, rod, creation_date) VALUES (?, ?, ?, ?, ?, ?)',
                      (name, design_type, json.dumps(dimensions), json.dumps(colors), rod, datetime.now().isoformat()))
            conn.commit()
            conn.close()
            logging.info(f'Saved design: {name}')
            return redirect(url_for('output', name=name, units=units))
        except ValueError as e:
            flash(f'Error: {e}')

    return render_template('configure.html', units=units, unit_label=unit_label, type=design_type,
                           dims=dims, colors_list=['red', 'blue', 'green', 'yellow', 'black', 'white'], rod_types=rod_types, principle=principle,
                           suggested_ratio=suggested_ratio, ratio_desc=ratio_desc, has_gore=has_gore, has_outlet=has_outlet)

@app.route('/output')
def output():
    name = request.args.get('name')
    units = request.args.get('units', 'metric')
    is_imperial = (units == 'imperial')
    unit_label = 'in' if is_imperial else 'cm'

    conn = sqlite3.connect('designs.db')
    c = conn.cursor()
    c.execute('SELECT * FROM designs WHERE name = ? ORDER BY id DESC LIMIT 1', (name,))
    design = c.fetchone()
    conn.close()

    if not design:
        flash('Design not found.')
        return redirect(url_for('start'))

    id, name, design_type, dims_json, colors_json, rod, date = design
    dimensions = json.loads(dims_json)
    colors = json.loads(colors_json)

    for dim in dimensions:
        if dim not in ['gore']:
            dimensions[dim] = round(convert_to_imperial(dimensions[dim], is_imperial), 0) if is_imperial else round(dimensions[dim], 0)

    text_output = f"{name} ({design_type}): Dimensions {dimensions} {unit_label}, Colors {colors} (Icarex Ripstop), Rod: {rod}"

    return render_template('output.html', name=name, type=design_type, dimensions=dimensions,
                           colors=colors, rod=rod, date=date, text_output=text_output, svg_url='/svg?name=' + name,
                           pdf_url='/pdf?name=' + name + '&units=' + units, yaml_url='/yaml?name=' + name, units=units, unit_label=unit_label)

@app.route('/svg')
def get_svg():
    name = request.args.get('name')
    conn = sqlite3.connect('designs.db')
    c = conn.cursor()
    c.execute('SELECT type, dimensions, colors FROM designs WHERE name = ? ORDER BY id DESC LIMIT 1', (name,))
    design = c.fetchone()
    conn.close()
    if not design:
        return 'Not found', 404
    design_type, dims_json, colors_json = design
    dimensions = json.loads(dims_json)
    colors = json.loads(colors_json)
    svg_io = generate_svg(design_type, dimensions, colors)
    svg_io.seek(0)
    return send_file(svg_io, mimetype='image/svg+xml', download_name=f'{name}.svg')

def generate_svg(design_type, dimensions, colors):
    gore = dimensions.get('gore', 8 if design_type == 'spinner' else 6)
    max_length = dimensions.get('length', 100) * 2
    max_width = dimensions.get('width', dimensions.get('entry_diameter', 10)) * 2
    frame_width = max(max_length * 1.2, 500)
    frame_height = max(max_width * 1.2, 500)
    dwg = svgwrite.Drawing(size=(f'{frame_width}px', f'{frame_height}px'))
    primary = colors[0] if colors else 'red'
    secondary = colors[1] if len(colors) > 1 else 'black'
    tertiary = colors[2] if len(colors) > 2 else secondary
    scale = min(400 / max_length, 400 / max_width)
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
        outlet_dia = 0  # Pointed tip for Helix Spinner
        dwg.add(dwg.polygon(points=[(10, 10), (10 + length, 10 + entry_dia/2), (10 + length, 10 + entry_dia/2), (10, 10 + entry_dia)], fill=primary, stroke=secondary))
        dwg.add(dwg.circle(center=(10, 10 + entry_dia/2), r=entry_dia/2, fill='none', stroke=secondary))  # Hoop at entry
        for i in range(1, gore):
            gore_x = 10 + i * (length / gore)
            gore_height = entry_dia - (entry_dia - outlet_dia) * (gore_x - 10) / length
            dwg.add(dwg.line(start=(gore_x, 10 + (entry_dia - gore_height) / 2), end=(gore_x, 10 + (entry_dia - gore_height) / 2 + gore_height), stroke='black', stroke_width=1))
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

@app.route('/pdf')
def get_pdf():
    name = request.args.get('name')
    units = request.args.get('units', 'metric')
    is_imperial = (units == 'imperial')
    unit_label = 'in' if is_imperial else 'cm'

    conn = sqlite3.connect('designs.db')
    c = conn.cursor()
    c.execute('SELECT * FROM designs WHERE name = ? ORDER BY id DESC LIMIT 1', (name,))
    design = c.fetchone()
    conn.close()

    if not design:
        return 'Not found', 404

    id, name, design_type, dims_json, colors_json, rod, date = design
    dimensions = json.loads(dims_json)
    colors = json.loads(colors_json)

    for dim in dimensions:
        if dim not in ['gore']:
            dimensions[dim] = round(convert_to_imperial(dimensions[dim], is_imperial), 0) if is_imperial else round(dimensions[dim], 0)

    pdf_io = generate_pdf(name, design_type, dimensions, colors, rod, date, unit_label)
    pdf_io.seek(0)
    return send_file(pdf_io, mimetype='application/pdf', download_name=f'{name}.pdf')

def generate_pdf(name, design_type, dimensions, colors, rod, date, unit_label):
    pdf_io = io.BytesIO()
    c = canvas.Canvas(pdf_io, pagesize=letter)
    width, height = letter
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, height - 50, f"Kite Laundry Design: {name}")
    c.setFont("Helvetica", 12)
    y = height - 80
    c.drawString(100, y, f"Type: {design_type.capitalize()}")
    y -= 20
    dims_str = ', '.join([f"{k}: {v} {unit_label}" for k, v in dimensions.items()])
    c.drawString(100, y, f"Dimensions: {dims_str}")
    y -= 20
    colors_str = ', '.join(colors)
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
        outlet_dia = 0  # Pointed tip
        c.setFillColor(primary)
        c.setStrokeColor(secondary)
        points = [(x_start, y_start), (x_start + length, y_start + entry_dia/2), (x_start + length, y_start + entry_dia/2), (x_start, y_start + entry_dia)]
        path = c.beginPath()
        path.moveTo(*points[0])
        for p in points[1:]:
            path.lineTo(*p)
        path.close()
        c.drawPath(path, fill=1, stroke=1)
        c.circle(x_start, y_start + entry_dia/2, entry_dia/2, fill=0, stroke=1)
        gore = dimensions.get('gore', 8)
        for i in range(1, gore):
            gore_x = x_start + i * (length / gore)
            gore_height = entry_dia - (entry_dia - outlet_dia) * (gore_x - x_start) / length
            c.line(gore_x, y_start + (entry_dia - gore_height) / 2, gore_x, y_start + (entry_dia - gore_height) / 2 + gore_height)
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

@app.route('/yaml')
def get_yaml():
    name = request.args.get('name')
    conn = sqlite3.connect('designs.db')
    c = conn.cursor()
    c.execute('SELECT * FROM designs WHERE name = ? ORDER BY id DESC LIMIT 1', (name,))
    design = c.fetchone()
    conn.close()
    if not design:
        return 'Not found', 404
    id, name, design_type, dims_json, colors_json, rod, date = design
    dimensions = json.loads(dims_json)
    colors = json.loads(colors_json)
    data = {'name': name, 'type': design_type, 'dimensions': dimensions, 'colors': colors, 'material': 'Icarex Ripstop', 'rod': rod, 'creation_date': date}
    yaml_io = io.StringIO()
    yaml.dump(data, yaml_io)
    yaml_io.seek(0)
    return send_file(yaml_io, mimetype='text/yaml', download_name=f'{name}.yaml')

@app.route('/designs')
def designs():
    conn = sqlite3.connect('designs.db')
    c = conn.cursor()
    c.execute('SELECT * FROM designs ORDER BY id DESC')
    all_designs = c.fetchall()
    conn.close()
    return render_template('designs.html', designs=all_designs)

@app.route('/help')
def help():
    return render_template('help.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
