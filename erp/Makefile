SOURCES := $(shell echo src/*/__main__.py)
TARGETS := $(patsubst src/%.py,templates/%.template,$(patsubst src/%/__main__.py,templates/%.template,$(SOURCES)))

all: $(TARGETS)

clean:
		rm -f $(TARGETS)

# templates/%.template: src/%.py
# 	python $< > $@

templates/%.template: src/%/
	python $< > $@