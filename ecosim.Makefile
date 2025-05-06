# Custom Makefile settings for ECOSIM

# starting with the ecosim.owl, export to csv
ecosim.csv: ecosim.owl
	robot export --input $< --format csv --export $@ --header "oboInOwl:id|oboInOwl:inSubset|LABEL|oboInOwl:hasExactSynonym|oboInOwl:hasRelatedSynonym|rdfs:comment|SubClass Of|Type|oboInOwl:hasDbXref|obo:IAO_0000115"