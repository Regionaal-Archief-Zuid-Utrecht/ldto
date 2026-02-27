(! English version below)

# LDTO plus: Het informatiemodel van het RAZU e-depot

Deze repository definieert **LDTO plus**, het informatiemodel dat gehanteerd wordt in het [op RDF gebaseerde e-depot](https://viewer.razu.nl/) van het [RAZU](https://www.razu.nl/). Bovendien biedt het hulpmiddelen om te controleren of RDF-bestanden aan het model voldoen.

## 1. De LDTO-ontologie

De ruggengraat van het informatiemodel wordt gevormd door **LDTO** (= *Linked Duurzaam Toegankelijke Overheidsinformatie*), een RDF-ontologie die direct afgeleid is van [MDTO](https://www.nationaalarchief.nl/archiveren/mdto) , de archief-uitwisselingsstandaard van het Nationaal Archief. LDTO is opgezet met de wens MDTO nauw te volgen maar wel meer aan te sluiten bij principes uit de wereld van linked data, zoals bijvoorbeeld het werken met URIs. Bovendien is LDTO, anders dan MDTO, vooral gericht op duurzame opslag, en niet als data-uitwisselingsstandaard. De afsplitsing van MDTO biedt RAZU de mogelijkheid om de standaard zelf te beheren en het optimaal aan te laten sluiten bij de doorontwikkeling van het door RAZU opgezette e-depot.

### 1.1. Formele definities van LDTO

* De definitie van LDTO als RDF-ontologie is te vinden in [def/ldto.ttl](def/ldto.ttl)
* RDF gebaseerd op LDTO kan gevalideerd worden met de SHACL shape in [shacl/ldto-core.ttl](shacl/ldto-core.ttl)

## 2. De ‘plus’-uitbreidingen op LDTO
LDTO is als afspiegeling van MDTO op zichzelf niet toegerust voor het voldoende gedetailleerd beschrijven van archiefmateriaal. Binnen het informatiemodel van het RAZU wordt daarom aanvullend gebruik gemaakt van andere RDF-ontologiëen, zoals bijvoorbeeld schema.org of premis. Het informatiemodel legt daarom ook vast welke uitbreidingen op LDTO toegestaan zijn, én hoe deze toe te passen.

Hoewel het streven is te komen tot een stabiel model, zullen de shapes komende jaren, naar gelang er meer materiaalsoorten in het e-depot geladen gaan worden, verder uitgebreid worden om aan te sluiten bij de informatiebehoeften. In de huidige stand van zaken is het model vooral gebaseerd op experimenten met publicatie van het RAZU-bestuursarchief en van door gemeente Houten gedigitaliseerde luchtfoto’s. Het [RAZU-krantenarchief](https://viewer.razu.nl/)  is de eerste collectie die met LDTO plus gepubliceerd is.

### 2.2. Formele definities van LDTO plus

De uitbreidingen op LDTO worden beschreven in SHACL shapes. Voor LDTO plus zijn er twee shapefiles beschikbaar:

* [shacl/ldto-plus.ttl](shacl/ldto-plus.ttl)
Het LDTO plus-model, in een definitie zonder verwijzingen naar door RAZU beheerde thesauri.
* [shacl/ldto-razu.ttl](shacl/ldto-razu.ttl)
Als voorgaande, maar strenger gedefinieerd door wel gebruik te maken van verwijzingen naar [door RAZU beheerde thesauri](https://github.com/Regionaal-Archief-Zuid-Utrecht/thesauri).

### 2.3. Voorbeeldbestanden

Voorbeelden van `LDTO plus` metadata is vinden in de map `examples`. Al deze voorbeelden zijn valide volgens de meest stricte SHACL shape [(ldto-razu.ttl)](shacl/ldto-razu.ttl).

* [examples/kranten](examples/kranten)
Verschillende voorbeeldbestanden zoals gebruik bij het beschrijven van de collectie gedigitaliseerde kranten van het RAZU.
* [examples/bestuursarchief.ttl](examples/bestuursarchief.ttl)
Een in de testfase gebruikte (nog experimentele) opzet voor het beschrijven van materiaal uit het RAZU-bestuursarchief.
* [examples/luchtfotos.ttl](examples/luchtfotos.ttl)
Een in de testfase gebruikte (nog experimentele) opzet voor het beschrijven van gedigitaliseerde luchtfoto’s van gemeente Houten.

## 3. Gebruik van de tools

De SHACL shapes zijn geschikt voor gangbare SHACL validators maar gebruikt van het meegeleverde python script [scripts/validate.py](scripts/validate.py) wordt aanbevolen.

### 3.1. Installatie

Maak na het clonen van deze repository bijvoorkeur een python virtual environment aan. Laad daarna de vereiste bibliotheken. Ter illustratie de installatie via de terminal van Linux of MacOS:
   
   ```bash
   python -m venv .venv
   . .venv/bin/activate
   pip install -r requirements.txt
   ```

Ter controle van de werking van de SHACL-bestanden zelf is er een testsuite. Run de testsuite met PyTest:

```bash
pytest tests/test_shacl.py -v
```

### 3.2. Gebruik van het validatiescript

Valideer een RDF-bestand tegen de LDTO SHACL shapes met:

```bash
python scripts/validate.py path/to/file.ttl_or_directory [core|plus|razu]
```

Het tweede argument is optioneel en bepaalt welke SHACL shapes gebruikt worden (standaard: core).

Als het eerste argument een directory is, dan zullen recursief alle onderliggende RDF-bestanden gevalideerd worden.

Optioneel kunnen externe URIs gecontroleerd worden op beschikbaarheid:

```bash
python scripts/validate.py path/to/file.ttl --check-resolvable
```

Met `--ignore-pattern` kunnen specifieke URIs (bijvoorbeeld die een bepaalde substring bevatten) worden overgeslagen bij deze check. Dit argument kan meerdere keren worden opgegeven:

```bash
python scripts/validate.py path/to/file.ttl --check-resolvable --ignore-pattern "example.com" --ignore-pattern "localhost"
```


#####################################################################################################

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
