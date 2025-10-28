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

from qgis.core import QgsVectorLayer, QgsSpatialIndex, QgsField
from qgis.PyQt.QtCore import QVariant

from copy import deepcopy
from csv import reader, writer
from math import exp, log, sqrt
from os import path, sep
from statistics import median
from time import sleep

from .cluz_messages import clear_progress_bar, empty_polygon_pu_id_set_error_message, make_progress_bar
from .cluz_messages import set_progress_bar_value, warning_message, critical_message,success_message
from .cluz_make_file_dicts import write_bound_dat_file


#
# # Prioritizr dialog  #####################################################
#
# def check_blm_value_para_dict(blm_value, check_bool):
#     try:
#         float(blm_value)
#         if float(blm_value) < 0:
#             warning_message('Input error', 'The boundary length modifier must be a non-negative number.')
#             check_bool = False
#     except ValueError:
#         warning_message('Input error', 'The boundary length modifier must be a non-negative number.')
#         check_bool = False
#
#     return check_bool
#
#

# def check_permission_to_use_marxan_folder_para_dict(marxan_parameter_dict, marxan_input_values_bool):
#     marxan_path_text = marxan_parameter_dict['marxan_path']
#     marxan_folder = path.dirname(marxan_path_text)
#     marxan_input_path = marxan_folder + sep + 'input.dat'
#     try:
#         with open(marxan_input_path, 'w', newline='', encoding='utf-8') as marxanFile:
#             marxan_writer = writer(marxanFile)
#     except PermissionError:
#         critical_message('Permission problem', 'You do not have permission to save files in the specified Marxan folder. CLUZ needs this to create input.dat and .bat files in the Marxan folder. Please move Marxan to a folder where you do have permission to save files.')
#         marxan_input_values_bool = False
#
#     return marxan_input_values_bool

def prioritizr_update_setup_object(prioritizr_dialog, setup_object, prioritizr_dialog_parameter_dict):
    setup_object.output_name = prioritizr_dialog_parameter_dict['output_name']
    setup_object.blm_value = prioritizr_dialog_parameter_dict['blm_value']
    setup_object.bound_flag = prioritizr_dialog.boundCheckBox.isChecked()
    setup_object.extra_outputs_flag = prioritizr_dialog.extraCheckBox.isChecked()

    return setup_object


def waiting_for_prioritizr(setup_object, output_name):
    prioritizr_best_output_file_name = setup_object.output_path + sep + output_name + '_best.txt'
    try:
        while path.isfile(prioritizr_best_output_file_name) is False:
            sleep(2)
    except KeyboardInterrupt:
        pass

