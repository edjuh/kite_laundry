import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, send_file
import io
import json
import logging
import os
from src.render import generate_svg, generate_pdf
from src.config import design_principles, rod_types

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
app.secret_key = 'super_secret_key'

# Custom filter for JSON parsing in templates
app.jinja_env.filters['from_json'] = json.loads

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
                  creation_date TEXT NOT NULL,
                  unit_label TEXT DEFAULT 'cm')''')
    c.execute('''PRAGMA table_info(designs)''')
    columns = [info[1] for info in c.fetchall()]
    if 'unit_label' not in columns:
        c.execute('''ALTER TABLE designs ADD COLUMN unit_label TEXT DEFAULT 'cm' ''')
    c.execute('''UPDATE designs SET unit_label = 'cm' WHERE unit_label IS NULL''')
    conn.commit()
    resource_dir = 'projects/resources'
    if os.path.exists(resource_dir):
        for yaml_file in os.listdir(resource_dir):
            if yaml_file.endswith('.yaml'):
                with open(os.path.join(resource_dir, yaml_file), 'r') as f:
                    data = yaml.safe_load(f)
                    if data and 'name' in data and 'type' in data:
                        c.execute('INSERT OR IGNORE INTO designs (name, type, dimensions, colors, rod, creation_date, unit_label) VALUES (?, ?, ?, ?, ?, ?, ?)',
                                  (data['name'], data['type'], json.dumps(data.get('dimensions', {})), json.dumps(data.get('colors', [])), data.get('rod', 'none'), data.get('creation_date', datetime.now().isoformat()), 'cm'))
                    conn.commit()
    conn.close()

init_db()

def convert_to_metric(value, is_imperial):
    return value * 2.54 if is_imperial else value

def convert_to_imperial(value, is_imperial):
    return value / 2.54 if is_imperial else value

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
    default_values = design_principles[design_type].get('default_values', {})

    if request.method == 'POST':
        name = request.form['name']
        colors = [request.form.get('color1', 'red'), request.form.get('color2', ''), request.form.get('color3', '')]
        colors = [c for c in colors if c]
        rod = request.form['rod']
        dimensions = {}
        try:
            for dim in dims:
                val = float(request.form.get(dim, default_values.get(dim, 0)))
                if val <= 0:
                    raise ValueError
                dimensions[dim] = round(convert_to_metric(val, is_imperial), 0)
            if has_gore:
                dimensions['gore'] = int(request.form.get('gore', default_values.get('gore', 8 if design_type == 'spinner' else 6)))
            if has_outlet:
                entry_dia = float(request.form.get('entry_diameter', default_values.get('entry_diameter', 0)))
                val = float(request.form.get('outlet_diameter', entry_dia / 4))
                if val > entry_dia:
                    raise ValueError("Outlet must be smaller than entry.")
                dimensions['outlet_diameter'] = round(convert_to_metric(val, is_imperial), 0)
            ratio = dimensions[ratio_field[0]] / dimensions[ratio_field[1]]
            if abs(ratio - suggested_ratio) > suggested_ratio * 0.2:
                flash(f'Suggestion: Optimal {ratio_desc} ratio ~{suggested_ratio}:1. Yours is {ratio:.1f}:1.')
            conn = sqlite3.connect('designs.db')
            c = conn.cursor()
            c.execute('INSERT INTO designs (name, type, dimensions, colors, rod, creation_date, unit_label) VALUES (?, ?, ?, ?, ?, ?, ?)',
                      (name, design_type, json.dumps(dimensions), json.dumps(colors), rod, datetime.now().isoformat(), unit_label))
            conn.commit()
            conn.close()
            logging.info(f'Saved design: {name}')
            return redirect(url_for('output', name=name, units=units))
        except ValueError as e:
            flash(f'Error: {e}')

    return render_template('configure.html', units=units, unit_label=unit_label, type=design_type,
                           dims=dims, colors_list=['red', 'blue', 'green', 'yellow', 'black', 'white'], rod_types=rod_types, principle=principle,
                           suggested_ratio=suggested_ratio, ratio_desc=ratio_desc, has_gore=has_gore, has_outlet=has_outlet, default_values=default_values)

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

    id, name, design_type, dims_json, colors_json, rod, date, unit_label = design
    dimensions = json.loads(dims_json)
    colors = json.loads(colors_json)

    for dim in dimensions:
        if dim not in ['gore']:
            dimensions[dim] = round(convert_to_imperial(dimensions[dim], is_imperial), 0) if is_imperial else round(dimensions[dim], 0)

    dims_str = ', '.join([f"{k}: {v} {unit_label}" if k != 'gore' else f"{k}: {v}" for k, v in dimensions.items()])
    text_output = f"{name} ({design_type}): Dimensions {dims_str}, Colors {', '.join(colors)} (Icarex Ripstop), Rod: {rod}"

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

    id, name, design_type, dims_json, colors_json, rod, date, unit_label = design
    dimensions = json.loads(dims_json)
    colors = json.loads(colors_json)

    for dim in dimensions:
        if dim not in ['gore']:
            dimensions[dim] = round(convert_to_imperial(dimensions[dim], is_imperial), 0) if is_imperial else round(dimensions[dim], 0)

    pdf_io = generate_pdf(name, design_type, dimensions, colors, rod, date, unit_label)
    pdf_io.seek(0)
    return send_file(pdf_io, mimetype='application/pdf', download_name=f'{name}.pdf')

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
    id, name, design_type, dims_json, colors_json, rod, date, unit_label = design
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
    c.execute('SELECT * FROM designs ORDER BY creation_date DESC')
    all_designs = c.fetchall()
    conn.close()
    return render_template('designs.html', designs=all_designs)

@app.route('/help')
def help():
    return render_template('help.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
