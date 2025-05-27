# Custom Makefile settings for ECOSIM

# Note these commands require ROBOT:
# https://robot.obolibrary.org/

# Source of truth for EcoSIM.
# This is a ROBOT template in a Google Sheet.
SRC_URL = 'https://docs.google.com/spreadsheets/d/1mS8VVtr-m24vZ7nQUtUbQrN8r-UBy3AwRzTfQsmwVL8/export?exportFormat=csv'

# Source of truth for ecosim.owl.
# This is the BioPortal version of the ontology.
ECOSIM_BP_URL = 'https://data.bioontology.org/ontologies/ECOSIM/submissions/3/download?apikey=8b5b7825-538d-40e0-9e9e-5ab9274a9aeb'

# Retrieve the latest version of the ontology from BioPortal.
# This should not need to be done when using the sheet as the source of truth.
ecosim_temp.owl:
	curl -L -s $(ECOSIM_BP_URL) > $@

# This produces the spreadsheet-ready CSV version of the ontology.
# Here, ecosim_temp.owl is a copy of the ecosim.owl file,
# retrieved from BioPortal (see above).
# starting with the ecosim.owl, export to csv
# This should not need to be done when using the sheet as the source of truth
# This makes two products first, then combines them.
# It also places all ECOSIMCONCEPT classes in their own file,
# as we want them to be more static and will merge them later.
# The product, ecosim_for_sheet.csv, is what should be placed in the
# sheet at the above URL.
ecosim_for_sheet.csv: ecosim_temp.owl
    # Get the set of all ECOSIMCONCEPT classes
	robot query --input $< --query ../sparql/ecosim_concepts.sparql ecosim_concepts.txt
    # Extract the ECOSIMCONCEPT classes into a separate file
	robot extract --method STAR --input $< --term-file ecosim_concepts.txt --output ecosim_concepts.owl
    # This makes the class list first, without subclasses
	robot export --input $< --format csv --export classes.csv --header "IRI|oboInOwl:id|oboInOwl:inSubset|LABEL|oboInOwl:hasExactSynonym|oboInOwl:hasRelatedSynonym|rdfs:comment|Type|oboInOwl:hasDbXref|obo:IAO_0000115"
    # Then we get the specific subclasses by type
	robot query --input $< --query ../sparql/get-ecosim-subclasses.sparql sc.csv
    # Merge the classes.csv and sc.csv files
	python ../scripts/merge_csv.py classes.csv sc.csv $@ --remove-first-column
    # Create a file with the two header lines we need
	echo "ID,Category,Label,Exact Synonyms,Related Synonyms,Comment,Type,DbXrefs,Description,has_units,qualifiers,attributes,measured_ins,measurement_ofs,contexts" > header.csv
	echo "ID,AI oio:inSubset SPLIT=|,LABEL,A oio:hasExactSynonym SPLIT=|,A oio:hasRelatedSynonym SPLIT=|,A rdfs:comment,TYPE,>AI oio:hasDbXref SPLIT=|,A IAO:0000115,A ECOSIM:has_unit SPLIT=|,A ECOSIMCONCEPT:Qualifier SPLIT=|,A ECOSIMCONCEPT:Attribute SPLIT=|,A ECOSIM:measured_in SPLIT=|,A ECOSIM:measurement_of SPLIT=|,A ECOSIMCONCEPT:Context SPLIT=|" >> header.csv
    # Combine header with data, skipping the first line of $@ (which will be replaced)
	tail -n +2 $@ > $@.data && cat header.csv $@.data > $@.temp && mv $@.temp $@ && rm $@.data
	rm header.csv
    # Remove all lines with ECOSIMCONCEPT classes
	grep -v 'ECOSIMCONCEPT' $@ > $@.temp && mv $@.temp $@
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
