# LDTO plus: Het informatiemodel van het RAZU e-depot

Deze repository definieert **LDTO plus**, het informatiemodel dat gehanteerd wordt in het op RDF gebaseerde e-depot van het [RAZU](https://www.razu.nl/).

## 1. De LDTO-ontologie

De ruggengraat van het model wordt gevormd door **LDTO** (= Linked Duurzaam Toegankelijke Overheidsinformatie), een RDF-ontologie die direct afgeleid is van [MDTO](https://www.nationaalarchief.nl/archiveren/mdto) , de archief-uitwisselingsstandaard van het Nationaal Archief. LDTO is opgezet met de wens MDTO nauw te volgen maar wel meer aan te sluiten bij principes uit de wereld van linked data, zoals bijvoorbeeld het werken met URIs. Bovendien is LDTO, anders dan MDTO, vooral gericht op duurzame opslag, en niet als data-uitwisselingsstandaard. De afsplitsing van MDTO biedt RAZU de mogelijkheid om de standaard zelf te beheren en het optimaal aan te laten sluiten bij de doorontwikkeling van het door RAZU opgezette e-depot.

### 1.1. Formele definities van LDTO

* De definitie van LDTO als RDF-ontologie is te vinden in [def/ldto.ttl](def/ldto.ttl)
* RDF gebaseerd op LDTO kan gevalideerd worden met de SHACL shape in [shacl/ldto-core.ttl](shacl/ldto-core.ttl])

## 2. De ‘plus’ uitbreidingen op LDTO
LDTO is als afspiegeling van MDTO onvoldoende rijk voor het voldoende gedetailleerd beschrijven van archiefmateriaal. Binnen het informatiemodel van het RAZU wordt daarom aanvullend gebruik gemaakt van andere RDF-ontologiëen, zoals bijvoorbeeld schema.org of premis. Het informatiemodel legt daarom ook vast welke uitbreidingen op LDTO toegestaan zijn en hoe deze toe te passen.

Hoewel het streven is om te komen tot een stabiel model, zullen de shapes komende jaren, naar gelang er meer materiaalsoorten in het e-depot geladen gaan worden, verder uitgebreid worden om aan te sluiten bij de informatiebehoeften. Het huidige model is vooral gebaseerd op experimenten met het RAZU-bestuursarchief, door gemeente Houten gedigitaliseerde luchtfoto’s. Het RAZU-krantenarchief is de eerste collectie die met LDTO plus gepubliceerd is.
De uitbreidingen op LDTO worden beschreven in SHACL shapes. Voor LDTO plus zijn er twee shapefiles beschikbaar:

### 2.2. Formele definities van LDTO plus

* [shacl/ldto-plus.ttl](shacl/ldto-plus.ttl)
Het LDTO plus-model, in een definitie zonder verwijzing naar door RAZU beheerde thesauri.
* [shacl/ldto-razu.ttl](shacl/ldto-razu.ttl)
Als voorgaande, maar strenger gedefinieerd door wel gebruik te maken van verwijzingen naar door RAZU beheerde thesauri.

### 2.3. Voorbeeldbestanden

Voorbeelden van LDTO plus metadata is vinden in de map `examples`. Als deze voorbeelden zijn valide volgens de meest stricte SHACL shape [(ldto-razu.ttl)](shacl/ldto-razu.ttl).

* [examples\kranten](examples\kranten)
Verschillende bestanden zoals gebruik bij het beschrijven van de collectie gedigitaliseerde kranten van het RAZU.
* [examples\bestuursarchief.ttl](examples\bestuursarchief.ttl)
Een in de testfase gebruikte (nog experimentele) opzet voor het beschrijven van materiaal uit het RAZU-bestuursarchief.
* [examples\luchtfotos.ttl](examples\luchtfotos.ttl)
Een in de testfase gebruikte (nog experimentele) opzet voor het beschrijven van gedigitaliseerde luchtfoto’s van gemeente Houten.

## 3. Gebruik van de tools

De SHACL shapes zijn geschikt voor gangbare SHACL validators maar gebruikt van het meegeleverde python script [scripts\validate.py](scripts\validate.py) wordt aanbevolen.

### 3.1. Installatie

Maak na het clonen van deze repository bijvoorkeur een python virtual environment aan. Laadt daarna de vereiste bibliotheken. Ter illustratie de installatie onder Linux of MacOS:
   
   ```bash
   python -m venv .venv
   . .venv/bin/activate
   pip install -r requirements.txt
   ```

Ter controle van de SHACL-bestanden zelf, is er een testsuite. Run de testsuite met PyTest:

```bash
pytest tests/test_shacl.py -v
```

### 3.2. Gebruik validatiescript

Valideer een RDF-bestand tegen de LDTO SHACL shapes:

```bash
python scripts/validate.py path/to/file.ttl_or_directory [core|plus|razu]
```

Het tweede argument is optioneel en bepaalt welke SHACL shapes gebruikt worden (standaard: core).

Als het eerste argument een directory is, dan zullen recursief alle onderliggende RDF-bestanden gevalideerd worden.

