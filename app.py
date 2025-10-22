from flask import Flask, render_template, request, session
import yaml
import svgwrite
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os
import re
import glob

app = Flask(__name__)
app.secret_key = 'kite-laundry-key'

def load_yaml(file_path):
    try:
        with open(file_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception:
        return {}

tools = load_yaml('projects/resources/tools.yaml') or {}
colors = load_yaml('projects/resources/colors.yaml') or {'palette': {}}
materials = load_yaml('projects/resources/materials.yaml') or {'materials': {}}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start', methods=['GET', 'POST'])
def start():
    if request.method == 'POST':
        session['units'] = request.form['units']
        return render_template('select.html', forms=['tail', 'drogue', 'windsock'])
    return render_template('start.html')

@app.route('/select', methods=['GET', 'POST'])
def select_form():
    if request.method == 'POST':
        session['form_type'] = request.form['form_type']
        units = session.get('units', 'metric')
        material_subset = {}
        for mat_type, mat_info in materials.get('materials', {}).items():
            if mat_type == 'ripstop':
                material_subset['ripstop'] = mat_info.get(units, {})
            else:
                material_subset[mat_type] = mat_info
        return render_template('configure.html', colors=colors['palette'], materials=material_subset)
    return render_template('select.html', forms=['tail', 'drogue', 'windsock'])

@app.route('/configure', methods=['GET', 'POST'])
def configure_form():
    if request.method == 'POST':
        form_type = session.get('form_type', 'tail')
        length = float(request.form['length'])
        width = float(request.form['width'])
        color_codes = request.form.getlist('colors')
        material = request.form['material']
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
        c.drawString(100, 690, f"Material: {material}")
        c.drawString(100, 670, f"Colors: {', '.join(colors['palette'].get(c, {'name': 'Unknown'})['name'] for c in color_codes)}")
        c.save()
        pattern_data = {
            'pieces': [
                {'width': width_cm * 10, 'height': length_cm * 10, 'position': {'x': 0, 'y': 0}},
                {'width': 50, 'height': 50, 'position': {'x': 0, 'y': length_cm * 10 * 0.25}},
                {'width': 50, 'height': 50, 'position': {'x': 0, 'y': length_cm * 10 * 0.75}}
            ]
        }
        return render_template('output.html', form_type=form_type, length=length, width=width, colors=[colors['palette'].get(c, {'name': 'Unknown'})['name'] for c in color_codes], material=material, units=units, svg_file=svg_file, pdf_file=pdf_file, tools=tools, pattern_data=pattern_data)
    units = session.get('units', 'metric')
    material_subset = {}
    for mat_type, mat_info in materials.get('materials', {}).items():
        if mat_type == 'ripstop':
            material_subset['ripstop'] = mat_info.get(units, {})
        else:
            material_subset[mat_type] = mat_info
    return render_template('configure.html', colors=colors['palette'], materials=material_subset)

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
                    return render_template('upload.html', message="Material added successfully!")
                else:
                    return render_template('upload.html', error="Invalid YAML structure: check required fields")
            except yaml.YAMLError as e:
                return render_template('upload.html', error=f"YAML parsing error: {str(e)}")
            except Exception as e:
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
    return render_template('designs.html', designs=designs)

@app.route('/calculate', methods=['GET', 'POST'])
def calculate():
    if request.method == 'POST':
        diameter = float(request.form.get('diameter', 50))
        length = float(request.form.get('length', 10000))
        material = request.form.get('material', 'ripstop')
        seam_allowance = float(request.form.get('seam_allowance', 10))
        units = session.get('units', 'metric')
        if units == 'imperial':
            diameter = diameter * 25.4
            length = length * 25.4
            seam_allowance = seam_allowance * 25.4
        circumference = 3.14159 * diameter
        pattern_width = circumference + (2 * seam_allowance)
        pattern_height = length + (2 * seam_allowance)
        total_area = (pattern_width * pattern_height) / 1000000
        prices = {'ripstop': 15, 'polyester': 12, 'cotton': 8}
        material_cost = total_area * prices.get(material, 15)
        additional_supplies = 5
        total_cost = material_cost + additional_supplies
        result = {
            'circumference': circumference / (25.4 if units == 'imperial' else 10),
            'pattern_width': pattern_width / (25.4 if units == 'imperial' else 10),
            'pattern_height': pattern_height / (25.4 if units == 'metric' else 10),
            'total_area': total_area,
            'material_cost': material_cost,
            'additional_supplies': additional_supplies,
            'total_cost': total_cost,
            'material': material,
            'shopping_list': [
                f"{total_area:.2f}m² of {material}",
                "2 carabiners",
                "Matching thread",
                "Sewing needles"
            ]
        }
        return render_template('material_calculator.html', result=result, units=units)
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
    if not re.match(r'^https?://', mat['supplier']['link']):
        return False
    return True

def merge_yaml(new_material):
    mat = new_material['material_template']
    type_key = mat['type'].lower()
    with open('projects/resources/materials.yaml', 'r') as f:
        current_materials = yaml.safe_load(f) or {'materials': {}}
    units = session.get('units', 'metric')
    if type_key == 'ripstop':
        current_materials['materials'].setdefault('ripstop', {}).setdefault(units, {}).update({
            mat['supplier']['name'].lower().replace(' ', '_'): {
                'manufacturer': mat['manufacturer']['name'],
                'product': mat['manufacturer']['product'],
                'type': mat['manufacturer']['type'],
                'weight': mat['manufacturer']['weight'],
                'properties': mat['manufacturer']['properties'],
                'price': mat['supplier']['price'],
                'colors': mat['supplier']['colors']
            }
        })
    else:
        current_materials['materials'][type_key] = {
            'supplier': mat['supplier']['name'],
            'type': mat['manufacturer']['type'],
            'weight': mat['manufacturer']['weight'],
            'properties': mat['manufacturer']['properties'],
            'price': mat['supplier']['price'],
            'colors': mat['supplier']['colors']
        }
    with open('projects/resources/materials.yaml', 'w') as f:
        yaml.safe_dump(current_materials, f)

if __name__ == '__main__':
    os.makedirs('output', exist_ok=True)
    app.run(host='0.0.0.0', port=5000)
