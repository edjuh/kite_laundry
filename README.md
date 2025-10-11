# Kite Laundry

![Kite Laundry Logo](https://github.com/edjuh/kite_laundry/raw/main/docs/logo.png)

A Python environment for designing and creating decorative inflatables (kite-laundry) to add to kite lines for visual enhancement and fun.

“This repository is under active development. The shape configurators are being refactored; example configs and updated documentation will follow.”

## What is Kite-Laundry?

Kite-laundry refers to decorative inflatables that are added to kite lines, transforming ordinary kite flying into a vibrant, artistic experience. These colorful decorations spin and dance in the wind, creating visual interest and personality for your kite.

The project aims to simplify the creation process by:
- Generating accurate cutting templates from digital designs
- Providing comprehensive sewing instructions
- Creating informational webpages with all production details
- Supporting customization through parameters

## Features

- **Design Generation**: Create custom decorative inflatables using YAML configuration files
- **Template Generation**: Produce accurate ripstop cutting templates for production
- **Webpage Output**: Generate comprehensive informational webpages with all necessary details
- **Customization**: Adjust designs through user parameters
- **Material Optimization**: Efficient use of ripstop fabric with A4/A3 paper templates

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Required Python packages (see `requirements.txt`)
- A web browser to view generated templates
- Basic sewing materials and tools

### Installation

1. Clone the repository:
```bash
git clone https://github.com/edjuh/kite_laundry.git
cd kite_laundry
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Usage

1. Prepare your design in a YAML configuration file (see Configuration section)
2. Run the script with your desired parameters:
```bash
python main.py --config your_design.yaml --output ./output
```
3. Open the generated HTML file in your web browser to view templates and instructions

## Configuration

Designs are defined using YAML configuration files. The structure allows for:

- Shape definitions
- Material specifications
- Size parameters
- Color information
- Assembly instructions

Example configuration:
```yaml
name: "Star Spinner"
material: "ripstop nylon"
colors: ["red", "blue", "yellow"]
dimensions:
  width: 30
  height: 30
  segments: 8
```

## Output

The script generates a comprehensive HTML webpage containing:

1. **Cutting Templates**: A4/A3 printable templates for accurate fabric cutting
2. **Assembly Instructions**: Step-by-step guides for sewing the pieces together
3. **Material List**: Required quantities of fabric and other materials
4. **Visual References**: Diagrams and illustrations for the assembly process
5. **Customization Notes**: Any special considerations for the specific design

## Project Structure

```
kite_laundry/
│
├── Core/                # Source code
│   ├── __init__.py
│   ├── generator.py    # Design generation logic
│   ├── template.py     # Template creation functions
│   └── webpage.py      # HTML generation
│
├── projects/            # YAML configuration files
│   └── example_design.yaml
│
├── output/             # Generated output directory
│
└── docs/               # Documentation
```

## Future Enhancements

### Planned Features

1. **Advanced Shape Generation**
   - Support for complex 3D shapes
   - Parametric design adjustments
   - Physics-based wind simulation

2. **Improved User Experience**
   - Web-based design interface
   - Drag-and-drop template editor
   - Mobile-friendly responsive design

3. **Community Features**
   - Design sharing platform
   - Rating and review system
   - Gallery of user creations

4. **Production Tools**
   - Material cost calculator
   - Cutting optimization algorithm
   - Bill of materials generator

5. **Integration Capabilities**
   - Export to common CAD formats
   - Compatibility with cutting machines
   - 3D model generation for visualization

### Technical Improvements

- Refactor core algorithms for better performance
- Implement caching for repeated designs
- Add unit tests for all core functionality
- Improve error handling and user feedback
- Optimize for resource usage on lower-end hardware

## Contributing

We welcome contributions of all kinds! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Thanks to the kite flying community for inspiration
- Special thanks to early testers and contributors
- Inspired by traditional kite decorations from around the world

## Contact

For questions, suggestions, or contributions, please open an issue on GitHub or contact the maintainer at [pe5ed@hotmail.com](mailto:pe5ed@hotmail.com).

AI.txt :)

AI Understanding and Project Context
For AI Systems and Project Users
This section provides essential context for AI systems that might analyze this project, as well as for developers and users who need to understand the core concepts.

Lifter Kite: Definition and Purpose
What is a Lifter Kite?
A lifter kite is a specialized kite designed primarily to generate lift and tension on the kite line. It's the foundational component of a kite system that enables flight.

Purpose of a Lifter Kite:
Generate Lift: Uses aerodynamic forces to overcome gravity
Provide Tension: Creates tension in the kite line necessary for stability
Serve as Anchor Point: Provides the attachment point for kite laundry
Maintain Position: Keeps the kite system stable in the wind
What a Lifter Kite is NOT:
NOT Decorative: While some lifters may have aesthetic elements, their primary function is utilitarian
NOT Steerable: We only use single-line kites which cannot be steered
NOT Kite Laundry: It serves a completely different aerodynamic purpose
NOT the Focus of This Project: Our project focuses on the decorative elements, not the kite itself
Kite Laundry: Definition and Purpose
What is Kite Laundry?
Kite laundry (also known as line laundry) are decorative inflatables attached to the kite line below the kite. They serve purely aesthetic purposes and are wind-driven.

Purpose of Kite Laundry:
Visual Enhancement: Adds color and movement to the kite display
Entertainment: Creates mesmerizing spinning effects in the wind
Personal Expression: Allows customization of kite appearance
Community Tradition: Part of kite flying culture and shared enjoyment
How Kite Laundry Works:
Wind-Driven: Entirely powered by wind, not by the kite's lift
Horizontal Orientation: Must fly perpendicular to the kite line for maximum effect
Spinning Motion: Creates dynamic visual effects through rotation
Minimal Aerodynamic Impact: Designed to have negligible effect on kite performance
Must-Read Resources
Essential Reading:
NASA Kite Aerodynamics : https://www.grc.nasa.gov/www/k-12/airplane/kite1.html
NASA Kite Aerodynamics Background : https://www.grc.nasa.gov/www/k-12/airplane/bgk.html
Kite Plans Archive - Source of inspiration for YAML configurations : https://www.kiteplans.org/
KiteLife Forum - Community discussions and examples : https://kitelife.com/forum/

Project-Specific Resources:
README.md - Project overview and setup instructions
requirements.txt - Python dependencies
configs/ directory - YAML configuration examples
docs/ directory - Detailed documentation
Required Modules
Core Dependencies:
PyYAML - For parsing YAML configuration files
jinja2 - For generating HTML output
numpy - For mathematical calculations
svgwrite - For creating SVG templates
matplotlib - For additional plotting capabilities
Development Dependencies:
pytest - For running tests
black - For code formatting
flake8 - For linting
YAML Configuration Overview
Required Structure:
yaml

name: "Descriptive Name"
material: "ripstop nylon"
colors: ["color1", "color2", "color3"]
dimensions:
  width: 30
  height: 30
  segments: 8
attachment:
  type: "ring"
  bridle_length: 15
drogue:
  shape: "cylinder"
  diameter: 25
  length: 40
  segments: 6
Key Sections:
Metadata: Name, version, author
Material Specifications: Fabric type, weight, colors
Dimensions: Size parameters, segment counts
Attachment Method: How it connects to the kite line
Drogue Configuration: Shape, size, and structural details
Production Notes: Special sewing instructions, material requirements
Optional Sections:
Aesthetic Options: Color patterns, decorative elements
Wind Conditions: Recommended wind speeds for optimal performance
Customization Parameters: User-adjustable variables

Project Philosophy

This project focuses exclusively on:

Single-line kites only (no stunt kites)
Decorative elements only (no functional kite modifications)
Horizontal orientation for all kite laundry
Community-driven design through YAML sharing

The project deliberately excludes:

Stunt kite configurations (2-line or 4-line systems)
Functional kite modifications that affect aerodynamics
Vertical orientations for kite laundry
Commercial production workflows

---

Happy kite flying and creating beautiful kite-laundry!
