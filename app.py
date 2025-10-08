#!/usr/bin/env python3
"""
Kite Laundry Builder - Turnkey Entry Point
"""

import os
import sys
import yaml

# Add Core to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'Core'))

from applications.generator import generate_production_article
from Core.web.article_viewer import article_bp
from flask import Flask, render_template, request, redirect, url_for

# Configure Flask to look in Core/web for templates and static files
app = Flask(__name__,
           template_folder='Core/web',
           static_folder='Core/web/static')

# Register article viewer blueprint
app.register_blueprint(article_bp, url_prefix='/article')

def scan_projects_directory():
    """Scan the projects directory for all available designs"""
    designs = []
    
    # Define the exact paths we know exist
    known_paths = [
        ('line_laundry', 'tube', None),
        ('line_laundry', 'windsock', None),
        ('line_laundry', 'animal', 'clownfish'),
    ]
    
    for base_dir, sub_dir, animal_dir in known_paths:
        if base_dir == 'line_laundry':
            if sub_dir == 'animal' and animal_dir:
                # Handle animal subdirectories
                animal_path = os.path.join('projects', base_dir, sub_dir, animal_dir)
                if os.path.exists(animal_path):
                    yaml_file = os.path.join(animal_path, f'{animal_dir}.yaml')
                    if os.path.exists(yaml_file):
                        try:
                            with open(yaml_file, 'r') as f:
                                data = yaml.safe_load(f)
                                name = data.get('name', animal_dir) if data else animal_dir
                                designs.append({
                                    'filename': os.path.join(base_dir, sub_dir, animal_dir, f'{animal_dir}.yaml'),
                                    'name': name,
                                    'complexity': data.get('complexity', 'Unknown') if data else 'Unknown',
                                    'category': sub_dir.replace('_', ' ').title(),
                                    'subcategory': animal_dir.replace('_', ' ').title()
                                })
                        except:
                            designs.append({
                                'filename': os.path.join(base_dir, sub_dir, animal_dir, f'{animal_dir}.yaml'),
                                'name': animal_dir,
                                'complexity': 'Unknown',
                                'category': sub_dir.replace('_', ' ').title(),
                                'subcategory': animal_dir.replace('_', ' ').title()
                            })
            else:
                # Handle tube and windsock directories
                dir_path = os.path.join('projects', base_dir, sub_dir)
                if os.path.exists(dir_path):
                    for file in os.listdir(dir_path):
                        if file.endswith('.yaml'):
                            file_path = os.path.join(dir_path, file)
                            try:
                                with open(file_path, 'r') as f:
                                    data = yaml.safe_load(f)
                                    name = data.get('name', os.path.splitext(file)[0]) if data else os.path.splitext(file)[0]
                                    designs.append({
                                        'filename': os.path.join(base_dir, sub_dir, file),
                                        'name': name,
                                        'complexity': data.get('complexity', 'Unknown') if data else 'Unknown',
                                        'category': sub_dir.replace('_', ' ').title(),
                                        'subcategory': 'N/A'
                                    })
                            except:
                                designs.append({
                                    'filename': os.path.join(base_dir, sub_dir, file),
                                    'name': os.path.splitext(file)[0],
                                    'complexity': 'Unknown',
                                    'category': sub_dir.replace('_', ' ').title(),
                                    'subcategory': 'N/A'
                                })
    
    # Check one_line_kites directory
    one_line_kites_path = os.path.join('projects', 'one_line_kites')
    if os.path.exists(one_line_kites_path):
        for item in os.listdir(one_line_kites_path):
            if item.endswith('.yaml'):
                file_path = os.path.join(one_line_kites_path, item)
                try:
                    with open(file_path, 'r') as f:
                        data = yaml.safe_load(f)
                        name = data.get('name', os.path.splitext(item)[0]) if data else os.path.splitext(item)[0]
                        designs.append({
                            'filename': os.path.join('one_line_kites', item),
                            'name': name,
                            'complexity': data.get('complexity', 'Unknown') if data else 'Unknown',
                            'category': 'One Line Kites',
                            'subcategory': 'N/A'
                        })
                except:
                    designs.append({
                        'filename': os.path.join('one_line_kites', item),
                        'name': os.path.splitext(item)[0],
                        'complexity': 'Unknown',
                        'category': 'One Line Kites',
                        'subcategory': 'N/A'
                    })
    
    return designs

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
            # Get all designs
            all_designs = scan_projects_directory()
            
            # Find the design with the matching name
            for design in all_designs:
                if design['name'] == design_name:
                    design_filename = design['filename']
                    break
        except:
            pass
        
        if not design_filename:
            return f"Design {design_name} not found", 404
        
        try:
            # Load the YAML file directly
            with open(os.path.join('projects', design_filename), 'r') as f:
                design_data = yaml.safe_load(f)
            
            # Generate production article - returns HTML string
            html_content = generate_production_article(design_data)
            
            # Create output directory if it doesn't exist
            os.makedirs('output', exist_ok=True)
            
            # Save production article to output directory
            output_filename = f"output/{os.path.splitext(os.path.basename(design_filename))[0]}_production.html"
            with open(output_filename, 'w') as f:
                f.write(html_content)
            
            # Return the generated HTML
            return render_template('result.html', content=html_content, design_name=design_name)
            
        except FileNotFoundError:
            return f"Design file {design_filename} not found", 404
        except Exception as e:
            return f"Error loading design: {str(e)}", 500
    
    # For GET request, show list of available designs
    try:
        designs = scan_projects_directory()
    except:
        designs = []
    
    return render_template('generate.html', designs=designs)

@app.route('/designs')
def designs():
    """View existing designs"""
    try:
        designs = scan_projects_directory()
    except:
        designs = []
    
    return render_template('designs.html', designs=designs)

if __name__ == '__main__':
    app.run(debug=True)
