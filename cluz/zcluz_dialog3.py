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

from cluz_form_remove import Ui_removeDialog

from .cluz_make_file_dicts import make_abundance_pu_key_dict
from .zcluz_dialog3_code import return_zones_earlock_amount_tot_dict, update_zones_ear_lock_tot_fields_target_dict
from .zcluz_make_file_dicts import update_zones_target_csv_from_target_dict
from .cluz_messages import success_message


def recalc_update_zones_target_table_details(setup_object):
    setup_object.abund_pu_key_dict = make_abundance_pu_key_dict(setup_object)
    new_zones_ear_lock_tot_dict = return_zones_earlock_amount_tot_dict(setup_object)
    target_dict = update_zones_ear_lock_tot_fields_target_dict(setup_object, new_zones_ear_lock_tot_dict)

    setup_object.target_dict = target_dict
    update_target_csv_success_bool = update_zones_target_csv_from_target_dict(setup_object, target_dict)

    if update_target_csv_success_bool:
        success_message('Target table updated: ', 'process completed.')