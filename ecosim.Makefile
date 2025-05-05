# Custom Makefile settings for ECOSIM

# starting with the ecosim.owl, export to csv
ecosim.csv: ecosim.owl
	robot export --input $< --format csv --export $@ --header "oboInOwl:id|LABEL|SYNONYMS|SubClass Of|Type|obo:IAO_0000115"