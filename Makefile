# Local metadata generation. Optional: CI does this automatically.
# Requirements: dpkg-scanpackages (brew install dpkg), gzip, bzip2, python3.
# xz is optional; Packages.xz is skipped when missing.

PYTHON ?= python3
SCAN   ?= dpkg-scanpackages
ROOT   := .

DEBS := $(shell find debs -name '*.deb' 2>/dev/null)

all: Packages Packages.gz Packages.bz2 Packages.xz Release

Packages: $(DEBS)
	@if test -n "$(DEBS)"; then \
		$(SCAN) --multiversion debs /dev/null > Packages; \
	else \
		: > Packages; \
	fi

Packages.gz: Packages
	gzip -9c Packages > Packages.gz

Packages.bz2: Packages
	bzip2 -9c Packages > Packages.bz2

Packages.xz: Packages
	@if command -v xz >/dev/null 2>&1; then \
		xz -9c Packages > Packages.xz; \
	fi

Release: Packages Packages.gz Packages.bz2 Packages.xz
	$(PYTHON) scripts/gen-release.py --root $(ROOT)

clean:
	rm -f Packages Packages.gz Packages.bz2 Packages.xz Release

.PHONY: all clean