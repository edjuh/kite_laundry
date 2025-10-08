import yaml
import os
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
    tube_yaml_path = os.path.join(project_path, 'tube.yaml')
    
    if not os.path.exists(tube_yaml_path):
        raise FileNotFoundError(f"tube.yaml not found at {tube_yaml_path}")
    
    try:
        with open(tube_yaml_path, 'r') as f:
            config = yaml.safe_load(f)
    except Exception as e:
        raise Exception(f"Error loading YAML from {tube_yaml_path}: {e}")
    
    if config is None:
        raise Exception(f"YAML file is empty or invalid: {tube_yaml_path}")
    
    # Ensure parameters exists
    if 'parameters' not in config:
        config['parameters'] = {}
    
    # Generate pattern
    pattern = generate_tube_pattern(config['parameters'])
    
    # Generate instructions
    instructions = generate_tube_instructions(config['parameters'])
    
    # Perform web search
    search_terms = config.get('search_terms', [])
    search_results = perform_web_search(search_terms)
    
    # Get difficulty level
    difficulty = config.get('complexity', 1)
    
    # Determine time and skill level based on difficulty
    if difficulty <= 2:
        time_level = "Easy"
        skill_level = "Beginner"
    elif difficulty <= 3:
        time_level = "Moderate"
        skill_level = "Intermediate"
    else:
        time_level = "Challenging"
        skill_level = "Advanced"
    
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
        .difficulty-meter {{ text-align: center; margin: 20px 0; }}
        .difficulty-meter svg {{ max-width: 200px; }}
        .info-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
        .info-box {{ background-color: #f9f9f9; padding: 15px; border-radius: 5px; }}
        .info-box h3 {{ margin-top: 0; }}
        .dimensions {{ background: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
        .dimensions p {{ margin: 8px 0; font-size: 16px; }}
        .pieces-list {{ list-style: none; padding: 0; }}
        .pieces-list li {{ background: #f8f9fa; padding: 12px; margin: 8px 0; border-radius: 5px; border-left: 4px solid #007bff; font-size: 16px; }}
        .pieces-list li strong {{ color: #007bff; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{config.get('name', 'Tube')}</h1>
        <div class="difficulty-meter">
            <h3>Project Difficulty</h3>
            <svg width="200" height="150" viewBox="0 0 200 150" xmlns="http://www.w3.org/2000/svg">
                <!-- Sky background -->
                <rect width="200" height="150" fill="#87CEEB"/>
                
                <!-- Ground -->
                <rect y="120" width="200" height="30" fill="#90EE90"/>
                
                <!-- Kite line -->
                <line x1="100" y1="120" x2="100" y2="30" stroke="#333" stroke-width="1"/>
                
                <!-- Kite - position based on difficulty -->
                <!-- Adjust the y position based on difficulty: lower difficulty = higher kite -->
                <g transform="translate(100, {30 + (5 - difficulty) * 15})">
                    <!-- Flag pole -->
                    <line x1="0" y1="-15" x2="0" y2="25" stroke="#333" stroke-width="2"/>
                    
                    <!-- Flag -->
                    <path d="M 0 -15 L 15 -10 L 15 5 L 0 10 Z" fill="white" stroke="#333" stroke-width="1"/>
                    
                    <!-- Flag attachment to pole -->
                    <circle cx="0" cy="-15" r="2" fill="#333"/>
                </g>
                
                <!-- Clouds -->
                <ellipse cx="30" cy="40" rx="15" ry="8" fill="white" opacity="0.7"/>
                <ellipse cx="170" cy="50" rx="20" ry="10" fill="white" opacity="0.7"/>
            </svg>
            <p>Difficulty Level: {difficulty}/5</p>
        </div>
        <div class="info-grid">
            <div class="info-box">
                <h3>Project Information</h3>
                <p><strong>Complexity:</strong> {difficulty}/5</p>
                <p><strong>Time:</strong> {time_level}</p>
                <p><strong>Skill Level:</strong> {skill_level}</p>
            </div>
            <div class="info-box">
                <h3>Design Information</h3>
                <p><strong>Geometry:</strong> pipe</p>
                <p><strong>Author:</strong> {config.get('author', 'Unknown')}</p>
                <p><strong>Version:</strong> {config.get('version', '1.0')}</p>
            </div>
        </div>
        <p>{config.get('description', '')}</p>
    </div>
    
    <div class="section pattern">
        <h2>Pattern</h2>
        <div class="dimensions">
            <p><strong>Length:</strong> {pattern['total_material']['height_cm']} cm ({pattern['total_material']['height_m']} meters)</p>
            <p><strong>Width:</strong> {pattern['total_material']['width_cm']} cm</p>
            <p><strong>Circumference:</strong> {pattern['total_material']['circumference_cm']} cm</p>
            <p><strong>Material needed:</strong> {pattern['total_material']['area_m2']} m²</p>
        </div>
        
        <h3>Pieces:</h3>
        <ul class="pieces-list">
"""
    
    for piece in pattern['pieces']:
        if piece['name'] == 'A':
            html_content += f"""
            <li><strong>{piece['name']}</strong> - {piece['description']}: {piece['width_cm']} cm × {piece['height_cm']} cm</li>
"""
        else:
            html_content += f"""
            <li><strong>{piece['name']}</strong> - {piece['description']}: {piece['width_cm']} cm × {piece['height_cm']} cm</li>
"""
    
    html_content += """        </ul>
    </div>
    
    <div class="section instructions">
        <h2>Production Instructions</h2>
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

