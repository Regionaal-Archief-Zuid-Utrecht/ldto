#!/usr/bin/env python3

import sys
import argparse
import urllib.request
import urllib.error
from functools import lru_cache
from pathlib import Path
import pyshacl
from rdflib import Graph, OWL, URIRef

ALLOWED_EXTENSIONS = {".ttl", ".meta.json"}

IMPORT_MAP = {
    # Map ontology IRIs used in owl:imports to local SHACL files
    "https://data.razu.nl/def/ldto-shacl/core": "ldto-core.ttl",
    "https://data.razu.nl/def/ldto-shacl/plus": "ldto-plus.ttl",
}


import time

@lru_cache(maxsize=2048)
def check_resolvability(uri: str) -> tuple:
    """Check if a URI is resolvable via HTTP.
    Returns (bool, str) where str is the reason/status.
    """
    if not uri.startswith("http"):
        return True, "Skipped (non-HTTP)"

    headers = {
        'User-Agent': 'LDTO-Validator/1.0',
        'Accept': 'text/turtle,application/ld+json,application/rdf+xml,text/html;q=0.9,*/*;q=0.8'
    }

    max_retries = 3
    last_error = "Unknown error"

    for attempt in range(max_retries):
        try:
            # Try HEAD first
            req = urllib.request.Request(uri, method='HEAD', headers=headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                if 200 <= response.status < 400:
                    return True, "OK"
        except Exception:
            # If HEAD fails, proceed to GET
            pass

        try:
            req = urllib.request.Request(uri, method='GET', headers=headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                if 200 <= response.status < 400:
                    return True, "OK"
                else:
                    return False, f"HTTP {response.status}"
        except urllib.error.HTTPError as e:
            last_error = f"HTTP {e.code} {e.reason}"
            # Don't retry client errors (4xx) except maybe 429 (Too Many Requests)
            if 400 <= e.code < 500 and e.code != 429:
                return False, last_error
        except urllib.error.URLError as e:
            last_error = f"Network Error: {e.reason}"
        except Exception as e:
            last_error = f"Error: {str(e)}"
        
        # Wait before retrying
        if attempt < max_retries - 1:
            time.sleep(1)

    return False, last_error


def get_external_uris(graph: Graph) -> set:
    """Identify external URIs. An external URI is a URI that occurs as an object
    in the graph but never as a subject.
    """
    subjects = set(graph.subjects())
    external_uris = set()
    for obj in graph.objects():
        if isinstance(obj, URIRef) and obj not in subjects:
            external_uris.add(str(obj))
    return external_uris


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

def validate_rdf(input_file, shapes_type='razu', check_resolvable=False, ignore_patterns=None):
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

        resolvable_ok = True
        if check_resolvable:
            external_uris = get_external_uris(data_graph)
            failed_uris = []
            for uri in sorted(external_uris):
                if ignore_patterns and any(pattern in uri for pattern in ignore_patterns):
                    continue

                is_ok, reason = check_resolvability(uri)
                if not is_ok:
                    failed_uris.append((uri, reason))
            
            if failed_uris:
                print("The following external URIs could not be resolved:")
                for uri, reason in sorted(failed_uris):
                    print(f"  - {uri} ({reason})")
                resolvable_ok = False

        if conforms and resolvable_ok:
            print(f"Validation successful: {input_file} conforms to ldto-{shapes_type}.ttl.")
            return 0
        else:
            if not conforms:
                print(f"Validation failed for {input_file}:")
                print(results_text)
            if not resolvable_ok:
                print(f"Validation failed for {input_file}: Unresolvable external URIs found.")
            return 1

    except Exception as e:
        print(f"Error during validation: {str(e)}")
        return 2

def main():
    parser = argparse.ArgumentParser(description="Validate RDF files against SHACL shapes.")
    parser.add_argument("input_path", type=Path, help="RDF file or directory to validate")
    parser.add_argument("shapes_variant", nargs="?", default="core", help="Shapes variant (default: core)")
    parser.add_argument("--check-resolvable", action="store_true", help="Check if external URIs are resolvable")
    parser.add_argument("--ignore-pattern", action="append", help="Substring patterns to ignore when checking resolvability (can be used multiple times)")
    
    args = parser.parse_args()

    input_path = args.input_path
    if not input_path.exists():
        print(f"Error: Path {input_path} does not exist")
        return 2

    shapes_type = args.shapes_variant
    # Verify shapes file exists
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
            status = validate_rdf(str(file_path), shapes_type, args.check_resolvable, args.ignore_pattern)
            if status > overall_status:
                overall_status = status
        return overall_status
    else:
        return validate_rdf(str(input_path), shapes_type, args.check_resolvable, args.ignore_pattern)

if __name__ == "__main__":
    sys.exit(main())