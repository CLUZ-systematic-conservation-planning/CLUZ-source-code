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

from .cluz_setup import update_clz_setup_file
from .cluz_dialog5_code import check_marxan_files_exist_bool
from .cluz_dialog6_code import set_prioritizr_dialog_parameters, make_prioritizr_raw_parameter_dict, make_prioritizr_parameter_dict
from .cluz_dialog6_code import launch_prioritizr_analysis, make_prioritizr_pathways_dict
from .cluz_functions5 import create_spec_dat_file
from .cluz_functions6 import prioritizr_update_setup_object

from cluz_form_prioritizr import Ui_prioritizrDialog

from .cluz_functions5 import add_best_marxan_output_to_pu_shapefile
from .cluz_display import display_best_output, remove_previous_marxan_layers, reload_pu_layer


class PrioritizrDialog(QDialog, Ui_prioritizrDialog):
    def __init__(self, iface, setup_object):
        QDialog.__init__(self)
        self.iface = iface
        self.setupUi(self)
        set_prioritizr_dialog_parameters(self, setup_object)
        self.startButton.clicked.connect(lambda: self.run_prioritizr(setup_object))
    def run_prioritizr(self, setup_object):
        prioritizr_raw_parameter_dict = make_prioritizr_raw_parameter_dict(self, setup_object)
        marxan_files_exist_bool = check_marxan_files_exist_bool(setup_object)
        if marxan_files_exist_bool:
            prioritizr_parameter_dict = make_prioritizr_parameter_dict(prioritizr_raw_parameter_dict)
            prioritizr_pathways_dict = make_prioritizr_pathways_dict(setup_object)
            create_spec_dat_file(setup_object)
            setup_object = prioritizr_update_setup_object(self, setup_object, prioritizr_parameter_dict)
            update_clz_setup_file(setup_object, True)  # saveSuccessfulBool = True
            self.close()

            best_layer_name = 'Best (' + prioritizr_parameter_dict['output_name'] + ')'

            best_output_file = launch_prioritizr_analysis(setup_object, prioritizr_parameter_dict, prioritizr_pathways_dict)

            add_best_marxan_output_to_pu_shapefile(setup_object, best_output_file, 'Best')

            remove_previous_marxan_layers()
            reload_pu_layer(setup_object)
            display_best_output(setup_object, 'Best', best_layer_name)  # Added second to be on top

