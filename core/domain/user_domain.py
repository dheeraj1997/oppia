# coding: utf-8
#
# Copyright 2014 The Oppia Authors. All Rights Reserved.
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

"""Domain objects for user."""

from __future__ import absolute_import  # pylint: disable=import-only-modules
from __future__ import unicode_literals  # pylint: disable=import-only-modules

from core.platform import models
import feconf
import python_utils
import utils

(user_models,) = models.Registry.import_models([models.NAMES.user])


class UserGlobalPrefs(python_utils.OBJECT):
    """Domain object for user global email preferences.

    Attributes:
        can_receive_email_updates: bool. Whether the user can receive
            email updates.
        can_receive_editor_role_email: bool. Whether the user can receive
            emails notifying them of role changes.
        can_receive_feedback_message_email: bool. Whether the user can
            receive emails when users submit feedback to their explorations.
        can_receive_subscription_email: bool. Whether the user can receive
             subscription emails notifying them about new explorations.
    """

    def __init__(
            self, can_receive_email_updates, can_receive_editor_role_email,
            can_receive_feedback_message_email,
            can_receive_subscription_email):
        """Constructs a UserGlobalPrefs domain object.

        Args:
            can_receive_email_updates: bool. Whether the user can receive
                email updates.
            can_receive_editor_role_email: bool. Whether the user can receive
                emails notifying them of role changes.
            can_receive_feedback_message_email: bool. Whether the user can
                receive emails when users submit feedback to their explorations.
            can_receive_subscription_email: bool. Whether the user can receive
                subscription emails notifying them about new explorations.
        """
        self.can_receive_email_updates = can_receive_email_updates
        self.can_receive_editor_role_email = can_receive_editor_role_email
        self.can_receive_feedback_message_email = ( # pylint: disable=invalid-name
            can_receive_feedback_message_email)
        self.can_receive_subscription_email = can_receive_subscription_email

    @classmethod
    def create_default_prefs(cls):
        """Returns UserGlobalPrefs with default attributes."""
        return cls(
            feconf.DEFAULT_EMAIL_UPDATES_PREFERENCE,
            feconf.DEFAULT_EDITOR_ROLE_EMAIL_PREFERENCE,
            feconf.DEFAULT_FEEDBACK_MESSAGE_EMAIL_PREFERENCE,
            feconf.DEFAULT_SUBSCRIPTION_EMAIL_PREFERENCE)


class UserExplorationPrefs(python_utils.OBJECT):
    """Domain object for user exploration email preferences.

    Attributes:
        mute_feedback_notifications: bool. Whether the given user has muted
            feedback emails.
        mute_suggestion_notifications: bool. Whether the given user has
            muted suggestion emails.
    """

    def __init__(
            self, mute_feedback_notifications, mute_suggestion_notifications):
        """Constructs a UserExplorationPrefs domain object.

        Args:
            mute_feedback_notifications: bool. Whether the given user has muted
                feedback emails.
            mute_suggestion_notifications: bool. Whether the given user has
                muted suggestion emails.
        """
        self.mute_feedback_notifications = mute_feedback_notifications
        self.mute_suggestion_notifications = mute_suggestion_notifications

    @classmethod
    def create_default_prefs(cls):
        """Returns UserExplorationPrefs with default attributes."""
        return cls(
            feconf.DEFAULT_FEEDBACK_NOTIFICATIONS_MUTED_PREFERENCE,
            feconf.DEFAULT_SUGGESTION_NOTIFICATIONS_MUTED_PREFERENCE)

    def to_dict(self):
        """Return dictionary representation of UserExplorationPrefs.

        Returns:
            dict. The keys of the dict are:
                'mute_feedback_notifications': bool. Whether the given user has
                    muted feedback emails.
                'mute_suggestion_notifications': bool. Whether the given user
                    has muted suggestion emails.
        """
        return {
            'mute_feedback_notifications': self.mute_feedback_notifications,
            'mute_suggestion_notifications': self.mute_suggestion_notifications
        }


class ExpUserLastPlaythrough(python_utils.OBJECT):
    """Domain object for an exploration last playthrough model."""

    def __init__(
            self, user_id, exploration_id, last_played_exp_version,
            last_updated, last_played_state_name):
        self.id = '%s.%s' % (user_id, exploration_id)
        self.user_id = user_id
        self.exploration_id = exploration_id
        self.last_played_exp_version = last_played_exp_version
        self.last_updated = last_updated
        self.last_played_state_name = last_played_state_name

    def update_last_played_information(
            self, last_played_exp_version, last_played_state_name):
        """Updates the last playthrough information of the user.

        Args:
            last_played_exp_version: int. The version of the exploration that
                was played by the user.
            last_played_state_name: str. The name of the state at which the
                learner left the exploration.
        """
        self.last_played_exp_version = last_played_exp_version
        self.last_played_state_name = last_played_state_name


class IncompleteActivities(python_utils.OBJECT):
    """Domain object for the incomplete activities model."""

    def __init__(
            self, user_id, exploration_ids, collection_ids):
        self.id = user_id
        self.exploration_ids = exploration_ids
        self.collection_ids = collection_ids

    def add_exploration_id(self, exploration_id):
        """Adds the exploration id to the list of incomplete exploration ids."""
        self.exploration_ids.append(exploration_id)

    def remove_exploration_id(self, exploration_id):
        """Removes the exploration id from the list of incomplete exploration
        ids.
        """
        self.exploration_ids.remove(exploration_id)

    def add_collection_id(self, collection_id):
        """Adds the collection id to the list of incomplete collection ids."""
        self.collection_ids.append(collection_id)

    def remove_collection_id(self, collection_id):
        """Removes the collection id from the list of incomplete collection
        ids.
        """
        self.collection_ids.remove(collection_id)


class CompletedActivities(python_utils.OBJECT):
    """Domain object for the activities completed by learner model."""

    def __init__(
            self, user_id, exploration_ids, collection_ids):
        self.id = user_id
        self.exploration_ids = exploration_ids
        self.collection_ids = collection_ids

    def add_exploration_id(self, exploration_id):
        """Adds the exploration id to the list of completed exploration ids."""
        self.exploration_ids.append(exploration_id)

    def remove_exploration_id(self, exploration_id):
        """Removes the exploration id from the list of completed exploration
        ids.
        """
        self.exploration_ids.remove(exploration_id)

    def add_collection_id(self, collection_id):
        """Adds the collection id to the list of completed collection ids."""
        self.collection_ids.append(collection_id)

    def remove_collection_id(self, collection_id):
        """Removes the collection id from the list of completed collection
        ids.
        """
        self.collection_ids.remove(collection_id)


class LearnerPlaylist(python_utils.OBJECT):
    """Domain object for the learner playlist model."""

    def __init__(
            self, user_id, exploration_ids, collection_ids):
        self.id = user_id
        self.exploration_ids = exploration_ids
        self.collection_ids = collection_ids

    def insert_exploration_id_at_given_position(
            self, exploration_id, position_to_be_inserted):
        """Inserts the given exploration id at the given position.

        Args:
            exploration_id: str. The exploration id to be inserted into the
                play later list.
            position_to_be_inserted: int. The position at which it
                is to be inserted.
        """
        self.exploration_ids.insert(
            position_to_be_inserted, exploration_id)

    def add_exploration_id_to_list(self, exploration_id):
        """Inserts the exploration id at the end of the list.

        Args:
            exploration_id: str. The exploration id to be appended to the end
                of the list.
        """
        self.exploration_ids.append(exploration_id)

    def insert_collection_id_at_given_position(
            self, collection_id, position_to_be_inserted):
        """Inserts the given collection id at the given position.

        Args:
            collection_id: str. The collection id to be inserted into the
                play later list.
            position_to_be_inserted: int. The position at which it
                is to be inserted.
        """
        self.collection_ids.insert(position_to_be_inserted, collection_id)

    def add_collection_id_to_list(self, collection_id):
        """Inserts the collection id at the end of the list.

        Args:
            collection_id: str. The collection id to be appended to the end
                of the list.
        """
        self.collection_ids.append(collection_id)

    def remove_exploration_id(self, exploration_id):
        """Removes the exploration id from the learner playlist.

        exploration_id: str. The id of the exploration to be removed.
        """
        self.exploration_ids.remove(exploration_id)

    def remove_collection_id(self, collection_id):
        """Removes the collection id from the learner playlist.

        collection_id: str. The id of the collection to be removed.
        """
        self.collection_ids.remove(collection_id)


class UserContributionProficiency(python_utils.OBJECT):
    """Domain object for UserContributionProficiencyModel."""

    def __init__(self, user_id, score_category, score, onboarding_email_sent):
        self.user_id = user_id
        self.score_category = score_category
        self.score = score
        self.onboarding_email_sent = onboarding_email_sent

    def increment_score(self, increment_by):
        """Increments the score of the user in the category by the given amount.

        In the first version of the scoring system, the increment_by quantity
        will be +1, i.e, each user gains a point for a successful contribution
        and doesn't lose score in any way.

        Args:
            increment_by: float. The amount to increase the score of the user
                by.
        """
        self.score += increment_by

    def can_user_review_category(self):
        """Checks if user can review suggestions in category score_category.
        If the user has score above the minimum required score, then the user
        is allowed to review.

        Returns:
            bool. Whether the user can review suggestions under category
            score_category.
        """
        return self.score >= feconf.MINIMUM_SCORE_REQUIRED_TO_REVIEW

    def mark_onboarding_email_as_sent(self):
        """Marks the email as sent."""
        self.onboarding_email_sent = True


class UserContributionRights(python_utils.OBJECT):
    """Domain object for the UserContributionRightsModel."""

    def __init__(
            self, user_id, can_review_translation_for_language_codes,
            can_review_voiceover_for_language_codes, can_review_questions):
        self.id = user_id
        self.can_review_translation_for_language_codes = (
            can_review_translation_for_language_codes)
        self.can_review_voiceover_for_language_codes = (
            can_review_voiceover_for_language_codes)
        self.can_review_questions = can_review_questions

    def can_review_at_least_one_item(self):
        """Checks whether user has rights to review at least one item.

        Returns:
            boolean. Whether user has rights to review at east one item.
        """
        return (
            self.can_review_translation_for_language_codes or
            self.can_review_voiceover_for_language_codes or
            self.can_review_questions)

    def validate(self):
        """Validates different attributes of the class."""
        if not isinstance(self.can_review_translation_for_language_codes, list):
            raise utils.ValidationError(
                'Expected can_review_translation_for_language_codes to be a '
                'list, found: %s' % type(
                    self.can_review_translation_for_language_codes))
        for language_code in self.can_review_translation_for_language_codes:
            if not utils.is_supported_audio_language_code(language_code):
                raise utils.ValidationError('Invalid language_code: %s' % (
                    language_code))
        if len(self.can_review_translation_for_language_codes) != len(set(
                self.can_review_translation_for_language_codes)):
            raise utils.ValidationError(
                'Expected can_review_translation_for_language_codes list not '
                'to have duplicate values, found: %s' % (
                    self.can_review_translation_for_language_codes))

        if not isinstance(self.can_review_voiceover_for_language_codes, list):
            raise utils.ValidationError(
                'Expected can_review_voiceover_for_language_codes to be a '
                'list, found: %s' % type(
                    self.can_review_voiceover_for_language_codes))
        for language_code in self.can_review_voiceover_for_language_codes:
            if not utils.is_supported_audio_language_code(language_code):
                raise utils.ValidationError('Invalid language_code: %s' % (
                    language_code))
        if len(self.can_review_voiceover_for_language_codes) != len(set(
                self.can_review_voiceover_for_language_codes)):
            raise utils.ValidationError(
                'Expected can_review_voiceover_for_language_codes list not to '
                'have duplicate values, found: %s' % (
                    self.can_review_voiceover_for_language_codes))

        if not isinstance(self.can_review_questions, bool):
            raise utils.ValidationError(
                'Expected can_review_questions to be a boolean value, '
                'found: %s' % type(self.can_review_questions))
