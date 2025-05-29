OBO = http://purl.obolibrary.org/obo
CORE = src/ontology/ecosim-core.obo
MAIN = src/ontology/ecosim.obo

release:
	cp src/ontology/ecosim.* .

%.owl: %.obo
	robot convert -i $< -o $@

%.db: %.owl
	runoak -i sqlite:$< terms

src/ontology/terms.txt: $(CORE)
	robot merge -i $< query -q src/queries/terms.rq $@

$(MAIN): $(CORE) src/ontology/generated.obo src/ontology/imports.owl src/ontology/terms.txt
	robot merge -i $< -i src/ontology/generated.obo filter -T src/ontology/terms.txt --trim true --signature false convert --check false -o $@



tmp/defs.kgcl.json:
	runoak --stacktrace -v -i llm:src/ontology/ecosim.db generate-definitions .all  -O json -o $@ --style-hints "Write definitions as if they come from an ontology of parameters for earth systems modeling."

index-ontology:
	curategpt view index -V oboformat -c ecosim --source-locator $(MAIN)

index-ontology-dragon:
	curategpt ontology index -c ont_ecosim -m openai: $(MAIN)

index-curated:
	curategpt view index -V oboformat -c curated --source-locator src/ontology/ecosim-curated.obo

tmp/dragon-inputs.yaml:
	./utils/obo2yamllines.pl $(CORE) > $@

tmp/dragon-output.yaml: tmp/dragon-inputs.yaml
	curategpt -v complete-multiple --model gpt-4 -c ont_curated $<  > $@.tmp && mv $@.tmp $@

tmp/dragon-output.obo.json: tmp/dragon-output.yaml
	curategpt view unwrap -V oaklib -c ont_ecosim $< -t json > $@

tmp/dragon-output.obo: tmp/dragon-output.obo.json
	runoak -v -i obograph:$< dump -O obo  > $@

tmp/candidate-MaterialEntity.txt:
	runoak -i simpleobo:src/ontology/generated.obo relationships -p ECOSIM:measured_in,ECOSIM:measurement_of .all | cut -f5| sort -u > $@

tmp/candidate-Context.txt:
	runoak -i simpleobo:src/ontology/generated.obo relationships -p ECOSIM:context .all | cut -f5| sort -u > $@

tmp/candidate-Attribute.txt:
	runoak -i simpleobo:src/ontology/generated.obo relationships -p ECOSIM:attribute .all | cut -f5| sort -u > $@

tmp/candidate-Qualifier.txt:
	runoak -i simpleobo:src/ontology/generated.obo relationships -p ECOSIM:qualifier .all | cut -f5| sort -u > $@

src/ontology/material-entity.obo: src/ontology/material-entity.csv
	robot template --prefix "ECOSIMCONCEPT: http://purl.obolibrary.org/obo/ECOSIMCONCEPT_" -vvv -t $< -o $@
src/ontology/attribute.obo: src/ontology/attribute.csv
	robot template --prefix "ECOSIMCONCEPT: http://purl.obolibrary.org/obo/ECOSIMCONCEPT_" -vvv -t $< -o $@

src/ontology/imports.owl: src/ontology/attribute.obo src/ontology/material-entity.obo
	robot merge $(patsubst %,-i %,$^) annotate -O $(OBO)/ecosim/imports.owl -o $@

include ecosim.Makefile
