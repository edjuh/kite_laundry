# Oversight Marker: Last Verified: October 26, 2025, 7:00 PM CET by Grok 3 (xAI)
# Purpose: Extends app.py with Configure and Output routes for Kite Laundry Design Generator MVP.
# Next Step: Add SVG/PDF generation in Step 7.

from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from datetime import datetime
import json
import logging

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
                          colors=colors, rod=rod, date=date, text_output=text_output)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
