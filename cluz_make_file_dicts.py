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

from qgis.core import QgsVectorLayer

from os import path, remove, rename, sep
from csv import reader, writer
from re import findall

from .cluz_messages import clear_progress_bar, make_progress_bar, set_progress_bar_value, warning_message, critical_message


def make_lowercase_header_list(orig_header_list):
    lowercase_header_list = list()  # convert to lowercase, so it doesn't matter whether the headers or lowercase, uppercase or a mix
    for aHeader in orig_header_list:
        lowercase_header_list.append(aHeader.lower())

    return lowercase_header_list


def return_temp_path_name(path_string, file_type):
    suffix_string = '.' + file_type
    temp_number = 0
    while path.exists(path_string.replace(suffix_string, '_tmp' + str(temp_number) + suffix_string)):
        temp_number += 1
    temp_path_name = path_string.replace(suffix_string, '_tmp' + str(temp_number) + suffix_string)

    return temp_path_name


def make_target_dict(setup_object):
    target_dict = dict()
    target_csv_file_path = setup_object.target_path
    with open(target_csv_file_path, mode='rt', encoding='utf-8') as f:
        target_reader = reader(f)
        lower_header_list = [x.lower() for x in next(target_reader)]  # convert to lowercase
        for a_row in target_reader:
            try:
                feat_id = int(a_row[lower_header_list.index('id')])
                feat_list = make_target_dict_row_feat_list(a_row, lower_header_list)
                target_dict[feat_id] = feat_list

            except ValueError:
                warning_message('Target table error', 'The Target table is incorrectly formatted. Please use the Troubleshoot all CLUZ files function to identify the problem.')
                target_dict = 'blank'

    return target_dict


def make_target_dict_row_feat_list(a_row, header_list):
    feat_name = str(a_row[header_list.index('name')])
    feat_type = int(a_row[header_list.index('type')])
    feat_spf = float(a_row[header_list.index('spf')])
    feat_target = float(a_row[header_list.index('target')])
    feat_conserved = float(a_row[header_list.index('ear+cons')])
    feat_total = float(a_row[header_list.index('total')])
    feat_pc_target = float(a_row[header_list.index('pc_target')])
    feat_list = [feat_name, feat_type, feat_spf, feat_target, feat_conserved, feat_total, feat_pc_target]

    return feat_list


def return_rounded_value(setup_object, raw_value):
    decimal_places = setup_object.decimal_places
    limbo_value = round(float(raw_value), decimal_places)
    final_value = format(limbo_value, "." + str(decimal_places) + "f")

    return final_value


def remove_prefix_make_id_value(a_string):
    num_list = findall(r'[0-9]+', a_string)
    rev_num_list = num_list[::-1]
    if len(rev_num_list) > 0:
        id_value = int(rev_num_list[0])
    else:
        id_value = ''

    return id_value


def make_target_dialog_row_list(setup_object):
    target_file_header_list = make_target_file_header_list(setup_object)
    target_file_data_row_count = return_target_file_data_row_count(setup_object)
    raw_target_dialog_dict = make_raw_target_dialog_dict(setup_object)

    target_dialog_row_list = list()
    target_dialog_row_list.append(target_file_header_list)

    numeric_cols_list = list()

    target_dialog_dict = dict()
    for col_name in target_file_header_list:
        raw_value_list = raw_target_dialog_dict[col_name]
        value_list, col_type_int_or_float = format_raw_value_list_identify_numerical_cols(setup_object, raw_value_list)
        target_dialog_dict[col_name] = value_list
        if col_type_int_or_float:
            numeric_cols_list.append(col_name.lower())  # Turned to lower case to allow later comparisons

    for aRow in range(0, target_file_data_row_count):
        row_list = list()
        for col_name in target_file_header_list:
            row_list.append(target_dialog_dict[col_name][aRow])
        target_dialog_row_list.append(row_list)

    return target_dialog_row_list, numeric_cols_list


def make_target_file_header_list(setup_object):
    target_csv_file_path = setup_object.target_path
    try:
        with open(target_csv_file_path, 'rt') as f:
            target_reader = reader(f)
            target_file_header_list = next(target_reader)

    except ValueError:
        target_file_header_list = 'blank'

    return target_file_header_list


def return_target_file_data_row_count(setup_object):
    target_csv_file_path = setup_object.target_path
    with open(target_csv_file_path, 'rt') as f:
        count_reader = reader(f)
        next(count_reader)
        target_file_data_row_count = len(list(count_reader))

    return target_file_data_row_count


def make_raw_target_dialog_dict(setup_object):
    raw_target_dialog_dict = dict()
    target_csv_file_path = setup_object.target_path
    with open(target_csv_file_path, 'rt') as f:
        target_reader = reader(f)
        target_file_header_list = next(target_reader)
        for a_row in target_reader:
            for a_col in range(0, len(target_file_header_list)):
                col_name = target_file_header_list[a_col]
                try:
                    raw_column_values_list = raw_target_dialog_dict[col_name]
                except KeyError:
                    raw_column_values_list = list()
                raw_column_values_list.append(a_row[a_col])
                raw_target_dialog_dict[col_name] = raw_column_values_list

    if len(raw_target_dialog_dict) == 0:
        with open(target_csv_file_path, 'rt') as f:
            target_reader = reader(f)
            target_file_header_list = next(target_reader)
            for a_col in range(0, len(target_file_header_list)):
                col_name = target_file_header_list[a_col]
                raw_target_dialog_dict[col_name] = list()

    return raw_target_dialog_dict


def format_raw_value_list_identify_numerical_cols(setup_object, raw_value_list):
    count_int_list = list()
    count_float_list = list()
    col_type_int_or_float = False
    for aValue in raw_value_list:
        try:
            count_int_list.append(int(aValue))
        except ValueError:
            pass
        try:
            count_float_list.append(float(aValue))
        except ValueError:
            pass

    value_list = list()
    if len(raw_value_list) == len(count_int_list):
        col_type_int_or_float = True
        for aValue in raw_value_list:
            value_list.append(int(aValue))
    elif len(raw_value_list) != len(count_int_list) and len(raw_value_list) == len(count_float_list):
        col_type_int_or_float = True
        for aValue in raw_value_list:
            float_value = float(aValue)
            rounded_value = return_rounded_value(setup_object, float_value)
            value_list.append(float(rounded_value))
    else:
        for aValue in raw_value_list:
            value_list.append(aValue)

    return value_list, col_type_int_or_float


def make_abundance_pu_key_dict(setup_object):
    abund_pu_key_dict = {}
    abund_pu_key_dict_correct = True
    puvspr2_file_path = setup_object.input_path + sep + 'puvspr2.dat'

    progress_bar = make_progress_bar('Processing target file')
    row_count = 1

    with open(puvspr2_file_path, encoding="utf-8") as f:
        row_total_count = sum(1 for _ in f)

    with open(puvspr2_file_path, mode='rt', encoding='utf-8') as f:
        abund_reader = reader(f)
        next(abund_reader)
        for a_row in abund_reader:
            set_progress_bar_value(progress_bar, row_count, row_total_count)
            row_count += 1
            try:
                feat_id = int(a_row[0])
                pu_id = int(a_row[1])
                abund_value = float(a_row[2])
                try:
                    pu_abund_dict = abund_pu_key_dict[pu_id]
                except KeyError:
                    pu_abund_dict = {}
                pu_abund_dict[feat_id] = abund_value
                abund_pu_key_dict[pu_id] = pu_abund_dict
            except ValueError:
                abund_pu_key_dict_correct = False

    clear_progress_bar()


    if abund_pu_key_dict_correct is False:
        warning_message('Target table error', 'The Target table is incorrectly formatted. Please use the Troubleshoot all CLUZ files function to identify the problem.')
        abund_pu_key_dict = 'blank'

    return abund_pu_key_dict


def make_puvspr2_dat_file(setup_object):
    input_path_name = setup_object.input_path
    puvspr2_dat_path_name = input_path_name + sep + 'puvspr2.dat'

    abund_pu_key_dict = setup_object.abund_pu_key_dict
    pu_list = list(abund_pu_key_dict.keys())
    pu_list.sort()

    progress_bar = make_progress_bar('Making a new puvspr2.dat file')
    row_total_count = len(pu_list)
    row_count = 1

    with open(puvspr2_dat_path_name, 'w', newline='', encoding='utf-8') as puvspr2DatFile:
        puvspr2_dat_writer = writer(puvspr2DatFile)
        puvspr2_dat_writer.writerow(['species', 'pu', 'amount'])
        for pu_id in pu_list:
            set_progress_bar_value(progress_bar, row_count, row_total_count)
            row_count += 1

            a_pu_abund_dict = abund_pu_key_dict[pu_id]
            a_feat_list = list(a_pu_abund_dict.keys())
            a_feat_list.sort()
            for featID in a_feat_list:
                feat_amount = a_pu_abund_dict[featID]
                puvspr2_dat_writer.writerow([featID, pu_id, feat_amount])
    clear_progress_bar()


def update_target_csv_from_target_dict(setup_object, target_dict):
    update_target_csv_success_bool = True
    decimal_places = setup_object.decimal_places
    target_csv_file_path = setup_object.target_path
    text_rows = []

    with open(target_csv_file_path, mode='rt', encoding='utf-8') as f:
        target_reader = reader(f)
        orig_header_list = next(target_reader)
        text_rows.append(orig_header_list)
        lower_header_list = [x.lower() for x in orig_header_list]  # convert to lowercase

        for a_row in target_reader:
            feat_id = int(a_row[lower_header_list.index('id')])
            feat_target = float(a_row[lower_header_list.index('target')])
            ear_cons_amount = format(target_dict[feat_id][4], "." + str(decimal_places) + "f")
            total_amount = format(target_dict[feat_id][5], "." + str(decimal_places) + "f")
            pc_target = return_pc_target_value_for_target_table(target_dict, feat_id, feat_target, decimal_places)

            a_row[lower_header_list.index('ear+cons')] = ear_cons_amount
            a_row[lower_header_list.index('total')] = total_amount
            a_row[lower_header_list.index('pc_target')] = pc_target
            text_rows.append(a_row)

    try:
        with open(target_csv_file_path, 'w', newline='', encoding='utf-8') as out_file:
            target_writer = writer(out_file)
            for b_row in text_rows:
                target_writer.writerow(b_row)
    except PermissionError:
        critical_message('Update error', 'Cannot update target csv file. This is often because the file is open in another software package.')
        update_target_csv_success_bool = False

    return update_target_csv_success_bool


def change_conserved_field_name_to_ear_cons(setup_object):
    target_csv_file_path = setup_object.target_path
    text_rows = list()
    with open(target_csv_file_path, 'rt') as in_file:
        target_reader = reader(in_file)
        orig_header_list = next(target_reader)
        new_header_list = list()
        for aHeader in orig_header_list:
            if aHeader == 'Conserved':
                new_header_list.append('Ear+Cons')
            elif aHeader == 'conserved':
                new_header_list.append('ear+cons')
            else:
                new_header_list.append(aHeader)
        text_rows.append(new_header_list)

        for aRow in target_reader:
            text_rows.append(aRow)

    with open(target_csv_file_path, 'w', newline='', encoding='utf-8') as out_file:
        target_writer = writer(out_file)
        for bRow in text_rows:
            target_writer.writerow(bRow)


def return_pc_target_value_for_target_table(target_dict, feat_id, feat_target, decimal_places):
    if feat_target > 0:
        pc_target = target_dict[feat_id][4] / feat_target
        pc_target *= 100
        pc_target = round(float(pc_target), decimal_places)
        pc_target = format(pc_target, "." + str(decimal_places) + "f")
    else:
        pc_target = -1

    return pc_target


def write_bound_dat_file(setup_object, bound_results_dict, ext_edge_bool):
    bound_dat_file_path = setup_object.input_path + sep + 'bound.dat'

    progress_bar = make_progress_bar('Saving bound.dat file')
    row_total_count = len(bound_results_dict)
    row_count = 1

    with open(bound_dat_file_path, 'w', newline='', encoding='utf-8') as out_file:
        bound_dat_writer = writer(out_file)
        bound_dat_writer.writerow(['id1', 'id2', 'boundary'])
        key_list = list(bound_results_dict.keys())
        key_list.sort()
        for aKey in key_list:
            set_progress_bar_value(progress_bar, row_count, row_total_count)
            row_count += 1

            (id1, id2) = aKey
            raw_amount = bound_results_dict[aKey]
            a_amount = round(float(raw_amount), setup_object.decimal_places)
            a_amount = format(a_amount, '.' + str(setup_object.decimal_places) + 'f')
            if id1 != id2:
                bound_dat_writer.writerow([id1, id2, a_amount])
            if id1 == id2:
                if ext_edge_bool:
                    bound_dat_writer.writerow([id1, id2, a_amount])
    clear_progress_bar()


def return_lowest_unused_file_name_number(dir_path, file_name_base, ext_type_text):
    file_name_number = 1
    while path.exists(dir_path + sep + file_name_base + str(file_name_number) + ext_type_text):
        file_name_number += 1

    return file_name_number


# Add data to target table from Add data from Vec, raster, csv files #######################################################################################

def add_features_to_target_csv_file(setup_object, add_abund_dict, feat_id_list):
    temp_target_path = return_temp_path_name(setup_object.target_path, 'csv')
    with open(temp_target_path, 'w', newline='', encoding='utf-8') as tempTargetFile:
        temp_target_writer = writer(tempTargetFile)

        pu_layer = QgsVectorLayer(setup_object.pu_path, 'Planning units', 'ogr')
        add_target_dict = make_add_target_dict(pu_layer, add_abund_dict, feat_id_list)

        with open(setup_object.target_path, 'rt') as f:
            target_reader = reader(f)
            target_file_header_list = next(target_reader)
            temp_target_writer.writerow(target_file_header_list)
            for row in target_reader:
                temp_target_writer.writerow(row)

            add_target_list = list(add_target_dict.keys())
            add_target_list.sort()
            for featID in add_target_list:
                row = make_new_row_target_csv_from_add_target_list(target_file_header_list, add_target_dict, featID)
                temp_target_writer.writerow(row)

    tempTargetFile.close()
    remove(setup_object.target_path)
    rename(temp_target_path, setup_object.target_path)


def make_new_row_target_csv_from_add_target_list(target_file_header_list, add_target_dict, feat_id):
    (featCon, featTotal) = add_target_dict[feat_id]
    new_row_list = [''] * len(target_file_header_list)
    for aTargetHeaderCol in range(0, len(target_file_header_list)):
        a_target_header_name = target_file_header_list[aTargetHeaderCol]
        if a_target_header_name.lower() == 'id':
            new_row_list[aTargetHeaderCol] = str(feat_id)
        elif a_target_header_name.lower() == 'name':
            new_row_list[aTargetHeaderCol] = 'blank'
        elif a_target_header_name.lower() == 'ear+cons':
            new_row_list[aTargetHeaderCol] = str(featCon)
        elif a_target_header_name.lower() == 'total':
            new_row_list[aTargetHeaderCol] = str(featTotal)
        elif a_target_header_name.lower() == 'pc_target':
            new_row_list[aTargetHeaderCol] = '-1'
        elif a_target_header_name.lower() in ['type', 'target', 'spf']:
            new_row_list[aTargetHeaderCol] = '0'

    return new_row_list


def make_add_target_dict(pu_layer, add_abund_dict, feat_id_list):
    pu_features = pu_layer.getFeatures()
    unit_id_field = pu_layer.fields().indexFromName('Unit_ID')
    unit_status_field = pu_layer.fields().indexFromName('Status')

    add_target_dict = dict()
    for feat_id in feat_id_list:
        add_target_dict[feat_id] = (0, 0)  # [Con amount, total amount]

    for pu_feature in pu_features:
        pu_attributes = pu_feature.attributes()
        pu_id = pu_attributes[unit_id_field]
        pu_status = pu_attributes[unit_status_field]

        for b_feat_id in feat_id_list:
            try:
                pu_add_abund_dict = add_abund_dict[pu_id]
                feat_amount = pu_add_abund_dict[b_feat_id]
                feat_con, feat_total = add_target_dict[b_feat_id]
                feat_total += feat_amount
                if pu_status == 'Conserved' or pu_status == 'Earmarked':
                    feat_con += feat_amount
                add_target_dict[b_feat_id] = (feat_con, feat_total)
            except KeyError:
                pass

    return add_target_dict
