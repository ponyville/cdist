# -*- coding: utf-8 -*-
#
# 2010-2011 Steven Armstrong (steven-cdist at armstrong.cc)
# 2012 Nico Schottelius (nico-cdist at schottelius.org)
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
import shutil

from cdist import test
from cdist import core

import cdist

import os.path as op
my_dir = op.abspath(op.dirname(__file__))
fixtures = op.join(my_dir, 'fixtures')
object_base_path = op.join(fixtures, 'object')
type_base_path = op.join(fixtures, 'type')

class ObjectClassTestCase(test.CdistTestCase):

    def test_list_object_names(self):
        found_object_names = sorted(list(core.CdistObject.list_object_names(object_base_path)))
        expected_object_names = sorted([
            '__first/child',
            '__first/dog',
            '__first/man',
            '__first/woman',
            '__second/on-the',
            '__second/under-the',
            '__third/moon'])
        self.assertEqual(found_object_names, expected_object_names)

    def test_list_type_names(self):
        type_names = list(cdist.core.CdistObject.list_type_names(object_base_path))
        self.assertEqual(type_names, ['__first', '__second', '__third'])

    def test_list_objects(self):
        objects = list(core.CdistObject.list_objects(object_base_path, type_base_path))
        objects_expected = [
            core.CdistObject(core.CdistType(type_base_path, '__first'), object_base_path, 'man'),
            core.CdistObject(core.CdistType(type_base_path, '__second'), object_base_path, 'on-the'),
            core.CdistObject(core.CdistType(type_base_path, '__third'), object_base_path, 'moon'),
        ]
        self.assertEqual(objects, objects_expected)


class ObjectIdTestCase(test.CdistTestCase):
    def test_object_id_contains_double_slash(self):
        cdist_type = core.CdistType(type_base_path, '__third')
        illegal_object_id = '/object_id//may/not/contain/double/slash'
        with self.assertRaises(core.IllegalObjectIdError):
            core.CdistObject(cdist_type, object_base_path, illegal_object_id)

    def test_object_id_contains_object_marker(self):
        cdist_type = core.CdistType(type_base_path, '__third')
        illegal_object_id = 'object_id/may/not/contain/%s/anywhere' % core.OBJECT_MARKER
        with self.assertRaises(core.IllegalObjectIdError):
            core.CdistObject(cdist_type, object_base_path, illegal_object_id)

    def test_object_id_contains_object_marker_string(self):
        cdist_type = core.CdistType(type_base_path, '__third')
        illegal_object_id = 'object_id/may/contain_%s_in_filename' % core.OBJECT_MARKER
        core.CdistObject(cdist_type, object_base_path, illegal_object_id)
        # if we get here, the test passed


class ObjectTestCase(test.CdistTestCase):

    def setUp(self):
        self.cdist_type = core.CdistType(type_base_path, '__third')
        self.cdist_object = core.CdistObject(self.cdist_type, object_base_path, 'moon') 

    def tearDown(self):
        self.cdist_object.changed = False
        self.cdist_object.prepared = False
        self.cdist_object.ran = False
        self.cdist_object.source = []
        self.cdist_object.code_local = ''
        self.cdist_object.code_remote = ''
        self.cdist_object.state = ''

    def test_name(self):
        self.assertEqual(self.cdist_object.name, '__third/moon')

    def test_object_id(self):
        self.assertEqual(self.cdist_object.object_id, 'moon')

    def test_path(self):
        self.assertEqual(self.cdist_object.path, '__third/moon/.cdist')

    def test_absolute_path(self):
        self.assertEqual(self.cdist_object.absolute_path, os.path.join(object_base_path, '__third/moon/.cdist'))

    def test_code_local_path(self):
        self.assertEqual(self.cdist_object.code_local_path, '__third/moon/.cdist/code-local')

    def test_code_remote_path(self):
        self.assertEqual(self.cdist_object.code_remote_path, '__third/moon/.cdist/code-remote')

    def test_parameter_path(self):
        self.assertEqual(self.cdist_object.parameter_path, '__third/moon/.cdist/parameter')

    def test_explorer_path(self):
        self.assertEqual(self.cdist_object.explorer_path, '__third/moon/.cdist/explorer')

    def test_parameters(self):
        expected_parameters = {'planet': 'Saturn', 'name': 'Prometheus'}
        self.assertEqual(self.cdist_object.parameters, expected_parameters)

    def test_explorers(self):
        self.assertEqual(self.cdist_object.explorers, {})

    # FIXME: actually testing fsproperty.DirectoryDictProperty here, move to their own test case
    def test_explorers_assign_dict(self):
        expected = {'first': 'foo', 'second': 'bar'}
        # when set, written to file
        self.cdist_object.explorers = expected
        object_explorer_path = os.path.join(self.cdist_object.base_path, self.cdist_object.explorer_path)
        self.assertTrue(os.path.isdir(object_explorer_path))
        # when accessed, read from file
        self.assertEqual(self.cdist_object.explorers, expected)
        # remove dynamically created folder
        self.cdist_object.explorers = {}
        os.rmdir(os.path.join(self.cdist_object.base_path, self.cdist_object.explorer_path))

    # FIXME: actually testing fsproperty.DirectoryDictProperty here, move to their own test case
    def test_explorers_assign_key_value(self):
        expected = {'first': 'foo', 'second': 'bar'}
        object_explorer_path = os.path.join(self.cdist_object.base_path, self.cdist_object.explorer_path)
        for key,value in expected.items():
            # when set, written to file
            self.cdist_object.explorers[key] = value
            self.assertTrue(os.path.isfile(os.path.join(object_explorer_path, key)))
        # when accessed, read from file
        self.assertEqual(self.cdist_object.explorers, expected)
        # remove dynamically created folder
        self.cdist_object.explorers = {}
        os.rmdir(os.path.join(self.cdist_object.base_path, self.cdist_object.explorer_path))

    def test_requirements(self):
        expected = []
        self.assertEqual(list(self.cdist_object.requirements), expected)

    def test_changed(self):
        self.assertFalse(self.cdist_object.changed)

    def test_changed_after_changing(self):
        self.cdist_object.changed = True
        self.assertTrue(self.cdist_object.changed)

    def test_state(self):
        self.assertEqual(self.cdist_object.state, '')

    def test_state_prepared(self):
        self.cdist_object.state = core.CdistObject.STATE_PREPARED
        self.assertEqual(self.cdist_object.state, core.CdistObject.STATE_PREPARED)

    def test_state_running(self):
        self.cdist_object.state = core.CdistObject.STATE_RUNNING
        self.assertEqual(self.cdist_object.state, core.CdistObject.STATE_RUNNING)

    def test_state_done(self):
        self.cdist_object.state = core.CdistObject.STATE_DONE
        self.assertEqual(self.cdist_object.state, core.CdistObject.STATE_DONE)

    def test_source(self):
        self.assertEqual(list(self.cdist_object.source), [])

    def test_source_after_changing(self):
        self.cdist_object.source = ['/path/to/manifest']
        self.assertEqual(list(self.cdist_object.source), ['/path/to/manifest'])

    def test_code_local(self):
        self.assertEqual(self.cdist_object.code_local, '')

    def test_code_local_after_changing(self):
        self.cdist_object.code_local = 'Hello World'
        self.assertEqual(self.cdist_object.code_local, 'Hello World')

    def test_code_remote(self):
        self.assertEqual(self.cdist_object.code_remote, '')

    def test_code_remote_after_changing(self):
        self.cdist_object.code_remote = 'Hello World'
        self.assertEqual(self.cdist_object.code_remote, 'Hello World')

    def test_object_from_name(self):
        self.cdist_object.code_remote = 'Hello World'
        other_name = '__first/man'
        other_object = self.cdist_object.object_from_name(other_name)
        self.assertTrue(isinstance(other_object, core.CdistObject))
        self.assertEqual(other_object.cdist_type.name, '__first')
        self.assertEqual(other_object.object_id, 'man')



class ObjectResolveRequirementsTestCase(test.CdistTestCase):

    def setUp(self):
        self.objects = list(core.CdistObject.list_objects(object_base_path, type_base_path))
        self.object_index = dict((o.name, o) for o in self.objects)
        self.object_names = [o.name for o in self.objects]

        print(self.objects)

        self.cdist_type = core.CdistType(type_base_path, '__third')
        self.cdist_object = core.CdistObject(self.cdist_type, object_base_path, 'moon') 

    def tearDown(self):
        for o in self.objects:
            o.requirements = []

    def test_find_requirements_by_name_string(self):
        """Check that resolving requirements by name works (require all objects)"""
        requirements = self.object_names

        self.cdist_object.requirements = requirements

        found_requirements = sorted(self.cdist_object.find_requirements_by_name(self.cdist_object.requirements))
        expected_requirements = sorted(self.objects)

        self.assertEqual(found_requirements, expected_requirements)

    def test_find_requirements_by_name_pattern(self):
        """Test whether pattern matching on requirements works"""

        # Matches all objects in the end
        requirements = ['__first/*', '__second/*-the', '__third/moon']

        self.cdist_object.requirements = requirements

        expected_requirements = sorted(self.objects)
        found_requirements = sorted(self.cdist_object.find_requirements_by_name(self.cdist_object.requirements))

        self.assertEqual(expected_requirements, found_requirements)

    def test_dependency_resolution(self):
        first_man = self.object_index['__first/man']
        second_on_the = self.object_index['__second/on-the']
        third_moon = self.object_index['__third/moon']
        first_man.requirements = [second_on_the.name]
        second_on_the.requirements = [third_moon.name]

        # FIXME :-)
        self.assertTrue(False)
#        self.assertEqual(
#            self.dependency_resolver.dependencies['__first/man'],
#            [third_moon, second_on_the, first_man]
#        )

    def test_requirement_not_found(self):
        first_man = self.object_index['__first/man']
        first_man.requirements = ['__does/not/exist']
        with self.assertRaises(core.cdist_object.RequirementNotFoundError):
            first_man.find_requirements_by_name(first_man.requirements)

