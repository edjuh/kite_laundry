# Oversight Marker: Last Verified: October 27, 2025, 09:20 AM CET by Grok 3 (xAI)
# Purpose: Adds Designs and Help routes with fixed rendering (gore unit, preview scale).
# Next Step: Test and finalize in Step 8.

from flask import Flask, render_template, request, redirect, url_for, flash, send_file
import sqlite3
from datetime import datetime
import json
import logging
import io
import svgwrite
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors as rl_colors
from reportlab.pdfgen import canvas

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
app.secret_key = 'super_secret_key'

def convert_to_metric(value, is_imperial):
    return value * 2.54 if is_imperial else value

def convert_to_imperial(value, is_imperial):
    return value / 2.54 if is_imperial else value

design_principles = {
    'tail': {'dimensions': ['length', 'width'], 'suggested_ratio': 10, 'has_gore': False, 'has_outlet': False},
    'drogue': {'dimensions': ['length', 'entry_diameter', 'outlet_diameter'], 'suggested_ratio': 3, 'has_gore': True, 'has_outlet': True},
    'graded_tail': {'dimensions': ['length', 'width'], 'suggested_ratio': 10, 'has_gore': True, 'has_outlet': False},
    'spinner': {'dimensions': ['length', 'entry_diameter'], 'suggested_ratio': 4, 'has_gore': True, 'has_outlet': False}
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
    suggested_ratio = design_principles[design_type]['suggested_ratio']
    ratio_field = design_principles[design_type]['ratio_field']
    has_gore = design_principles[design_type]['has_gore']
    has_outlet = design_principles[design_type]['has_outlet']

    if request.method == 'POST':
        name = request.form['name']
        colors = [c for c in [request.form.get('color1', 'red'), request.form.get('color2', ''), request.form.get('color3', '')] if c]
        rod = request.form['rod']
        dimensions = {}
        try:
            for dim in dims:
                val = float(request.form[dim])
                if val <= 0:
                    raise ValueError(f"{dim} must be positive")
                dimensions[dim] = round(convert_to_metric(val, is_imperial), 0)
            if has_gore:
                dimensions['gore'] = int(request.form.get('gore', 6))
            if has_outlet:
                entry_dia = float(request.form['entry_diameter'])
                val = float(request.form.get('outlet_diameter', entry_dia / 4))
                if val > entry_dia:
                    raise ValueError("Outlet must be smaller than entry.")
                dimensions['outlet_diameter'] = round(convert_to_metric(val, is_imperial), 0)
            ratio = dimensions[ratio_field[0]] / dimensions[ratio_field[1]]
            if abs(ratio - suggested_ratio) > suggested_ratio * 0.2:
                flash(f"Suggested ratio ~{suggested_ratio}:1, yours is {ratio:.1f}:1")
            conn = sqlite3.connect('designs.db')
            c = conn.cursor()
            c.execute('INSERT INTO designs (name, type, dimensions, colors, rod, creation_date) VALUES (?, ?, ?, ?, ?, ?)',
                      (name, design_type, json.dumps(dimensions), json.dumps(colors), rod, datetime.now().isoformat()))
            conn.commit()
            conn.close()
            logging.info(f"Saved design: {name}")
            return redirect(url_for('output', name=name, units=units))
        except ValueError as e:
            flash(f"Error: {e}")

    return render_template('configure.html', units=units, unit_label=unit_label, type=design_type,
                          dims=dims, colors_list=['red', 'blue', 'green', 'yellow'], rod_types=rod_types,
                          has_gore=has_gore, has_outlet=has_outlet)

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

    dims_str = ', '.join([f"{k}: {v} {unit_label}" if k != 'gore' else f"{k}: {v}" for k, v in dimensions.items()])
    text_output = f"{name} ({design_type}): Dimensions {dims_str}, Colors {', '.join(colors)} (Icarex Ripstop), Rod: {rod}"

    return render_template('output.html', name=name, type=design_type, dimensions=dimensions,
                          colors=colors, rod=rod, date=date, text_output=text_output, svg_url='/svg?name=' + name,
                          pdf_url='/pdf?name=' + name + '&units=' + units)

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
    scale = 10  # Increased for better visibility
    dwg = svgwrite.Drawing(size=('100%', '100%'), viewBox=(0, 0, dimensions['length'] * scale / 100, dimensions['width'] * scale / 100))
    primary = colors[0] if colors else 'red'
    secondary = colors[1] if len(colors) > 1 else 'black'
    if design_type == 'tail':
        length = dimensions['length'] * scale / 100
        width = dimensions['width'] * scale / 100
        dwg.add(dwg.rect(insert=(10, 10), size=(length, width), rx=width/2, ry=width/2, fill=primary, stroke=secondary))
    elif design_type == 'drogue':
        entry_dia = dimensions['entry_diameter'] * scale / 100
        outlet_dia = dimensions.get('outlet_diameter', entry_dia / 4) * scale / 100
        length = dimensions['length'] * scale / 100
        dwg.add(dwg.polygon(points=[(10, 10), (10 + length, 10 + (entry_dia - outlet_dia)/2), (10 + length, 10 + (entry_dia + outlet_dia)/2), (10, 10 + entry_dia)], fill=primary, stroke=secondary))
        gore = dimensions.get('gore', 6)
        for i in range(1, gore):
            gore_x = 10 + i * (length / gore)
            gore_height = entry_dia - (entry_dia - outlet_dia) * (gore_x - 10) / length
            dwg.add(dwg.line(start=(gore_x, 10 + (entry_dia - gore_height) / 2), end=(gore_x, 10 + (entry_dia - gore_height) / 2 + gore_height), stroke='black', stroke_width=1))
    elif design_type == 'spinner':
        entry_dia = dimensions['entry_diameter'] * scale / 100
        length = dimensions['length'] * scale / 100
        gore = dimensions.get('gore', 8)
        for i in range(gore):
            start_x = 10 + i * (length / gore)
            end_x = 10 + (i + 1) * (length / gore)
            start_height = entry_dia - (entry_dia * i / gore)
            end_height = entry_dia - (entry_dia * (i + 1) / gore)
            color = colors[i % len(colors)]
            dwg.add(dwg.polygon(points=[(start_x, 10 + (entry_dia - start_height)/2), (end_x, 10 + (entry_dia - end_height)/2), (end_x, 10 + (entry_dia + end_height)/2), (start_x, 10 + (entry_dia + start_height)/2)], fill=color, stroke=secondary))
        dwg.add(dwg.circle(center=(10, 10 + entry_dia/2), r=entry_dia/2, fill='none', stroke=secondary, stroke_width=5))
    elif design_type == 'graded_tail':
        length = dimensions['length'] * scale / 100
        width = dimensions['width'] * scale / 100
        gore = dimensions.get('gore', 6)
        for i in range(gore):
            start_x = 10 + i * (length / gore)
            end_x = 10 + (i + 1) * (length / gore)
            start_width = width - (width * 0.75 * i / gore)
            end_width = width - (width * 0.75 * (i + 1) / gore)
            color = colors[i % len(colors)]
            dwg.add(dwg.polygon(points=[(start_x, 10), (end_x, 10), (end_x, 10 + end_width), (start_x, 10 + start_width)], fill=color, stroke=secondary))
    svg_io = io.BytesIO()
    dwg.write(svg_io)
    svg_io.seek(0)
    return send_file(svg_io, mimetype='image/svg+xml', download_name=f'{name}.svg')

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

    pdf_io = generate_pdf(name, design_type, dimensions, colors, rod, date)
    pdf_io.seek(0)
    return send_file(pdf_io, mimetype='application/pdf', download_name=f'{name}.pdf')

def generate_pdf(name, design_type, dimensions, colors, rod, date):
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
    scale = 10  # Increased for larger preview
    x_start = 100
    y_start = y
    if design_type == 'tail':
        length = dimensions['length'] * scale / 100
        width = dimensions['width'] * scale / 100
        c.setFillColor(primary)
        c.setStrokeColor(secondary)
        c.rect(x_start, y_start, length, width, fill=1)
    elif design_type == 'drogue':
        entry_dia = dimensions['entry_diameter'] * scale / 100
        outlet_dia = dimensions.get('outlet_diameter', entry_dia / 4) * scale / 100
        length = dimensions['length'] * scale / 100
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
        entry_dia = dimensions['entry_diameter'] * scale / 100
        length = dimensions['length'] * scale / 100
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
        c.setStrokeWidth(5)
        c.circle(x_start, y_start + entry_dia/2, entry_dia/2, fill=0, stroke=1)
    elif design_type == 'graded_tail':
        length = dimensions['length'] * scale / 100
        width = dimensions['width'] * scale / 100
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
