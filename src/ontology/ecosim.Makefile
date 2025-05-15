# Custom Makefile settings for ECOSIM

# Note these commands require ROBOT:
# https://robot.obolibrary.org/

# Source of truth for EcoSIM.
# This is a ROBOT template.
SRC_URL = 'https://docs.google.com/spreadsheets/d/1mS8VVtr-m24vZ7nQUtUbQrN8r-UBy3AwRzTfQsmwVL8/export?exportFormat=csv'

# starting with the ecosim.owl, export to csv
# This should not need to be done when using the sheet as the source of truth
# This makes two products first, then combines them
# The product, ecosim_for_sheet.csv, is what should be placed in the
# sheet at the above URL.
ecosim_for_sheet.csv: ecosim_temp.owl
	# This makes the class list first, without subclasses
	robot export --input $< --format csv --export classes.csv --header "IRI|oboInOwl:id|oboInOwl:inSubset|LABEL|oboInOwl:hasExactSynonym|oboInOwl:hasRelatedSynonym|rdfs:comment|Type|oboInOwl:hasDbXref|obo:IAO_0000115"
	# Then we get the specific subclasses by type
	robot query --input $< --query ../sparql/get-ecosim-subclasses.sparql sc.csv
	# Merge the classes.csv and sc.csv files
	python ../scripts/merge_csv.py classes.csv sc.csv $@ --remove-first-column
	# Modify header to include names and ROBOT template commands we will use later
	sed '1i ID,Category,Label,Exact Synonyms,Related Synonyms,Comment,Type,DbXrefs,Description,has_units,qualifiers,attributes,measured_ins,measurement_ofs,contexts' $@ > $@.temp && mv $@.temp $@
	# Clean up
	rm classes.csv sc.csv

# This will retrieve the latest version of the ontology
# from the Google Sheet
ecosim-src.csv:
	curl -L -s $(SRC_URL) > $@

# Make a merge-ready OWL file from the CSV
components/ecosim-src.owl: ecosim-src.csv
	robot template \
	  --add-prefix 'ECOSIM: https://w3id.org/ecosim/' \
	  --add-prefix 'oboInOwl: http://www.geneontology.org/formats/oboInOwl#' \
	  -t $< \
	  annotate --annotation-file ecosim-annotations.ttl \
	  -o $@