#!/usr/bin/env python

import re
import sys
from typing import Dict
import json

def extract_functions_from_js(file_path: str) -> Dict[str, str]:
    """
    Extract all function definitions from a JavaScript file.

    Args:
        file_path (str): Path to the JavaScript file.

    Returns:
        Dict[str, str]: A dictionary with function names as keys and their code as values.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Regex to find function definitions
    function_pattern = re.compile(
        r"function\s+(\w+)\s*\((.*?)\)\s*\{(.*?)\}$", re.MULTILINE | re.DOTALL
    )

    functions = {}
    for match in function_pattern.finditer(content):
        func_name = match.group(1)
        func_body = match.group(0)
        functions[func_name] = func_body

    return functions

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]
    functions = extract_functions_from_js(file_path)
    json.dump(functions, sys.stdout, ensure_ascii=False, indent=4)