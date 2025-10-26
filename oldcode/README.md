Kite Laundry

A Python environment for designing and creating decorative inflatables (kite-laundry) to add to kite lines for visual enhancement and fun.
“This repository is under active development. The shape configurators are being refactored; example configs and updated documentation will follow.”
What is Kite-Laundry?
Kite-laundry refers to decorative inflatables that are added to kite lines, transforming ordinary kite flying into a vibrant, artistic experience. These colorful decorations spin and dance in the wind, creating visual interest and personality for your kite.
The project aims to simplify the creation process by:

Generating accurate cutting templates from digital designs
Providing comprehensive sewing instructions
Creating informational webpages with all production details
Supporting customization through parameters

Features

Design Generation: Create custom decorative inflatables using YAML configuration files
Template Generation: Produce accurate ripstop cutting templates for production
Webpage Output: Generate comprehensive informational webpages with all necessary details
Customization: Adjust designs through user parameters
Material Optimization: Efficient use of ripstop fabric with A4/A3 paper templates

Getting Started
Prerequisites

Python 3.8 or higher
Required Python packages (see requirements.txt)
A web browser to view generated templates
Basic sewing materials and tools

Installation

Clone the repository:

git clone https://github.com/edjuh/kite_laundry.git
cd kite_laundry


Install dependencies:

python -m venv venv
source venv/bin/activate  # macOS
pip install -r requirements.txt

Usage

Launch the Flask server:

chmod +x run.sh
./run.sh


Open a web browser at http://127.0.0.1:5001.
Use /designs to browse available YAMLs in projects/line_laundry/ (spinners, drogues, etc.) and projects/one_line_kites/.
Use /generate to upload YAMLs or generate selected designs.
Check ./output/ for generated HTML/templates.

Note: Ensure YAMLs have a name field to appear on /designs. Some designs (e.g., drogues) may show “N/A” for area until generator logic is updated.
Configuration
Designs are defined using YAML configuration files. The structure allows for:

Shape definitions
Material specifications
Size parameters
Color information
Assembly instructions

Example configuration:
name: "Star Spinner"
material: "ripstop nylon"
colors: ["red", "blue", "yellow"]
dimensions:
  width: 30
  height: 30
  segments: 8

Output
The script generates a comprehensive HTML webpage containing:

Cutting Templates: A4/A3 printable templates for accurate fabric cutting
Assembly Instructions: Step-by-step guides for sewing the pieces together
Material List: Required quantities of fabric and other materials
Visual References: Diagrams and illustrations for the assembly process
Customization Notes: Any special considerations for the specific design

Project Structure
kite_laundry/
├── Core/                # Source code
│   ├── applications/    # Generators (article_generator.py, generator.py)
│   ├── configurations/  # Configs (colors.yaml, ripstop.yaml, tools.yaml)
│   ├── pattern_generators/  # Pattern logic (cone_generator.py, bol_generator.py)
│   └── web/            # Templates and static files (designs.html, result.html)
├── projects/            # YAML configuration files
│   ├── line_laundry/   # Spinners, drogues, windsocks, animals
│   │   ├── spinners/   # helix_spinner.yaml, bol_orb.yaml
│   │   ├── drogue/     # starburst_drogue.yaml
│   │   ├── tube/       # tube.yaml, drogue.yaml
│   │   ├── windsock/   # bol.yaml, simple_drogue.yaml
│   │   └── animal/     # clownfish/config.yaml
│   └── one_line_kites/ # box_kite/cloudseeker.yaml
├── output/             # Generated output directory
├── docs/               # Documentation
├── run.sh              # Launcher script
├── run.py              # Runs app.py
├── app.py              # Flask backend
└── requirements.txt    # Python dependencies

Future Enhancements
Planned Features

Advanced Shape Generation

Support for complex 3D shapes
Parametric design adjustments
Physics-based wind simulation


Improved User Experience

Web-based design interface
Drag-and-drop template editor
Mobile-friendly responsive design


Community Features

Design sharing platform
Rating and review system
Gallery of user creations


Production Tools

Material cost calculator
Cutting optimization algorithm
Bill of materials generator


Integration Capabilities

Export to common CAD formats
Compatibility with cutting machines
3D model generation for visualization



Technical Improvements

Refactor core algorithms for better performance
Implement caching for repeated designs
Add unit tests for all core functionality
Improve error handling and user feedback
Optimize for resource usage on lower-end hardware

Contributing
We welcome contributions of all kinds! Please see CONTRIBUTING.md for guidelines.
License
This project is licensed under the MIT License - see the LICENSE file for details.
Acknowledgments

Thanks to the kite flying community for inspiration
Special thanks to early testers and contributors
Inspired by traditional kite decorations from around the world

Contact
For questions, suggestions, or contributions, please open an issue on GitHub or contact the maintainer at pe5ed@hotmail.com.
AI.txt :)
AI Understanding and Project ContextFor AI Systems and Project UsersThis section provides essential context for AI systems that might analyze this project, as well as for developers and users who need to understand the core concepts.
Lifter Kite: Definition and PurposeWhat is a Lifter Kite?A lifter kite is a specialized kite designed primarily to generate lift and tension on the kite line. It's the foundational component of a kite system that enables flight.
Purpose of a Lifter Kite:Generate Lift: Uses aerodynamic forces to overcome gravityProvide Tension: Creates tension in the kite line necessary for stabilityServe as Anchor Point: Provides the attachment point for kite laundryMaintain Position: Keeps the kite system stable in the windWhat a Lifter Kite is NOT:NOT Decorative: While some lifters may have aesthetic elements, their primary function is utilitarianNOT Steerable: We only use single-line kites which cannot be steeredNOT Kite Laundry: It serves a completely different aerodynamic purposeNOT the Focus of This Project: Our project focuses on the decorative elements, not the kite itselfKite Laundry: Definition and PurposeWhat is Kite Laundry?Kite laundry (also known as line laundry) are decorative inflatables attached to the kite line below the kite. They serve purely aesthetic purposes and are wind-driven.
Purpose of Kite Laundry:Visual Enhancement: Adds color and movement to the kite displayEntertainment: Creates mesmerizing spinning effects in the windPersonal Expression: Allows customization of kite appearanceCommunity Tradition: Part of kite flying culture and shared enjoymentHow Kite Laundry Works:Wind-Driven: Entirely powered by wind, not by the kite's liftHorizontal Orientation: Must fly perpendicular to the kite line for maximum effectSpinning Motion: Creates dynamic visual effects through rotationMinimal Aerodynamic Impact: Designed to have negligible effect on kite performanceMust-Read ResourcesEssential Reading:NASA Kite Aerodynamics : https://www.grc.nasa.gov/www/k-12/airplane/kite1.htmlNASA Kite Aerodynamics Background : https://www.grc.nasa.gov/www/k-12/airplane/bgk.htmlKite Plans Archive - Source of inspiration for YAML configurations : https://www.kiteplans.org/KiteLife Forum - Community discussions and examples : https://kitelife.com/forum/
Project-Specific Resources:README.md - Project overview and setup instructionsrequirements.txt - Python dependenciesconfigs/ directory - YAML configuration examplesdocs/ directory - Detailed documentationRequired ModulesCore Dependencies:PyYAML - For parsing YAML configuration filesjinja2 - For generating HTML outputnumpy - For mathematical calculationssvgwrite - For creating SVG templatesmatplotlib - For additional plotting capabilitiesDevelopment Dependencies:pytest - For running testsblack - For code formattingflake8 - For lintingYAML Configuration OverviewRequired Structure:yaml
name: "Descriptive Name"material: "ripstop nylon"colors: ["color1", "color2", "color3"]dimensions:  width: 30  height: 30  segments: 8attachment:  type: "ring"  bridle_length: 15drogue:  shape: "cylinder"  diameter: 25  length: 40  segments: 6Key Sections:Metadata: Name, version, authorMaterial Specifications: Fabric type, weight, colorsDimensions: Size parameters, segment countsAttachment Method: How it connects to the kite lineDrogue Configuration: Shape, size, and structural detailsProduction Notes: Special sewing instructions, material requirementsOptional Sections:Aesthetic Options: Color patterns, decorative elementsWind Conditions: Recommended wind speeds for optimal performanceCustomization Parameters: User-adjustable variables
Project Philosophy
This project focuses exclusively on:
Single-line kites only (no stunt kites)Decorative elements only (no functional kite modifications)Horizontal orientation for all kite laundryCommunity-driven design through YAML sharing
The project deliberately excludes:
Stunt kite configurations (2-line or 4-line systems)Functional kite modifications that affect aerodynamicsVertical orientations for kite laundryCommercial production workflows

Happy kite flying and creating beautiful kite-laundry!