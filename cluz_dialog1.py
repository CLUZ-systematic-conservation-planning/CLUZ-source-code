"""
/***************************************************************************
                                 A QGIS plugin
 CLUZ for QGIS
                             -------------------
        begin                : 2025-10-22
        copyright            : (C) 2025 by Bob Smith, DICE
        email                : r.j.smith@kent.ac.uk
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 3 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from qgis.PyQt.QtWidgets import QDialog, QFileDialog

from os import path
import sys

from .cluz_messages import warning_message, success_message
from .cluz_dialog1_code import load_setup_file_code, save_as_setup_file_code, save_setup_file_code, add_setup_dialog_text_from_setup_object
from .cluz_dialog1_code import set_marxan_labels_buttons_visibility, set_zones_labels_buttons_visibility, set_prioritizr_labels_buttons_visibility
from .cluz_dialog1_code import set_inputs_to_reflect_software_package
from .cluz_display import remove_then_add_pu_layer

sys.path.append(path.dirname(path.abspath(__file__)) + "/forms")
from cluz_form_start import Ui_startDialog
from cluz_form_setup import Ui_setupDialog


class StartDialog(QDialog, Ui_startDialog):
    def __init__(self, iface, setup_object):
        QDialog.__init__(self)
        self.iface = iface
        self.setupUi(self)

        self.okButton.clicked.connect(lambda: self.return_start_bool(setup_object))
        self.cancelButton.clicked.connect(self.close_start_dialog)

    def return_start_bool(self, setup_object):
        if self.openRadioButton.isChecked():
            setup_object.setup_action = 'open'
        elif self.createButton.isChecked():
            setup_object.setup_action = 'new'
        self.close()

    def close_start_dialog(self):
        self.close()


class SetupDialog(QDialog, Ui_setupDialog):
    def __init__(self, iface, setup_object):
        QDialog.__init__(self)
        self.iface = iface
        self.setupUi(self)

        # self.analysisComboBox.addItems(['Marxan', 'Marxan with Zones', 'Prioritizr'])
        self.analysisComboBox.addItems(['Marxan', 'Marxan with Zones'])
        add_setup_dialog_text_from_setup_object(self, setup_object)

        if setup_object.analysis_type == 'Marxan':
            set_marxan_labels_buttons_visibility(self, True)
            set_zones_labels_buttons_visibility(self, False)
            set_prioritizr_labels_buttons_visibility(self, False)
        elif setup_object.analysis_type == 'Marxan with Zones':
            set_marxan_labels_buttons_visibility(self, True)
            set_zones_labels_buttons_visibility(self, True)
            set_prioritizr_labels_buttons_visibility(self, False)
        elif  setup_object.analysis_type == 'Prioritizr':
            set_marxan_labels_buttons_visibility(self, False)
            set_zones_labels_buttons_visibility(self, False)
            set_prioritizr_labels_buttons_visibility(self, True)
        else:
            set_marxan_labels_buttons_visibility(self, False)
            set_zones_labels_buttons_visibility(self, True)
            set_prioritizr_labels_buttons_visibility(self, True)

        self.analysisComboBox.currentTextChanged.connect(self.update_inputs_to_reflect_software_package)

        self.marxanButton.clicked.connect(self.set_marxan_path)
        self.prioritizrButton.clicked.connect(self.set_prioritizr_path)

        self.inputButton.clicked.connect(self.set_input_path)
        self.outputButton.clicked.connect(self.set_output_path)
        self.puButton.clicked.connect(self.set_pu_path)
        self.targetButton.clicked.connect(self.set_target_path)
        self.zonesButton.clicked.connect(self.set_zones_path)

        self.loadButton.clicked.connect(lambda: self.load_setup_file(setup_object))
        self.saveButton.clicked.connect(lambda: self.save_setup_file(setup_object))
        self.saveAsButton.clicked.connect(lambda: self.save_as_setup_file(setup_object))

    def update_inputs_to_reflect_software_package(self, text):
        set_inputs_to_reflect_software_package(self, text)

    def set_marxan_path(self):
        (marxan_path_name_raw_text, file_type_text) = QFileDialog.getOpenFileName(self, 'Select Marxan file', '*.exe')
        marxan_path_name_text = path.abspath(marxan_path_name_raw_text)
        if marxan_path_name_text is not None:
            self.marxanLineEdit.setText(marxan_path_name_text)

    def set_prioritizr_path(self):
        (prioritizr_path_name_raw_text, file_type_text) = QFileDialog.getOpenFileName(self, 'Select Prioritizr setup instructions file', '*.txt')
        prioritizr_path_name_text = path.abspath(prioritizr_path_name_raw_text)
        if prioritizr_path_name_text is not None:
            self.prioritizrLineEdit.setText(prioritizr_path_name_text)

    def set_input_path(self):
        input_path_name_raw_text = QFileDialog.getExistingDirectory(self, 'Select input folder')
        input_path_name_text = path.abspath(input_path_name_raw_text)
        if input_path_name_text is not None:
            self.inputLineEdit.setText(input_path_name_text)

    def set_output_path(self):
        output_path_name_raw_text = QFileDialog.getExistingDirectory(self, 'Select output folder')
        output_path_name_text = path.abspath(output_path_name_raw_text)
        if output_path_name_text is not None:
            self.outputLineEdit.setText(output_path_name_text)

    def set_pu_path(self):
        (pu_path_name_raw_text, file_type_text) = QFileDialog.getOpenFileName(self, 'Select planning unit shapefile', '*.shp')
        pu_path_name_text = path.abspath(pu_path_name_raw_text)
        if pu_path_name_text is not None:
            self.puLineEdit.setText(pu_path_name_text)

    def set_target_path(self):
        (target_path_name_raw_text, file_type_text) = QFileDialog.getOpenFileName(self, 'Select target table', '*.csv')
        target_path_name_text = path.abspath(target_path_name_raw_text)
        if target_path_name_text is not None:
            self.targetLineEdit.setText(target_path_name_text)

    def set_zones_path(self):
        (zone_path_name_raw_text, file_type_text) = QFileDialog.getOpenFileName(self, 'Select zone table', '*.csv')
        zone_path_name_text = path.abspath(zone_path_name_raw_text)
        if zone_path_name_text is not None:
            self.zonesLineEdit.setText(zone_path_name_text)

    def set_prec_value(self, prec_value):
        self.precComboBox.addItems(['0', '1', '2', '3', '4', '5'])
        number_list = [0, 1, 2, 3, 4, 5]
        if prec_value > 5:
            title_text = 'Decimal precision value problem'
            main_text = 'The number of decimal places specified in the CLUZ setup file cannot be more than 5. The specified value has been changed to 5.'
            warning_message(title_text, main_text)
            prec_value = 5
        index_value = number_list.index(prec_value)
        self.precComboBox.setCurrentIndex(index_value)

    def load_setup_file(self, setup_object):
        (setup_path_label_text, file_type_text) = QFileDialog.getOpenFileName(self, 'Select CLUZ setup file', '*.clz')
        if setup_path_label_text != '':
            load_setup_file_code(self, setup_object, setup_path_label_text)
            remove_then_add_pu_layer(setup_object, 0)

    def save_setup_file(self, setup_object):
        setup_file_path = setup_object.setup_path
        if path.isfile(setup_file_path):
            save_successful_bool = save_setup_file_code(self, setup_object, setup_file_path)
            if save_successful_bool:
                success_message('File saved', 'The CLUZ setup file has been saved successfully.')
        elif setup_file_path == 'blank':
            warning_message("No CLUZ setup file name", "The CLUZ setup file name has not been set. Please use the Save As... option instead.")
        else:
            warning_message("CLUZ setup file name error", "The current CLUZ setup file path is incorrect.")

    def save_as_setup_file(self, setup_object):
        (new_setup_file_path, file_type_text) = QFileDialog.getSaveFileName(self, 'Save new CLUZ setup file', '*.clz')
        if new_setup_file_path != '':
            save_as_setup_file_code(self, setup_object, new_setup_file_path)
            if setup_object.setup_status:
                success_message('File saved', 'The CLUZ setup file has been saved successfully.')
        else:
            warning_message("CLUZ setup file name error", "The current CLUZ setup file path is incorrect.")

