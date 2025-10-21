
# Around line 107-108, change 'parameters' to 'config'
# Before:
pattern = generate_tube_pattern(parameters)
instructions = generate_tube_instructions(parameters, pattern)

# After:
pattern = generate_tube_pattern(config)
instructions = generate_tube_instructions(config, pattern)
