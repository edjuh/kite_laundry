from flask import Blueprint, render_template
from app.models import Design
from app.utils.svg_generator import generate_svg

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
