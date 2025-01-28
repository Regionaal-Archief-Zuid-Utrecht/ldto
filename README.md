# LDTO - Linked Data voor Duurzaam Toegankelijke Overheidsinformatie

LDTO is een op [MDTO](https://www.nationaalarchief.nl/archiveren/mdto) gebaseerd model voor het beschrijven van duurzaam te bewaren overheidsinformatie als *linked data*. Het model wordt gebruik in het e-Depot van het [Regionaal Archief Zuid-Utrecht](https://www.razu.nl/).

Bij LDTO ligt de nadruk minder dan bij MDTO op het *uitwisselen* van metadatagegevens maar meer op de *duurzame opslag en toegang*. Bovendien is LDTO gebaseerd op *RDF* en *linked data-principes*. LDTO-metadata zal altijd vertaald kunnen worden naar MDTO.

Deze repostory bevat de *SHACL shapes* voor het valideren van linked data volgens het LDTO-model.

**LET OP: LDTO en de SHACL shapes zijn in ontwikkeling en kunnen in deze fase nog zonder waarschuwing vooraf veranderen.**


## Projectstructuur

- [`def/`](def/) - Definitiebestanden
  - [`ldto.ttl`](def/ldto.ttl) - De RDF-ontologie van LDTO, gebaseerd op MDTO
- [`shacl/`](shacl/) - SHACL shapes voor validatie
  - [`ldto-core.ttl`](shacl/ldto-core.ttl) - Kern met SHACL shapes voor het LDTO model
  - [`ldto-extensions.ttl`](shacl/ldto-extensions.ttl) - Aanvullende shapes voor validatie van niet-LDTO vocabulaires, zoals toegepast binnen het informatiemodel van het RAZU e-Depot.
- [`examples/`](examples/) - Voorbeelden van LDTO RDF, die voldoet aan zowel de *core* als ook de *extension* shapes.
  - [`bestuursarchief.ttl`](examples/bestuursarchief.ttl) - Voorbeeld 'bestuursarchief' met LDTO-metadata
  - [`luchtfotos.ttl`](examples/luchtfotos.ttl) - Voorbeeld 'luchtfotos' met LDTO metadata
- [`tests/`](tests/) - Test suite
  - [`core/invalid/`](tests/core/invalid/) - RDF bestanden die niet zouden moeten valideren tegen de *core* shapes
  - [`extensions/invalid/`](tests/extensions/invalid/) - RDF-bestanden die niet valideren tegen de *extension* shapes
  - [`test_shacl.py`](tests/test_shacl.py) - PyTest testsuite voor twee sets SHACL shapes
- [`scripts/`](scripts/) - Hulpscripts
  - [`validate.py`](scripts/validate.py) - Script voor het valideren van RDF-bestanden

## SHACL Shapes

Het project bevat twee sets van SHACL shapes:

1. **Core Shapes** (`ldto-core.ttl`): Bevat de basis-validatieregels voor het [LDTO-model](def/ldto.ttl).
2. **Extension Shapes** (`ldto-extensions.ttl`): Bevat aanvullende validatieregels voor andere vocabulaires die door het RAZU in combinatie met LDTO worden gebruikt.

## Gebruik

De SHACL shapes kunnen met iedere op SHACL gebaseerde validator worden gebruikt ter validatie van RDF-bestanden. Het is ook mogelijk om LDTO bestanden te valideren met het pythonscript `scripts/validate.py`.

### Installatie validatie-script

1. Zorg dat Python 3.8 of hoger is geïnstalleerd
2. Installeer de vereiste packages:
   ```bash
   pip install -r requirements.txt
   ```

### Validatiescript

Valideer een RDF-bestand tegen de LDTO SHACL shapes:

```bash
python scripts/validate.py path/to/file.ttl [core|extensions]
```

Het tweede argument is optioneel en bepaalt welke SHACL shapes gebruikt worden (standaard: core).

### Tests uitvoeren

Ter controle van de SHACL-bestanden zelf, is er een PyTest testsuite.

Run de testsuite met PyTest:

```bash
pytest tests/test_shacl.py -v
```

Dit zal alle tests uitvoeren, inclusief validatie tegen zowel de *core* als de *extension* shapes.
