# LDTO: The information model of the RAZU e-depot

This repository documents **LDTO**, the information model used in the [RDF-based e-depot](https://viewer.razu.nl/) of the [RAZU](https://www.razu.nl/). In addition, it provides shacl shapes to check whether RDF files are up to the model.

**LDTO** (= *Linked Sustainably Accessible Government Information*), is an [RDF](https://www.w3.org/RDF/) ontology directly derived from [MDTO](https://www.nationaalarchief.nl/archiveren/mdto), the National Archives'standard for recording and exchanging unambiguous metadata. LDTO follows MDTO closely, but is designed to be more in line with principles from the world of [linked data](https://www.w3.org/wiki/LinkedData), such as working with resolvable URIs. Moreover LDTO domain and scope extend beyond MDTO -used mainly as an exchange standard- and defines metadata to describe long term preservation and access of digital archival records. Accordingly, additional use is made of other RDF ontologies and vocabularies, such as [schema.org](https://schema.org/) or [PREMIS](https://id.loc.gov/ontologies/premis-3-0-0.html).

The separation from MDTO offers RAZU the flexibility to manage the standard itself, adapting it to further developments of the e-depot, all while ensuring MDTO compatibility for government institutions whishing to preserve their archives at RAZU.

This document is structured as follows:

1. further comparison between MDTO and LDTO + example of using uris thesauri > the rdf version of mdto, derived from xml, still uses string to define concepts related to data (ex. to express that a certain term is defined in a glossary:IO > retenion period > TermijnData (bn, they call it a data group) > startterm > begripGegevens > label > string from a glossary and the same long path to define what is the reference glossary). From a linked data point of view, this is extremely inpractical and nests information using blank nodes, which are not resolvable. Razu uses rdf thesauri to define terms, hence mints resolvable uris for defined concepts. we can then write the same information simply in 1 triple: IO > retention period > thesaury uri.
2. repository index (ttls + examples + shacl + html view) + scope comparison (check main MDTO page). 
3. how to use locally this repository to vcalidate your data 

- def / turtles / 
- def / models (ER + ontology)
- examples /
- shacl / 
- scripts /
- docs /

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
