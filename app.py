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
from flask import Flask, render_template, request, redirect, url_for

# Configure Flask to look in Core/web for templates and static files
app = Flask(__name__,
           template_folder='Core/web',
           static_folder='Core/web/static')

# Import and register the article viewer blueprint
try:
    from Core.web.article_viewer import article_bp
    app.register_blueprint(article_bp, url_prefix='/article')
except ImportError:
    print("Warning: Could not import article viewer blueprint")

# Import the new article generator
try:
    from Core.applications.article_generator import generate_article
    print("Successfully imported article generator")
except ImportError as e:
    print(f"Warning: Could not import article generator: {e}")
    generate_article = None

def scan_projects_directory():
    """Scan the projects directory for all available designs"""
    designs = []
    
    print("=== Scanning projects directory ===")
    
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
                print(f"Checking animal path: {animal_path}")
                if os.path.exists(animal_path):
                    yaml_file = os.path.join(animal_path, f'{animal_dir}.yaml')
                    print(f"Checking animal YAML: {yaml_file}")
                    if os.path.exists(yaml_file):
                        try:
                            with open(yaml_file, 'r') as f:
                                data = yaml.safe_load(f)
                                print(f"Animal YAML data: {data}")
                                name = data.get('name', animal_dir.capitalize()) if data else animal_dir.capitalize()
                                # Skip config files
                                if not yaml_file.endswith('config.yaml'):
                                    designs.append({
                                        'filename': os.path.join(base_dir, sub_dir, animal_dir, f'{animal_dir}.yaml'),
                                        'name': name,
                                        'complexity': data.get('complexity', 'Unknown') if data else 'Unknown',
                                        'category': sub_dir.replace('_', ' ').title(),
                                        'subcategory': animal_dir.replace('_', ' ').title()
                                    })
                                    print(f"Added animal design: {name}")
                        except Exception as e:
                            print(f"Error reading animal YAML: {e}")
                            # Skip config files
                            if not yaml_file.endswith('config.yaml'):
                                designs.append({
                                    'filename': os.path.join(base_dir, sub_dir, animal_dir, f'{animal_dir}.yaml'),
                                    'name': animal_dir.capitalize(),
                                    'complexity': 'Unknown',
                                    'category': sub_dir.replace('_', ' ').title(),
                                    'subcategory': animal_dir.replace('_', ' ').title()
                                })
            else:
                # Handle tube and windsock directories
                dir_path = os.path.join('projects', base_dir, sub_dir)
                print(f"Checking directory: {dir_path}")
                if os.path.exists(dir_path):
                    for file in os.listdir(dir_path):
                        if file.endswith('.yaml') and not file.startswith('config'):
                            file_path = os.path.join(dir_path, file)
                            print(f"Checking file: {file_path}")
                            try:
                                with open(file_path, 'r') as f:
                                    data = yaml.safe_load(f)
                                    print(f"YAML data for {file}: {data}")
                                    name = data.get('name', os.path.splitext(file)[0].capitalize()) if data else os.path.splitext(file)[0].capitalize()
                                    designs.append({
                                        'filename': os.path.join(base_dir, sub_dir, file),
                                        'name': name,
                                        'complexity': data.get('complexity', 'Unknown') if data else 'Unknown',
                                        'category': sub_dir.replace('_', ' ').title(),
                                        'subcategory': 'N/A'
                                    })
                                    print(f"Added design: {name}")
                            except Exception as e:
                                print(f"Error reading YAML {file_path}: {e}")
                                designs.append({
                                    'filename': os.path.join(base_dir, sub_dir, file),
                                    'name': os.path.splitext(file)[0].capitalize(),
                                    'complexity': 'Unknown',
                                    'category': sub_dir.replace('_', ' ').title(),
                                    'subcategory': 'N/A'
                                })
    
    # Check one_line_kites directory
    one_line_kites_path = os.path.join('projects', 'one_line_kites')
    print(f"Checking one_line_kites path: {one_line_kites_path}")
    if os.path.exists(one_line_kites_path):
        for item in os.listdir(one_line_kites_path):
            if item.endswith('.yaml') and not item.startswith('config'):
                file_path = os.path.join(one_line_kites_path, item)
                try:
                    with open(file_path, 'r') as f:
                        data = yaml.safe_load(f)
                        name = data.get('name', os.path.splitext(item)[0].capitalize()) if data else os.path.splitext(item)[0].capitalize()
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
                        'name': os.path.splitext(item)[0].capitalize(),
                        'complexity': 'Unknown',
                        'category': 'One Line Kites',
                        'subcategory': 'N/A'
                    })
    
    print(f"Total designs found: {len(designs)}")
    for design in designs:
        print(f"Design: {design}")
    
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
        print(f"Selected design: {design_name}")
        
        # Find the corresponding filename
        design_filename = None
        try:
            # Get all designs
            all_designs = scan_projects_directory()
            
            # Find the design with the matching name
            for design in all_designs:
                if design['name'] == design_name:
                    design_filename = design['filename']
                    print(f"Found filename: {design_filename}")
                    break
        except Exception as e:
            print(f"Error scanning designs: {e}")
            pass
        
        if not design_filename:
            return f"Design {design_name} not found", 404
        
        try:
            # Get the project path
            project_path = os.path.join('projects', os.path.dirname(design_filename))
            print(f"Project path: {project_path}")
            
            # Generate article based on design type
            if 'tube' in design_filename and generate_article:
                print("Using tube article generator")
                html_content = generate_article(project_path)
            else:
                print("Using original generator")
                # Use the original generator for other designs
                with open(os.path.join('projects', design_filename), 'r') as f:
                    design_data = yaml.safe_load(f)
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
            print(f"Error in generate: {e}")
            import traceback
            traceback.print_exc()
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

@app.route('/tube-designer', methods=['GET', 'POST'])
def tube_designer():
    """Tube designer with parameter form"""
    result = None
    
    if request.method == 'POST':
        # Get form parameters
        parameters = {
            'diameter': float(request.form.get('diameter', 50)),
            'length': float(request.form.get('length', 10000)),
            'color': request.form.get('color', 'single'),
            'material': request.form.get('material', 'ripstop'),
            'weight': float(request.form.get('weight', 30)),
            'seam_allowance': float(request.form.get('seam_allowance', 10)),
            'attachment_points': [
                {'position': 0.25, 'type': 'carabiner'},
                {'position': 0.75, 'type': 'carabiner'}
            ]
        }
        
        try:
            # Generate pattern
            pattern = generate_tube_pattern(parameters)
            
            # Generate instructions
            instructions = generate_tube_instructions(parameters)
            
            # Generate HTML result
            result = f"""
            <div class="pattern-info">
                <h3>Pattern Information</h3>
                <p><strong>Circumference:</strong> {pattern['total_material']['circumference']:.1f}mm</p>
                <p><strong>Pattern Width:</strong> {pattern['total_material']['width']:.1f}mm</p>
                <p><strong>Pattern Height:</strong> {pattern['total_material']['height']:.1f}mm</p>
                <p><strong>Material Needed:</strong> {pattern['total_material']['area_cm2']:.1f}cm² ({pattern['total_material']['area_m2']:.4f}m²)</p>
            </div>
            
            <div class="pattern-pieces">
                <h3>Pattern Pieces</h3>
                <ul>
                    <li><strong>Main tube:</strong> {pattern['pieces'][0]['width']:.1f}mm × {pattern['pieces'][0]['height']:.1f}mm</li>
                    <li><strong>Reinforcement 1:</strong> {pattern['pieces'][1]['width']:.1f}mm × {pattern['pieces'][1]['height']:.1f}mm (at 25%)</li>
                    <li><strong>Reinforcement 2:</strong> {pattern['pieces'][2]['width']:.1f}mm × {pattern['pieces'][2]['height']:.1f}mm (at 75%)</li>
                </ul>
            </div>
            
            <div class="instructions">
                <h3>Instructions</h3>
                <pre>{instructions}</pre>
            </div>
            """
            
        except ValueError as e:
            result = f"<div class='error'>Error: {str(e)}</div>"
    
    return render_template('tube_form.html', result=result)

@app.route('/material-calculator')
def material_calculator():
    return render_template('material_calculator.html')

@app.route('/construction-tutorial')
def construction_tutorial():
    return render_template('construction_tutorial.html')