SPECFILE := $(PACKAGE).spec
SPECFILE_FILELIST := /^%files/,/^%pre/s,^%attr.*/\([^/]*\),\1,p
FILES := $(shell sed -ne '$(SPECFILE_FILELIST)' $(SPECFILE))
VERSION := $(shell sed -ne 's/^Version: \(.*\)/\1/p' $(SPECFILE))
RELEASE := $(shell sed -ne 's/^Release: \(.*\)/\1/p' $(SPECFILE))
NAME := $(PACKAGE)-$(VERSION)
FULLNAME := $(NAME)-$(RELEASE)
TARBALL := $(FULLNAME).tar.gz
RPM_BUILDDIR := .rpmbuild
CWD := $(shell pwd)

#
# we have to jump through hoops to make RPM work nicely
#
RPM_RC_SYS := /usr/lib/rpm/rpmrc:$(wildcard /usr/lib/rpm/redhat/rpmrc)
RPM_RC_USER := $(wildcard $(HOME)/.rpmrc)
RPM_RC_LOCAL := .rpmrc
RPM_RCFILES := $(subst ::,:,$(RPM_RC_SYS):$(RPM_RC_LOCAL):$(RPM_RC_USER))

# ask RPM what architecture it will build for
ARCH := $(shell rpm --showrc | sed -ne 's/^build arch.*: *\(.*\)/\1/p')

# find out what the standard list of macro files is
RPM_MACROS_SYS := $(shell rpm --showrc | \
	sed -ne 's,^macrofiles[^:]*: \(.*\):~.*,\1,p')
RPM_MACROS_LOCAL := .rpmmacros
RPM_MACROS_USER := $(wildcard $(HOME)/.rpmmacros)
RPM_MACROFILES := $(RPM_MACROS_SYS):$(RPM_MACROS_LOCAL):$(RPM_MACROS_USER)

LOCALFILES := $(RPM_RC_LOCAL) $(RPM_MACROS_LOCAL) $(RPM_BUILDDIR)

RPMFILE := $(FULLNAME).$(ARCH).rpm

tarball: $(TARBALL)

#
# the idiosyncracies of RPM building require that the tarball has files
# located in directory $(NAME), not $(FULLNAME)
#
$(TARBALL): $(FILES)
	@echo creating $@...
	@[ -d $(NAME) ] || ln -s . $(NAME)
	@tar czvf $(TARBALL) $(addprefix $(NAME)/,$^)
	@rm $(NAME)

rpm: $(RPMFILE)

$(RPMFILE): $(TARBALL) $(SPECFILE) $(LOCALFILES)
	rpmbuild --buildroot=$(CWD)/$(RPM_BUILDDIR)/tmp \
	--rcfile $(RPM_RCFILES) -bb $(SPECFILE)

$(RPM_RC_LOCAL):
	@echo 'macrofiles: $(RPM_MACROFILES)' >$@
	@echo created $@

$(RPM_MACROS_LOCAL):
	@exec >$@; \
	echo "%distribution PlanetLab"; \
	echo "%_fullname %{name}-%{version}-%{release}"; \
	echo "%_topdir $(CWD)"; \
	echo "%_sourcedir %{_topdir}"; \
	echo "%_builddir %{_topdir}/$(RPM_BUILDDIR)"; \
	echo "%_rpmdir %{_builddir}"
	@echo created $@

$(RPM_BUILDDIR):
	mkdir -p $(RPM_BUILDDIR)/tmp
	ln -s .. $(RPM_BUILDDIR)/$(ARCH)

rpm-config: $(LOCALFILES)
	@echo RPM_RCFILES=$(RPM_RCFILES)
	@echo RPM_MACROFILES=$(RPM_MACROFILES)
	@echo RPM_ARCH=$(ARCH)

rpm-clean:
	rm -f $(NAME) $(RPMFILE) $(TARBALL)
	rm -rf $(LOCALFILES)
