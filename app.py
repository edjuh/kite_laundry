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
        'description': 'Simple pipe tail for stability. Recommended length-to-width ratio: 10:1.',
        'dimensions': ['length', 'width'],
        'suggested_ratio': 10,
        'ratio_field': ('length', 'width'),
        'ratio_desc': 'length to width',
        'has_gore': False
    },
    'drogue': {
        'description': 'Cone-shaped drogue for drag. Length ~3 times diameter, gores for shape.',
        'dimensions': ['length', 'diameter'],
        'suggested_ratio': 3,
        'ratio_field': ('length', 'diameter'),
        'ratio_desc': 'length to diameter',
        'has_gore': True
    },
    'spinner': {
        'description': 'Oregon Spinner (windsock-like). Length ~4 times diameter, 6 gores default.',
        'dimensions': ['length', 'diameter'],
        'suggested_ratio': 4,
        'ratio_field': ('length', 'diameter'),
        'ratio_desc': 'length to diameter',
        'has_gore': True
    },
    'graded_tail': {
        'description': 'Graded tapering tail. Length-to-width ratio: 10:1, gores for grading.',
        'dimensions': ['length', 'width'],
        'suggested_ratio': 10,
        'ratio_field': ('length', 'width'),
        'ratio_desc': 'length to width',
        'has_gore': True
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
    units = request.args.get('units', 'metric')  # Default to metric
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

    if request.method == 'POST':
        name = request.form['name']
        colors = [request.form.get('color1', 'red'), request.form.get('color2', ''), request.form.get('color3', '')]
        colors = [c for c in colors if c]  # Remove empty
        rod = request.form['rod']
        dimensions = {}
        try:
            for dim in dims:
                val = float(request.form[dim])
                if val <= 0:
                    raise ValueError
                dimensions[dim] = round(convert_to_metric(val, is_imperial), 0)  # Round to 1mm tolerance
            if has_gore:
                dimensions['gore'] = int(request.form.get('gore', 6))
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
        except ValueError:
            flash('Dimensions/gore must be positive numbers.')

    return render_template('configure.html', units=units, unit_label=unit_label, type=design_type,
                           dims=dims, colors_list=['red', 'blue', 'green', 'yellow'], rod_types=rod_types, principle=principle,
                           suggested_ratio=suggested_ratio, ratio_desc=ratio_desc, has_gore=has_gore)

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

    for dim in ['length', 'width', 'diameter']:
        if dim in dimensions:
            dimensions[dim] = round(convert_to_imperial(dimensions[dim], is_imperial), 0) if is_imperial else round(dimensions[dim], 0)

    text_output = f"{name} ({design_type}): Dimensions {dimensions} {unit_label}, Colors {colors}, Rod: {rod}"

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
    dwg = svgwrite.Drawing(size=('500px', '500px'))
    primary = colors[0] if colors else 'red'
    secondary = colors[1] if len(colors) > 1 else 'black'
    scale = 2
    if design_type in ['tail', 'graded_tail']:
        length = dimensions['length'] * scale
        width = dimensions['width'] * scale
        dwg.add(dwg.rect(insert=(10, 10), size=(width, length), fill=primary, stroke=secondary))
    elif design_type == 'drogue':
        diameter = dimensions['diameter'] * scale
        length = dimensions['length'] * scale
        points = [(10, 10), (10 + diameter, 10), (10 + diameter / 2, 10 + length)]
        dwg.add(dwg.polygon(points, fill=primary, stroke=secondary))
    elif design_type == 'spinner':
        diameter = dimensions['diameter'] * scale
        length = dimensions['length'] * scale
        dwg.add(dwg.rect(insert=(10, 10), size=(length, diameter), fill=primary, stroke=secondary))
        dwg.add(dwg.circle(center=(10 + length, 10 + diameter / 2), r=diameter / 2, fill='white', stroke=secondary))
    svg_io = io.BytesIO()
    dwg.write(svg_io)
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

    for dim in ['length', 'width', 'diameter']:
        if dim in dimensions:
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
    y -= 20
    primary_color = getattr(rl_colors, colors[0] if colors else 'red', rl_colors.black)
    secondary_color = getattr(rl_colors, colors[1] if len(colors) > 1 else 'black', rl_colors.black)
    scale = 5
    x_start = 100
    y_start = y - 200
    if design_type in ['tail', 'graded_tail']:
        length = dimensions['length'] * scale
        width = dimensions['width'] * scale
        c.setFillColor(primary_color)
        c.setStrokeColor(secondary_color)
        c.rect(x_start, y_start, width, length, fill=1)
    elif design_type == 'drogue':
        diameter = dimensions['diameter'] * scale
        length = dimensions['length'] * scale
        points = [(x_start, y_start + length), (x_start + diameter / 2, y_start), (x_start + diameter, y_start + length)]
        c.setFillColor(primary_color)
        c.setStrokeColor(secondary_color)
        path = c.beginPath()
        path.moveTo(*points[0])
        for p in points[1:]:
            path.lineTo(*p)
        path.close()
        c.drawPath(path, fill=1, stroke=1)
    elif design_type == 'spinner':
        diameter = dimensions['diameter'] * scale
        length = dimensions['length'] * scale
        c.setFillColor(primary_color)
        c.setStrokeColor(secondary_color)
        c.rect(x_start, y_start, length, diameter, fill=1)
        c.setFillColor(rl_colors.white)
        c.circle(x_start + length, y_start + diameter / 2, diameter / 2, fill=1, stroke=1)
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
    data = {'name': name, 'type': design_type, 'dimensions': dimensions, 'colors': colors, 'rod': rod, 'creation_date': date, 'material': 'Icarex Ripstop'}
    yaml_io = io.StringIO()
    yaml.dump(data, yaml_io)
    yaml_io.seek(0)
    return send_file(yaml_io, mimetype='text/yaml', download_name=f'{name}.yaml')

@app.route('/designs')
def designs():
    conn = sqlite3.connect('designs.db')
    c = conn.cursor()
    c.execute('SELECT * FROM designs ORDER BY creation_date DESC')
    all_designs = c.fetchall()
    conn.close()
    return render_template('designs.html', designs=all_designs)

@app.route('/help')
def help():
    return render_template('help.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
