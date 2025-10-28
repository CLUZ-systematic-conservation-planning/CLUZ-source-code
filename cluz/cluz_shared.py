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

from PyQt5 import QtCore, QtGui, QtWidgets
from qgis.PyQt.QtCore import Qt

from PyQt5.QtWidgets import QWidget


class QCustomTableWidgetItem(QtWidgets.QTableWidgetItem):  # Designed so column sort is based on value of number, not string of number
    def __init__(self, value):
        super(QCustomTableWidgetItem, self).__init__(str('%s' % value))

    def __lt__ (self, other):
        if isinstance(other, QCustomTableWidgetItem):
            self_data_value = float(self.data(QtCore.Qt.EditRole))
            other_data_value = float(other.data(QtCore.Qt.EditRole))
            return self_data_value < other_data_value
        else:
            return QtGui.QTableWidgetItem.__lt__(self, other)


# http://stackoverflow.com/questions/24971305/copy-pyqt-table-selection-including-column-and-row-headers
def copy_table_contents_to_clipboard(target_dialog, widget_name, e):
    table_widget = target_dialog.findChild(QWidget, widget_name)
    if e.modifiers() & Qt.ControlModifier:
        selected = table_widget.selectedRanges()
        if e.key() == Qt.Key_C:  # copy
            s = ''
            for r in range(selected[0].topRow(), selected[0].bottomRow() + 1):
                for c in range(selected[0].leftColumn(), selected[0].rightColumn()+1):
                    try:
                        s += str(table_widget.item(r, c).text()) + '\t'
                    except AttributeError:
                        s += '\t'
                s = s[:-1] + '\n'  # eliminate last '\t'
            target_dialog.clip.setText(s)
