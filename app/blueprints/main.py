from flask import Blueprint, render_template, request, redirect, url_for
from app.models import Design
from app.utils.svg_generator import generate_svg
from weasyprint import HTML
from app import db
from flask import make_response
import json

main = Blueprint('main', __name__, template_folder='../templates')

@main.route('/')
@main.route('/start')
def start():
    return render_template('start.html')

@main.route('/select')
def select():
    return render_template('select.html')

@main.route('/configure', methods=['GET', 'POST'])
def configure():
    if request.method == 'POST':
        name = request.form['name']
        type_ = request.form['type']
        dimensions_str = request.form['dimensions']  # e.g., 'length:500,width:50,num_gores:6'
        # Parse dimensions to JSON, store num_gores as int without units
        dims = {}
        for pair in dimensions_str.split(','):
            key, value = pair.split(':')
            if key == 'num_gores':
                dims[key] = int(value)
            else:
                dims[key] = float(value)
        dimensions = json.dumps(dims)
        colors = request.form['colors']
        rod = request.form['rod']
        unit_label = request.form['unit_label']

        design = Design(name=name, type=type_, dimensions=dimensions, colors=colors, rod=rod, unit_label=unit_label)
        db.session.add(design)
        db.session.commit()
        return redirect(url_for('main.output', design_id=design.id))
    return render_template('configure.html')

@main.route('/output/<int:design_id>')
def output():
    design = Design.query.get_or_404(design_id)
    svg = generate_svg(design)
    return render_template('output.html', design=design, svg=svg)

@main.route('/designs')
def designs():
    designs = Design.query.all()
    designs_with_svg = [(design, generate_svg(design)) for design in designs]
    return render_template('designs.html', designs_with_svg=designs_with_svg)

@main.route('/help')
def help():
    return render_template('help.html')

@main.route('/download_pdf/<int:design_id>')
def download_pdf(design_id):
    design = Design.query.get_or_404(design_id)
    svg = generate_svg(design)
    html_content = f"""
    <html>
    <body>
    <h1>{design.name}</h1>
    <p>Type: {design.type}</p>
    <p>Dimensions: {design.dimensions}</p>
    <p>Colors: {design.colors}</p>
    <p>Rod: {design.rod or 'None'}</p>
    <p>Unit: {design.unit_label}</p>
    <img src="{svg}" alt="Preview">
    </body>
    </html>
    """
    pdf = HTML(string=html_content).write_pdf()
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename={design.name}.pdf'
    return response
