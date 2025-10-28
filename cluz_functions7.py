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

import qgis
from qgis.core import QgsVectorLayer
from qgis.utils import iface

from .cluz_messages import success_message, check_change_earmarked_to_available_pu, warning_message
from .cluz_make_file_dicts import update_target_csv_from_target_dict
from .cluz_display import update_pu_layer_to_show_changes_by_shifting_extent


def return_targets_met_tuple(setup_object):
    num_targets = 0
    num_targets_met = 0
    target_dict = setup_object.target_dict
    for aFeat in target_dict:
        target_list = target_dict[aFeat]
        target_amount = target_list[3]
        con_amount = target_list[4]
        if target_amount > 0:
            num_targets += 1
            if con_amount >= target_amount:
                num_targets_met += 1

    return num_targets_met, num_targets


def change_status_pu_layer(setup_object, change_status_type, change_locked_pus_bool):
    pu_layer = QgsVectorLayer(setup_object.pu_path, 'Planning units', 'ogr')
    qgis.utils.iface.setActiveLayer(pu_layer)
    pu_layer = qgis.utils.iface.activeLayer()
    provider = pu_layer.dataProvider()
    id_field_order = provider.fieldNameIndex('Unit_ID')
    status_field_order = provider.fieldNameIndex('Status')

    selected_pus = pu_layer.selectedFeatures()
    pu_layer.startEditing()

    selected_pu_id_status_dict = dict()
    for a_pu in selected_pus:
        pu_row = a_pu.id()
        pu_id = a_pu.attributes()[id_field_order]
        pu_status = a_pu.attributes()[status_field_order]
        if change_locked_pus_bool:
            selected_pu_id_status_dict[pu_id] = pu_status
            pu_layer.changeAttributeValue(pu_row, status_field_order, change_status_type)
        else:
            if pu_status == 'Available' or pu_status == 'Earmarked':
                if pu_status != change_status_type:
                    selected_pu_id_status_dict[pu_id] = str(pu_status)
                    pu_layer.changeAttributeValue(pu_row, status_field_order, change_status_type)

    pu_layer.commitChanges()
    pu_layer.removeSelection()

    return selected_pu_id_status_dict


def calc_change_abund_dict(setup_object, selected_pu_id_status_dict, status_type):
    status_bool_dict = {'Available': False, 'Conserved': True, 'Earmarked': True, 'Excluded': False}
    change_status_bool_type = status_bool_dict[status_type]

    change_abund_dict = dict()
    for pu_id in selected_pu_id_status_dict:
        pu_status = selected_pu_id_status_dict[pu_id]
        current_status_bool_type = status_bool_dict[pu_status]

        if current_status_bool_type is False and change_status_bool_type:
            try:
                pu_abund_dict = setup_object.abund_pu_key_dict[pu_id]
                for featID in pu_abund_dict:
                    abund_value = pu_abund_dict[featID]
                    try:
                        running_change = change_abund_dict[featID]
                    except KeyError:
                        running_change = 0
                    running_change += abund_value
                    change_abund_dict[featID] = running_change
            except KeyError:
                pass

        if current_status_bool_type and change_status_bool_type is False:
            try:
                pu_abund_dict = setup_object.abund_pu_key_dict[pu_id]
                for featID in pu_abund_dict:
                    abund_value = pu_abund_dict[featID]
                    try:
                        running_change = change_abund_dict[featID]
                    except KeyError:
                        running_change = 0
                    running_change -= abund_value
                    change_abund_dict[featID] = running_change
            except KeyError:
                pass

    return change_abund_dict


def update_target_dict_with_changes(setup_object, change_abund_dict):
    target_dict = setup_object.target_dict
    for feat_id in change_abund_dict:
        change_amount = change_abund_dict[feat_id]
        target_list = setup_object.target_dict[feat_id]
        con_amount = target_list[4]
        new_amount = con_amount + change_amount
        target_list[4] = new_amount
        target_dict[feat_id] = target_list

    return target_dict


# #########http://www.opengis.ch/2015/04/29/performance-for-mass-updating-features-on-layers/
def undo_status_change_in_pu_layer(setup_object):
    selected_pu_id_status_dict = setup_object.selected_pu_id_status_dict
    pu_layer = QgsVectorLayer(setup_object.pu_path, 'Planning units', 'ogr')
    provider = pu_layer.dataProvider()
    pu_id_field_order = provider.fieldNameIndex('Unit_ID')
    status_field_order = provider.fieldNameIndex('Status')

    pu_layer.startEditing()
    if status_field_order != -1:
        pu_features = pu_layer.getFeatures()
        for puFeature in pu_features:
            pu_row = puFeature.id()
            pu_attributes = puFeature.attributes()
            pu_id = pu_attributes[pu_id_field_order]
            try:
                backup_pu_status = selected_pu_id_status_dict[pu_id]
                if backup_pu_status == 'Available' or backup_pu_status == 'Earmarked' or backup_pu_status == 'Conserved' or backup_pu_status == 'Excluded':
                    pu_layer.changeAttributeValue(pu_row, status_field_order, backup_pu_status)
            except KeyError:
                pass

    pu_layer.commitChanges()
    iface.mapCanvas().refresh()


def change_best_to_earmarked_pus(setup_object):
    pu_layer = QgsVectorLayer(setup_object.pu_path, 'Planning units', 'ogr')
    pu_provider = pu_layer.dataProvider()
    id_field_order = pu_provider.fieldNameIndex('Unit_ID')
    status_field_order = pu_provider.fieldNameIndex('Status')
    best_field_order = pu_provider.fieldNameIndex('Best')

    if best_field_order == -1:
        warning_message('Incorrect format', 'The planning unit layer has no field named Best (which is produced by running Marxan). This process will terminate.')
    else:
        selected_pu_id_status_dict = change_status_make_selected_pu_id_status_dict(pu_layer, id_field_order, status_field_order, best_field_order)
        status_type = 'Earmarked'  # This works out the changes needed to update the Best PUs to Earmarked
        change_abund_dict = calc_change_abund_dict(setup_object, selected_pu_id_status_dict, status_type)
        update_target_dict_with_changes(setup_object, change_abund_dict)
        update_target_csv_from_target_dict(setup_object, setup_object.target_dict)
        success_message('Process completed', 'Planning units that were selected in the Best portfolio now have Earmarked status and the target table has been updated accordingly.')
    update_pu_layer_to_show_changes_by_shifting_extent()


def change_status_make_selected_pu_id_status_dict(pu_layer, id_field_order, status_field_order, best_field_order):
    selected_pu_id_status_dict = dict()
    pu_layer.startEditing()
    pu_features = pu_layer.getFeatures()
    for puFeature in pu_features:
        pu_row = puFeature.id()
        pu_id = puFeature.attributes()[id_field_order]
        pu_status = puFeature.attributes()[status_field_order]
        best_status = puFeature.attributes()[best_field_order]
        if best_status == 'Selected':
            pu_layer.changeAttributeValue(pu_row, status_field_order, 'Earmarked')
            selected_pu_id_status_dict[pu_id] = pu_status
    pu_layer.commitChanges()

    return selected_pu_id_status_dict


def change_earmarked_to_available_pus(setup_object):
    pu_layer = QgsVectorLayer(setup_object.pu_path, "Planning units", "ogr")
    pu_provider = pu_layer.dataProvider()
    id_field_order = pu_provider.fieldNameIndex("Unit_ID")
    status_field_order = pu_provider.fieldNameIndex("Status")
    change_bool = check_change_earmarked_to_available_pu()
    
    if change_bool:
        earmarked_pu_id_status_dict = change_status_make_earmarked_pu_id_status_dict(pu_layer, id_field_order, status_field_order)
        change_abund_dict = calc_change_abund_dict(setup_object, earmarked_pu_id_status_dict, "Available")
        update_target_dict_with_changes(setup_object, change_abund_dict)
        update_target_csv_from_target_dict(setup_object, setup_object.target_dict)
        success_message("Process completed", "Planning units with Earmarked status have been changed to Available status and the target table has been updated accordingly.")
    update_pu_layer_to_show_changes_by_shifting_extent()


def change_status_make_earmarked_pu_id_status_dict(pu_layer, id_field_order, status_field_order):
    earmarked_pu_id_status_dict = dict()
    pu_layer.startEditing()
    pu_features = pu_layer.getFeatures()
    for puFeature in pu_features:
        pu_row = puFeature.id()
        pu_id = puFeature.attributes()[id_field_order]
        pu_status = puFeature.attributes()[status_field_order]
        if pu_status == 'Earmarked':
            pu_layer.changeAttributeValue(pu_row, status_field_order, 'Available')
            earmarked_pu_id_status_dict[pu_id] = pu_status
    pu_layer.commitChanges()

    return earmarked_pu_id_status_dict


def make_ident_dict(target_dict, pu_abund_dict):
    ident_dict = dict()
    target_met_dict = dict()
    for featID in pu_abund_dict:
        feat_amount = pu_abund_dict[featID]
        feat_name = target_dict[featID][0]
        feat_target = target_dict[featID][3]
        con_total = target_dict[featID][4]
        feat_total = target_dict[featID][5]
        prop_of_total = feat_amount / feat_total
        pc_of_total = prop_of_total * 100
        pc_of_total_string = str(round(pc_of_total, 2)) + ' %'
        if feat_target > 0:
            if con_total < feat_target:
                target_met_dict[featID] = 'Not met'
            else:
                target_met_dict[featID] = 'Met'

            prop_of_target = feat_amount / feat_target
            pc_of_target = prop_of_target * 100
            pc_of_target_string = str(round(pc_of_target, 2)) + ' %'

            prop_target_met = target_dict[featID][4] / feat_target
            pc_target_met = prop_target_met * 100
            pc_target_met_string = str(round(pc_target_met, 2)) + ' %'
        else:
            pc_of_target_string = 'No target'
            pc_target_met_string = 'No target'
            target_met_dict[featID] = 'No target'

        ident_dict[featID] = [str(featID), feat_name, str(feat_amount), pc_of_total_string, str(feat_target), pc_of_target_string, pc_target_met_string]

    return ident_dict, target_met_dict
