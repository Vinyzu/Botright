import logging
import os
import re
import warnings

from pkg_resources import Requirement as Req

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse


__version__ = "0.1.0"

logging.basicConfig(level=logging.WARNING)

VCS = ["git", "hg", "svn", "bzr"]


class Requirement(object):
    """
    This class is inspired from
    https://github.com/davidfischer/requirements-parser/blob/master/requirements/requirement.py#L30
    License: BSD
    """

    def __init__(self, line):
        self.line = line
        self.is_editable = False
        self.is_local_file = False
        self.is_specifier = False
        self.vcs = None
        self.name = None
        self.uri = None
        self.full_uri = None
        self.path = None
        self.revision = None
        self.scheme = None
        self.login = None
        self.extras = []
        self.specs = []

    def __repr__(self):
        return '<Requirement: "{0}">'.format(self.line)

    @classmethod
    def parse(cls, line, editable=False):
        """
        Parses a Requirement from an "editable" requirement which is either
        a local project path or a VCS project URI.
        See: pip/req.py:from_editable()
        :param line: an "editable" requirement
        :returns: a Requirement instance for the given line
        :raises: ValueError on an invalid requirement
        """
        if editable:
            req = cls("-e {0}".format(line))
            req.is_editable = True
        else:
            req = cls(line)

        url = urlparse(line)
        req.uri = None
        if url.scheme:
            req.scheme = url.scheme
            req.uri = url.scheme + "://" + url.netloc + url.path
            fragment = url.fragment.split(" ")[0].strip()
            req.name = fragment.split("egg=")[-1] or None
            req.path = url.path
            if fragment:
                req.uri += "#{}".format(fragment)
            if url.username or url.password:
                username = url.username or ""
                password = url.password or ""
                req.login = username + ":" + password
            if "@" in url.path:
                req.revision = url.path.split("@")[-1]

            for vcs in VCS:
                if req.uri.startswith(vcs):
                    req.vcs = vcs
            if req.scheme.startswith("file://"):
                req.is_local_file = True

        if not req.vcs and not req.is_local_file and "egg=" not in line:
            # This is a requirement specifier.
            # Delegate to pkg_resources and hope for the best
            req.is_specifier = True
            pkg_req = Req.parse(line)
            req.name = pkg_req.unsafe_name
            req.extras = list(pkg_req.extras)
            req.specs = pkg_req.specs
            if req.specs:
                req.specs = sorted(req.specs)

        return req


class Requirements:
    def __init__(self, requirements="requirements.txt", tests_requirements="requirements-test.txt"):
        self.requirements_path = requirements
        self.tests_requirements_path = tests_requirements

    def format_specifiers(self, requirement):
        return ", ".join(["{} {}".format(s[0], s[1]) for s in requirement.specs])

    @property
    def install_requires(self):
        dependencies = []
        for requirement in self.parse(self.requirements_path):
            if not requirement.is_editable and not requirement.uri and not requirement.vcs:
                full_name = requirement.name
                specifiers = self.format_specifiers(requirement)
                if specifiers:
                    full_name = "{} {}".format(full_name, specifiers)
                dependencies.append(full_name)
        for requirement in self.get_dependency_links():
            print(":: (base:install_requires) {}".format(requirement.name))
            dependencies.append(requirement.name)
        return dependencies

    @property
    def tests_require(self):
        dependencies = []
        for requirement in self.parse(self.tests_requirements_path):
            if not requirement.is_editable and not requirement.uri and not requirement.vcs:
                full_name = requirement.name
                specifiers = self.format_specifiers(requirement)
                if specifiers:
                    full_name = "{} {}".format(full_name, specifiers)
                print(":: (tests:tests_require) {}".format(full_name))
                dependencies.append(full_name)
        return dependencies

    @property
    def dependency_links(self):
        dependencies = []
        for requirement in self.parse(self.requirements_path):
            if requirement.uri or requirement.vcs or requirement.path:
                print(":: (base:dependency_links) {}".format(requirement.uri))
                dependencies.append(requirement.uri)
        return dependencies

    @property
    def dependencies(self):
        install_requires = self.install_requires
        dependency_links = self.dependency_links
        tests_require = self.tests_require
        if dependency_links:
            print("\n" "!! Some dependencies are linked to repository or local path.")
            print("!! You'll need to run pip with following option: " "`--process-dependency-links`" "\n")
        return {"install_requires": install_requires, "dependency_links": dependency_links, "tests_require": tests_require}

    def get_dependency_links(self):
        dependencies = []
        for requirement in self.parse(self.requirements_path):
            if requirement.uri or requirement.vcs or requirement.path:
                dependencies.append(requirement)
        return dependencies

    def parse(self, path=None):
        path = path or self.requirements_path
        path = os.path.abspath(path)
        base_directory = os.path.dirname(path)

        if not os.path.exists(path):
            warnings.warn("Requirements file: {} does not exists.".format(path))
            return

        with open(path) as requirements:
            for index, line in enumerate(requirements.readlines()):
                index += 1
                line = line.strip()
                if not line:
                    logging.debug("Empty line (line {} from {})".format(index, path))
                    continue
                elif line.startswith("#"):
                    logging.debug("Comments line (line {} from {})".format(index, path))
                elif line.startswith("-f") or line.startswith("--find-links") or line.startswith("-i") or line.startswith("--index-url") or line.startswith("--extra-index-url") or line.startswith("--no-index"):
                    warnings.warn("Private repos not supported. Skipping.")
                    continue
                elif line.startswith("-Z") or line.startswith("--always-unzip"):
                    warnings.warn("Unused option --always-unzip. Skipping.")
                    continue
                elif line.startswith("-r") or line.startswith("--requirement"):
                    logging.debug("Pining to another requirements file " "(line {} from {})".format(index, path))
                    for _line in self.parse(path=os.path.join(base_directory, line.split()[1])):
                        yield _line
                elif line.startswith("-e") or line.startswith("--editable"):
                    # Editable installs are either a local project path
                    # or a VCS project URI
                    yield Requirement.parse(re.sub(r"^(-e|--editable=?)\s*", "", line), editable=True)
                else:
                    logging.debug('Found "{}" (line {} from {})'.format(line, index, path))
                    yield Requirement.parse(line, editable=False)


r = Requirements(tests_requirements="")
