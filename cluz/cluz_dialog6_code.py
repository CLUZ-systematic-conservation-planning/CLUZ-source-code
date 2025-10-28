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

from qgis.core import QgsApplication, QgsProcessingFeedback

from os import path, pathsep, environ
from re import findall
import subprocess

from .cluz_functions5 import return_output_name
from .cluz_functions6 import waiting_for_prioritizr


# Prioritizr Dialog###########################################
def set_prioritizr_dialog_parameters(prioritizr_dialog, setup_object):
    prioritizr_dialog.boundLineEdit.setVisible(False)

    output_name = return_output_name(setup_object, '_best.txt')
    prioritizr_dialog.outputLineEdit.setText(output_name)
    blm_string = f'{round(setup_object.blm_value, 15):.15f}'.rstrip('0').rstrip('.') or '0'
    prioritizr_dialog.boundLineEdit.setText(blm_string)

    if setup_object.bound_flag:
        prioritizr_dialog.boundCheckBox.setChecked(True)
        prioritizr_dialog.boundLineEdit.setVisible(True)

    if setup_object.extra_outputs_flag:
        prioritizr_dialog.extraCheckBox.setChecked(True)


def make_prioritizr_raw_parameter_dict(prioritizr_dialog, setup_object):
    output_name = str(prioritizr_dialog.outputLineEdit.text())
    setup_object.output_name = output_name
    if prioritizr_dialog.boundCheckBox.isChecked():
        blm_value_string = prioritizr_dialog.boundLineEdit.text()
    else:
        blm_value_string = "0"
    extra_outputs_bool = prioritizr_dialog.extraCheckBox.isChecked()

    prioritizr_raw_parameter_dict = dict()
    prioritizr_raw_parameter_dict['blm_value_string'] = blm_value_string
    prioritizr_raw_parameter_dict['extra_outputs_bool'] = extra_outputs_bool
    prioritizr_raw_parameter_dict['output_name'] = output_name

    return prioritizr_raw_parameter_dict


def make_prioritizr_parameter_dict(marxan_raw_parameter_dict):
    prioritizr_parameter_dict = dict()
    prioritizr_parameter_dict['blm_value'] = float(marxan_raw_parameter_dict['blm_value_string'])
    prioritizr_parameter_dict['extra_outputs_bool'] = marxan_raw_parameter_dict['extra_outputs_bool']
    prioritizr_parameter_dict['output_name'] = marxan_raw_parameter_dict['output_name']

    return prioritizr_parameter_dict


def make_prioritizr_pathways_dict(setup_object):
    prioritizr_pathways_dict = {}
    prioritizr_pathways_list = []

    with open(setup_object.prioritizr_path, 'r') as file:
        for line in file:
            line = line.strip()  # Remove leading and trailing spaces
            if line.startswith('r_path'):
                prioritizr_pathways_dict['r_path'] = line.split('=')[1].strip()
            elif line.startswith('r_script_path'):
                prioritizr_pathways_dict['r_script_path'] = line.split('=')[1].strip()
            elif line.startswith('#'):
                continue
            else:
                prioritizr_pathways_list.append(line)

    prioritizr_pathways_dict['r_parameter_list'] = prioritizr_pathways_list

    return prioritizr_pathways_dict


def launch_prioritizr_analysis(setup_object, prioritizr_parameter_dict, prioritizr_pathways_dict):
    environ_dict = make_prioritizr_environ_dict(prioritizr_pathways_dict)

    # for environ_key in environ_dict:
    #     if environ_key == 'PATH':
    #         environ[environ_key] += environ_dict[environ_key]
    #     else:
    #         environ[environ_key] = environ_dict[environ_key]

    for environ_key, environ_value in environ_dict.items():
        if environ_key == 'PATH':
            environ[environ_key] += pathsep + environ_value
        else:
            environ[environ_key] = environ_value

    r_script_path_name = prioritizr_pathways_dict['r_script_path']
    r_path = prioritizr_pathways_dict['r_path']

    blm_value = prioritizr_parameter_dict['blm_value']
    prioritizr_output_name = prioritizr_parameter_dict['output_name']

    make_prioritizr_r_script(setup_object, 'best', r_script_path_name, blm_value, prioritizr_output_name)

    subprocess.run([r_path, r_script_path_name])
    waiting_for_prioritizr(setup_object, prioritizr_output_name)

    best_output_file = path.join(setup_object.output_path, f"{prioritizr_output_name}_best.txt")

    return best_output_file


def make_prioritizr_environ_dict(prioritizr_pathways_dict):
    prioritizr_pathways_list = prioritizr_pathways_dict['r_parameter_list']
    environ_dict = {}
    for pathway_item in prioritizr_pathways_list:
        if pathway_item.startswith('environ['):
            match = findall(r'"(.*?)"', pathway_item)
            if len(match) == 2:
                key, value = match
                environ_dict[key] = value



    return environ_dict


def make_prioritizr_r_script(setup_object, r_script_type, r_script_path_name, blm_value, output_name):
    with open(r_script_path_name, 'w', newline='', encoding='utf-8') as out_file:
        # Extract input folder path from setup_object
        input_folder_text = setup_object.input_path.replace('\\', '/')
        output_folder_text = setup_object.output_path.replace('\\', '/')

        # Write the R script content directly
        out_file.write('##CLUZ=group\n\n')
        out_file.write(f'##{r_script_type}=name\n\n')
        out_file.write('##blm={}\n\n'.format(blm_value))

        out_file.write('library(prioritizr)\n\n')
        out_file.write('Sys.setenv(GRB_LICENSE_FILE = "C:/Users/rjsmi/gurobi.lic")\n\n')
        out_file.write(f'pu_data <- read.csv("{input_folder_text}/pu.dat", header=TRUE, sep=",")\n')
        out_file.write(f'spec_data <- read.csv("{input_folder_text}/spec.dat", header=TRUE, sep=",")\n')
        out_file.write(f'puvspr_data <- read.csv("{input_folder_text}/puvspr2.dat", header=TRUE, sep=",")\n')
        out_file.write(f'bound_data <- read.csv("{input_folder_text}/bound.dat", header=TRUE, sep=",")\n')
        out_file.write('names(spec_data)[names(spec_data) == "target"] <- "amount"\n')

        out_file.write(f'problem_best <- marxan_problem(pu_data, spec_data, puvspr_data, bound_data, blm = {blm_value})\n')
        out_file.write('solution_best <- solve(problem_best)\n')
        out_file.write(f'output_best <- solution_best[, c("id", "solution_1")]\n\n')
        out_file.write(f'colnames(output_best) <- c("planning_unit", "solution")\n\n')

        out_file.write(f'write.csv(output_best, file = "{output_folder_text}/{output_name}_best.txt", row.names = FALSE)\n\n')