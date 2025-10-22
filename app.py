from flask import Flask, render_template, request, session, redirect, url_for
import yaml
import svgwrite
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os
import re
import glob
import logging
import json

app = Flask(__name__)
app.secret_key = 'kite-laundry-key'
logging.basicConfig(level=logging.INFO)

def load_yaml(file_path):
    if not os.path.exists(file_path):
        logging.warning(f"Missing file: {file_path}")
        return {}
    try:
        with open(file_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logging.error(f"Error loading {file_path}: {str(e)}")
        return {}

tools = load_yaml('projects/resources/tools.yaml') or {}
colors = load_yaml('projects/resources/colors.yaml') or {'palette': {}}
materials = load_yaml('projects/resources/materials.yaml') or {'materials': {}}
suppliers = load_yaml('projects/resources/suppliers.yaml') or {'suppliers': {}}
rods = load_yaml('projects/resources/rods.yaml') or {'rods': {}}

@app.route('/')
def index():
    session.pop('form_type', None)  # Clear form_type on home
    return render_template('index.html')

@app.route('/start', methods=['GET', 'POST'])
def start():
    if request.method == 'POST':
        session['units'] = request.form.get('units', 'metric')
        logging.info(f"Start: Set units to {session['units']}")
        return render_template('select.html', forms=['tail', 'drogue', 'windsock'])
    return render_template('start.html')

@app.route('/select', methods=['GET', 'POST'])
def select_form():
    if request.method == 'POST':
        form_type = request.form.get('form_type')
        if form_type not in ['tail', 'drogue', 'windsock']:
            logging.error(f"Invalid form_type: {form_type}")
            return render_template('select.html', forms=['tail', 'drogue', 'windsock'], error="Invalid form type")
        session['form_type'] = form_type
        logging.info(f"Select: Set form_type to {session['form_type']}")
        units = session.get('units', 'metric')
        material_subset = {}
        for mat_type, mat_info in materials.get('materials', {}).items():
            material_subset[mat_type] = {
                'type': mat_info.get('type', 'Unknown'),
                'weight': mat_info.get('weight', 'N/A'),
                'properties': mat_info.get('properties', []),
                'suppliers': {}
            }
            for supplier_key in mat_info.get('suppliers', []):
                supplier_data = suppliers['suppliers'].get(supplier_key, {})
                if supplier_data and supplier_data.get('materials', {}).get(mat_type):
                    material_subset[mat_type]['suppliers'][supplier_key] = {
                        'name': supplier_data.get('name', supplier_key),
                        'price': supplier_data['materials'][mat_type].get('price', 'N/A'),
                        'colors': supplier_data['materials'][mat_type].get('colors', []),
                        'eco': supplier_data['materials'][mat_type].get('eco', False),
                        'link': supplier_data['materials'][mat_type].get('link', '')
                    }
                else:
                    logging.warning(f"Skipping invalid supplier {supplier_key} for {mat_type}")
        rod_subset = {}
        for rod_type, rod_info in rods.get('rods', {}).get(units, {}).items():
            rod_subset[rod_type] = {}
            for supplier_key, supplier_info in rod_info.items():
                rod_subset[rod_type][supplier_key] = {
                    'name': supplier_info.get('name', supplier_key),
                    'product': supplier_info.get('product', ''),
                    'price': supplier_info.get('price', 'N/A'),
                    'diameter': supplier_info.get('diameter', ''),
                    'length': supplier_info.get('length', ''),
                    'link': supplier_info.get('link', '')
                }
        logging.info(f"Select: material_subset={json.dumps(material_subset, indent=2)}, suppliers={json.dumps(suppliers, indent=2)}")
        return render_template('configure.html', colors=colors['palette'], materials=material_subset, rods=rod_subset)
    return render_template('select.html', forms=['tail', 'drogue', 'windsock'])

@app.route('/configure', methods=['GET', 'POST'])
def configure_form():
    if request.method == 'POST':
        try:
            form_type = session.get('form_type', 'tail')
            logging.info(f"Configure POST: form_type={form_type}, session={json.dumps(dict(session), indent=2)}")
            length = round(float(request.form['length']), 1)
            width = round(float(request.form['width']), 1)
            if length <= 0 or width <= 0:
                return render_template('configure.html', error="Dimensions must be positive numbers", colors=colors['palette'], materials=materials['materials'], rods=rods['rods'].get(session.get('units', 'metric'), {}))
            color_codes = request.form.getlist('colors')
            material = request.form.get('material')
            logging.info(f"Configure POST: material={material}")
            # Parse material as mat_type:supplier_key
            try:
                mat_type, supplier_key = material.split(':')
                material_display = f"{mat_type.capitalize()} ({suppliers['suppliers'].get(supplier_key, {}).get('name', supplier_key)} - {suppliers['suppliers'].get(supplier_key, {}).get('materials', {}).get(mat_type, {}).get('price', 'N/A')})"
            except (ValueError, KeyError) as e:
                logging.error(f"Material parsing error: {str(e)}")
                material_display = "Unknown Material"
            rod = request.form.get('rod', '')
            rod_display = "None"
            if rod:
                try:
                    rod_type, rod_supplier_key = rod.split(':')
                    rod_display = f"{rod_type.capitalize()} ({rods['rods'][session.get('units', 'metric')].get(rod_supplier_key, {}).get('name', rod_supplier_key)} - {rods['rods'][session.get('units', 'metric')].get(rod_supplier_key, {}).get('product', 'N/A')} - {rods['rods'][session.get('units', 'metric')].get(rod_supplier_key, {}).get('price', 'N/A')})"
                except (ValueError, KeyError) as e:
                    logging.error(f"Rod parsing error: {str(e)}")
                    rod_display = "None"
            units = session.get('units', 'metric')
            if units == 'imperial':
                length_cm = length * 2.54
                width_cm = width * 2.54
            else:
                length_cm = length
                width_cm = width
            svg_file = f"output/{form_type}_template.svg"
            dwg = svgwrite.Drawing(svg_file, profile='tiny', size=(f"{width_cm*10}mm", f"{length_cm*10}mm"))
            segment_width = (width_cm*10) / len(color_codes) if color_codes else width_cm*10
            for i, color in enumerate(color_codes):
                dwg.add(dwg.rect((i*segment_width, 0), (segment_width, length_cm*10), fill=colors['palette'].get(color, {'hex': '#FFFFFF'})['hex']))
            dwg.save()
            pdf_file = f"output/{form_type}_template.pdf"
            c = canvas.Canvas(pdf_file, pagesize=A4)
            c.drawString(100, 750, f"{form_type.capitalize()} Template")
            c.drawString(100, 730, f"Length: {length} {'cm' if units == 'metric' else 'in'}")
            c.drawString(100, 710, f"Width: {width} {'cm' if units == 'metric' else 'in'}")
            c.drawString(100, 690, f"Material: {material_display}")
            c.drawString(100, 670, f"Colors: {', '.join(colors['palette'].get(c, {'name': 'Unknown'})['name'] for c in color_codes)}")
            if rod_display != "None":
                c.drawString(100, 650, f"Rod: {rod_display}")
            c.save()
            pattern_data = {
                'pieces': [
                    {'width': width_cm * 10, 'height': length_cm * 10, 'position': {'x': 0, 'y': 0}},
                    {'width': 50, 'height': 50, 'position': {'x': 0, 'y': length_cm * 10 * 0.25}},
                    {'width': 50, 'height': 50, 'position': {'x': 0, 'y': length_cm * 10 * 0.75}}
                ]
            }
            logging.info(f"Configure POST: Generated SVG={svg_file}, PDF={pdf_file}, material_display={material_display}, pattern_data={json.dumps(pattern_data)}")
            return render_template('output.html', form_type=form_type, length=length, width=width, colors=[colors['palette'].get(c, {'name': 'Unknown'})['name'] for c in color_codes], material=material_display, rod=rod_display, units=units, svg_file=svg_file, pdf_file=pdf_file, tools=tools, pattern_data=pattern_data)
        except ValueError as e:
            logging.error(f"Input validation error: {str(e)}")
            return render_template('configure.html', error="Invalid input: use positive numbers for dimensions", colors=colors['palette'], materials=materials['materials'], rods=rods['rods'].get(session.get('units', 'metric'), {}))
    units = session.get('units', 'metric')
    material_subset = {}
    for mat_type, mat_info in materials.get('materials', {}).items():
        material_subset[mat_type] = {
            'type': mat_info.get('type', 'Unknown'),
            'weight': mat_info.get('weight', 'N/A'),
            'properties': mat_info.get('properties', []),
            'suppliers': {}
        }
        for supplier_key in mat_info.get('suppliers', []):
            supplier_data = suppliers['suppliers'].get(supplier_key, {})
            if supplier_data and supplier_data.get('materials', {}).get(mat_type):
                material_subset[mat_type]['suppliers'][supplier_key] = {
                    'name': supplier_data.get('name', supplier_key),
                    'price': supplier_data['materials'][mat_type].get('price', 'N/A'),
                    'colors': supplier_data['materials'][mat_type].get('colors', []),
                    'eco': supplier_data['materials'][mat_type].get('eco', False),
                    'link': supplier_data['materials'][mat_type].get('link', '')
                }
            else:
                logging.warning(f"Skipping invalid supplier {supplier_key} for {mat_type}")
    rod_subset = {}
    for rod_type, rod_info in rods.get('rods', {}).get(units, {}).items():
        rod_subset[rod_type] = {}
        for supplier_key, supplier_info in rod_info.items():
            rod_subset[rod_type][supplier_key] = {
                'name': supplier_info.get('name', supplier_key),
                'product': supplier_info.get('product', ''),
                'price': supplier_info.get('price', 'N/A'),
                'diameter': supplier_info.get('diameter', ''),
                'length': supplier_info.get('length', ''),
                'link': supplier_info.get('link', '')
            }
    logging.info(f"Configure GET: material_subset={json.dumps(material_subset, indent=2)}, rod_subset={json.dumps(rod_subset, indent=2)}")
    return render_template('configure.html', colors=colors['palette'], materials=material_subset, rods=rod_subset)

@app.route('/upload', methods=['GET', 'POST'])
def upload_yaml():
    if request.method == 'POST':
        file = request.files.get('yaml_file')
        if file and file.filename.endswith(('.yaml', '.yml')):
            try:
                new_material = yaml.safe_load(file)
                if not new_material or 'material_template' not in new_material:
                    return render_template('upload.html', error="Invalid YAML: missing material_template")
                if validate_yaml(new_material):
                    merge_yaml(new_material)
                    return render_template('upload.html', message="Material added successfully! Redirecting to configure...", redirect_url=url_for('configure_form'))
                else:
                    return render_template('upload.html', error="Invalid YAML structure: check required fields")
            except yaml.YAMLError as e:
                logging.error(f"YAML parsing error: {str(e)}")
                return render_template('upload.html', error=f"YAML parsing error: {str(e)}")
            except Exception as e:
                logging.error(f"Upload error: {str(e)}")
                return render_template('upload.html', error=f"Error processing file: {str(e)}")
        return render_template('upload.html', error="Please upload a valid YAML file (.yaml or .yml)")
    return render_template('upload.html')

@app.route('/designs')
def designs():
    design_files = glob.glob('projects/resources/*.yaml')
    designs = []
    for file in design_files:
        data = load_yaml(file)
        if data:
            designs.append({'name': os.path.basename(file), 'complexity': 'Unknown'})
    logging.info(f"Designs: Loaded {len(designs)} designs")
    return render_template('designs.html', designs=designs)

@app.route('/calculate', methods=['GET', 'POST'])
def calculate():
    if request.method == 'POST':
        try:
            diameter = round(float(request.form.get('diameter', 50)), 1)
            length = round(float(request.form.get('length', 10000)), 1)
            seam_allowance = round(float(request.form.get('seam_allowance', 10)), 1)
            if diameter <= 0 or length <= 0 or seam_allowance <= 0:
                return render_template('material_calculator.html', error="Dimensions must be positive numbers", units=session.get('units', 'metric'))
            material = request.form.get('material', 'ripstop')
            units = session.get('units', 'metric')
            if units == 'imperial':
                diameter = diameter * 2.54
                length = length * 2.54
                seam_allowance = seam_allowance * 2.54
            circumference = 3.14159 * diameter
            pattern_width = circumference + (2 * seam_allowance)
            pattern_height = length + (2 * seam_allowance)
            total_area = (pattern_width * pattern_height) / 1000000
            prices = {'ripstop': 15, 'polyester': 12, 'cotton': 8}
            material_cost = total_area * prices.get(material, 15)
            additional_supplies = 5
            total_cost = material_cost + additional_supplies
            result = {
                'circumference': round(circumference / (25.4 if units == 'imperial' else 10), 1),
                'pattern_width': round(pattern_width / (25.4 if units == 'imperial' else 10), 1),
                'pattern_height': round(pattern_height / (25.4 if units == 'metric' else 10), 1),
                'total_area': round(total_area, 4),
                'material_cost': round(material_cost, 2),
                'additional_supplies': round(additional_supplies, 2),
                'total_cost': round(total_cost, 2),
                'material': material,
                'shopping_list': [
                    f"{total_area:.2f}m² of {material}",
                    "2 carabiners",
                    "Matching thread",
                    "Sewing needles"
                ]
            }
            logging.info(f"Calculate: Generated result={json.dumps(result, indent=2)}")
            return render_template('material_calculator.html', result=result, units=units)
        except ValueError as e:
            logging.error(f"Calculate input error: {str(e)}")
            return render_template('material_calculator.html', error="Invalid input: use positive numbers", units=session.get('units', 'metric'))
    return render_template('material_calculator.html', units=session.get('units', 'metric'))

@app.route('/tutorial')
def tutorial():
    return render_template('construction_tutorial.html')

def validate_yaml(data):
    template_keys = {'type', 'manufacturer', 'supplier', 'eco'}
    manufacturer_keys = {'name', 'product', 'type', 'weight', 'properties'}
    supplier_keys = {'name', 'price', 'colors', 'link'}
    if not isinstance(data, dict) or 'material_template' not in data:
        return False
    mat = data['material_template']
    if not all(key in mat for key in template_keys):
        return False
    if not all(key in mat['manufacturer'] for key in manufacturer_keys):
        return False
    if not all(key in mat['supplier'] for key in supplier_keys):
        return False
    if not isinstance(mat['manufacturer']['properties'], list):
        return False
    if not isinstance(mat['supplier']['colors'], list):
        return False
    if not re.match(r'^https?://', mat['supplier']['link'):
        return False
    return True

def merge_yaml(new_material):
    mat = new_material['material_template']
    type_key = mat['type'].lower()
    supplier_key = mat['supplier']['name'].lower().replace(' ', '_')
    with open('projects/resources/suppliers.yaml', 'r') as f:
        current_suppliers = yaml.safe_load(f) or {'suppliers': {}}
    current_suppliers['suppliers'][supplier_key] = {
        'name': mat['supplier']['name'],
        'country': 'Unknown',
        'materials': {
            type_key: {
                'price': mat['supplier']['price'],
                'colors': mat['supplier']['colors'],
                'eco': mat['eco'],
                'link': mat['supplier']['link']
            }
        }
    }
    with open('projects/resources/materials.yaml', 'r') as f:
        current_materials = yaml.safe_load(f) or {'materials': {}}
    if type_key not in current_materials['materials']:
        current_materials['materials'][type_key] = {
            'manufacturer': mat['manufacturer']['name'],
            'type': mat['manufacturer']['type'],
            'weight': mat['manufacturer']['weight'],
            'properties': mat['manufacturer']['properties'],
            'suppliers': [supplier_key]
        }
    else:
        if supplier_key not in current_materials['materials'][type_key]['suppliers']:
            current_materials['materials'][type_key]['suppliers'].append(supplier_key)
    with open('projects/resources/suppliers.yaml', 'w') as f:
        yaml.safe_dump(current_suppliers, f)
    with open('projects/resources/materials.yaml', 'w') as f:
        yaml.safe_dump(current_materials, f)

if __name__ == '__main__':
    os.makedirs('projects/resources', exist_ok=True)
    required_files = ['projects/resources/tools.yaml', 'projects/resources/colors.yaml', 'projects/resources/materials.yaml', 'projects/resources/suppliers.yaml', 'projects/resources/rods.yaml']
    for file in required_files:
        if not os.path.exists(file):
            logging.error(f"Required file missing: {file}")
            exit(1)
    os.makedirs('output', exist_ok=True)
    app.run(host='0.0.0.0', port=5000)
