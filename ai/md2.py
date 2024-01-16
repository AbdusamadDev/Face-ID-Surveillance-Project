# module_b.py

from .md1 import original_variable

# Modify the imported variable
original_variable.append(4)

# Print the modified variable
print(original_variable)
