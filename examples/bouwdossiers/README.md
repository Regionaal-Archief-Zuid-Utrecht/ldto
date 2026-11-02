# Adres-URIs en referentielijst bouwvergunningen
Concept, RV 2025-11-02

## Waarom

1. We willen dat bezoekers kunnen zoeken naar alles wat bij een specifiek adres hoort; dan heeft elk adres een eigen, stabiele URI nodig.
2. Veel (oudere) adressen staan niet in de BAG, dus we kunnen niet op BAG-URIs bouwen. En ook als alles erin zou staan: bij het indexeren voor Elasticsearch willen we alles lokaal beschikbaar hebben (geen externe lookups).
3. We willen dus een eigen referentielijst (betere naam dan 'thesaurus', een adres is niet gemodelleerd als een skos:Concept) met alle adressen die we tegenkomen, waaronder de relevante actuele BAG-adressen.

## Keuzes

1. Eigen URI-ruimte: `https://data.razu.nl/id/adres/`. 
2. Twee patronen, beide zonder een lookup in code te hoeven te construeren:
   - actueel BAG-adres: `/id/adres/{16-cijferige nummeraanduiding}` (BAG-identificaties zijn permanent);
   - historisch adres: `/id/adres/hist-{hash}` (normalisatie en hash: zie hieronder).
3. Een adres zonder BAG is en blijft historisch. Krijgt een dergelijke aanduiding later alsnog een BAG-nummeraanduiding, dan is dat een ander adres (vergelijkbare aanduiding): we promoveren nooit, want dan breken we links en forceren we een "zelfde adres"-relatie die we niet kunnen onderbouwen.
4. De volledige adresbeschrijving (huisnummer, postcode, ligtAan, ligtIn, sameAs, geometrie) leeft alleen in de referentielijst; het dossier refereert via `schema:address <adres-uri>`.

## Normalisatieregel en hash

Van elke bronrecord construeren we een normalisatiesleutel:

1. Velden, in vaste volgorde, gescheiden met `|`: `woonplaats|straatnaam|huisnummer|huisletter|huisnummertoevoeging`.
2. Elke waarde: trimmen, lowercase, diakritieten naar ASCII (é→e, ï→i); ontbrekende velden blijven leeg (dus `cothen|caspargauw|8||`).
3. Huisnummer als integer zonder voorloopnullen; huisletter al uppercase in de BAG-conventie, maar in de sleutel dus lowercase.
4. MD5 van die string (UTF-8), genomen als hexadecimaal (lowercase), **de eerste 12 tekens** (om het hanteerbaar te maken - nogs steeds minimale kans op 'collision'): `/id/adres/hist-{12 hex}`.

Deze regel is definitief en deel van het ontwerp: zonder exact deze stappen is de URI niet te reproduceren. Bij twijfel over een veld (bijv. woonplaatsnaam met spatie) geldt: eerst de BAG-schrijfwijze, anders de bron, maar altijd via dezelfde normalisatie.

## Voorbeeld

```turtle
# dossier (fragment)
ldto:dekkingInRuimte [
    a ldto:Locatie, bag:Verblijfsobject ;
    schema:address <https://data.razu.nl/id/adres/hist-7f3a9c1b2d4e> ;
] .

# referentielijst: historisch adres
<https://data.razu.nl/id/adres/hist-7f3a9c1b2d4e>
    a schema:PostalAddress ;
    rdfs:label "Caspargauw 8, Cothen" ;
    rdfs:comment "Historisch adres, niet in huidige BAG"@nl ;
    bag:huisnummer 8 ;
    bag:ligtAan [ a bag:OpenbareRuimte ; bag:naam "Caspargauw" ] ;
    bag:ligtIn <https://data.razu.nl/id/locatie/f5ef414df02e8a28bb60055ff6e1c151> .  # Cothen, bestaande locatie-referentielijst

# referentielijst: actueel adres
<https://data.razu.nl/id/adres/0321200000005558>
    a schema:PostalAddress, bag:Nummeraanduiding ;
    rdfs:label "Caspargauw 8, 3945PH Cothen" ;
    bag:huisnummer 8 ; 
    bag:postcode "3945PH" ;
    bag:identificatie "0321200000005558" ;
    owl:sameAs <http://bag.basisregistraties.overheid.nl/bag/id/nummeraanduiding/0321200000005558> ;
    bag:ligtAan [
        a bag:OpenbareRuimte ; bag:naam "Caspargauw" ;
        bag:identificatie "0352300000000247" ;
        owl:sameAs <http://bag.basisregistraties.overheid.nl/bag/id/openbare-ruimte/0352300000000247>
    ] ;
    bag:ligtIn <https://data.razu.nl/id/locatie/f5ef414df02e8a28bb60055ff6e1c151> .  # Cothen, bestaande locatie-referentielijst
```

## Normalisatie in code (pseudocode)

```python
def adres_uri(woonplaats, straat, huisnummer, huisletter="", toevoeging=""):
    norm = lambda s: unicodedata.normalize("NFKD", s.strip().lower()) \
                       .encode("ascii", "ignore").decode()
    sleutel = "|".join([
        norm(woonplaats), norm(straat),
        str(int(huisnummer)), norm(huisletter), norm(toevoeging)
    ])
    return f"https://data.razu.nl/id/adres/hist-{hashlib.md5(sleutel.encode()).hexdigest()[:12]}"
```