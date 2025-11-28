#!/usr/bin/env python3

import sys
from pathlib import Path
import pyshacl
from rdflib import Graph

ALLOWED_EXTENSIONS = {".ttl", ".meta.json"}

def validate_rdf(input_file, shapes_type='razu'):
    # Load the data graph from the input file
    data_graph = Graph()
    data_graph.parse(input_file)

    # Load the SHACL shapes graph
    shapes_file = Path(__file__).parent.parent / "shacl" / f"ldto-{shapes_type}.ttl"
    if not shapes_file.exists():
        raise ValueError(f"SHACL shapes file not found for variant '{shapes_type}': {shapes_file}")

    shapes_graph = Graph()
    shapes_graph.parse(shapes_file)

    # Perform the validation
    try:
        validation_result = pyshacl.validate(
            data_graph,
            shacl_graph=shapes_graph,
            inference='rdfs',
            abort_on_first=False,
            meta_shacl=False,
            debug=False
        )
        
        conforms, results_graph, results_text = validation_result

        if conforms:
            print(f"Validation successful: {input_file} conforms to ldto-{shapes_type}.ttl.")
            return 0
        else:
            print(f"Validation failed for {input_file}:")
            print(results_text)
            return 1

    except Exception as e:
        print(f"Error during validation: {str(e)}")
        return 2

def main():
    if len(sys.argv) not in [2, 3]:
        print("Usage: python validate.py <rdf-file-or-directory> [shapes-variant]")
        return 2

    input_path = Path(sys.argv[1])
    if not input_path.exists():
        print(f"Error: Path {input_path} does not exist")
        return 2

    shapes_type = 'core'  # default value
    if len(sys.argv) == 3:
        shapes_type = sys.argv[2]
        shapes_file = Path(__file__).parent.parent / "shacl" / f"ldto-{shapes_type}.ttl"
        if not shapes_file.exists():
            print(f"Error: SHACL shapes file not found for variant '{shapes_type}': {shapes_file}")
            return 2

    if input_path.is_dir():
        overall_status = 0
        for file_path in sorted(
            p for p in input_path.rglob("*")
            if p.is_file() and any(str(p).endswith(ext) for ext in ALLOWED_EXTENSIONS)
        ):
            status = validate_rdf(str(file_path), shapes_type)
            if status > overall_status:
                overall_status = status
        return overall_status
    else:
        return validate_rdf(str(input_path), shapes_type)

if __name__ == "__main__":
    sys.exit(main())