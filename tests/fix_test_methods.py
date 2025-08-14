#!/usr/bin/env python3
"""
Fix all test methods to use test_client fixture
"""
import re

# Read the file
with open("tests/test_api.py", "r") as f:
    content = f.read()

# Pattern to find test methods without test_client parameter
pattern = r'(\s+def test_\w+)\(self\):'
replacement = r'\1(self, test_client):'

# Replace all occurrences
fixed_content = re.sub(pattern, replacement, content)

# Add "client = test_client" after each test method that doesn't have it
lines = fixed_content.split('\n')
new_lines = []
for i, line in enumerate(lines):
    new_lines.append(line)
    # If this is a test method definition
    if re.match(r'\s+def test_\w+\(self, test_client\):', line):
        # Check if next non-empty line already has client = test_client
        j = i + 1
        while j < len(lines) and (not lines[j].strip() or lines[j].strip().startswith('"""')):
            j += 1
        if j < len(lines) and not lines[j].strip().startswith('client = test_client'):
            # Find the right indentation
            indent = len(line) - len(line.lstrip()) + 4
            # Add after docstring if present
            if j < len(lines) and '"""' in lines[i+1]:
                # Find end of docstring
                k = i + 2
                while k < len(lines) and '"""' not in lines[k]:
                    k += 1
                if k < len(lines):
                    new_lines.extend(lines[i+1:k+1])
                    new_lines.append(' ' * indent + 'client = test_client')
                    i = k
                    continue

fixed_content = '\n'.join(new_lines)

# Write back
with open("tests/test_api.py", "w") as f:
    f.write(fixed_content)

print("Fixed test_api.py")