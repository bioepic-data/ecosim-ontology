# BERVO - Biological and Environmental Research Variable Ontology

(Formerly the EcoSIM Ontology)

**EXPERIMENTAL**

## Editing BERVO

The source of truth for BERVO terms is here: https://docs.google.com/spreadsheets/d/1mS8VVtr-m24vZ7nQUtUbQrN8r-UBy3AwRzTfQsmwVL8/edit?usp=sharing

All terms are preceded by the BERVO: prefix.

## Methods

See also [this slide deck](https://docs.google.com/presentation/d/1W6FHsfv1p4Ko_RVKFgrVg2ruJnZwBW3M9dKoz4HR7n8/edit#slide=id.p)

### Seeding of initial parameter list

chatgpt ADA was used to create a program to iterate through the bervo fortran codebase and generate an obo format file of all parameter codes plus their names.

IDs of the form `BERVO:<CODE>` were created

Note: in future these may be translated to numeric IDs but for now the codes are convenient

### Generation of definitions

The OAK generate-definitions command was used to generate definitions for all terms

### Generation of grouping classes

Each parameter was organized into a grouping class.

We used Claude due to the large context window. A csv of all CODE-label pairs were uploaded to Claude, Claude then suggested groupings for these.
These were examined in text format, we then asked Claude to convert to OBO format.

### Inferring linkages to other concepts

We curated a handful of OBO stanzas where we linked each parameter to other concepts.

This was loaded into a curategpt database, to serve as in-context examples.

