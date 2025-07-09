#!/usr/bin/env python3
"""
Script to automatically fix telegram package imports by analyzing what telegram.ext needs
"""

import os
import re
import glob

def find_all_telegram_classes():
    """Find all available telegram classes"""
    telegram_dir = ".pythonlibs/lib/python3.11/site-packages/telegram"
    classes = []
    
    # Find all Python files in telegram directory
    for py_file in glob.glob(f"{telegram_dir}/**/*.py", recursive=True):
        if "__pycache__" in py_file:
            continue
            
        try:
            with open(py_file, 'r') as f:
                content = f.read()
                
            # Find class definitions
            class_matches = re.findall(r'^class\s+([A-Z][A-Za-z0-9_]*)', content, re.MULTILINE)
            
            for class_name in class_matches:
                # Determine module path
                rel_path = os.path.relpath(py_file, telegram_dir)
                module_path = rel_path.replace('/', '.').replace('.py', '')
                if module_path.startswith('.'):
                    module_path = module_path[1:]
                
                classes.append((module_path, class_name))
                
        except Exception:
            continue
    
    return classes

def create_comprehensive_init():
    """Create a comprehensive __init__.py with all available classes"""
    classes = find_all_telegram_classes()
    
    init_content = '''#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Auto-generated comprehensive init file
#

"""Python Telegram Bot Library"""

# Import all available classes
__all__ = []

'''
    
    for module_path, class_name in classes:
        try:
            init_content += f'''# Import {class_name} from {module_path}
try:
    from .{module_path} import {class_name}
    globals()['{class_name}'] = {class_name}
    __all__.append('{class_name}')
except (ImportError, AttributeError):
    pass

'''
        except Exception:
            continue
    
    init_content += '\n__version__ = "22.2"\n'
    
    return init_content

if __name__ == "__main__":
    print("Generating comprehensive telegram __init__.py...")
    content = create_comprehensive_init()
    
    with open(".pythonlibs/lib/python3.11/site-packages/telegram/__init__.py", "w") as f:
        f.write(content)
    
    print("Done! Generated comprehensive telegram __init__.py")