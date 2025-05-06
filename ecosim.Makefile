# Custom Makefile settings for ECOSIM

# Note these commands require ROBOT:
# https://robot.obolibrary.org/

# Source of truth for EcoSIM.
# This is a ROBOT template.
SRC_URL = 'https://docs.google.com/spreadsheets/d/1mS8VVtr-m24vZ7nQUtUbQrN8r-UBy3AwRzTfQsmwVL8/export?exportFormat=csv'

# starting with the ecosim.owl, export to csv
# This should not need to be done when using the sheet as the source of truth
ecosim_direct.csv: ecosim.owl
	robot export --input $< --format csv --export $@ --header "oboInOwl:id|oboInOwl:inSubset|LABEL|oboInOwl:hasExactSynonym|oboInOwl:hasRelatedSynonym|rdfs:comment|SubClass Of|Type|oboInOwl:hasDbXref|obo:IAO_0000115"

# This will retrieve the latest version of the ontology
# from the Google Sheet
ecosim.csv:
	curl -L -s $(SRC_URL) > $@