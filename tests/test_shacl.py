import sys
from pathlib import Path

import pytest
import pyshacl
from rdflib import Graph
from rdflib.namespace import RDF, SH

# Ensure project root (containing the 'scripts' module) is on sys.path
PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.validate import validate_rdf, load_shapes_with_imports, ALLOWED_EXTENSIONS


TESTS_ROOT = Path(__file__).parent


def iter_data_files(expectation: str):
    """Yield (data_file, shapes_type) pairs for tests/<shapes_type>/<expectation>/.

    - <shapes_type>  -> name of the SHACL profile (e.g. core, plus, razu)
    - <expectation>  -> 'valid', 'invalid' or 'warning'
    """
    for shapes_dir in TESTS_ROOT.iterdir():
        if not shapes_dir.is_dir():
            continue

        data_dir = shapes_dir / expectation
        if not data_dir.is_dir():
            continue

        for data_file in data_dir.iterdir():
            if not data_file.is_file():
                continue
            if not any(str(data_file).endswith(ext) for ext in ALLOWED_EXTENSIONS):
                continue

            yield data_file, shapes_dir.name


def iter_test_cases():
    """Yield pytest parameters for all valid/invalid test files."""
    for expectation in ("valid", "invalid"):
        for data_file, shapes_type in iter_data_files(expectation):
            test_id = f"{shapes_type}-{expectation}-{data_file.name}"
            yield pytest.param(
                data_file, shapes_type, expectation == "valid", id=test_id
            )


@pytest.mark.parametrize("data_file,shapes_type,expected_conforms", list(iter_test_cases()))
def test_files_against_ldto_profiles(data_file: Path, shapes_type: str, expected_conforms: bool):
    """Validate all test files using scripts/validate.py according to directory naming.

    - tests/<shapes_type>/valid/*   -> must conform (validate.py exit code 0)
    - tests/<shapes_type>/invalid/* -> must NOT conform (validate.py exit code != 0)
    - tests/<shapes_type>/warning/* -> must conform but emit >= 1 sh:Warning
                                       (see test_warning_files)
    """
    status = validate_rdf(str(data_file), shapes_type)

    if expected_conforms:
        assert status == 0, (
            f"Expected validation to succeed for {data_file} with profile '{shapes_type}', "
            f"but validate.py returned status {status}."
        )
    else:
        assert status != 0, (
            f"Expected validation to fail for {data_file} with profile '{shapes_type}', "
            f"but validate.py returned status {status}."
        )


def iter_warning_cases():
    """Yield pytest parameters for files under tests/<shapes_type>/warning/.

    These files must conform (no sh:Violation) but produce at least one
    sh:Warning result.
    """
    for data_file, shapes_type in iter_data_files("warning"):
        test_id = f"{shapes_type}-warning-{data_file.name}"
        yield pytest.param(data_file, shapes_type, id=test_id)


@pytest.mark.parametrize("data_file,shapes_type", list(iter_warning_cases()))
def test_warning_files(data_file: Path, shapes_type: str):
    """Files in tests/<shapes_type>/warning/ must conform but emit >= 1 sh:Warning."""
    data_graph = Graph()
    data_graph.parse(str(data_file), format="turtle")
    shapes_graph = load_shapes_with_imports(shapes_type)

    _, results_graph, _ = pyshacl.validate(
        data_graph,
        shacl_graph=shapes_graph,
        inference="rdfs",
        advanced=True,
        abort_on_first=False,
        meta_shacl=False,
        debug=False,
    )

    severities = {
        results_graph.value(r, SH.resultSeverity) or SH.Violation
        for r in results_graph.subjects(RDF.type, SH.ValidationResult)
    }
    assert SH.Violation not in severities, (
        f"Expected only warnings for {data_file} with profile '{shapes_type}', "
        f"but found sh:Violation results."
    )
    assert SH.Warning in severities, (
        f"Expected at least one sh:Warning for {data_file} with profile '{shapes_type}', "
        f"but found none."
    )


EXAMPLES_DIR = PROJECT_ROOT / "examples"


def test_examples_conform_to_razu_profile():
    """All example files must conform to the 'razu' profile."""
    assert EXAMPLES_DIR.is_dir(), f"Examples directory not found: {EXAMPLES_DIR}"

    for example_file in EXAMPLES_DIR.rglob("*"):
        if not example_file.is_file():
            continue
        if not any(str(example_file).endswith(ext) for ext in ALLOWED_EXTENSIONS):
            continue

        status = validate_rdf(str(example_file), "razu")
        assert status == 0, (
            f"Expected example {example_file} to conform to 'razu' profile, "
            f"but validate.py returned status {status}."
        )