# Custom Makefile settings for ECOSIM

# Note these commands require ROBOT:
# https://robot.obolibrary.org/

# Source of truth for EcoSIM.
# This is a ROBOT template in a Google Sheet.
SRC_URL = 'https://docs.google.com/spreadsheets/d/1mS8VVtr-m24vZ7nQUtUbQrN8r-UBy3AwRzTfQsmwVL8/export?exportFormat=csv'

# Former source of truth for ecosim.owl.
# This is the BioPortal version of the ontology.
ECOSIM_BP_URL = 'https://data.bioontology.org/ontologies/ECOSIM/submissions/3/download?apikey=8b5b7825-538d-40e0-9e9e-5ab9274a9aeb'

# Retrieve the latest version of the ontology from BioPortal.
# This should not need to be done when using the sheet as the source of truth.
ecosim_temp.owl:
	curl -L -s $(ECOSIM_BP_URL) > $@

# This produces the spreadsheet-ready CSV version of the ontology.
# Here, ecosim_temp.owl is a copy of the ecosim.owl file,
# retrieved from BioPortal (see above).
# Starting with the ecosim.owl, export to csv.
# This should not need to be done when using the sheet as the source of truth.
# This makes two products first, then combines them.
# The product, ecosim_for_sheet.csv, is what should be placed in the
# sheet at the above URL.
ecosim_for_sheet.csv: ecosim_temp.owl
    # This makes the class list first, without subclasses
    # This includes object properties and annotation properties
	robot export --input $< --include "classes properties" --format csv --export classes.csv --header "IRI|oboInOwl:id|oboInOwl:id|oboInOwl:id|oboInOwl:inSubset|LABEL|obo:IAO_0000115|rdfs:comment|oboInOwl:hasRelatedSynonym|oboInOwl:hasExactSynonym|Type|oboInOwl:hasDbXref"
    # Then we get the specific subclasses by type
	robot query --input $< --query ../sparql/get-ecosim-subclasses.sparql sc.csv
    # Merge the classes.csv and sc.csv files
	python ../scripts/merge_csv.py classes.csv sc.csv $@
    # Process the CSV file to fix IDs and make other transformations
	python ../scripts/process_ecosim_csv.py --input $@ --output $@.processed && mv $@.processed $@
    # Create a file with the two header lines we need
	echo "ID,Label,EcoSIM Other Names,Category,EcoSIM Variable Name,Description,Comment,Related Synonyms,Exact Synonyms,Type,DbXrefs,has_units,qualifiers,attributes,measured_ins,measurement_ofs,contexts,Parents" > header.csv
	echo "ID,LABEL,A oio:hasRelatedSynonym SPLIT=|,AI oio:inSubset SPLIT=|,A oio:hasRelatedSynonym,A IAO:0000115,A rdfs:comment,A oio:hasRelatedSynonym SPLIT=|,A oio:hasExactSynonym SPLIT=|,TYPE,AI oio:hasDbXref SPLIT=|,AI ECOSIM:has_unit SPLIT=|,AI ECOSIM:Qualifier SPLIT=|,AI ECOSIM:Attribute SPLIT=|,AI ECOSIM:measured_in SPLIT=|,AI ECOSIM:measurement_of SPLIT=|,AI ECOSIM:Context SPLIT=|,SC % SPLIT=|" >> header.csv
    # Combine header with data, skipping the first line of $@ (which will be replaced)
	tail -n +2 $@ > $@.data && cat header.csv $@.data > $@.temp && mv $@.temp $@ && rm $@.data
    # Clean up
	rm header.csv classes.csv sc.csv

# This will retrieve the latest version of the ontology
# from the Google Sheet
ecosim-src.csv:
	curl -L -s $(SRC_URL) > $@

# Make a merge-ready OWL file from the CSV
components/ecosim-src.owl: ecosim-src.csv
	robot template \
	  --add-prefix 'ECOSIM: https://w3id.org/ecosim/ECOSIM_' \
	  --add-prefix 'oio: http://www.geneontology.org/formats/oboInOwl#' \
	  -t $< \
	  annotate --annotation-file ecosim-annotations.ttl \
	  -o $@

remove-old-input:
	rm -rf ecosim-src.csv
	rm -rf components/ecosim-src.owl