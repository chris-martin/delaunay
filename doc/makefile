x=delaunay
latex=pdflatex -file-line-error -halt-on-error $(x).tex
chrome: $(x).pdf
	google-chrome $(x).pdf
$(x).pdf: $(x).tex chris.jpg
	$(latex) && $(latex)
evince: $(x).pdf
	evince $(x).pdf
