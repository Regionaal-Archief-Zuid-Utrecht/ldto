# LDTO - Linked Data voor Duurzaam Toegankelijke Overheidsinformatie

LDTO is een op [MDTO](https://www.nationaalarchief.nl/archiveren/mdto) gebaseerd model voor het beschrijven van duurzaam te bewaren overheidsinformatie als linked data. Het model wordt gebruik in het e-Depot van het [Regionaal Archief Zuid-Utrecht](https://www.razu.nl/).

Onderscheid met MDTO is dat bij LDTO de nadruk niet zozeer ligt op het uitwisselen van metadatagegevens maar meer op de duurzame opslag en toegang, en daarbij aansluit bij linked data-principes. LDTO metadata zal altijd vertaald kunnen worden naar MDTO.

Deze repostory bevat de SHACL shapes voor het valideren van linked data volgens het LDTO model.

## Projectstructuur

- `shacl/` - SHACL shapes voor validatie
  - `ldto-core.ttl` - Core SHACL shapes voor het LDTO model
- `examples/` - Voorbeelden van geldige LDTO RDF
- `tests/` - Test suite
  - `invalid/` - RDF bestanden die niet zouden moeten valideren
  - `test_shacl.py` - PyTest test suite voor SHACL validatie
- `scripts/` - Hulpscripts
  - `validate.py` - Script voor het valideren van RDF bestanden

## Gebruik

De SHACL shapes zouden met ieder op SHACL gebaseerde validatie kunnen worden gebruikt ter validatie van RDF bestanden. Het is ook mogelijk om LDTO RDF bestanden te valideren met het python script `scripts/validate.py`.



### Installatie

1. Zorg dat Python 3.8 of hoger is geïnstalleerd
2. Installeer de vereiste packages:
   ```bash
   pip install -r requirements.txt
   ```


### Validatiescript

Valideer een RDF bestand tegen de LDTO SHACL shapes:

```bash
python scripts/validate.py path/to/file.ttl
```

### Tests uitvoeren

Ter controle van de SHACL-bestanden zelf, is er een PyTest test suite.

Run de test suite met PyTest:

```bash
pytest tests/test_shacl.py -v
```
