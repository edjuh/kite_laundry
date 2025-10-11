# -*- coding: utf-8 -*-
import os

import yaml


def load_color_palette():
    colors_path = os.path.join(os.path.dirname(__file__), "colors.yaml")

    try:
        with open(colors_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            return data.get("palette", {})
    except FileNotFoundError:
        print(f"Warning: colors.yaml not found at {colors_path}")
        return {}
    except Exception as e:
        print(f"Error loading colors.yaml: {e}")
        return {}


def get_color_name(color_code):
    palette = load_color_palette()
    color_info = palette.get(color_code, {})
    return color_info.get("name", color_code)


def get_color_hex(color_code):
    palette = load_color_palette()
    color_info = palette.get(color_code, {})
    return color_info.get("hex", "#CCCCCC")


__all__ = ["load_color_palette", "get_color_name", "get_color_hex"]
