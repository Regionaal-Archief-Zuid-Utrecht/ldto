#!/usr/bin/env python3

import sys
from pathlib import Path
import pyshacl
from rdflib import Graph

def validate_rdf(input_file):
    # Load the data graph from the input file
    data_graph = Graph()
    data_graph.parse(input_file)

    # Load the SHACL shapes graph
    shapes_file = Path(__file__).parent.parent / "shacl" / "ldto-core.ttl"
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
            print(f"Validation successful: {input_file} conforms to the SHACL shapes.")
            return 0
        else:
            print(f"Validation failed for {input_file}:")
            print(results_text)
            return 1

    except Exception as e:
        print(f"Error during validation: {str(e)}")
        return 2

def main():
    if len(sys.argv) != 2:
        print("Usage: python validate.py <rdf-file>")
        return 2

    input_file = sys.argv[1]
    if not Path(input_file).exists():
        print(f"Error: File {input_file} does not exist")
        return 2

    return validate_rdf(input_file)

if __name__ == "__main__":
    sys.exit(main())