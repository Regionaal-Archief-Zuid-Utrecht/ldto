#!/usr/bin/env python3

import sys
from pathlib import Path
import pyshacl
from rdflib import Graph

def validate_rdf(input_file, shapes_type='core'):
    # Load the data graph from the input file
    data_graph = Graph()
    data_graph.parse(input_file)

    # Load the SHACL shapes graph
    if shapes_type not in ['core', 'extensions']:
        raise ValueError("shapes_type must be either 'core' or 'extensions'")
        
    shapes_file = Path(__file__).parent.parent / "shacl" / f"ldto-{shapes_type}.ttl"
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
        print("Usage: python validate.py <rdf-file> [core|extensions]")
        return 2

    input_file = sys.argv[1]
    if not Path(input_file).exists():
        print(f"Error: File {input_file} does not exist")
        return 2

    shapes_type = 'core'  # default value
    if len(sys.argv) == 3:
        shapes_type = sys.argv[2]
        if shapes_type not in ['core', 'extensions']:
            print("Error: Second parameter must be either 'core' or 'extensions'")
            return 2

    return validate_rdf(input_file, shapes_type)

if __name__ == "__main__":
    sys.exit(main())