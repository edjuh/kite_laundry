rod_types = ['none', 'carbon', 'fiberglass', 'bamboo']

design_principles = {
    'tail': {
        'description': 'Simple pipe tail for stability. Recommended length-to-width ratio: 10:1. Icarex ripstop material.',
        'dimensions': ['length', 'width'],
        'suggested_ratio': 10,
        'ratio_field': ('length', 'width'),
        'ratio_desc': 'length to width',
        'has_gore': False,
        'has_outlet': False
    },
    'drogue': {
        'description': 'Cone-shaped drogue for drag (tapered like bucket). Length ~3 times entry diameter, outlet ~1/4 entry, 6 gores default. Icarex ripstop material.',
        'dimensions': ['length', 'entry_diameter', 'outlet_diameter'],
        'suggested_ratio': 3,
        'ratio_field': ('length', 'entry_diameter'),
        'ratio_desc': 'length to entry diameter',
        'has_gore': True,
        'has_outlet': True
    },
    'graded_tail': {
        'description': 'Graded tapering tail (diagonal grading for color shift). Cut 12"x41" rectangles, diagonal taper to 4" strips, 6-10 gores/sections. Icarex ripstop, no rod.',
        'dimensions': ['length', 'width'],
        'suggested_ratio': 10,
        'ratio_field': ('length', 'width'),
        'ratio_desc': 'length to width',
        'has_gore': True,
        'has_outlet': False
    },
    'spinner': {
        'description': 'Helix Spinner (tapering cone with hoop). Length ~4 times entry diameter, 8 gores for taper, carbon hoop for spin. Icarex ripstop material.',
        'dimensions': ['length', 'entry_diameter'],
        'suggested_ratio': 4,
        'ratio_field': ('length', 'entry_diameter'),
        'ratio_desc': 'length to entry diameter',
        'has_gore': True,
        'has_outlet': False,
        'default_values': {'length': 1000, 'entry_diameter': 40, 'gore': 8}
    }
}
