#!/usr/bin/env python3

import sys
import argparse
import re
import urllib.request
import urllib.error
from functools import lru_cache
from pathlib import Path
import pyshacl
from rdflib import BNode, Graph, OWL, URIRef
from rdflib.namespace import RDF, RDFS, SH
import time

ALLOWED_EXTENSIONS = {".ttl", ".meta.json"}

IMPORT_MAP = {
    # Map ontology IRIs used in owl:imports to local SHACL files
    "https://data.razu.nl/def/ldto-shacl/core": "ldto-core.ttl",
    "https://data.razu.nl/def/ldto-shacl/plus": "ldto-plus.ttl",
}




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
            print(f"Warning: no local mapping for owl:imports <{iri}>; skipping import", file=sys.stderr)
            continue

        import_path = base_dir / filename
        if not import_path.exists():
            print(f"Warning: owl:imports <{iri}> resolves to missing file {import_path}; skipping", file=sys.stderr)
            continue

        shapes_graph.parse(import_path)

        # Also process imports that may be introduced by the newly parsed file
        for imported_iri in shapes_graph.objects(None, OWL.imports):
            imported_iri_str = str(imported_iri)
            if imported_iri_str not in seen:
                to_process.append(imported_iri_str)

    return shapes_graph

def compact_report(results_graph: Graph, data_graph: Graph = None, include_warnings: bool = True) -> str:
    """Build a compact report from a SHACL results graph: one line per
    leaf violation, grouped by focus node."""
    detailed = set(results_graph.objects(None, SH.detail))
    top_level = [
        r for r in results_graph.subjects(RDF.type, SH.ValidationResult)
        if r not in detailed
    ]

    def leaf_results(node):
        children = list(results_graph.objects(node, SH.detail))
        if not children:
            yield node
        for child in children:
            yield from leaf_results(child)

    grouped = {}
    for r in top_level:
        for leaf in leaf_results(r):
            focus = results_graph.value(leaf, SH.focusNode)
            item = (
                results_graph.value(leaf, SH.resultPath),
                results_graph.value(leaf, SH.value),
                results_graph.value(leaf, SH.resultMessage),
                results_graph.value(leaf, SH.sourceConstraintComponent),
                results_graph.value(leaf, SH.resultSeverity),
            )
            grouped.setdefault(focus, set()).add(item)

    if not grouped:
        return ""

    nm = results_graph.namespace_manager

    def q(term):
        return term.n3(nm) if term is not None else "-"

    def local(uri):
        s = str(uri)
        return s.rsplit("#", 1)[-1].rsplit("/", 1)[-1]

    def describe(focus):
        """Label for a focus node; for blank nodes add a type hint."""
        label = q(focus)
        if data_graph is not None and isinstance(focus, BNode):
            types = [
                t for t in data_graph.objects(focus, RDF.type)
                if t not in (RDFS.Resource, OWL.Thing)
            ]
            if types:
                label += f" (a {q(sorted(types, key=str)[0])})"
        return label

    def clean_message(msg, focus):
        text = str(msg)
        # "Node <huge node dump> must conform ..." -> "must conform ..."
        text = re.sub(r"^Node\b.*?\bmust\b", "must", text, flags=re.S)
        # "... shapes in [ <shape turtle> ] ..." -> list the constrained
        # classes/properties instead of dumping the shapes
        m = re.search(r"must conform to (all|one or more) shapes in (.*)", text, flags=re.S)
        if m:
            quantifier = "all of" if m.group(1) == "all" else "one or more of"
            refs = re.findall(r"sh:(?:class|path)\s+([^\s\],;]+)", m.group(2))
            if refs:
                text = f"must conform to {quantifier}: {', '.join(dict.fromkeys(refs))}"
        # "... on <node>->path" / "... on [ <bnode dump> ]->path" -> drop it
        text = re.sub(
            r"\s+on\s+(<[^>]+>|_:\S+|\[.*\])(->\S*)?$", "", text, flags=re.S
        )
        if focus is not None:
            text = text.replace(str(focus), "this")
        if len(text) > 300:
            text = text[:300].rsplit(" ", 1)[0] + " ..."
        return text

    lines = []
    n_viol = 0
    n_warn_shown = 0
    n_warn_hidden = 0
    for focus in sorted(grouped, key=lambda f: str(f)):
        items = sorted(
            grouped[focus], key=lambda i: (str(i[0]), str(i[3]), str(i[2]))
        )
        shown = []
        for item in items:
            sev = item[4]
            if sev in (None, SH.Violation):
                n_viol += 1
                shown.append(item)
            elif include_warnings:
                n_warn_shown += 1
                shown.append(item)
            else:
                n_warn_hidden += 1
        if not shown:
            continue
        lines.append(describe(focus))
        for path, value, msg, comp, sev in shown:
            text = clean_message(msg, focus) if msg else "does not conform"
            location = f"{q(path)}: " if path is not None else ""
            val = f" (value: {q(value)})" if value is not None and value != focus else ""
            sev_tag = "" if sev in (None, SH.Violation) else f" [{local(sev)}]"
            comp_tag = f" [{local(comp)}]" if comp is not None else ""
            lines.append(f"  - {location}{text}{comp_tag}{val}{sev_tag}")
        lines.append("")

    if not lines:
        return f"({n_warn_hidden} warning(s) suppressed)" if n_warn_hidden else ""

    parts = [f"{n_viol} violation(s)"] if n_viol else []
    if n_warn_shown:
        parts.append(f"{n_warn_shown} warning(s)")
    if n_warn_hidden:
        parts.append(f"{n_warn_hidden} warning(s) suppressed")
    lines.append(", ".join(parts) + " total")
    return "\n".join(lines)


def validate_rdf(input_file, shapes_type='razu', check_resolvable=False, ignore_patterns=None, rdf_format=None, verbose=False, include_warnings=True):
    # Load the data graph from the input file
    data_graph = Graph()
    data_graph.parse(input_file, format=rdf_format)

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
            advanced=True,
            abort_on_first=False,
            meta_shacl=False,
            debug=False
        )
        
        conforms, results_graph, results_text = validation_result

        # Per the SHACL spec only sh:Violation results break conformance;
        # pyshacl's `conforms` is False whenever any result (incl. warnings)
        # exists, so recompute it from the result severities.
        conforms = not any(
            sev in (None, SH.Violation)
            for r in results_graph.subjects(RDF.type, SH.ValidationResult)
            for sev in [results_graph.value(r, SH.resultSeverity)]
        )

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
            report = results_text if verbose else compact_report(results_graph, data_graph, include_warnings)
            if report:
                print(report)
            return 0
        else:
            if not conforms:
                print(f"Validation failed for {input_file}:")
                print(results_text if verbose else compact_report(results_graph, data_graph, include_warnings))
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
    parser.add_argument("--format", choices=["turtle"], default=None, help="Force RDF parse format (e.g. turtle)")
    parser.add_argument("--verbose", action="store_true", help="Print the full pySHACL report instead of a compact summary")
    parser.add_argument("--no-warnings", action="store_true", help="Hide sh:Warning results (only show violations)")
    
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
            status = validate_rdf(str(file_path), shapes_type, args.check_resolvable, args.ignore_pattern, args.format, args.verbose, not args.no_warnings)
            if status > overall_status:
                overall_status = status
        return overall_status
    else:
        return validate_rdf(str(input_path), shapes_type, args.check_resolvable, args.ignore_pattern, args.format, args.verbose, not args.no_warnings)

if __name__ == "__main__":
    sys.exit(main())