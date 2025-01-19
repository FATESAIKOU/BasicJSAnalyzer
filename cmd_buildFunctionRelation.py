#!/usr/bin/env python
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def load_json(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except UnicodeDecodeError:
        with open(file_path, 'r', encoding='shift_jis') as file:
            return json.load(file)


def first_find(src_structure, arg_keyword):
    queue = []
    result = []

    for file, file_def in src_structure.items():
        # Check file raw
        if arg_keyword in file_def['raw']:
            queue.append(f"{file}")

        # Check functions in file
        for function_name, function_def in file_def['functions'].items():
            if arg_keyword in function_name:
                queue.append(f"{file}.f-{function_name}")

        # Check classes in file
        for class_name, class_def in file_def['classes'].items():
            if arg_keyword in class_name:
                queue.append(f"{file}.c-{class_name}")

            # Check methods in class
            for method_name, method_def in class_def['methods'].items():
                if arg_keyword in method_name:
                    queue.append(f"{file}.c-{class_name}.m-{method_name}")

            # Check static methods in class
            for static_method_name, static_method_def in class_def['static_methods'].items():
                if arg_keyword in static_method_name:
                    queue.append(f"{file}.c-{class_name}.s-{static_method_name}")

    return queue, result

def match(code_def_str, internal_keyword):
    internal_keyword_parts = internal_keyword.split('.')

    # keyword = "file"
    if len(internal_keyword_parts) == 1:
        # Just skip
        return False
    # keyword = "file.f-functionName" or "file.c-className"
    elif len(internal_keyword_parts) == 2:
        second_part_split = internal_keyword_parts[1].split('-')

        # keyword = "file.f-functionName"
        if second_part_split[0] == 'f':
            return second_part_split[1] + "(" in code_def_str
        # keyword = "file.c-className
        elif second_part_split[0] == 'c':
            return second_part_split[1] + " " in code_def_str

    # keyword = "file.c-classname.m-methodname" or "file.c-classname.s-staticmethodname"
    elif len(internal_keyword_parts) == 3:
        second_part_split = internal_keyword_parts[1].split('-')
        third_part_split = internal_keyword_parts[2].split('-')

        return third_part_split[1] + "(" in code_def_str
    else:
        return False

def flattern_iterator(src_structure):
    for file, file_def in src_structure.items():
        yield [file, file_def['raw']]

        for function_name, function_def in file_def['functions'].items():
            yield [f"{file}.f-{function_name}", function_def['body']]

        for class_name, class_def in file_def['classes'].items():
            yield [f"{file}.c-{class_name}", class_def['raw']]

            for method_name, method_def in class_def['methods'].items():
                yield [f"{file}.c-{class_name}.m-{method_name}", method_def['body']]

            for static_method_name, static_method_def in class_def['static_methods'].items():
                yield [f"{file}.c-{class_name}.s-{static_method_name}", static_method_def['body']]

def main(input_path, arg_keyword, output_path):
    src_structure = load_json(input_path)

    # Data structure of internal keyword
    #   "file",
    #   "file.f-functionName",
    #   "file.c-className",
    #   "file.c-classname.m-methodname",
    #   "file.c-classname.s-staticmethodname"
    
    # Data structure of queue
    # [<internal_keyword>]

    # Proc. First find (get init queue)
    queue, result = first_find(src_structure, arg_keyword)

    # Proc. Keep find keyword with queue (Loop)
    visited = set()
    while len(queue) > 0:
        internal_keyword = queue.pop()

        if internal_keyword in visited:
            continue

        for next_internal_keyword, code_def in flattern_iterator(src_structure):
            if match(code_def, internal_keyword):
                queue.insert(0, next_internal_keyword)
                result.append([next_internal_keyword, internal_keyword])

        visited.add(internal_keyword)

    # Proc. write result to output_path
    with open(output_path, 'w', encoding='utf-8') as file:
        json.dump(result, file, ensure_ascii=False, indent=4)
    
if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python cmd_buildFunctionRelation.py <input.json> <init keyword> <output.json>", file=sys.stderr)
        sys.exit(1)

    input_path = sys.argv[1]
    arg_keyword = sys.argv[2]
    output_path = sys.argv[3]

    main(input_path, arg_keyword, output_path)