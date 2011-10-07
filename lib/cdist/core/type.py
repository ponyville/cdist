# -*- coding: utf-8 -*-
#
# 2011 Steven Armstrong (steven-cdist at armstrong.cc)
# 2011 Nico Schottelius (nico-cdist at schottelius.org)
#
# This file is part of cdist.
#
# cdist is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# cdist is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with cdist. If not, see <http://www.gnu.org/licenses/>.
#
#

import os

import cdist


class Type(object):
    """Represents a cdist type.

    All interaction with types in cdist should be done through this class.
    Directly accessing an type through the file system from python code is 
    a bug.

    """

    @classmethod
    def list_types(cls, base_path):
        """Return a list of type instances"""
        for name in cls.list_type_names(base_path):
            yield cls(base_path, name)

    @classmethod
    def list_type_names(cls, base_path):
        """Return a list of type names"""
        return os.listdir(base_path)


    def __init__(self, base_path, name):
        self._base_path = base_path
        self.name = name
        self.manifest_path = os.path.join(self.name, "manifest")
        self.explorer_path = os.path.join(self.name, "explorer")
        self.manifest_path = os.path.join(self.name, "manifest")
        self.gencode_local_path = os.path.join(self.name, "gencode-local")
        self.gencode_remote_path = os.path.join(self.name, "gencode-remote")
        self.manifest_path = os.path.join(self.name, "manifest")

        self.transferred_explorers = False

        self.__explorers = None
        self.__required_parameters = None
        self.__optional_parameters = None


    def __repr__(self):
        return '<Type %s>' % self.name

    @property
    def is_singleton(self):
        """Check whether a type is a singleton."""
        return os.path.isfile(os.path.join(self.path, "singleton"))

    @property
    def is_install(self):
        """Check whether a type is used for installation (if not: for configuration)"""
        return os.path.isfile(os.path.join(self.path, "install"))

    @property
    def explorers(self):
        """Return a list of available explorers"""
        if not self.__explorers:
            try:
                self.__explorers = os.listdir(os.path.join(self.path, "explorer"))
            except EnvironmentError:
                # error ignored
                self.__explorers = []
        return self.__explorers

    @property
    def required_parameters(self):
        """Return a list of required parameters"""
        if not self.__required_parameters:
            parameters = []
            try:
                with open(os.path.join(self.path, "parameter", "required")) as fd:
                    for line in fd:
                        parameters.append(line.strip())
            except EnvironmentError:
                # error ignored
                pass
            finally:
                self.__required_parameters = parameters
        return self.__required_parameters

    @property
    def optional_parameters(self):
        """Return a list of optional parameters"""
        if not self.__optional_parameters:
            parameters = []
            try:
                with open(os.path.join(self.path, "parameter", "optional")) as fd:
                    for line in fd:
                        parameters.append(line.strip())
            except EnvironmentError:
                # error ignored
                pass
            finally:
                self.__optional_parameters = parameters
        return self.__optional_parameters
