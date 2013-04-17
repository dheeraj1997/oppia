# coding: utf-8
#
# Copyright 2013 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Model for an Oppia exploration."""

__author__ = 'Sean Lip'

import os

from base_model import BaseModel
import feconf
import logging
from models.image import Image
from models.parameter import Parameter
from state import State
import utils

from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.ext.db import BadValueError


# TODO(sll): Add an anyone-can-edit mode.
class Exploration(BaseModel):
    """An exploration (which is made up of several states)."""
    # The category this exploration belongs to.
    category = ndb.StringProperty(required=True)
    # What this exploration is called.
    title = ndb.StringProperty(default='New exploration')
    # The state which forms the start of this exploration.
    init_state = ndb.KeyProperty(kind=State, required=True)
    # The list of states this exploration consists of. This list may not be
    # empty.
    states = ndb.KeyProperty(kind=State, repeated=True)
    # The list of parameters associated with this exploration.
    parameters = ndb.LocalStructuredProperty(Parameter, repeated=True)
    # Whether this exploration is publicly viewable.
    is_public = ndb.BooleanProperty(default=False)
    # The id for the image to show as a preview of the exploration.
    image_id = ndb.StringProperty()
    # List of users who can edit this exploration. If the exploration is a demo
    # exploration, the list is empty. Otherwise, the first element is the
    # original creator of the exploration.
    editors = ndb.UserProperty(repeated=True)

    def _has_state_named(self, state_name):
        """Checks if a state with the given name exists in this exploration."""
        state = State.query(ancestor=self.key).filter(
            State.name == state_name).count(limit=1)
        return bool(state)

    def _pre_put_hook(self):
        """Validates the exploration before it is put into the datastore."""
        if not self.states:
            raise BadValueError('This exploration does not have any states.')
        if not self.is_demo_exploration() and not self.editors:
            raise BadValueError('This exploration does not have any editors.')

    @classmethod
    def create(cls, user, title, category, exploration_id=None,
               init_state_name='Activity 1', image_id=None):
        """Creates and returns a new exploration."""
        # Generate a new exploration id, if one wasn't passed in.
        exploration_id = exploration_id or cls.get_new_id(title)

        # Temporarily create a fake initial state key.
        state_id = State.get_new_id(init_state_name)
        fake_state_key = ndb.Key(Exploration, exploration_id, State, state_id)

        # Note that demo explorations do not have owners, so user may be None.
        exploration = cls(
            id=exploration_id, title=title, init_state=fake_state_key,
            category=category, image_id=image_id, states=[fake_state_key],
            editors=[user] if user else [])
        exploration.put()

        # Finally, create the initial state and check that it has the right key.
        new_init_state = State.create(
            exploration, init_state_name, state_id=state_id)
        assert fake_state_key == new_init_state.key

        return exploration

    @classmethod
    def get(cls, exploration_id, strict=True):
        """Gets an exploration by id. Fails noisily if strict == True."""
        exploration = cls.get_by_id(exploration_id)
        if strict and not exploration:
            raise Exception('Exploration id %s not found' % exploration_id)
        return exploration

    def delete(self):
        """Deletes an exploration."""
        for state_key in self.states:
            state_key.delete()
        self.key.delete()

    def is_editable_by(self, user):
        """Checks whether the given user has rights to edit this exploration."""
        return users.is_current_user_admin() or user in self.editors

    @classmethod
    def get_viewable_explorations(cls, user):
        """Returns a list of explorations viewable by a given user."""
        return cls.query().filter(
            ndb.OR(cls.is_public == True, cls.editors == user)
        )

    def add_state(self, state_name):
        """Adds a new state, and returns it."""
        if self._has_state_named(state_name):
            raise Exception('Duplicate state name %s' % state_name)

        state = State.create(self, state_name)
        self.states.append(state.key)
        self.put()

        return state

    def rename_state(self, state, new_state_name):
        """Renames a state of this exploration."""
        if state.name == new_state_name:
            return

        if self._has_state_named(new_state_name):
            raise Exception('Duplicate state name: %s' % new_state_name)

        state.name = new_state_name
        state.put()

    @classmethod
    def create_from_yaml(
        cls, yaml_file, user, title, category, exploration_id=None,
            image_id=None):
        """Creates an exploration from a YAML file."""
        init_state_name = yaml_file[:yaml_file.index(':\n')]
        if not init_state_name or '\n' in init_state_name:
            raise Exception('Invalid YAML file: the name of the initial state '
                            'should be left-aligned on the first line and '
                            'followed by a colon')

        exploration = cls.create(
            user, title, category, exploration_id=exploration_id,
            init_state_name=init_state_name, image_id=image_id)

        init_state = State.get_by_name(init_state_name, exploration)

        try:
            exploration_dict = utils.dict_from_yaml(yaml_file)
            state_list = []

            for state_name, state_description in exploration_dict.iteritems():
                state = (init_state if state_name == init_state_name
                         else exploration.add_state(state_name))
                state_list.append({'state': state, 'desc': state_description})

            for index, state in enumerate(state_list):
                State.modify_using_dict(
                    exploration, state['state'], state['desc'])
        except Exception:
            exploration.delete()
            raise

        return exploration

    def as_yaml(self):
        """Returns a YAML version of the exploration."""
        init_dict = {}
        others_dict = {}

        for state_key in self.states:
            state = state_key.get()
            state_internals = state.internals_as_dict(human_readable_dests=True)

            if self.init_state.get().id == state.id:
                init_dict[state.name] = state_internals
            else:
                others_dict[state.name] = state_internals

        result = utils.yaml_from_dict(init_dict)
        result += utils.yaml_from_dict(others_dict) if others_dict else ''
        return result

    def is_demo_exploration(self):
        """Checks if the exploration is one of the demo explorations."""
        if not self.id.isdigit():
            return False

        id_int = int(self.id)
        return id_int >= 0 and id_int < len(feconf.DEMO_EXPLORATIONS)

    @classmethod
    def load_demo_explorations(cls):
        """Initializes the demo explorations."""
        for index, exploration in enumerate(feconf.DEMO_EXPLORATIONS):
            assert len(exploration) in [3, 4], (
                'Invalid format for demo exploration: %s' % exploration)

            yaml_filename = '%s.yaml' % exploration[0]
            yaml_file = utils.get_file_contents(
                os.path.join(feconf.SAMPLE_EXPLORATIONS_DIR, yaml_filename))

            title = exploration[1]
            category = exploration[2]
            image_filename = exploration[3] if len(exploration) == 4 else None

            image_id = None
            if image_filename:
                with open(os.path.join(
                        feconf.SAMPLE_IMAGES_DIR, image_filename)) as f:
                    raw_image = f.read()
                image_id = Image.create(raw_image)

            exploration = cls.create_from_yaml(
                yaml_file=yaml_file, user=None, title=title, category=category,
                exploration_id=str(index), image_id=image_id)
            exploration.is_public = True
            exploration.put()

    @classmethod
    def delete_demo_explorations(cls):
        """Deletes the demo explorations."""
        exploration_list = []
        for int_id in range(len(feconf.DEMO_EXPLORATIONS)):
            exploration = cls.get(str(int_id), strict=False)
            if not exploration:
                # This exploration does not exist, so it cannot be deleted.
                logging.info('No exploration with id %s found.' % int_id)
            else:
                exploration_list.append(exploration)

        for exploration in exploration_list:
            exploration.delete()
