# RAZU RDF Design principles

A work in progress...

The RDF in the RAZU e-depot is based on MDTO.
There are three levels of compliance to the RAZU RDF standard.

1. LDTO-core, based on MDTO, is oin essence a fork of MDTO and providing a new namespace.
2. LDTO-plus, builds on LDTO-core and provided the additional predicates and classes from other vocabularies in order to create semantically richer RDF.
3. LDTO-razu, build on the previous two, but provides additional restrictions to both.

The RAZU edepot requires level 3 compliance. A usecase for level 2 compliance validation is that it can be run without using SPARQL queries in the SHACL definitions. Level 1 compliance ensures an easy conversion path to MDTO metadata.


## General Design principles for RAZU RDF

- LDTO (and thus MDTO) provides the hierarchical backbone for the RDF.
- The LDTO hierarchy is provided only using ldto:isOnderdeelVan or ldto:isRepresentatieVan relations. The inverse relations are always implicit only.
- Contextual relations are provided by linking to RAZU maintained thesauri, unless the terms are in a consistently matching common external vocabulary.
- RAZU intends to enrich all terms in its concept schemes to one or more equivalent terms from the NDE network of terms, or to Wikidata entities.
- Semantical 'substructures' to ldto-entities are created as blank nodes (or skolems, when blanks are not supported by the toolset). 
- All RDF entities must have at least one rdf:type property. Providing multiple types is allowed.
- All blanks nodes should have a meaningfull rdfs:label.
- All triple objects should have a datatype (these might be implied, for example rdf:langstring or xsd:string in turtle RDF).
- The use of rdf:langstring is preferred above xsd:string (but current MDTO / LDTO requires xsd:string). 


### TODO's and open issues
- solve / describe issues with MDTO not liking langstrings even when we prefer them
- describe / explain inconstistency in how MDTO/ LDTO deals with inheritance.
- describe how ldto-core is different from MDTO, specifically in defaulting to URI's as a prefered method of referencing (iso of the Verwijzingsgegevens-structures) 


## Specific principles for LDTO entities

In addition to what MDTO and thus LDTO requires (LDTO-core), there are additional requirements for RAZU RDF entities.

- The ldto:aggreggatieniveau predicate is required for each Informatieobject and should point to a term in the "aggregatieniveau"-thesaurus (<https://data.razu.nl/id/aggregatieniveau/37b10081ed00e0e430c071ed04c99aee>).
- The ldto:classificatie predicate is required for each Informatieobject and should point to a term in the "soort"-thesaurus (<https://data.razu.nl/id/soort/bbc3a6702c26cc0f1ca33eb5e80c9d4a>).



## Additional principles for specific materals

TODO

### Principles for a newspaper collection

From a collection perspective, there is a single archive consisting of series, where each series aggregates a title. A series *is* not the title itself — the title is considered an abstract entity — but rather *concerns* a title, expressed via `schema:mainEntity`. The (abstract) bibliographic title is modelled as a `schema:Newspaper`. A series consists of file items (*archiefstukken*), each of which *concerns* an issue. These too are linked to the abstract bibliographic issue via `schema:mainEntity`, modelled as a `schema:PublicationIssue`.

Pages as such do not occur in the model. They are represented by files carrying a sequence number (`schema:position`) that indicates the order of the pages within the issue. For each page there may be multiple files, for example an ALTO-XML file, an image (the scan), and sometimes a second image format as well. Although a page does not occur as such in the RDF, it can still be identified by a URI: the URI of the issue followed by `#{page-number}`. This identifier can be useful, for example for page references in the Elasticsearch index.


### Principles for an archive with bouwvergunningen

See the README.md file in the bouwvergunningen directory for specific principles.






