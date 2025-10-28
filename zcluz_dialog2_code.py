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

from qgis.core import QgsProject, QgsVectorLayer

import csv
from os import sep, mkdir, path
from shutil import copy
from itertools import combinations

from .cluz_messages import warning_message
from .zcluz_functions2 import convert_old_to_new_target_dict, create_zone_target_csv_file
from .zcluz_functions2 import create_zones_pu_layer, create_zone_zones_csv_file

# Transform to Marxan with Zones ########################################


def update_marxan_with_zones_transform_object(zones_transform_dialog, zones_transform_object):
    zones_transform_object.updated = False
    zones_transform_object_error_count = 0

    mwz_path = zones_transform_dialog.mwzInputLineEdit.text()
    if transform_check_mwz_path_ok(mwz_path) is False:
        zones_transform_object_error_count += 1
    blank_folder_path = zones_transform_dialog.folderLineEdit.text()
    if transform_check_blank_folder_path_ok(blank_folder_path) is False:
        zones_transform_object_error_count += 1

    transform_setup_file_name = zones_transform_dialog.setupLineEdit.text()
    transform_pu_layer_file_name = zones_transform_dialog.puLineEdit.text()
    transform_target_file_name = zones_transform_dialog.targetLineEdit.text()
    transform_zones_file_name = zones_transform_dialog.zonesLineEdit.text()

    file_name_list = [transform_setup_file_name, transform_pu_layer_file_name, transform_target_file_name, transform_zones_file_name]
    file_type_list = ['CLUZ setup file', 'Planning unit shapefile', 'Target csv file', 'Zones csv file']
    if transform_file_names(file_name_list, file_type_list) is False:
        zones_transform_object_error_count += 1

    if zones_transform_object_error_count == 0:
        zones_transform_object.updated = True
        zones_transform_object.marxanWithZonesPath = mwz_path
        zones_transform_object.transformFolderPath = blank_folder_path
        zones_transform_object.setupFileName = transform_setup_file_name.strip()  # Removes any whitespace from around name
        zones_transform_object.puLayerName = transform_pu_layer_file_name.strip()  # Removes any whitespace from around name
        zones_transform_object.zonesTargetCSVFileName = transform_target_file_name.strip()  # Removes any whitespace from around name
        zones_transform_object.zonesZonesCSVFileName = transform_zones_file_name.strip()  # Removes any whitespace from around name
        zones_transform_object.zoneNum = int(zones_transform_dialog.zoneComboBox.currentText())

    return zones_transform_object


def transform_check_mwz_path_ok(mwz_path):
    check_mwz_path_ok = True
    if mwz_path == '':
        warning_message('Marxan with Zones pathway', 'The Marxan with Zones pathway is blank - please specify a correct pathway.')
        check_mwz_path_ok = False
    elif path.isfile(mwz_path):
        pass
    else:
        warning_message('Marxan with Zones pathway', 'The Marxan with Zones pathway is not valid - please specify a correct pathway.')
        check_mwz_path_ok = False

    return check_mwz_path_ok


def transform_check_blank_folder_path_ok(blank_folder_path):
    check_folder_path_ok = True
    if blank_folder_path == '':
        warning_message('Folder pathway', 'The empty folder pathway is blank - please specify a correct pathway.')
        check_folder_path_ok = False
    elif path.isdir(blank_folder_path):
        pass
    else:
        warning_message('Folder pathway', 'The empty folder pathway is not valid - please specify a correct pathway.')
        check_folder_path_ok = False

    return check_folder_path_ok


def transform_file_names(file_name_list, file_type_list):
    check_file_names_ok = True
    for aNum in range(0, 4):
        a_file_name = file_name_list[aNum]
        a_file_name_type = file_type_list[aNum]
        a_stripped_file_name = a_file_name.strip()
        if a_stripped_file_name == '':
            warning_message(a_file_name_type + ' format problem', 'The ' + a_file_name_type + ' name is blank. Please specify a name.')
            check_file_names_ok = False

    return check_file_names_ok


def zones_transform_make_input_folder(zones_transform_object):
    transform_input_folder_path = zones_transform_object.transformFolderPath + sep + 'input'
    mkdir(transform_input_folder_path)


def zones_transform_make_output_folder(zones_transform_object):
    transform_output_folder_path = zones_transform_object.transformFolderPath + sep + 'output'
    mkdir(transform_output_folder_path)


def zones_transform_copy_puvspr2_file(setup_object, zones_transform_object):
    orig_puvspr2_dat_file = setup_object.input_path + sep + 'puvspr2.dat'
    transform_input_folder_path = zones_transform_object.transformFolderPath + sep + 'input'
    copy(orig_puvspr2_dat_file, transform_input_folder_path)


def zones_transform_pu_layer(setup_object, zones_transform_object):
    create_zones_pu_layer(setup_object, zones_transform_object)


def zones_transform_target_csv_file(setup_object, zones_transform_object):
    zone_target_dict = convert_old_to_new_target_dict(setup_object, zones_transform_object.zoneNum)
    create_zone_target_csv_file(zone_target_dict, zones_transform_object)


def zones_transform_zones_csv_file(zones_transform_object):
    create_zone_zones_csv_file(zones_transform_object)


def zones_transform_create_clz_setup_file(setup_object, zones_transform_object):
    transform_clz_setup_file_path = zones_transform_object.transformFolderPath + sep + zones_transform_object.setupFileName + '.clz'
    with open(transform_clz_setup_file_path, 'w', newline='', encoding='utf-8') as out_file:
        target_writer = csv.writer(out_file)

        target_writer.writerow(['analysis_type = MarxanWithZones'])
        target_writer.writerow(['decimal_places = ' + str(setup_object.decimal_places)])
        target_writer.writerow(['marxan_path = ' + zones_transform_object.marxanWithZonesPath])
        target_writer.writerow(['input_dir = ' + zones_transform_object.transformFolderPath + sep + 'input'])
        target_writer.writerow(['output_dir = ' + zones_transform_object.transformFolderPath + sep + 'output'])
        target_writer.writerow(['unit_theme = ' + zones_transform_object.transformFolderPath + sep + zones_transform_object.puLayerName + '.shp'])
        target_writer.writerow(['target_table = ' + zones_transform_object.transformFolderPath + sep + zones_transform_object.zonesTargetCSVFileName + '.csv'])
        target_writer.writerow(['zones_table = ' + zones_transform_object.transformFolderPath + sep + zones_transform_object.zonesZonesCSVFileName + '.csv'])
        target_writer.writerow(['output_name = output1'])
        target_writer.writerow(['num_iterations = 1000000'])
        target_writer.writerow(['num_runs = 10'])
        target_writer.writerow(['bound_flag = True'])
        target_writer.writerow(['blm = 0.0'])
        target_writer.writerow(['extra_flag = True'])
        target_writer.writerow(['start_prop = 0.2'])
        target_writer.writerow(['target_prop = 1.0'])
        target_writer.writerow(['zones_bound_flag = False'])

        for (zoneA, zoneB) in list(combinations(range(1, zones_transform_object.zoneNum + 1), 2)):
            target_writer.writerow(['BLM_Zone_' + str(zoneA) + '_vs_Zone_' + str(zoneB) + ' = 1.0'])


# Import Vec data #######################################################################

def zones_load_vec_themes_list(setup_object):
    zones_zones_pu_layer_name_list = list()
    for zoneID in list(setup_object.zones_dict):
        zones_pu_layer_name = 'Z' + str(zoneID) + ' ' + setup_object.zones_dict[zoneID] + ' Planning units'
        zones_zones_pu_layer_name_list.append(zones_pu_layer_name)

    list_map_items = QgsProject.instance().mapLayers()
    zones_layer_name_list = list()
    for nameCode, layer in list_map_items.items():
        layer_name = layer.name()
        try:
            layer_geom_type = layer.geometryType()
            if layer_name in zones_zones_pu_layer_name_list:
                pass
            else:
                if layer_geom_type != 0:
                    zones_layer_name_list.append(str(layer_name))
        except AttributeError:
            pass

    return zones_layer_name_list
