from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from .models import Design
from .render import generate_svg, generate_pdf
from .db import save_design, get_design_by_name
from .models import design_principles, rod_types
from flask_sqlalchemy import SQLAlchemy

design_bp = Blueprint('design', __name__)

@design_bp.route('/configure', methods=['GET', 'POST'])
def configure():
    units = request.args.get('units', 'metric')
    design_type = request.args.get('type')
    is_imperial = (units == 'imperial')
    unit_label = 'inches' if is_imperial else 'cm'

    if design_type not in design_principles:
        flash('Invalid design type.')
        return redirect(url_for('main.select_type', units=units))

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
                entry_dia = float(request.form['entry_diameter'])
                val = float(request.form.get('outlet_diameter', entry_dia / 4))
                if val > entry_dia:
                    raise ValueError("Outlet must be smaller than entry.")
                dimensions['outlet_diameter'] = round(convert_to_metric(val, is_imperial), 0)
            ratio = dimensions[ratio_field[0]] / dimensions[ratio_field[1]]
            if abs(ratio - suggested_ratio) > suggested_ratio * 0.2:
                flash(f'Suggestion: Optimal {ratio_desc} ratio ~{suggested_ratio}:1. Yours is {ratio:.1f}:1.')
            save_design(name, design_type, dimensions, colors, rod, unit_label)
            return redirect(url_for('design.output', name=name, units=units))
        except ValueError as e:
            flash(f'Error: {e}')

    return render_template('configure.html', units=units, unit_label=unit_label, type=design_type,
                           dims=dims, colors_list=['red', 'blue', 'green', 'yellow', 'black', 'white'], rod_types=rod_types, principle=principle,
                           suggested_ratio=suggested_ratio, ratio_desc=ratio_desc, has_gore=has_gore, has_outlet=has_outlet, default_values=default_values)

@design_bp.route('/output')
def output():
    name = request.args.get('name')
    units = request.args.get('units', 'metric')
    is_imperial = (units == 'imperial')
    unit_label = 'in' if is_imperial else 'cm'

    design = get_design_by_name(name)
    if not design:
        flash('Design not found.')
        return redirect(url_for('main.start'))

    id, name, design_type, dims_json, colors_json, rod, date, unit_label = design
    dimensions = json.loads(dims_json)
    colors = json.loads(colors_json)

    for dim in dimensions:
        if dim not in ['gore']:
            dimensions[dim] = round(convert_to_imperial(dimensions[dim], is_imperial), 0) if is_imperial else round(dimensions[dim], 0)

    # Adjust dimensions string to exclude units for 'gore'
    dims_str = ', '.join([f'{k}: {v} {unit_label}' if k != 'gore' else f'{k}: {v}' for k, v in dimensions.items()])
    text_output = f"{name} ({design_type}): Dimensions {dims_str}, Colors {', '.join(colors)} (Icarex Ripstop), Rod: {rod}"

    return render_template('output.html', name=name, type=design_type, dimensions=dimensions,
                           colors=colors, rod=rod, date=date, text_output=text_output, svg_url='/svg?name=' + name,
                           pdf_url='/pdf?name=' + name + '&units=' + units, yaml_url='/yaml?name=' + name, units=units, unit_label=unit_label)

@design_bp.route('/svg')
def get_svg():
    name = request.args.get('name')
    design = get_design_by_name(name)
    if not design:
        return 'Not found', 404
    design_type, dims_json, colors_json = design[2], design[3], design[4]
    dimensions = json.loads(dims_json)
    colors = json.loads(colors_json)
    svg_io = generate_svg(design_type, dimensions, colors)
    svg_io.seek(0)
    return send_file(svg_io, mimetype='image/svg+xml', download_name=f'{name}.svg')

@design_bp.route('/pdf')
def get_pdf():
    name = request.args.get('name')
    units = request.args.get('units', 'metric')
    is_imperial = (units == 'imperial')
    unit_label = 'in' if is_imperial else 'cm'

    design = get_design_by_name(name)
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

@design_bp.route('/yaml')
def get_yaml():
    name = request.args.get('name')
    design = get_design_by_name(name)
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

@design_bp.route('/designs')
def designs():
    conn = sqlite3.connect('designs.db')
    c = conn.cursor()
    c.execute('SELECT * FROM designs ORDER BY id DESC')
    all_designs = c.fetchall()
    conn.close()
    return render_template('designs.html', designs=all_designs)
