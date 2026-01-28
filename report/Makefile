# Makefile for LaTeX project cleanup
# Usage: make clean, make veryclean, make clean-all

# Directories to clean
REPORT_DIR = "."
BUILD_DIR = _build

# Main targets
.PHONY: clean veryclean clean-all help list compile

# Default target
help:
	@echo "Available targets:"
	@echo "  clean      - Remove common LaTeX auxiliary files"
	@echo "  veryclean  - Remove all generated files except PDF"
	@echo "  clean-all  - Remove all generated files including PDF"
	@echo "  list       - List files that would be removed"
	@echo "  compile    - Clean and compile"

# Clean common auxiliary files
clean:
	@echo "Cleaning LaTeX auxiliary files..."
	find $(REPORT_DIR) -type f \( \
		-name "*.aux" -o \
		-name "*.bbl" -o \
		-name "*.blg" -o \
		-name "*.log" -o \
		-name "*.out" -o \
		-name "*.toc" -o \
		-name "*.lof" -o \
		-name "*.lot" -o \
		-name "*.fls" -o \
		-name "*.fdb_latexmk" -o \
		-name "*.synctex.gz" -o \
		-name "*.nav" -o \
		-name "*.snm" -o \
		-name "*.vrb" -o \
		-name "*.dvi" -o \
		-name "*.ps" -o \
		-name "*.bcf" -o \
		-name "*.run.xml" \
	\) -delete
	@echo "✓ Clean completed"

# Clean all generated files except PDF
veryclean: clean
	@echo "Removing extra generated files..."
	find $(REPORT_DIR) -type f \( \
		-name "*.glg" -o \
		-name "*.glo" -o \
		-name "*.gls" -o \
		-name "*.ist" -o \
		-name "*.alg" -o \
		-name "*.acr" -o \
		-name "*.acn" -o \
		-name "*.lol" -o \
		-name "*.idx" -o \
		-name "*.ilg" -o \
		-name "*.ind" -o \
		-name "*.brf" -o \
		-name "*.nlo" -o \
		-name "*.nls" -o \
		-name "*.ent" -o \
		-name "*.pyg" \
	\) -delete
	find $(REPORT_DIR) -name "*.thm" -delete
	find $(REPORT_DIR) -name "*Notes.bib" -delete
	@echo "✓ Very clean completed"

# Clean everything including PDF
clean-all: veryclean
	@echo "Removing PDF files..."
	find $(REPORT_DIR) -name "*.pdf" -delete
	rm -rf $(BUILD_DIR)
	@echo "✓ Complete cleanup done"

# List files that would be removed
list:
	@echo "Files that would be removed by 'clean':"
	find $(REPORT_DIR) -type f \( \
		-name "*.aux" -o \
		-name "*.bbl" -o \
		-name "*.blg" -o \
		-name "*.log" -o \
		-name "*.out" -o \
		-name "*.toc" -o \
		-name "*.lof" -o \
		-name "*.lot" -o \
		-name "*.fls" -o \
		-name "*.fdb_latexmk" -o \
		-name "*.synctex.gz" -o \
		-name "*.nav" -o \
		-name "*.snm" -o \
		-name "*.vrb" -o \
		-name "*.dvi" -o \
		-name "*.ps" -o \
		-name "*.bcf" -o \
		-name "*.run.xml" \
	\) -print
	@echo ""
	@echo "Files that would be removed by 'veryclean':"
	find $(REPORT_DIR) -type f \( \
		-name "*.glg" -o \
		-name "*.glo" -o \
		-name "*.gls" -o \
		-name "*.ist" -o \
		-name "*.alg" -o \
		-name "*.acr" -o \
		-name "*.acn" -o \
		-name "*.lol" -o \
		-name "*.idx" -o \
		-name "*.ilg" -o \
		-name "*.ind" -o \
		-name "*.brf" -o \
		-name "*.nlo" -o \
		-name "*.nls" -o \
		-name "*.ent" -o \
		-name "*.pyg" \
	\) -print

# Auto-clean on compilation
compile: clean
	cd $(REPORT_DIR) && pdflatex main.tex

