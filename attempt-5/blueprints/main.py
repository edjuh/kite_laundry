from flask import Blueprint, render_template, request, redirect, url_for

main_bp = Blueprint('main', __name__)

@main_bp.route('/', methods=['GET', 'POST'])
def start():
    if request.method == 'POST':
        units = request.form['units']
        return redirect(url_for('main.select_type', units=units))
    return render_template('start.html')

@main_bp.route('/select', methods=['GET', 'POST'])
def select_type():
    units = request.args.get('units')
    if request.method == 'POST':
        design_type = request.form['type']
        return redirect(url_for('design.configure', units=units, type=design_type))
    return render_template('select.html', units=units, types=['tail', 'drogue', 'graded_tail', 'spinner'])

@main_bp.route('/help')
def help():
    return render_template('help.html')
