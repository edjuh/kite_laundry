import yaml
import os
from pathlib import Path
from ..pattern_generators.tube_generator import generate_tube_pattern, generate_tube_instructions, perform_web_search

def generate_article(project_path):
    """
    Generate a comprehensive article for a tube design
    
    Args:
        project_path (str): Path to the project directory
    
    Returns:
        str: HTML content for the article
    """
    # Load the YAML configuration
    with open(os.path.join(project_path, 'tube.yaml'), 'r') as f:
        config = yaml.safe_load(f)
    
    # Generate pattern
    pattern = generate_tube_pattern(config.get('parameters', {}))
    
    # Generate instructions
    instructions = generate_tube_instructions(config.get('parameters', {}))
    
    # Perform web search
    search_terms = config.get('search_terms', [])
    search_results = perform_web_search(search_terms)
    
    # Generate HTML
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>{config.get('name', 'Tube')} - Kite Laundry Design</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
        .pattern {{ background-color: #f9f9f9; padding: 15px; }}
        .instructions {{ background-color: #f9f9f9; padding: 15px; }}
        .search-results {{ background-color: #f9f9f9; padding: 15px; }}
        .result {{ margin: 10px 0; padding: 10px; background-color: white; border: 1px solid #eee; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{config.get('name', 'Tube')}</h1>
        <p>Complexity: {'★' * config.get('complexity', 1)}</p>
        <p>{config.get('description', '')}</p>
    </div>
    
    <div class="section pattern">
        <h2>Pattern</h2>
        <p>Width: {pattern['total_material']['width']:.1f}mm</p>
        <p>Height: {pattern['total_material']['height']:.1f}mm</p>
        <p>Material needed: {pattern['total_material']['area']:.0f}mm²</p>
        
        <h3>Pieces:</h3>
        <ul>
"""
    
    for piece in pattern['pieces']:
        html_content += f"            <li>{piece['name']}: {piece['shape']} ({piece['width']:.1f}mm x {piece['height']:.1f}mm)</li>\n"
    
    html_content += """        </ul>
    </div>
    
    <div class="section instructions">
        <h2>Sewing Instructions</h2>
        <pre>"""
    
    # Convert markdown to HTML (simplified)
    html_content += instructions.replace('\n', '<br>').replace('###', '<h3>').replace('##', '<h2>').replace('#', '<h1>')
    
    html_content += """</pre>
    </div>
    
    <div class="section search-results">
        <h2>Related Resources</h2>
"""
    
    if search_results:
        for result in search_results:
            html_content += f"""        <div class="result">
            <h3><a href="{result['url']}" target="_blank">{result['title']}</a></h3>
            <p>{result['description']}</p>
        </div>
"""
    else:
        html_content += "        <p>No search results available.</p>\n"
    
    html_content += """    </div>
</body>
</html>
"""
    
    return html_content
