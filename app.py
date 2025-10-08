#!/usr/bin/env python3
"""
Kite Laundry Builder - Turnkey Entry Point
"""

import os
import sys
import yaml
import json
import subprocess

# Add Core to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'Core'))

from applications.generator import generate_production_article
from flask import Flask, render_template, request, redirect, url_for

# Configure Flask to look in Core/web for templates and static files
app = Flask(__name__,
           template_folder='Core/web',
           static_folder='Core/web/static')

@app.route('/')
def index():
    """Main menu page"""
    return render_template('index.html')

@app.route('/generate', methods=['GET', 'POST'])
def generate():
    """Generate production plan from existing YAML"""
    if request.method == 'POST':
        # Get selected design from form
        design_name = request.form['design']
        
        # Find the corresponding filename
        design_filename = None
        try:
            for file in os.listdir('projects'):
                if file.endswith('.yaml'):
                    with open(f'projects/{file}', 'r') as f:
                        try:
                            # Load YAML directly without validation
                            data = yaml.safe_load(f)
                            if data and data.get('name') == design_name:
                                design_filename = file
                                break
                        except:
                            continue
        except FileNotFoundError:
            pass
        
        if not design_filename:
            return f"Design {design_name} not found", 404
        
        try:
            # Load the YAML file directly
            with open(f'projects/{design_filename}', 'r') as f:
                design_data = yaml.safe_load(f)
            
            # Generate production article - returns HTML string
            html_content = generate_production_article(design_data)
            
            # Create output directory if it doesn't exist
            os.makedirs('output', exist_ok=True)
            
            # Save production article to output directory
            output_filename = f"output/{os.path.splitext(design_filename)[0]}_production.html"
            with open(output_filename, 'w') as f:
                f.write(html_content)
            
            # Return the generated HTML
            return render_template('result.html', content=html_content, design_name=design_name)
            
        except FileNotFoundError:
            return f"Design file {design_filename} not found", 404
        except Exception as e:
            return f"Error loading design: {str(e)}", 500
    
    # For GET request, show list of available designs
    designs = []
    try:
        for file in os.listdir('projects'):
            if file.endswith('.yaml'):
                try:
                    with open(f'projects/{file}', 'r') as f:
                        data = yaml.safe_load(f)
                        if data and 'name' in data:
                            designs.append({
                                'filename': file,
                                'name': data['name'],
                                'complexity': data.get('complexity', 'Unknown')
                            })
                except:
                    continue
    except FileNotFoundError:
        designs = []
    
    return render_template('generate.html', designs=designs)

@app.route('/designs')
def designs():
    """View existing designs"""
    designs = []
    try:
        for file in os.listdir('projects'):
            if file.endswith('.yaml'):
                try:
                    with open(f'projects/{file}', 'r') as f:
                        data = yaml.safe_load(f)
                        if data and 'name' in data:
                            designs.append({
                                'filename': file,
                                'name': data['name'],
                                'complexity': data.get('complexity', 'Unknown')
                            })
                except:
                    continue
    except FileNotFoundError:
        designs = []
    
    return render_template('designs.html', designs=designs)

if __name__ == '__main__':
    app.run(debug=True)

