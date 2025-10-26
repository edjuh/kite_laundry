# Oversight Marker: Last Verified: October 26, 2025, 6:57 PM CET by Grok 3 (xAI)
# Purpose: Sets up Flask app with Start and Select routes for Kite Laundry Design Generator MVP.
# Next Step: Add design configuration routes in Step 6.

from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'super_secret_key'

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
    return render_template('select.html', units=units, types=['tail', 'drogue', 'graded_tail', 'spinner'])

if __name__ == '__main__':
    app.run(debug=True, port=5000)
