// Copyright 2018 The Oppia Authors. All Rights Reserved.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS-IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

/**
 * @fileoverview Factory for creating and mutating instances of frontend
 * question domain objects.
 */
import { downgradeInjectable } from '@angular/upgrade/static';
import { Injectable } from '@angular/core';
import { State, StateObjectFactory, StateBackendDict }
  from 'domain/state/StateObjectFactory';

const DEFAULT_LANGUAGE_CODE = require(
  '../../../../assets/constants').DEFAULT_LANGUAGE_CODE;
const INTERACTION_SPECS = require('interactions/interaction_specs.json');

export interface QuestionBackendDict {
  'id': string;
  'question_state_data': StateBackendDict,
  'language_code': string;
  'version': number;
  'linked_skill_ids': string[];
  'inapplicable_misconception_ids': string[];
}

export class Question {
  constructor(
    private _id: string,
    private _stateData: State,
    private _languageCode: string,
    private _version: number,
    private _linkedSkillIds: string[],
    private _inApplicableMisconceptionIds: string[]
  ) { }

  getId(): string {
    return this._id;
  }

  getStateData(): State {
    return this._stateData;
  }

  setStateData(newStateData: State): void {
    this._stateData = angular.copy(newStateData);
  }

  getLanguageCode(): string {
    return this._languageCode;
  }

  setLanguageCode(languageCode: string): void {
    this._languageCode = languageCode;
  }

  getVersion(): number {
    return this._version;
  }

  getLinkedSkillIds(): string[] {
    return this._linkedSkillIds;
  }

  setLinkedSkillIds(linkedSkillIds: string[]): void {
    this._linkedSkillIds = linkedSkillIds;
  }


  getInApplicableMisconceptionIds(): string[] {
    return this._inApplicableMisconceptionIds;
  }

  setInApplicableMisconceptionIds(
      inApplicableMisconceptionIds: string[]): void {
    this._inApplicableMisconceptionIds = inApplicableMisconceptionIds;
  }

  getValidationErrorMessage(): string {
    var interaction = this._stateData.interaction;
    if (interaction.id === null) {
      return 'An interaction must be specified';
    }
    if (interaction.hints.length === 0) {
      return 'At least 1 hint should be specified';
    }
    if (
      !interaction.solution &&
      INTERACTION_SPECS[interaction.id].can_have_solution) {
      return 'A solution must be specified';
    }
    var answerGroups = this._stateData.interaction.answerGroups;
    var atLeastOneAnswerCorrect = false;
    for (var i = 0; i < answerGroups.length; i++) {
      if (answerGroups[i].outcome.labelledAsCorrect) {
        atLeastOneAnswerCorrect = true;
        continue;
      }
    }
    if (!atLeastOneAnswerCorrect) {
      return 'At least one answer should be marked correct';
    }
    return null;
  }

  getUnaddressedMisconceptionNames(misconceptionsBySkill: object): string[] {
    var answerGroups = this._stateData.interaction.answerGroups;
    var taggedSkillMisconceptionIds = {};
    for (var i = 0; i < answerGroups.length; i++) {
      if (!answerGroups[i].outcome.labelledAsCorrect &&
          answerGroups[i].taggedSkillMisconceptionId !== null) {
        taggedSkillMisconceptionIds[
          answerGroups[i].taggedSkillMisconceptionId] = true;
      }
    }
    var unaddressedMisconceptionNames = [];
    Object.keys(misconceptionsBySkill).forEach(function(skillId) {
      for (var i = 0; i < misconceptionsBySkill[skillId].length; i++) {
        if (!misconceptionsBySkill[skillId][i].isMandatory()) {
          continue;
        }
        var skillMisconceptionId = (
          skillId + '-' + misconceptionsBySkill[skillId][i].getId());
        if (!taggedSkillMisconceptionIds.hasOwnProperty(
          skillMisconceptionId)) {
          unaddressedMisconceptionNames.push(
            misconceptionsBySkill[skillId][i].getName());
        }
      }
    });
    return unaddressedMisconceptionNames;
  }

  toBackendDict(isNewQuestion: boolean): QuestionBackendDict {
    var questionBackendDict = {
      id: null,
      question_state_data: this._stateData.toBackendDict(),
      language_code: this._languageCode,
      linked_skill_ids: this._linkedSkillIds,
      inapplicable_misconception_ids: this._inApplicableMisconceptionIds,
      version: 0,
    };
    if (!isNewQuestion) {
      questionBackendDict.id = this._id;
      questionBackendDict.version = this._version;
    }
    return questionBackendDict;
  }
}

@Injectable({
  providedIn: 'root'
})
export class QuestionObjectFactory {
  constructor(
    private stateObjectFactory: StateObjectFactory
  ) { }

  createDefaultQuestion(skillIds: string[]): Question {
    /* eslint-enable dot-notation */
    return new Question(
      null, this.stateObjectFactory.createDefaultState(null),
      DEFAULT_LANGUAGE_CODE, 1, skillIds, []);
  }

  createFromBackendDict(questionBackendDict: QuestionBackendDict): Question {
    return new Question(
      questionBackendDict.id,
      this.stateObjectFactory.createFromBackendDict(
        'question', questionBackendDict.question_state_data),
      questionBackendDict.language_code, questionBackendDict.version,
      questionBackendDict.linked_skill_ids,
      questionBackendDict.inapplicable_misconception_ids
    );
  }
}

angular.module('oppia').factory(
  'QuestionObjectFactory',
  downgradeInjectable(QuestionObjectFactory));
