import math
import os

def generate_tube_pattern(parameters):
    """
    Generate a 2D pattern for a tube based on parameters
    
    Args:
        parameters (dict): Dictionary of tube parameters
    
    Returns:
        dict: Pattern information including dimensions and pieces
    """
    diameter = parameters.get('diameter', 50)
    length = parameters.get('length', 10000)
    seam_allowance = parameters.get('seam_allowance', 10)
    
    # Calculate dimensions
    circumference = math.pi * diameter
    pattern_width = circumference + (2 * seam_allowance)
    pattern_height = length + (2 * seam_allowance)
    
    # Create pattern pieces
    pieces = []
    
    # Main tube piece
    main_piece = {
        'name': 'tube_body',
        'shape': 'rectangle',
        'width': pattern_width,
        'height': pattern_height,
        'seam_allowance': seam_allowance,
        'description': 'Main tube body'
    }
    pieces.append(main_piece)
    
    # Add reinforcement pieces at attachment points
    attachment_points = parameters.get('attachment_points', [])
    for i, point in enumerate(attachment_points):
        position = point.get('position', 0)
        reinforcement_type = point.get('type', 'carabiner')
        
        # Calculate position on the pattern
        y_position = (position * pattern_height) - (seam_allowance/2)
        
        # Create reinforcement piece
        if reinforcement_type == 'carabiner':
            # Carabiner reinforcement - a small rectangle
            reinforcement = {
                'name': f'carabiner_reinforcement_{i}',
                'shape': 'rectangle',
                'width': diameter + (2 * seam_allowance),
                'height': seam_allowance * 2,
                'position': {'x': 0, 'y': y_position},
                'description': f'Carabiner reinforcement at {position*100}%'
            }
            pieces.append(reinforcement)
    
    return {
        'pieces': pieces,
        'total_material': {
            'width': pattern_width,
            'height': pattern_height,
            'area': pattern_width * pattern_height
        }
    }

def generate_tube_instructions(parameters):
    """
    Generate sewing instructions for a tube
    
    Args:
        parameters (dict): Dictionary of tube parameters
    
    Returns:
        str: Markdown formatted instructions
    """
    diameter = parameters.get('diameter', 50)
    length = parameters.get('length', 10000)
    material = parameters.get('material', 'ripstop')
    color = parameters.get('color', 'single')
    attachment_points = parameters.get('attachment_points', [])
    
    instructions = f"""# Tube Tail Instructions

## Materials Needed
- {material} fabric ({length}mm x {math.pi * diameter + 20}mm)
- Thread matching fabric color
- 2 carabiners
- Seam allowance: {parameters.get('seam_allowance', 10)}mm

## Cutting Instructions
1. Cut a rectangle of {material} fabric {length}mm long and {math.pi * diameter + 20}mm wide
2. Add {parameters.get('seam_allowance', 10)}mm seam allowance to all edges

## Sewing Instructions
"""
    
    if color == 'multicolor':
        instructions += """
1. If using multiple colors, create color segments before sewing
2. Sew color segments together along length
"""
    
    instructions += f"""
3. Sew the long edges together with right sides facing
4. Leave a small opening (about 50mm) for turning
5. Trim seams to {parameters.get('seam_allowance', 10)}mm and clip curves
6. Turn right side out through opening
7. Press seams flat
8. Topstitch close to edge to reinforce

## Attachment Points
"""
    
    for i, point in enumerate(attachment_points):
        position = point.get('position', 0)
        instructions += f"""
{i+1}. At {position*100}% of the length:
    - Fold fabric to create a reinforcement patch
    - Sew double layers at this point for strength
    - Attach carabiner through the reinforced section
"""
    
    instructions += f"""
## Finishing
1. Press the entire tube
2. Check that carabiners move freely
3. Test fly with a kite in light winds

## Tips
- The tube should be light enough to fly in light winds
- For stronger winds, consider using lighter fabric
- The length can be adjusted based on your preference
- Multiple tubes can be attached to the same line for more visual impact
"""
    
    return instructions

def perform_web_search(search_terms):
    """
    Simulate web search functionality (in real implementation, would use search API)
    
    Args:
        search_terms (list): List of search terms
    
    Returns:
        list: List of search results
    """
    # This is a simulation - in a real implementation, you'd use a search API
    simulated_results = {
        "kite tube tail": [
            {"title": "Tube Tail Design Guide", "url": "https://example.com/tube-guide", "description": "Comprehensive guide to making tube tails"},
            {"title": "Kite Line Laundry", "url": "https://example.com/line-laundry", "description": "Various types of kite decorations"}
        ],
        "line laundry tube": [
            {"title": "Line Laundry Techniques", "url": "https://example.com/line-laundry-techniques", "description": "Advanced techniques for line laundry"},
            {"title": "Tube Tail Patterns", "url": "https://example.com/tube-patterns", "description": "Free patterns for tube tails"}
        ]
    }
    
    results = []
    for term in search_terms:
        if term in simulated_results:
            results.extend(simulated_results[term])
    
    return results
