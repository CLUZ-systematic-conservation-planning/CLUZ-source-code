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

from .cluz_setup import CluzSetupObject

from os import path

from .cluz_setup import update_setup_object_from_setup_file, check_status_object_values, create_and_check_cluz_files, update_clz_setup_file
from .cluz_checkup import check_add_pu_layer
from .zcluz_checkup import check_add_zones_pu_layer


def set_inputs_to_reflect_software_package(setup_dialog, software_type_text):
    if software_type_text == 'Marxan':
        set_marxan_labels_buttons_visibility(setup_dialog, True)
        set_zones_labels_buttons_visibility(setup_dialog, False)
        set_prioritizr_labels_buttons_visibility(setup_dialog, False)
    elif software_type_text == 'Marxan with Zones':
        set_marxan_labels_buttons_visibility(setup_dialog, True)
        set_zones_labels_buttons_visibility(setup_dialog, True)
        set_prioritizr_labels_buttons_visibility(setup_dialog, False)
    elif software_type_text == 'Prioritizr':
        set_marxan_labels_buttons_visibility(setup_dialog, False)
        set_zones_labels_buttons_visibility(setup_dialog, False)
        set_prioritizr_labels_buttons_visibility(setup_dialog, True)
    elif software_type_text == 'Prioritizr with Zones':
        set_marxan_labels_buttons_visibility(setup_dialog, False)
        set_zones_labels_buttons_visibility(setup_dialog, True)
        set_prioritizr_labels_buttons_visibility(setup_dialog, True)

def add_setup_dialog_text_from_setup_object(setup_dialog, setup_object):
    setup_dialog.analysisComboBox.setCurrentIndex(setup_dialog.analysisComboBox.findText(setup_object.analysis_type))

    setup_dialog.marxanLineEdit.setText(setup_object.marxan_path)

    if setup_object.analysis_type == 'Marxan' or setup_object.analysis_type == 'Marxan with Zones':
        set_marxan_labels_buttons_visibility(setup_dialog, True)
        set_prioritizr_labels_buttons_visibility(setup_dialog, False)
        setup_dialog.marxanLineEdit.setText(setup_object.marxan_path)

    if setup_object.analysis_type == 'Prioritizr' or setup_object.analysis_type == 'Prioritizr with Zones':
        set_marxan_labels_buttons_visibility(setup_dialog, False)
        set_prioritizr_labels_buttons_visibility(setup_dialog, True)
        setup_dialog.prioritizrLineEdit.setText(setup_object.prioritizr_path)

    setup_dialog.inputLineEdit.setText(setup_object.input_path)
    setup_dialog.outputLineEdit.setText(setup_object.output_path)
    setup_dialog.puLineEdit.setText(setup_object.pu_path)
    setup_dialog.targetLineEdit.setText(setup_object.target_path)
    setup_dialog.set_prec_value(setup_object.decimal_places)

    if path.isfile(setup_object.setup_path):
        setup_path_text = path.abspath(setup_object.setup_path)
    else:
        setup_path_text = 'blank'

    if setup_object.analysis_type == 'Marxan':
        set_marxan_labels_buttons_visibility(setup_dialog, True)
        set_zones_labels_buttons_visibility(setup_dialog, False)
        set_prioritizr_labels_buttons_visibility(setup_dialog, False)
        setup_dialog.zonesLineEdit.setText(setup_object.zones_path)
    else:
        pass

        setup_dialog.zonesLineEdit.setText(setup_object.zones_path)

    setup_path_label_text = 'Setup file location: ' + setup_path_text
    setup_dialog.setupPathLabel.setText(setup_path_label_text)


def set_marxan_labels_buttons_visibility(setup_dialog, visibility_bool):
    setup_dialog.marxanLabel.setVisible(visibility_bool)
    setup_dialog.marxanLineEdit.setVisible(visibility_bool)
    setup_dialog.marxanButton.setVisible(visibility_bool)


def set_zones_labels_buttons_visibility(setup_dialog, visibility_bool):
    setup_dialog.zonesLabel.setVisible(visibility_bool)
    setup_dialog.zonesLineEdit.setVisible(visibility_bool)
    setup_dialog.zonesButton.setVisible(visibility_bool)


def set_prioritizr_labels_buttons_visibility(setup_dialog, visibility_bool):
    setup_dialog.prioritizrLabel.setVisible(visibility_bool)
    setup_dialog.prioritizrLineEdit.setVisible(visibility_bool)
    setup_dialog.prioritizrButton.setVisible(visibility_bool)



def load_setup_file_code(setup_dialog, setup_object, setup_file_path):
    setup_object = update_setup_object_from_setup_file(setup_object, setup_file_path)

    if setup_object.setup_status == 'values_checked':
        setup_object = create_and_check_cluz_files(setup_object)

    if setup_object.setup_status == "files_checked":
        setup_object.setup_action = "blank"
        setup_path_label_text = path.abspath(setup_file_path)
        setup_path_label_text = "Setup file location: " + str(setup_path_label_text)
        setup_dialog.setupPathLabel.setText(setup_path_label_text)

        setup_dialog.analysisComboBox.setCurrentIndex(setup_dialog.analysisComboBox.findText(setup_object.analysis_type))

        setup_dialog.inputLineEdit.setText(path.abspath(setup_object.input_path))
        setup_dialog.outputLineEdit.setText(setup_object.output_path)
        setup_dialog.puLineEdit.setText(setup_object.pu_path)
        setup_dialog.targetLineEdit.setText(setup_object.target_path)
        setup_dialog.set_prec_value(setup_object.decimal_places)

        if setup_object.analysis_type == 'Marxan':
            setup_dialog.marxanLineEdit.setText(path.abspath(setup_object.marxan_path))
            check_add_pu_layer(setup_object)

        if setup_object.analysis_type == 'Prioritizr':
            setup_dialog.prioritizrLineEdit.setText(path.abspath(setup_object.prioritizr_path))
            check_add_pu_layer(setup_object)

        if setup_object.analysis_type == 'MarxanWithZones':
            setup_dialog.marxanLineEdit.setText(path.abspath(setup_object.marxan_path))
            setup_dialog.zonesLineEdit.setText(setup_object.zones_path)
            check_add_zones_pu_layer(setup_object)

        if setup_object.analysis_type == 'PrioritizrWithZones':
            setup_dialog.prioritizrLineEdit.setText(path.abspath(setup_object.prioritizr_path))
            setup_dialog.zonesLineEdit.setText(setup_object.zones_path)
            check_add_zones_pu_layer(setup_object)


        update_setup_object_with_enabled_functions(setup_object)


def update_setup_object_with_enabled_functions(setup_object):
    if setup_object.analysis_type == 'Marxan':

        setup_object.ZonesAction.setEnabled(True)
        setup_object.ConvertVecAction.setEnabled(False)
        setup_object.ConvertRasterAction.setEnabled(False)
        setup_object.ConvertCsvAction.setEnabled(False)
        setup_object.MinPatchAction.setEnabled(False)
    else:
        setup_object.ZonesAction.setEnabled(False)
        setup_object.ConvertVecAction.setEnabled(True)
        setup_object.ConvertRasterAction.setEnabled(True)
        setup_object.ConvertCsvAction.setEnabled(True)
        setup_object.MinPatchAction.setEnabled(True)


def save_setup_file_code(setup_dialog, setup_object, setup_file_path):
    limbo_setup_object = CluzSetupObject()
    limbo_setup_object.TargetsMetAction = setup_object.TargetsMetAction
    limbo_setup_object.ZonesAction = setup_object.ZonesAction
    limbo_setup_object.MinPatchAction = setup_object.MinPatchAction
    limbo_setup_object.setup_status = 'blank'

    limbo_setup_object = add_details_to_setup_object(setup_dialog, limbo_setup_object)

    limbo_setup_object = check_status_object_values(limbo_setup_object)
    save_successful_bool = False

    if limbo_setup_object.setup_status == 'values_checked':
        limbo_setup_object = create_and_check_cluz_files(limbo_setup_object)

    if limbo_setup_object.setup_status == 'files_checked':
        save_successful_bool = True
        copy_limbo_parameters_to_setup_object(setup_object, limbo_setup_object)
        save_successful_bool = update_clz_setup_file(setup_object, save_successful_bool)
        if save_successful_bool:
            setup_path_label_text = 'Setup file location: ' + str(setup_file_path)
            setup_dialog.setupPathLabel.setText(setup_path_label_text)

            check_add_pu_layer(setup_object)

    return save_successful_bool


def copy_limbo_parameters_to_setup_object(setup_object, limbo_setup_object):
    setup_object.decimal_places = limbo_setup_object.decimal_places
    setup_object.marxan_path = limbo_setup_object.marxan_path
    setup_object.prioritizr_path = limbo_setup_object.prioritizr_path
    setup_object.input_path = limbo_setup_object.input_path
    setup_object.output_path = limbo_setup_object.output_path
    setup_object.pu_path = limbo_setup_object.pu_path
    setup_object.target_path = limbo_setup_object.target_path


def save_as_setup_file_code(setup_dialog, setup_object, new_setup_file_path):
    setup_object = add_details_to_setup_object(setup_dialog, setup_object)
    setup_object.setup_path = new_setup_file_path

    setup_object = check_status_object_values(setup_object)
    if setup_object.setup_status == 'values_checked':
        setup_object = create_and_check_cluz_files(setup_object)
    if setup_object.setup_status == 'files_checked':
        save_successful_bool = True
        save_successful_bool = update_clz_setup_file(setup_object, save_successful_bool)
        if save_successful_bool:
            setup_path_label_text = 'Setup file location: ' + str(new_setup_file_path)
            setup_dialog.setupPathLabel.setText(setup_path_label_text)
            check_add_pu_layer(setup_object)


def add_details_to_setup_object(setup_dialog, setup_object):
    prioritisation_type = setup_dialog.analysisComboBox.currentText()
    if prioritisation_type == 'Marxan':
        setup_object.analysis_type = 'Marxan'
    if prioritisation_type == 'Marxan with Zones':
        setup_object.analysis_type = 'Prioritizr'
    if prioritisation_type == 'Prioritizr':
        setup_object.analysis_type = 'Prioritizr'
    if prioritisation_type == 'Prioritizr with Zones':
        setup_object.analysis_type = 'PrioritizrWithZones'

    setup_object.decimal_places = int(setup_dialog.precComboBox.currentText())

    if setup_object.analysis_type == 'Marxan' or setup_object.analysis_type == 'MarxanWithZones':
        setup_object.marxan_path = setup_dialog.marxanLineEdit.text()
        setup_object.prioritizr_path = 'blank'
    else:
        setup_object.marxan_path = 'blank'
        setup_object.prioritizr_path = setup_dialog.prioritizrLineEdit.text()

    setup_object.marxan_path = setup_dialog.marxanLineEdit.text()
    setup_object.input_path = setup_dialog.inputLineEdit.text()
    setup_object.output_path = setup_dialog.outputLineEdit.text()
    setup_object.pu_path = setup_dialog.puLineEdit.text()
    setup_object.target_path = setup_dialog.targetLineEdit.text()

    if setup_object.analysis_type == 'MarxanWithZones' or setup_object.analysis_type == 'PrioritizrWithZones':
        setup_object.zones_path = setup_dialog.zonesLineEdit.text()
    else:
        setup_object.zones_path = 'blank'

    return setup_object