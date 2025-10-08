import math
import os

def validate_parameters(parameters):
    """Validate input parameters"""
    errors = []
    
    # Validate diameter
    diameter = parameters.get('diameter', 50)
    if not isinstance(diameter, (int, float)) or diameter < 10 or diameter > 200:
        errors.append("Diameter must be between 10 and 200mm")
    
    # Validate length
    length = parameters.get('length', 10000)
    if not isinstance(length, (int, float)) or length < 100 or length > 50000:
        errors.append("Length must be between 100 and 50000mm")
    
    # Validate seam allowance
    seam_allowance = parameters.get('seam_allowance', 10)
    if not isinstance(seam_allowance, (int, float)) or seam_allowance < 5 or seam_allowance > 30:
        errors.append("Seam allowance must be between 5 and 30mm")
    
    return errors

def generate_tube_pattern(parameters):
    """
    Generate a 2D pattern for a tube based on parameters
    
    Args:
        parameters (dict): Dictionary of tube parameters
    
    Returns:
        dict: Pattern information including dimensions and pieces
    """
    # Validate parameters first
    errors = validate_parameters(parameters)
    if errors:
        raise ValueError(f"Invalid parameters: {', '.join(errors)}")
    
    # Ensure parameters is a dictionary
    if parameters is None:
        parameters = {}
    
    diameter = parameters.get('diameter', 50)
    length = parameters.get('length', 10000)
    seam_allowance = parameters.get('seam_allowance', 10)
    
    # Calculate dimensions
    circumference = math.pi * diameter
    pattern_width = circumference + (2 * seam_allowance)
    pattern_height = length + (2 * seam_allowance)
    
    # Convert to user-friendly units
    material_area_cm2 = (pattern_width * pattern_height) / 100
    material_area_m2 = material_area_cm2 / 10000
    
    # Create pattern pieces with better naming
    pieces = []
    
    # Main tube piece (A)
    main_piece = {
        'name': 'A',
        'description': 'Main tube body',
        'shape': 'rectangle',
        'width_mm': round(pattern_width, 1),
        'height_mm': round(pattern_height, 1),
        'width_cm': round(pattern_width / 10, 1),
        'height_cm': round(pattern_height / 10, 1),
        'width_m': round(pattern_width / 1000, 2),
        'height_m': round(pattern_height / 1000, 2),
        'seam_allowance': seam_allowance
    }
    pieces.append(main_piece)
    
    # Add reinforcement pieces with better naming
    attachment_points = parameters.get('attachment_points', [])
    for i, point in enumerate(attachment_points):
        position_str = point.get('position', 0)
        reinforcement_type = point.get('type', 'carabiner')
        
        # Convert position string to float (remove '%' if present)
        if isinstance(position_str, str) and position_str.endswith('%'):
            position = float(position_str.rstrip('%')) / 100.0
        else:
            position = float(position_str)
        
        # Calculate position on the pattern
        y_position = (position * pattern_height) - (seam_allowance/2)
        
        # Create reinforcement piece with letter designation
        letter = chr(66 + i)  # B, C, D, etc.
        if reinforcement_type == 'carabiner':
            reinforcement = {
                'name': letter,
                'description': f'Reinforcement ({position*100}%)',
                'shape': 'rectangle',
                'width_mm': round(diameter + (2 * seam_allowance), 1),
                'height_mm': round(seam_allowance * 2, 1),
                'width_cm': round((diameter + (2 * seam_allowance)) / 10, 1),
                'height_cm': round((seam_allowance * 2) / 10, 1),
                'position': {'x': 0, 'y': round(y_position, 1)},
                'position_percent': position * 100
            }
            pieces.append(reinforcement)
    
    return {
        'pieces': pieces,
        'total_material': {
            'width_mm': round(pattern_width, 1),
            'height_mm': round(pattern_height, 1),
            'width_cm': round(pattern_width / 10, 1),
            'height_cm': round(pattern_height / 10, 1),
            'width_m': round(pattern_width / 1000, 2),
            'height_m': round(pattern_height / 1000, 2),
            'area_cm2': round(material_area_cm2, 1),
            'area_m2': round(material_area_m2, 4),
            'area_m': round(material_area_m2, 2),
            'circumference_mm': round(circumference, 1),
            'circumference_cm': round(circumference / 10, 1)
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
    # Ensure parameters is a dictionary
    if parameters is None:
        parameters = {}
    
    diameter = parameters.get('diameter', 50)
    length = parameters.get('length', 10000)
    material = parameters.get('material', 'ripstop')
    color = parameters.get('color', 'single')
    attachment_points = parameters.get('attachment_points', [])
    seam_allowance = parameters.get('seam_allowance', 10)
    
    # Convert measurements to more user-friendly units
    length_cm = length / 10
    diameter_cm = diameter / 10
    seam_allowance_cm = seam_allowance / 10
    
    instructions = f"""# Tube Tail Instructions

## Materials Needed
- {material} fabric ({length_cm}cm x {math.pi * diameter_cm + 2}cm)
- Thread matching fabric color
- 2 carabiners
- Seam allowance: {seam_allowance}mm ({seam_allowance_cm}cm)

## Cutting Instructions
1. Cut a rectangle of {material} fabric {length_cm}cm long and {math.pi * diameter_cm + 2}cm wide
2. Add {seam_allowance_cm}cm seam allowance to all edges

## Pattern Dimensions
- Tube circumference: {math.pi * diameter:.1f}cm
- Pattern width: {math.pi * diameter_cm + 2:.1f}cm
- Pattern height: {length_cm + 2 * seam_allowance_cm:.1f}cm

## Sewing Instructions
"""
    
    if color == 'multicolor':
        instructions += """
1. If using multiple colors, create color segments before sewing
2. Sew color segments together along length
"""
    
    instructions += f"""
3. Sew the long edges together with right sides facing
4. Leave a small opening (about 5cm) for turning
5. Trim seams to {seam_allowance_cm}cm and clip curves
6. Turn right side out through opening
7. Press seams flat
8. Topstitch close to edge to reinforce

## Attachment Points
"""
    
    for i, point in enumerate(attachment_points):
        position_str = point.get('position', 0)
        # Convert position string to float (remove '%' if present)
        if isinstance(position_str, str) and position_str.endswith('%'):
            position = float(position_str.rstrip('%')) / 100.0
        else:
            position = float(position_str)
        
        instructions += f"""
{i+1}. At {position*100}% of the length ({position * length_cm:.1f}cm from top):
    - Fold fabric to create a reinforcement patch
    - Sew double layers at this point for strength
    - Attach carabiner through the reinforced section
"""
    
    instructions += f"""
## Finishing
1. Press the entire tube
2. Check that carabiners move freely
3. Test fly with a kite in light winds

## Flying Tips
- The tube should hang vertically from the kite line
- For stronger winds, consider using lighter fabric or reducing the length
- The length can be adjusted based on your preference and wind conditions
- Multiple tubes can be attached to the same line for more visual impact
- Attach the tube to the kite line using the carabiners at the marked positions
- Tube tails create a flowing, ribbon-like effect that adds color and movement to your kite
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

