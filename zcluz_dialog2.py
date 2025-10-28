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

from os import listdir, path
import sys

from .zcluz_dialog2_code import update_marxan_with_zones_transform_object, zones_transform_make_input_folder, zones_transform_make_output_folder, zones_transform_copy_puvspr2_file, zones_transform_target_csv_file, zones_transform_pu_layer
from .zcluz_dialog2_code import zones_transform_zones_csv_file, zones_transform_create_clz_setup_file
from .cluz_messages import critical_message, success_message


sys.path.append(path.dirname(path.abspath(__file__)) + "/forms")
from cluz_form_zones_transform import Ui_zonesTransformDialog


class MarxanWithZonesTransformObject:
    def __init__(self):
        self.updated = False


class ZonesTransformDialog(QDialog, Ui_zonesTransformDialog):
    def __init__(self, iface, setup_object):
        QDialog.__init__(self)
        self.iface = iface
        self.setupUi(self)

        self.zoneComboBox.addItems(['2', '3', '4', '5'])
        self.zoneComboBox.setCurrentIndex(1)
        self.setupPathLabel.setText('CLUZ setup file for files that will be transformed: ' + setup_object.setup_path)
        self.setupLineEdit.setText('zones_ex1')
        self.puLineEdit.setText('zones_puLayer')
        self.targetLineEdit.setText('zones_targets')
        self.zonesLineEdit.setText('zones_details')

        self.mwzInputButton.clicked.connect(self.set_marxan_with_zones_path)
        self.folderButton.clicked.connect(self.set_transform_folder_path)
        self.okButton.clicked.connect(lambda: self.create_new_zones_cluz_files(setup_object))

        self.close()

    def set_marxan_with_zones_path(self):
        (marxanWithZonesPathNameRawText, fileTypeDetailsText) = QFileDialog.getOpenFileName(self, 'Select Marxan with Zones file', '*.exe')
        marxan_with_zones_path_name_text = path.abspath(marxanWithZonesPathNameRawText)
        if marxan_with_zones_path_name_text is not None:
            self.mwzInputLineEdit.setText(marxan_with_zones_path_name_text)

    def set_transform_folder_path(self):
        transform_path_name_raw_text = QFileDialog.getExistingDirectory(self, 'Select empty folder where new files will be saved')
        transform_path_name_text = path.abspath(transform_path_name_raw_text)
        if transform_path_name_text is not None:
            if len(listdir(transform_path_name_text)) == 0:
                self.folderLineEdit.setText(transform_path_name_text)
            else:
                critical_message('Selected folder is not empty', ' You must specify a folder that does not contain any files or subfolders.')

    def create_new_zones_cluz_files(self, setup_object):
        zones_transform_object = MarxanWithZonesTransformObject
        zones_transform_object = update_marxan_with_zones_transform_object(self, zones_transform_object)
        if zones_transform_object.updated:
            zones_transform_make_input_folder(zones_transform_object)
            zones_transform_make_output_folder(zones_transform_object)
            zones_transform_copy_puvspr2_file(setup_object, zones_transform_object)

            zones_transform_pu_layer(setup_object, zones_transform_object)
            zones_transform_target_csv_file(setup_object, zones_transform_object)
            zones_transform_zones_csv_file(zones_transform_object)

            zones_transform_create_clz_setup_file(setup_object, zones_transform_object)

        success_message('Marxan with Zones transformation: ', 'process completed.')

        self.close()
