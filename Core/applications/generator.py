import yaml
from jinja2 import Template
import json
import os

def load_resources():
    """Load resource files"""
    resources = {}
    
    # Load colors
    try:
        with open('Core/configurations/resources/colors.yaml', 'r') as f:
            resources['colors'] = yaml.safe_load(f)
    except FileNotFoundError:
        resources['colors'] = {'palette': {}, 'tips': []}
    
    # Load materials
    try:
        with open('Core/configurations/resources/ripstop.yaml', 'r') as f:
            resources['materials'] = yaml.safe_load(f)
    except FileNotFoundError:
        resources['materials'] = {'materials': {}}
    
    # Load tools
    try:
        with open('Core/configurations/resources/tools.yaml', 'r') as f:
            resources['tools'] = yaml.safe_load(f)
    except FileNotFoundError:
        resources['tools'] = {'tools': {}}
    
    return resources

def get_kite_y_position(complexity):
    """Calculate the Y position for the kite based on complexity"""
    # Map complexity (1-5) to kite Y position
    # Complexity 1 (easy) -> kite higher (y=40)
    # Complexity 5 (expert) -> kite lower (y=80)
    if complexity <= 1:
        return 40  # High position (easy to fly)
    elif complexity >= 5:
        return 80  # Low position (hard to fly)
    else:
        return 40 + (complexity - 1) * 10  # Linear interpolation

def get_difficulty_pointer_position(complexity):
    """Calculate the Y position for the difficulty pointer based on complexity"""
    # Clamp complexity to valid range (1-5)
    clamped_complexity = max(1, min(5, complexity))
    
    # Map complexity (1-5) to pointer position (0-50)
    # Complexity 1 -> position 50 (bottom)
    # Complexity 5 -> position 0 (top)
    if clamped_complexity <= 1:
        return 25  # Bottom position
    elif clamped_complexity >= 5:
        return -25  # Top position
    else:
        return 25 - (clamped_complexity - 1) * 12.5  # Linear interpolation

def normalize_yaml_structure(params, resources):
    """Normalize different YAML structures to a common format"""
    normalized = params.copy()
    
    # Handle geometry field
    if 'geometry_type' in params:
        normalized['geometry'] = {'type': params['geometry_type']}
    elif 'geometry' not in params:
        normalized['geometry'] = {'type': 'unknown'}
    
    # Handle materials field - convert dict to list if needed
    if isinstance(params.get('materials'), dict):
        materials_list = []
        for item, qty in params['materials'].items():
            materials_list.append({'item': item, 'qty': qty})
        normalized['materials'] = materials_list
    elif isinstance(params.get('materials'), list):
        # Already in correct format
        pass
    else:
        normalized['materials'] = []
    
    # Add color information from palette
    if 'colors' in params:
        color_info = []
        for color_code in params['colors']:
            if color_code in resources['colors']['palette']:
                color_info.append({
                    'code': color_code,
                    'name': resources['colors']['palette'][color_code]['name'],
                    'hex': resources['colors']['palette'][color_code]['hex']
                })
        normalized['color_info'] = color_info
    
    # Ensure parameters exists
    if 'parameters' not in params:
        normalized['parameters'] = {}
    
    return normalized

def generate_production_article(params):
    """Generate HTML production article based on parameters"""
    try:
        # Load resources
        resources = load_resources()
        
        # Load the template
        with open('Core/web/article_template.html', 'r') as f:
            template_content = f.read()
        
        # Create Jinja2 template
        template = Template(template_content)
        
        # Calculate positions
        pointer_position = get_difficulty_pointer_position(params.get('complexity', 1))
        kite_y_position = get_kite_y_position(params.get('complexity', 1))
        
        # Normalize the params for the template
        normalized_params = normalize_yaml_structure(params, resources)
        
        # Add positions to params
        normalized_params['pointer_position'] = pointer_position
        normalized_params['kite_y_position'] = kite_y_position
        
        # Add static URL base for resources
        normalized_params['static_url'] = '/static'
        
        # Render the template with normalized params
        html_content = template.render(params=normalized_params, resources=resources)
        
        return html_content
        
    except Exception as e:
        # Return error details in the HTML
        error_html = f"""
        <html>
        <body>
            <h1>Error Generating Production Article</h1>
            <p><strong>Error:</strong> {str(e)}</p>
            <h2>Debug Information:</h2>
            <pre>{json.dumps(params, indent=2)}</pre>
        </body>
        </html>
        """
        return error_html

