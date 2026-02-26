# LDTO: The information model of the RAZU e-depot

This repository documents the [RAZU](https://www.razu.nl/) (linked data) e-depot Information Model. This includes the **LDTO** (= *Linked Sustainably Accessible Government Information*) core ontology, semantically describing the sctructure of digital archive records metadata; and **LDTO plus**, the current *data application profile* extension, defining how data should be modeled to conform to LDTO and making explicit how RAZU reuses other existing RDF ontologies and vocabularies, such as [schema.org](https://schema.org/) or [PREMIS](https://id.loc.gov/ontologies/premis-3-0-0.html) to further describe the records on a content level. 

In addition, this repository provides a script and shacl shapes to check whether RDF files are up to the model.

## Index:

1. [LDTO ontology](#1-ldto-ontology)
2. [LDTO plus](#2-ldto-plus)
3. [Examples](#3-examples)
4. [Validation tools](#4-tools)

## Repository structure

- [def](def): contains the formal declaration of LDTO in turtle, further documentation on LDTO design choices.
- [shacl](shacl): contains the  formal shacl declaration of LDTO plus and other shacl shapes to validate LDTO RDF files.
- [examples](examples): contains example RDF files in turtle using LDTO Plus.
- [scripts](scripts): contains a python script to validate RDF files against LDTO SHACL shapes.

### 1. LDTO ontology

**LDTO** is an [RDF](https://www.w3.org/RDF/) ontology directly derived from [MDTO](https://www.nationaalarchief.nl/archiveren/mdto), the National Archives'standard for recording and exchanging unambiguous metadata. LDTO follows MDTO closely, but is designed to be more in line with principles from the world of [linked data](https://www.w3.org/wiki/LinkedData), such as working with resolvable URIs. Moreover LDTO domain and scope extend beyond MDTO -used mainly as an exchange standard- and defines metadata to describe long term preservation and access of digital archival records. 

The separation from MDTO offers RAZU the flexibility to manage the standard itself, adapting it to further developments of the e-depot, all while ensuring MDTO compatibility for government institutions whishing to preserve their archives at RAZU.

For a detailed overview of the differences between MDTO and LDTO, see [def/R.md](def/MDTO-LDTO-Mapping.md).

#### 1.1. Formal definition of LDTO

- [def/ldto.ttl](def/ldto.ttl): the definition of LDTO as RDF ontology.Click [here](https://regionaal-archief-zuid-utrecht.github.io/ldto/def/ldto.html) for an HTML view of the ontology.
- [shacl/ldto-core.ttl](shacl/ldto-core.ttl): SHACL shapes to validate RDF files that use LDTO.


### 2. LDTO plus

As a reflection of MDTO, LDTO is not itself equipped to describe domain-specific metadata for archival material in sufficient detail. Within the information model of the RAZU, **LDTO plus** is used to describe how we use other RDF ontologies and vocabularies to describe the content of archived material. This can be considered RAZU's [application profile](https://op.europa.eu/en/web/eu-vocabularies/application-profiles) and it is formally defined in shacle shapes files determining which extensions to LDTO are permitted, and how they can be applied.

Additionally, RAZU manages its own [thesauri](https://github.com/Regionaal-Archief-Zuid-Utrecht/thesauri), minting URIs for the main entities described in the archive (ex. Places, People, Organizations, etc.). 

#### 2.1. Formal definition of LDTO plus

- [shacl/ldto-plus.ttl](shacl/ldto-plus.ttl): The LDTO Plus application profile in shacle shapes without references to RAZU thesauri.
- [shacl/ldto-plus-razu.ttl](shacl/ldto-plus-razu.ttl): The LDTO Plus application profile in shacle shapes with references to RAZU thesauri.

Although the aim is to arrive at a stable model, the shapes will be further expanded in the coming years as more types of material are loaded into the e-depot to meet the information needs. In the current state of affairs, the model is mainly based on experiments with the publication of the RAZU board archive and of aerial photographs digitized by the municipality of Houten. The [RAZU newspaper archive](https://viewer.razu.nl/) is the first collection published with LDTO plus.


### 3. Examples

Examples of RDF metadata using LDTO Plus can be found in the 'examples' folder. All these examples are valid according to the strictest SHACL shape [(ldto-plus-razu.ttl)](shacl/ldto-plus-razu.ttl).

* [examples/kranten](examples/kranten): various example files such as use in describing the collection of digitized newspapers of the RAZU.
* [examples/bestuursarchief.ttl](examples/bestuursarchief.ttl): a (still experimental) design used in the test phase to describe material from the RAZU board archive.
* [examples/luchtfotos.ttl](examples/luchtfotos.ttl): a (still experimental) design used in the test phase to describe digitized aerial photographs of the municipality of Houten.


### 4. Validation tools

The SHACL shapes are suitable for common SHACL validators but using the supplied python script [scripts/validate.py](scripts/validate.py) is recommended.

#### 4.1. Installation

After cloning this repository, it is preferable to create a python virtual environment. After that, load the required libraries. To illustrate the installation via the terminal of Linux or MacOS:
   
   ```bash
   python -m venv .venv
   . .venv/bin/activate
   pip install -r requirements.txt
   ```

To check the operation of the SHACL files themselves, there is a test suite. Run the test suite with PyTest:

```bash
pytest tests/test_shacl.py -v
```


#### 4.2. Using the validation script

Validate an RDF file against the LDTO SHACL shapes with:

```bash
python scripts/validate.py path/to/file.ttl_or_directory [core|plus|razu]
```

The second argument is optional and determines which SHACL shapes are used (default: core).

If the first argument is a directory, then all underlying RDF files will be recursively validated.

Optionally, external URIs can be checked for availability:

```bash
python scripts/validate.py path/to/file.ttl --check-resolvable
```

With '--ignore-pattern', specific URIs (e.g. containing a certain substring) can be skipped in this check. This argument can be made multiple times:

```bash
python scripts/validate.py path/to/file.ttl --check-resolvable --ignore-pattern "example.com" --ignore-pattern "localhost"
```
