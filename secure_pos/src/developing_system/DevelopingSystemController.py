import os
import sys

import joblib
import json

from developing_system.TrainingConfiguration import TrainingConfiguration
from developing_system.MLPTraining import MLPTraining
from developing_system.GridSearchController import GridSearchController
from developing_system.DevelopingSystemConfiguration import DevelopingSystemConfiguration
from developing_system.ClassifierArchiver import ClassifierArchiver
from developing_system.TestBestClassifier import TestBestClassifier
from developing_system.TestBestClassifierReportGenerator import TestBestCLassifierReportGenerator
from developing_system.CommunicationController import CommunicationController

import utility

SYSTEM_CONFIGURATION_PATH = 'development_system/configuration_files/developing_system_configuration.json'
SYSTEM_CONFIGURATION_SCHEMA_PATH = 'development_system/json_schemas/developing_system_configuration_schema.json'

TRAINING_CONFIGURATION_PATH = 'development_system/configuration_files/training_configuration.json'
TRAINING_CONFIGURATION_SCHEMA_PATH = 'development_system/json_schemas/training_configuration_schema.json'

class DevelopingSystemController:

    def __init__(self):
        self.training_configuration = TrainingConfiguration(TRAINING_CONFIGURATION_PATH, TRAINING_CONFIGURATION_SCHEMA_PATH)
        self.developing_system_configuration = DevelopingSystemConfiguration(SYSTEM_CONFIGURATION_PATH, SYSTEM_CONFIGURATION_SCHEMA_PATH)
        self.communication_controller = CommunicationController(self.developing_system_configuration, self)


    def execution_of_the_initial_phase_training(self):

        initial_phase_classifier = MLPTraining(self.training_configuration.is_initial_phase_over)
        initial_phase_classifier.train_neural_network(self.training_configuration.average_parameters)


    def execution_of_the_grid_search_algorithm(self):

        loaded_classifier = joblib.load(os.path.join(utility.data_folder, 'development_system/classifiers/initial_phase_classifier.sav'))
        classifier_for_grid_search = MLPTraining(self.training_configuration.is_initial_phase_over)
        classifier_for_grid_search.set_mlp(loaded_classifier)
        grid_search_controller = GridSearchController(classifier_for_grid_search, self.training_configuration)
        grid_search_controller.generate_grid_search_hyperparameters(self.training_configuration.hyper_parameters)
        for elem in grid_search_controller.top_classifiers_object_list:
            elem.print()

    def reset_of_the_system(self):
        classifier_archive_manager = ClassifierArchiver(self.training_configuration.best_classifier_number)
        classifier_archive_manager.delete_remaining_classifiers()
        with open(os.path.join(utility.data_folder,TRAINING_CONFIGURATION_PATH), 'r') as read_file:
            json_data = json.load(read_file)
            json_data['is_initial_phase_over'] = "No"
            json_data['is_grid_search_over'] = "No"

        with open(os.path.join(utility.data_folder,TRAINING_CONFIGURATION_PATH), 'w') as write_file:
            json.dump(json_data, write_file, indent=2)

    def run(self):
        self.communication_controller.start_developing_rest_server()

    def analysis_of_the_best_classifier(self):

        classifier_archive_manager = ClassifierArchiver(self.training_configuration.best_classifier_number)
        classifier_archive_manager.delete_remaining_classifiers()
        training_error_best_classifier = None

        with open(os.path.join(utility.data_folder, 'development_system/reports/top_classifiers/report_top_classifiers.json'), 'r') as report:
            json_data = json.load(report)
            for i in json_data['top_classifiers']:
                if i['classifier_id'] == self.training_configuration.best_classifier_number:
                    training_error_best_classifier = i['training_error']

        test = TestBestClassifier(self.training_configuration)
        test.test_best_classifier(classifier_archive_manager.return_path_best_classifier())
        test.print()

        TestBestCLassifierReportGenerator().generate_report(test, training_error_best_classifier)

    def identify_the_top_mlp_classifiers(self):

        if self.training_configuration.best_classifier_number == 0:
            if self.training_configuration.is_grid_search_over in ['No', 'no', 'NO']:
                if self.training_configuration.is_initial_phase_over in ['No', 'no', 'NO']:
                    self.execution_of_the_initial_phase_training()
                    sys.exit(0)
                elif self.training_configuration.is_initial_phase_over in ['Yes', 'yes', 'YES']:
                    self.execution_of_the_grid_search_algorithm()
                    sys.exit(0)
                else:
                    print("Unknown value for 'is_initial_phase_over' param, in the training configuration file: please insert 'yes' or 'no'")

            elif self.training_configuration.is_grid_search_over in ['Yes', 'yes', 'YES']:
                self.reset_of_the_system()
                sys.exit(0)
            else:
                print("Unknown value for 'is_grid_search_over' param, in the training configuration file: please insert 'yes' or 'no'")

        else:
            self.analysis_of_the_best_classifier()
            sys.exit(0)