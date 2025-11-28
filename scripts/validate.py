#!/usr/bin/env python3

import sys
from pathlib import Path
import pyshacl
from rdflib import Graph, OWL

ALLOWED_EXTENSIONS = {".ttl", ".meta.json"}

IMPORT_MAP = {
    # Map ontology IRIs used in owl:imports to local SHACL files
    "https://data.razu.nl/def/ldto-shacl/minimal": "ldto-minimal.ttl",
    "https://data.razu.nl/def/ldto-shacl/plus": "ldto-plus.ttl",
}


def load_shapes_with_imports(shapes_type: str) -> Graph:
    """Load the base SHACL file for the given type and resolve known owl:imports
    to local TTL files in the shacl directory.
    """
    base_dir = Path(__file__).parent.parent / "shacl"
    main_file = base_dir / f"ldto-{shapes_type}.ttl"

    shapes_graph = Graph()
    shapes_graph.parse(main_file)

    # Collect owl:imports from the graph and resolve them via IMPORT_MAP
    to_process = [str(iri) for iri in shapes_graph.objects(None, OWL.imports)]
    seen = set()

    while to_process:
        iri = to_process.pop()
        if iri in seen:
            continue
        seen.add(iri)

        filename = IMPORT_MAP.get(iri)
        if not filename:
            continue

        import_path = base_dir / filename
        if not import_path.exists():
            continue

        shapes_graph.parse(import_path)

        # Also process imports that may be introduced by the newly parsed file
        for imported_iri in shapes_graph.objects(None, OWL.imports):
            imported_iri_str = str(imported_iri)
            if imported_iri_str not in seen:
                to_process.append(imported_iri_str)

    return shapes_graph

def validate_rdf(input_file, shapes_type='razu'):
    # Load the data graph from the input file
    data_graph = Graph()
    data_graph.parse(input_file)

    # Load the SHACL shapes graph
    shapes_file = Path(__file__).parent.parent / "shacl" / f"ldto-{shapes_type}.ttl"
    if not shapes_file.exists():
        raise ValueError(f"SHACL shapes file not found for variant '{shapes_type}': {shapes_file}")

    shapes_graph = load_shapes_with_imports(shapes_type)

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