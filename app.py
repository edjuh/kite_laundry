from flask import Flask, render_template, request, session
import yaml
import svgwrite
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os

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
materials = load_yaml('projects/resources/ripstop.yaml') or {'materials': {}}

beaufort_to_kph = {0: (0, 1), 1: (1, 5), 2: (6, 11), 3: (12, 19), 4: (20, 28), 5: (29, 38), 6: (39, 49), 7: (50, 61)}

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
        return render_template('configure.html', colors=colors['palette'], materials=materials['materials'], beaufort_range=range(8))
    return render_template('select.html', forms=['tail', 'drogue', 'windsock'])

@app.route('/configure', methods=['GET', 'POST'])
def configure_form():
    if request.method == 'POST':
        form_type = session.get('form_type', 'tail')
        length = float(request.form['length'])
        width = float(request.form['width'])
        color = request.form['color']
        material = request.form['material']
        beaufort = int(request.form['beaufort'])
        units = session.get('units', 'metric')
        if units == 'imperial':
            length_cm = length * 2.54
            width_cm = width * 2.54
        else:
            length_cm = length
            width_cm = width
        svg_file = f"output/{form_type}_template.svg"
        dwg = svgwrite.Drawing(svg_file, profile='tiny', size=(f"{width_cm*10}mm", f"{length_cm*10}mm"))
        dwg.add(dwg.rect((0, 0), (width_cm*10, length_cm*10), fill=colors['palette'].get(color, {'hex': '#FFFFFF'})['hex']))
        dwg.save()
        pdf_file = f"output/{form_type}_template.pdf"
        c = canvas.Canvas(pdf_file, pagesize=A4)
        c.drawString(100, 750, f"{form_type.capitalize()} Template")
        c.drawString(100, 730, f"Length: {length} {'cm' if units == 'metric' else 'in'}")
        c.drawString(100, 710, f"Width: {width} {'cm' if units == 'metric' else 'in'}")
        c.drawString(100, 690, f"Material: {material}")
        c.drawString(100, 670, f"Color: {colors['palette'].get(color, {'name': 'Unknown'})['name']}")
        c.drawString(100, 650, f"Wind: {beaufort} Beaufort ({beaufort_to_kph[beaufort][0]}-{beaufort_to_kph[beaufort][1]} kph)")
        c.save()
        return render_template('output.html', form_type=form_type, length=length, width=width, color=colors['palette'].get(color, {'name': 'Unknown'})['name'], material=material, beaufort=beaufort, units=units, svg_file=svg_file, pdf_file=pdf_file)
    return render_template('configure.html', colors=colors['palette'], materials=materials['materials'], beaufort_range=range(8))

if __name__ == '__main__':
    os.makedirs('output', exist_ok=True)
    app.run(host='0.0.0.0', port=5000)
