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
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from qgis.PyQt.QtWidgets import QFileDialog
from qgis.core import QgsVectorLayer
from qgis.utils import iface

from os import path
from csv import reader
from time import ctime

from .cluz_messages import warning_message, critical_message
from .zcluz_display import add_zones_pu_layers


def create_and_check_zones_file(setup_object, check_bool):
    zones_csv_file_path = setup_object.zones_path
    zones_file_field_name_list = ['id', 'name']
    zones_id_list = list()
    zones_name_list = list()
    try:
        with open(zones_csv_file_path, 'rt') as f:
            zones_reader = reader(f)
            orig_header_list = next(zones_reader)
            for a_row in zones_reader:
                zones_id = int(a_row[0])
                zones_name = a_row[1]
                zones_id_list.append(zones_id)
                zones_name_list.append(zones_name)

        lowercase_header_list = list()
        for aHeader in orig_header_list:
            lowercase_header = aHeader.lower()
            lowercase_header_list.append(lowercase_header)

        for aHeader in zones_file_field_name_list:
            if lowercase_header_list.count(aHeader) == 0:
                warning_message('Formatting error:', 'the Zones table is missing a ' + aHeader + ' field. Please select a table with the correct format.')
                check_bool = False

        if len(zones_id_list) != len(set(zones_id_list)):
            warning_message('Formatting error:',
                            'At least one of the Zone ID values is duplicated. Please use different ID values for each zone')
            check_bool = False

        if len(zones_name_list) != len(set(zones_name_list)):
            warning_message('Formatting error:',
                            'At least one of the Zone ID names is duplicated. Please use different names for each zone')
            check_bool = False

    except FileNotFoundError:
        check_bool = False

    return check_bool


def create_and_check_zones_target_file(setup_object, check_bool):
    target_csv_file_path = setup_object.target_path
    setup_object.target_file_date = ctime(path.getmtime(target_csv_file_path))
    target_file_field_name_list = ['id', 'name', 'type', 'spf', 'target', 'ear+lock', 'total', 'pc_target']
    zone_id_list = setup_object.zones_dict.keys()
    try:
        with open(target_csv_file_path, 'rt') as f:
            target_reader = reader(f)
            orig_header_list = next(target_reader)

        lowercase_header_list = list()
        for a_header in orig_header_list:
            lowercase_header = a_header.lower()
            lowercase_header_list.append(lowercase_header)

        for a_header in target_file_field_name_list:
            if lowercase_header_list.count(a_header) == 0:
                warning_message('Formatting error:', 'the Target table is missing a ' + a_header + ' field. Please select a table with the correct format.')
                check_bool = False

        z_code_mismatch_error_count = 0
        for a_header in lowercase_header_list:
            if a_header[0:1] == 'z':
                zone_id_text = a_header.split('_')[0].replace('z', '')
                if int(zone_id_text) not in zone_id_list:
                    z_code_mismatch_error_count += 1
        if z_code_mismatch_error_count > 0:
            warning_message('Formatting error:', 'there is a mismatch between the Zone ID numeric codes used in the Target table and those specified in the Zones table.')
            check_bool = False

    except FileNotFoundError:
        check_bool = False

    return check_bool


def check_values_in_zones_target_file(setup_object, check_bool):
    for feat_id in setup_object.target_dict:
        target_list = setup_object.target_dict[feat_id]
        for zone_id in setup_object.zones_dict:
            zone_id_additional_list_pos_value = list(setup_object.zones_dict).index(zone_id) + 1
            prop_value_target_list_pos = 6 + (0 * len(setup_object.zones_dict)) + zone_id_additional_list_pos_value
            target_value_target_list_pos = 6 + (1 * len(setup_object.zones_dict)) + zone_id_additional_list_pos_value
            zone_prop_value = target_list[prop_value_target_list_pos]
            try:
                if zone_prop_value < 0 or zone_prop_value > 1:
                    critical_message('Target table error ', 'Proportion values specified in the target table must be numbers between 0 and 1')
                    check_bool = False
            except ValueError:
                critical_message('Target table error ', 'Proportion values specified in the target table must be numbers between 0 and 1')
                check_bool = False

    return check_bool


def check_add_zones_pu_layer(setup_object):
    if setup_object.setup_status == 'files_checked':
        if not check_zones_pu_layer_present(setup_object):
            add_zones_pu_layers(setup_object, 0)  # 0 = Position


def check_zones_pu_layer_present(setup_object):
    all_layers = iface.mapCanvas().layers()
    pu_layer_present_bool = True
    zone_pu_name_list = list()
    for a_zone_num in list(setup_object.zones_dict):
        zone_pu_layer_name = 'Z' + str(a_zone_num) + ' Planning units'
        zone_pu_name_list.append(zone_pu_layer_name)

    zones_layer_count = 0
    for aLayer in all_layers:
        if aLayer.name() in zone_pu_name_list:
            zones_layer_count += 1
            zone_pu_name_list.remove(aLayer.name())

    if zones_layer_count != len(setup_object.zones_dict):
        pu_layer_present_bool = False

    return pu_layer_present_bool
