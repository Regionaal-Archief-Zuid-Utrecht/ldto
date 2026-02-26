## Directory index

- **ldto.ttl**: The formal declaration of the core LDTO ontology.
- **ldto.html**: HTML view of the ontology following [LODE](https://essepuntato.it/lode/) [here](https://regionaal-archief-zuid-utrecht.github.io/ldto/def/ldto.html)
- **LDTO-MDTO-mapping.xlsx**: Mapping between LDTO and MDTO properties, detailing the differences and the rationale behind LDTO choices.

## How to update the html version

1. install pylode: `pip install pylode`
2. in this directory, run: `python3 -m pylode.cli ldto.ttl -o ldto.html`

## to do:

[x] IO ldto:dekkingInRuimte ldto:Locatie (now a schema:Place) 
[ ] IO ldto:radpleegLocatie ldto:Locatie (we don't use this property now but if we will, we might want to use a URI pointoing to Valeros)
[ ] Add to excel mapping properties of mdto:InformatieObject and mdto:Bestand, mdot:Actor and mdto:Locatie