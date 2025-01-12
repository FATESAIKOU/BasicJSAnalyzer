#!/usr/bin/env python

import sys
import os
import json
import subprocess
from typing import Dict

def process_files(file_list: str, output_path: str):
    """
    Process a list of files using the old extraction script and save the result to a JSON file.

    Args:
        file_list (str): A space-separated string of file paths.
        output_path (str): Path to save the output JSON file.
    """
    old_program_path = os.path.join(os.path.dirname(__file__), "structurelizeFunction.py")
    
    result = {}
    for file_path in file_list.split():
        if not os.path.isfile(file_path):
            print(f"Warning: {file_path} does not exist or is not a file.")
            continue

        # Call the old program and capture the output
        try:
            output = subprocess.check_output(
                ["python", old_program_path, file_path],
                text=True
            )
            result[file_path] = json.loads(output)
        except subprocess.CalledProcessError as e:
            print(f"Error processing {file_path}: {e}")
        except json.JSONDecodeError:
            print(f"Error decoding JSON for {file_path}: Output may be malformed.")

    # Write the combined results to the output file
    with open(output_path, 'w', encoding='utf-8') as output_file:
        json.dump(result, output_file, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: ./newProgram.py \"$(find xxx -name \"*.js\")\" outputJson.json")
        sys.exit(1)

    file_list = sys.argv[1]
    output_path = sys.argv[2]

    process_files(file_list, output_path)
    print(f"Output written to {output_path}")
