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

from qgis.PyQt.QtWidgets import QFileDialog

from csv import reader, writer

from re import match

from .cluz_messages import critical_message, warning_message
from .cluz_checkup import check_marxan_input_numbers_in_setup_object, check_analysis_input_values_in_setup_object, check_status_object_values
from .cluz_checkup import create_and_check_target_file, create_and_check_puvspr2_file, create_and_check_pu_layer_file, check_add_pu_layer
from .cluz_make_file_dicts import make_target_dict

from .zcluz_checkup import create_and_check_zones_file, check_add_zones_pu_layer, create_and_check_zones_target_file
from .zcluz_checkup import check_values_in_zones_target_file
from .zcluz_make_file_dicts import make_zones_target_dict, make_zones_dict, make_zones_prop_dict
from .zcluz_make_file_dicts import make_zones_bound_cost_dict_from_zoneboundcost_dat, make_zones_target_zones_dict

class CluzSetupObject:
    def __init__(self):
        #################################################
        self.over_ride = False
        #################################################

        self.setup_status = 'blank'  # Can be 'values_set', 'values_checked' or 'files_checked'
        self.setup_action = 'blank'  # Can be 'new' or 'open'
        self.setup_path = 'blank'

        # Specify the field names used in the Marxan outputs
        self.best_heading_field_names = ['planning_unit', 'solution']
        self.summed_heading_field_names = ['planning_unit', 'number']
        self.zones_best_heading_field_names = ['planning_unit', 'zone']
        self.zones_summed_heading_field_names = ['planning unit', 'number']

        self.decimal_places = 3
        self.marxan_path = 'blank'
        self.input_path = 'blank'
        self.output_path = 'blank'
        self.pu_path = 'blank'
        self.target_path = 'blank'
        self.zones_path = 'blank'
        self.abund_file_date = 'blank'
        self.target_file_date = 'blank'

        self.prioritizr_path = 'blank'

        # These are the default values
        self.analysis_type = 'Marxan'
        self.output_name = 'output1'
        self.num_iter = 1000000
        self.num_runs = 10
        self.bound_flag = False
        self.blm_value = 0
        self.zones_bound_flag = False
        self.extra_outputs_flag = False
        self.start_prop = 0.2
        self.target_prop = 1

        self.abund_pu_key_dict = 'blank'
        self.zones_bound_cost_dict = 'blank'
        self.zones_bound_cost_dict = 'blank'

        self.table_heading_style = '::section {''background-color: lightblue; }'


def check_all_relevant_files(cluz_object, setup_object, start_dialog, setup_dialog):
    check_setup_file_loaded(cluz_object, setup_object, start_dialog, setup_dialog)
    open_setup_dialog_if_setup_files_incorrect(cluz_object, setup_object, setup_dialog)
    update_cluz_menu_buttons_based_on_software_type(setup_object)
    check_create_add_files(setup_object)


def check_setup_file_loaded(cluz_class, setup_object, start_dialog, setup_dialog):
    if setup_object.over_ride:
        pass
    else:
        if setup_object.setup_path == 'blank':
            cluz_class.startDialog = start_dialog(cluz_class, setup_object)
            cluz_class.startDialog.show()
            cluz_class.startDialog.exec_()

            if setup_object.setup_action == 'new':
                cluz_class.setup_dialog = setup_dialog(cluz_class, setup_object)
                cluz_class.setup_dialog.show()
                cluz_class.setup_dialog.exec_()
            elif setup_object.setup_action == 'open':
                (setupPathNameText, fileTypeDetailsText) = QFileDialog.getOpenFileName(None, 'Open existing CLUZ setup file', '*.clz')
                try:
                    update_setup_object_from_setup_file(setup_object, setupPathNameText)
                except IOError:
                    pass
            else:
                cluz_class.startDialog.close()


def open_setup_dialog_if_setup_files_incorrect(cluz_class, setup_object, setup_dialog):
    if setup_object.setup_status == 'values_set':
        cluz_class.setup_dialog = setup_dialog(cluz_class, setup_object)
        # show the dialog
        cluz_class.setup_dialog.show()
        # Run the dialog event loop
        cluz_class.setup_dialog.exec_()


def update_cluz_menu_buttons_based_on_software_type(setup_object):
    if setup_object.analysis_type == 'MarxanWithZones' or setup_object.analysis_type == 'PrioritizrWithZones':
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


class MinPatchObject:
    def __init__(self):
        self.setupStatus = 'blank'  # Can be 'values_set', 'values_checked' or 'files_checked'


def make_setup_dict_from_setup_file(setup_file_path):
    setup_dict = dict()
    with open(setup_file_path, 'rt') as f:
        setup_reader = reader(f)
        for a_row in setup_reader:
            a_list = a_row[0].split(' = ')
            if len(a_list) == 2:
                the_key = a_list[0]
                the_value = a_list[1]
                setup_dict[the_key] = the_value

    return setup_dict


def update_setup_object_from_setup_file(setup_object, setup_file_path):
    setup_dict = make_setup_dict_from_setup_file(setup_file_path)
    setup_file_ok = True

    try:
        analysis_type = setup_dict['analysis_type']
    except KeyError:
        analysis_type = 'Marxan'
    try:
        setup_object.analysis_type = analysis_type
        dec_place_text = setup_dict['decimal_places']
        setup_object.input_path = setup_dict['input_dir']
        setup_object.output_path = setup_dict['output_dir']
        setup_object.pu_path = setup_dict['unit_theme']
        setup_object.target_path = setup_dict['target_table']
        num_blm_text = setup_dict['blm']
        setup_object.setup_path = setup_file_path

        setup_object.bound_flag = setup_dict['bound_flag'] == 'True'
        setup_object.extra_outputs_flag = setup_dict['extra_flag'] == 'True'

        if analysis_type == 'Marxan':
            setup_object.marxan_path = setup_dict['marxan_path']
            num_iter_text = setup_dict['num_iterations']
            num_run_text = setup_dict['num_runs']
            start_prop_text = setup_dict['start_prop']
            target_prop_text = setup_dict['target_prop']
            setup_file_ok = check_marxan_input_numbers_in_setup_object(setup_object, setup_file_ok, num_iter_text, num_run_text, start_prop_text, target_prop_text)

        elif analysis_type == 'Prioritizr':
            setup_object.prioritizr_path = setup_dict['prioritizr_path']

        elif analysis_type == 'MarxanWithZones':
            setup_object.marxan_path = setup_dict['marxan_path']
            setup_object.zones_path = setup_dict['zones_table']
            num_iter_text = setup_dict['num_iterations']
            num_run_text = setup_dict['num_runs']
            start_prop_text = setup_dict['start_prop']
            target_prop_text = setup_dict['target_prop']
            setup_object.zones_bound_flag = setup_dict['zones_bound_flag'] == 'True'
            setup_file_ok = check_marxan_input_numbers_in_setup_object(setup_object, setup_file_ok, num_iter_text, num_run_text, start_prop_text, target_prop_text)

        elif analysis_type == 'PrioritizrWithZones':
            setup_object.prioritizr_path = setup_dict['prioritizr_path']
            setup_object.zones_path = setup_dict['zones_table']
            setup_object.zones_bound_flag = setup_dict['zones_bound_flag'] == 'True'

        setup_file_ok = check_analysis_input_values_in_setup_object(setup_object, setup_file_ok, analysis_type, dec_place_text, num_blm_text)

    # except KeyError:
    except ValueError:
        warning_message('Setup file incorrect format', 'The specified setup file does not contain all of the correct factors. Please correct this.')
        setup_file_ok = False

    if setup_file_ok:
        setup_object.setup_status = 'values_set'
        setup_object = check_status_object_values(setup_object)
        if setup_object.setup_status == 'values_checked':
            setup_object.setup_path = setup_file_path

    return setup_object


def update_clz_setup_file(setup_object, save_successful_bool):
    setup_file_path = setup_object.setup_path
    try:
        with open(setup_file_path, 'w', newline='', encoding='utf-8') as setupFile:
            setup_writer = writer(setupFile)

            setup_writer.writerow(['analysis_type = ' + str(setup_object.analysis_type)])
            setup_writer.writerow(['decimal_places = ' + str(setup_object.decimal_places)])

            if setup_object.analysis_type == 'Marxan' or setup_object.analysis_type == 'MarxanWithZones':
                setup_writer.writerow(['marxan_path = ' + setup_object.marxan_path])

            elif setup_object.analysis_type == 'Prioritizr' or setup_object.analysis_type == 'PrioritizrWithZones':
                setup_writer.writerow(['prioritizr_path = ' + setup_object.prioritizr_path])

            setup_writer.writerow(['input_dir = ' + setup_object.input_path])
            setup_writer.writerow(['output_dir = ' + setup_object.output_path])
            setup_writer.writerow(['unit_theme = ' + setup_object.pu_path])
            setup_writer.writerow(['target_table = ' + setup_object.target_path])

            if setup_object.analysis_type == 'MarxanWithZones' or setup_object.analysis_type == 'PrioritizrWithZones':
                setup_writer.writerow(['zones_table = ' + setup_object.zones_path])

            setup_writer.writerow(['output_name = ' + setup_object.output_name])

            if setup_object.analysis_type == 'Marxan' or setup_object.analysis_type == 'MarxanWithZones':
                setup_writer.writerow(['num_iterations = ' + str(setup_object.num_iter)])
                setup_writer.writerow(['num_runs = ' + str(setup_object.num_runs)])

            setup_writer.writerow(['bound_flag = ' + str(setup_object.bound_flag)])

            blm_string = str(setup_object.blm_value)
            if bool(match(r'^[+-]?\d+(\.\d+)?[eE][+-]?\d+$', blm_string)):
                blm_string = f'{round(setup_object.blm_value, 15):.20f}'.rstrip('0').rstrip('.')
            else:
                blm_string = str(setup_object.blm_value)  # For non-scientific notation, use the original value
            setup_writer.writerow([f'blm = {blm_string}'])

            setup_writer.writerow(['extra_flag = ' + str(setup_object.extra_outputs_flag)])

            if setup_object.analysis_type == 'Marxan' or setup_object.analysis_type == 'MarxanWithZones':
                setup_writer.writerow(['start_prop = ' + str(setup_object.start_prop)])
                setup_writer.writerow(['target_prop = ' + str(setup_object.target_prop)])

            if setup_object.analysis_type == 'MarxanWithZones' or setup_object.analysis_type == 'PrioritizrWithZones':
                setup_writer.writerow(['zones_bound_flag = ' + str(setup_object.zones_bound_flag)])

    except PermissionError:
        critical_message('Failed to save', 'You do not have permission to save the CLUZ setup file in the specified folder.')
        save_successful_bool = False

    return save_successful_bool


def check_create_add_files(setup_object):
    setup_object = create_and_check_cluz_files(setup_object)
    if setup_object.setup_status == 'files_checked':
        if setup_object.analysis_type == 'Marxan' or setup_object.analysis_type == 'Prioritizr':
            check_add_pu_layer(setup_object)
        if setup_object.analysis_type == 'MarxanWithZones' or setup_object.analysis_type == 'PrioritizrWithZones':
            check_add_zones_pu_layer(setup_object)


def create_and_check_cluz_files(setup_object):
    if setup_object.setup_status == 'values_checked' and setup_object.analysis_type == 'Marxan':
        check_bool = True
        check_bool = create_and_check_target_file(setup_object, check_bool)
        check_bool = create_and_check_puvspr2_file(setup_object, check_bool)
        check_bool = create_and_check_pu_layer_file(setup_object, check_bool)
        if check_bool:
            setup_object.target_dict = make_target_dict(setup_object)
            setup_object.setup_status = 'files_checked'

    elif setup_object.setup_status == 'values_checked' and setup_object.analysis_type == 'MarxanWithZones':
        check_bool = True
        check_bool = create_and_check_zones_file(setup_object, check_bool)
        if check_bool:
            setup_object.zones_dict = make_zones_dict(setup_object)

            check_bool = create_and_check_zones_target_file(setup_object, check_bool)
            check_bool = create_and_check_puvspr2_file(setup_object, check_bool)
            check_bool = create_and_check_pu_layer_file(setup_object, check_bool)
            if check_bool:
                setup_object.target_dict = make_zones_target_dict(setup_object)
                check_bool = check_values_in_zones_target_file(setup_object, check_bool)

            if check_bool:
                setup_object.zones_prop_dict = make_zones_prop_dict(setup_object)
                setup_object.zones_target_dict = make_zones_target_zones_dict(setup_object)
                setup_object.zones_bound_cost_dict = make_zones_bound_cost_dict_from_zoneboundcost_dat(setup_object)
                setup_object.setup_status = 'files_checked'

    if setup_object.setup_status == 'values_checked' and setup_object.analysis_type == 'Prioritizr':
        check_bool = True
        check_bool = create_and_check_target_file(setup_object, check_bool)
        check_bool = create_and_check_puvspr2_file(setup_object, check_bool)
        check_bool = create_and_check_pu_layer_file(setup_object, check_bool)
        if check_bool:
            setup_object.target_dict = make_target_dict(setup_object)
            setup_object.setup_status = 'files_checked'

    return setup_object

