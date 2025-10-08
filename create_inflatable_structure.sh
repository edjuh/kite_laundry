#!/bin/bash

# Create line laundry project structure
mkdir -p projects/line_laundry/tube
mkdir -p projects/line_laundry/windsock
mkdir -p projects/line_laundry/animal/clownfish

# Create one-line kite project structure (for future expansion)
mkdir -p projects/one_line_kites
mkdir -p projects/one_line_kites/delta
mkdir -p projects/one_line_kites/box_kite

# Create core application file
touch Core/applications/generate_line_laundry.py

# Create line laundry YAML files
touch projects/line_laundry/tube/tube.yaml
touch projects/line_laundry/tube/rotating_tube.yaml
touch projects/line_laundry/windsock/windsock.yaml
touch projects/line_laundry/animal/clownfish/clownfish.yaml

# Create placeholder for kite building (future)
touch projects/one_line_kites/README.md

echo "Clean directory structure created:"
echo ""
echo "Line Laundry Projects:"
echo "  projects/line_laundry/tube/"
echo "    - tube.yaml"
echo "    - rotating_tube.yaml"
echo "  projects/line_laundry/windsock/"
echo "    - windsock.yaml"
echo "  projects/line_laundry/animal/clownfish/"
echo "    - clownfish.yaml"
echo ""
echo "One-Line Kites (future expansion):"
echo "  projects/one_line_kites/"
echo "    - delta/"
echo "    - box_kite/"
echo "    - README.md"

