from flask import Blueprint, render_template, make_response
from app.models import Design
from app.utils.svg_generator import generate_svg
from weasyprint import HTML

main = Blueprint('main', __name__, template_folder='../templates')

@main.route('/')
@main.route('/start')
def start():
    return render_template('start.html')

@main.route('/select')
def select():
    return render_template('select.html')

@main.route('/configure')
def configure():
    return render_template('configure.html')

@main.route('/output')
def output():
    return render_template('output.html')

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
