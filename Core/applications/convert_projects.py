#!/usr/bin/env python3
"""
utils/convert_projects.py
Batch-convert all YAMLs in ./projects to the new normalized schema.
Creates converted copies with '_converted' suffix.
"""

import argparse
import shutil
from pathlib import Path
import yaml
import sys
import logging
from datetime import datetime
from typing import Dict, Any  # Add this import

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def normalize_project_dict(project_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize project dictionary to new schema"""
    normalized = project_dict.copy()
    
    # Convert geometry_fn to geometry_type
    if 'geometry_fn' in normalized and 'geometry_type' not in normalized:
        normalized['geometry_type'] = normalized.pop('geometry_fn')
        logger.info("  → Converted geometry_fn to geometry_type")
    
    # Convert dimensions to parameters
    if 'dimensions' in normalized and 'parameters' not in normalized:
        normalized['parameters'] = normalized.pop('dimensions')
        logger.info("  → Converted dimensions to parameters")
    
    # Convert nested materials to flat format
    if 'materials' in normalized and isinstance(normalized['materials'], list):
        # Convert list format to dict format
        materials_dict = {}
        for item in normalized['materials']:
            if isinstance(item, dict) and 'item' in item:
                key = item['item'].lower().replace(' ', '_').replace('(', '').replace(')', '')
                materials_dict[key] = item.get('qty', 'Unknown')
        normalized['materials'] = materials_dict
        logger.info("  → Converted materials list to dictionary")
    
    return normalized

def convert_projects(dry_run=False):
    """Convert all project files and create converted copies"""
    projects_dir = Path(__file__).parent.parent / "projects"
    
    if not projects_dir.exists():
        logger.error(f"Projects directory not found: {projects_dir}")
        return False
    
    converted_count = 0
    skipped_count = 0
    
    for yaml_file in projects_dir.glob("*.yaml"):
        try:
            # Load YAML file
            with open(yaml_file, 'r') as f:
                project_dict = yaml.safe_load(f)
            
            # Check if conversion is needed
            needs_conversion = False
            if 'geometry_fn' in project_dict or 'dimensions' in project_dict:
                needs_conversion = True
            
            if not needs_conversion:
                logger.info(f"✅ Already normalized: {yaml_file.name}")
                skipped_count += 1
                continue
            
            # Create converted filename
            converted_name = f"{yaml_file.stem}_converted.yaml"
            converted_path = yaml_file.parent / converted_name
            
            # Normalize project
            normalized = normalize_project_dict(project_dict)
            
            # Write converted file
            if not dry_run:
                with open(converted_path, 'w') as f:
                    yaml.dump(normalized, f, default_flow_style=False, sort_keys=False)
                logger.info(f"✅ Converted: {yaml_file.name} → {converted_name}")
                converted_count += 1
            else:
                logger.info(f"🔍 Would convert: {yaml_file.name} → {converted_name}")
                converted_count += 1
                
        except Exception as e:
            logger.error(f"❌ Error processing {yaml_file.name}: {e}")
    
    logger.info(f"\n📊 Summary:")
    logger.info(f"   Converted: {converted_count} files")
    logger.info(f"   Skipped: {skipped_count} files")
    
    return converted_count > 0

def main():
    parser = argparse.ArgumentParser(description='Convert project YAML files to normalized schema')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be converted without actually converting')
    
    args = parser.parse_args()
    
    logger.info("🔄 Starting project conversion...")
    logger.info("This will create converted copies with '_converted' suffix")
    logger.info("Original files will remain unchanged.\n")
    
    success = convert_projects(dry_run=args.dry_run)
    
    if success:
        logger.info("\n✅ Conversion completed successfully!")
        logger.info("📝 Review the converted files, then manually replace originals if needed.")
    else:
        logger.info("\nℹ️  No files needed conversion")

if __name__ == "__main__":
    main()

