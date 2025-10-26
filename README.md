# Kite Laundry Design Generator

## Overview
A web-based tool to assist kite enthusiasts in creating custom kite laundry designs (e.g., tails, drogues, windsocks, streamers). Simplifies configuration, generates design files, and stores designs. Educates on design principles and supports personal project tracking.

## Intended Purpose
- For kite builders and hobbyists to design laundry components efficiently.
- Educational use for design basics (e.g., aerodynamics).
- Personal management for saving and revisiting designs.
Audience: Beginners with basic computer skills—prioritize simplicity.

## Core Functionality
- Workflow: Start (select units: metric/imperial), Select (design type: tail, drogue, windsock, streamer), Configure (dimensions, colors, rod), Output (details, SVG preview), Designs (view saved).
- Storage: Local SQLite with fields (id, name, type, dimensions, colors, rod, creation_date).
- Generation: Basic SVG preview without actionable details.
- Validation: Positive dimensions, ratio suggestions.
- Logging: Terminal feedback for debugging.

## Installation
- Clone repo: git clone https://github.com/edjuh/kite_laundry.git
- Activate venv: source venv/bin/activate
- Install deps: pip install -r requirements.txt
- Run: python app.py
- Access: http://localhost:5000

## Usage Example
1. Start: Choose units.
2. Select: Pick design type.
3. Configure: Input dimensions (e.g., length, width), colors (up to 3), rod.
4. Output: View text description, SVG preview, download PDF/YAML.
5. Designs: List all saved designs.

## Future Additions
- Material cost calculations.
- PDF/DXF export.
- User authentication.
- Docker deployment.
- REST API.
- 3D modeling (Q1 2026).

## Caveats
- Technical: Single-user, local DB; optimize for scale later.
- Challenges: Accurate conversions, browser compatibility.
- Dependencies: Python 3.x, Flask, SQLite.
- Risks: Complex UI; input sanitization needed.

## References
- NASA Kite Aerodynamics: https://www.grc.nasa.gov/www/k-12/airplane/kite1.html
- NASA Background: https://www.grc.nasa.gov/www/k-12/airplane/bgk.html
- Kite Plans: https://www.kiteplans.org/
- KiteLife Forum: https://kitelife.com/forum/

## Trigger Mechanism
- **PARR Review**: Call "PARR Review" to reset AI focus. Grok 3 will reread thread, oversight_plan.txt, and replan.
- **Purpose**: Prevents derailment, ensures alignment.

## AI.txt (Original Guidance)
AI.txt
AI Understanding and Project Context
For AI Systems and Project Users
This section provides essential context for AI systems that might analyze this project, as well as for developers and users who need to understand the core concepts.

Lifter Kite: Definition and Purpose

* What is a Lifter Kite?
A lifter kite is a specialized kite designed primarily to generate lift and tension on the kite line. It's the foundational component of a kite system that enables flight.

* Purpose of a Lifter Kite
Generate Lift: Uses aerodynamic forces to overcome gravity
Provide Tension: Creates tension in the kite line necessary for stability
Serve as Anchor Point: Provides the attachment point for kite laundry
Maintain Position: Keeps the kite system stable in the wind

* What a Lifter Kite is NOT
NOT Decorative: While some lifters may have aesthetic elements, their primary function is utilitarian
NOT Steerable: We only use single-line kites which cannot be steered
NOT Kite Laundry: It serves a completely different aerodynamic purpose
NOT the Focus of This Project: Our project focuses on the decorative elements, not the kite itself

Kite Laundry: Definition and Purpose

* What is Kite Laundry?
Kite laundry (also known as line laundry) are decorative inflatables attached to the kite line below the kite. They serve purely aesthetic purposes and are wind-driven.

* Purpose of Kite Laundry
Visual Enhancement: Adds color and movement to the kite display
Entertainment: Creates mesmerizing spinning effects in the wind
Personal Expression: Allows customization of kite appearance
Community Tradition: Part of kite flying culture and shared enjoyment

* How Kite Laundry Works
Wind-Driven: Entirely powered by wind, not by the kite's lift
Horizontal Orientation: Must fly perpendicular to the kite line for maximum effect
Spinning Motion: Creates dynamic visual effects through rotation
Minimal Aerodynamic Impact: Designed to have negligible effect on kite performance

Must-Read Resources

* Essential Reading
NASA Kite Aerodynamics: https://www.grc.nasa.gov/www/k-12/airplane/kite1.html
NASA Kite Aerodynamics Background: https://www.grc.nasa.gov/www/k-12/airplane/bgk.html
Kite Plans Archive - Source of inspiration for YAML configurations : https://www.kiteplans.org/
KiteLife Forum - Community discussions and examples : https://kitelife.com/forum/

Project-Specific Resources

* README.md - Project overview and setup instructions
* requirements.txt - Python dependencies
* configs/ directory - YAML configuration examples
* docs/ directory - Detailed documentation

Required Modules

* Core Dependencies
PyYAML - For parsing YAML configuration files
jinja2 - For generating HTML output
numpy - For mathematical calculations
svgwrite - For creating SVG templates
matplotlib - For additional plotting capabilities

* Development Dependencies
pytest - For running tests
black - For code formatting
flake8 - For linting

YAML Configuration Overview

* Required Structure
yaml
name: "Descriptive Name"
material: "ripstop nylon"
colors: ["color1", "color2", "color3"]
dimensions: width: 30 height: 30 segments: 8
attachment: type: "ring" bridle_length: 15
drogue: shape: "cylinder" diameter: 25 length: 40 segments: 6

* Key Sections
Metadata: Name, version, author
Material Specifications: Fabric type, weight, colors
Dimensions: Size parameters, segment counts
Attachment Method: How it connects to the kite line
Drogue Configuration: Shape, size, and structural details
Production Notes: Special sewing instructions, material requirements

* Optional Sections
Aesthetic Options: Color patterns, decorative elements
Wind Conditions: Recommended wind speeds for optimal performance
Customization Parameters: User-adjustable variables

## Development
- **Requirements**: See `requirements.txt`.
- **Config**: `config.py` for settings.
- **Oversight**: Managed via `oversight_plan.txt`.

## Next Steps
- Follow `oversight_plan.txt` for module build-up.
