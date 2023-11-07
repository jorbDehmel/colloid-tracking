# This file is used for the generation of the attached .pdf files.
# You should not need to use this.

all:	filter_overview.pdf project_overview.pdf

%.pdf:	%.md
	pandoc $^ -o $@

clean:
	rm *.pdf
