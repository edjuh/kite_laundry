from flask import Flask, render_template, request, redirect, url_for
import os
from src.generator import generate_production_article

app = Flask(__name__)

@app.route('/')
def index():
    """Main menu page"""
    return render_template('index.html')

@app.route('/design', methods=['GET', 'POST'])
def design():
    """Design creation page"""
    if request.method == 'POST':
        # Process form data
        design_params = {
            'name': request.form['name'],
            'material': request.form['material'],
            'colors': request.form.getlist('colors'),
            'dimensions': {
                'width': request.form['width'],
                'height': request.form['height']
            }
        }
        
        # Generate production article
        html_content = generate_production_article(design_params)
        
        # Return the generated HTML
        return render_template('result.html', content=html_content)
    
    return render_template('design_form.html')

@app.route('/designs')
def designs():
    """View existing designs"""
    # List YAML files in configs directory
    designs = []
    for file in os.listdir('configs'):
        if file.endswith('.yaml'):
            designs.append(file[:-5])  # Remove .yaml extension
    
    return render_template('designs.html', designs=designs)

if __name__ == '__main__':
    app.run(debug=True)

