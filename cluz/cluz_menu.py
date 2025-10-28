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

from qgis.PyQt.QtCore import QSettings, QCoreApplication, QTranslator, qVersion
from qgis.PyQt.QtWidgets import QMenu, QAction
from qgis.PyQt.QtGui import QIcon

from os import path

# # Import the code for the Setup Object
from .cluz_setup import CluzSetupObject

from .cluz_dialog1 import StartDialog, SetupDialog
from .cluz_dialog2 import CreateDialog, ConvertVecDialog, ConvertRasterDialog, ConvertCsvDialog
from .cluz_dialog3 import RemoveDialog, recalc_update_target_table_details
from .cluz_dialog4 import DistributionDialog, IdentifySelectedDialog, RichnessDialog, PortfolioDialog
from .cluz_dialog5 import InputsDialog, MarxanDialog, LoadDialog, CalibrateDialog, check_cluz_is_not_running_on_mac, check_marxan_path
from .cluz_dialog7 import MinpatchDialog
from .cluz_dialog9 import TargetDialog, AbundSelectDialog, MetDialog, ChangeStatusDialog, IdentifyTool
from .cluz_dialog8 import AboutDialog

from .zcluz_dialog2 import ZonesTransformDialog
from .zcluz_dialog3 import recalc_update_zones_target_table_details
from .zcluz_dialog4 import ZonesIdentifySelectedDialog
from .zcluz_dialog5 import ZonesInputsDialog, ZonesMarxanDialog, ZonesLoadDialog
from .zcluz_dialog7 import ZonesDialog, ZonesChangeStatusDialog

from .cluz_functions3 import trouble_shoot_cluz_files
from .cluz_make_file_dicts import make_abundance_pu_key_dict
from .cluz_functions7 import change_best_to_earmarked_pus, change_earmarked_to_available_pus
from .cluz_setup import check_all_relevant_files

from .zcluz_functions7 import zones_change_best_to_earmarked_pus, zones_change_earmarked_to_available_pus


class Cluz:
    def __init__(self, iface):
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = path.join(
            self.plugin_dir,
            'i18n',
            'cluz_{}.qm'.format(locale))

        self.cluz_menu = QMenu(self.iface.mainWindow())
        self.cluz_menu.setTitle('CLUZ')
        self.cluz_toolbar = self.iface.addToolBar('CLUZ')
        self.cluz_toolbar.setObjectName('CLUZ')

        # Create action that will start plugin configuration
        self.SetupAction = QAction(QIcon(path.dirname(__file__) + "/icons/cluz_menu_setup.png"), "View and edit CLUZ setup file", self.iface.mainWindow())

        self.CreateAction = QAction(QIcon(path.dirname(__file__) + "/icons/cluz_menu_create.png"), "Create initial CLUZ files", self.iface.mainWindow())
        self.ZonesTransformAction = QAction(QIcon(path.dirname(__file__) + "/icons/cluz_menu_transform.png"), "Transform CLUZ files from Marxan to Marxan with Zones format", self.iface.mainWindow())
        self.ConvertVecAction = QAction(QIcon(path.dirname(__file__) + "/icons/cluz_menu_convpoly.png"), "Convert polyline or polygon themes to Marxan abundance data", self.iface.mainWindow())
        self.ConvertRasterAction = QAction(QIcon(path.dirname(__file__) + "/icons/cluz_menu_convraster.png"), "Convert raster layer to Marxan abundance data", self.iface.mainWindow())
        self.ConvertCsvAction = QAction(QIcon(path.dirname(__file__) + "/icons/cluz_menu_convcsv.png"), "Import fields from table to Marxan abundance file", self.iface.mainWindow())

        self.RemoveAction = QAction(QIcon(path.dirname(__file__) + "/icons/cluz_menu_rem.png"), "Remove features from CLUZ tables", self.iface.mainWindow())
        self.RecalcAction = QAction(QIcon(path.dirname(__file__) + "/icons/cluz_menu_recalc.png"), "Recalculate target table data", self.iface.mainWindow())
        self.TroubleAction = QAction(QIcon(path.dirname(__file__) + "/icons/cluz_menu_trouble.png"), "Troubleshoot all CLUZ files", self.iface.mainWindow())

        self.DistributionAction = QAction(QIcon(path.dirname(__file__) + "/icons/cluz_menu_dist.png"), "Display distributions of conservation features", self.iface.mainWindow())
        self.IdentifySelectedAction = QAction(QIcon(path.dirname(__file__) + "/icons/cluz_menu_selident.png"), "Identify features in selected units", self.iface.mainWindow())
        self.RichnessAction = QAction(QIcon(path.dirname(__file__) + "/icons/cluz_menu_richness.png"), "Calculate richness scores", self.iface.mainWindow())
        self.PortfolioAction = QAction(QIcon(path.dirname(__file__) + "/icons/cluz_menu_portfolio.png"), "Calculate portfolio characteristics", self.iface.mainWindow())

        self.InputsAction = QAction(QIcon(path.dirname(__file__) + "/icons/cluz_menu_marxcreate.png"), "Create Marxan input files", self.iface.mainWindow())
        self.MarxanAction = QAction(QIcon(path.dirname(__file__) + "/icons/cluz_menu_marxan.png"), "Launch Marxan", self.iface.mainWindow())
        self.LoadAction = QAction(QIcon(path.dirname(__file__) + "/icons/cluz_menu_load.png"), "Load previous Marxan outputs", self.iface.mainWindow())
        self.CalibrateAction = QAction(QIcon(path.dirname(__file__) + "/icons/cluz_menu_calibrate.png"), "Calibrate Marxan parameters", self.iface.mainWindow())

        self.MinPatchAction = QAction(QIcon(path.dirname(__file__) + "/icons/cluz_menu_minpatch.png"), "Launch MinPatch", self.iface.mainWindow())

        self.AboutAction = QAction(QIcon(path.dirname(__file__) + "/icons/cluz_menu_about.png"), "About CLUZ", self.iface.mainWindow())

        self.TargetAction = QAction(QIcon(path.dirname(__file__) + "/icons/cluz_target.png"), "Open Target Table", self.iface.mainWindow())
        self.AbundAction = QAction(QIcon(path.dirname(__file__) + "/icons/cluz_abund.png"), "Open Abundance Table", self.iface.mainWindow())
        self.ZonesAction = QAction(QIcon(path.dirname(__file__) + "/icons/cluz_zones.png"), "Open Zones Table", self.iface.mainWindow())
        self.ZonesAction.setEnabled(False)

        self.EarmarkedToAvailableAction = QAction(QIcon(path.dirname(__file__) + "/icons/cluz_ear_avail.png"), "Change the status of the Earmarked units to Available", self.iface.mainWindow())
        self.BestToEarmarkedAction = QAction(QIcon(path.dirname(__file__) + "/icons/cluz_best_ear.png"), "Change the status of the Best units to Earmarked", self.iface.mainWindow())
        self.TargetsMetAction = QAction(QIcon(path.dirname(__file__) + "/icons/cluz_target_met.png"), "Open Marxan results table", self.iface.mainWindow())
        self.TargetsMetAction.setEnabled(False)
        self.ChangeAction = QAction(QIcon(path.dirname(__file__) + "/icons/cluz_change.png"), "Change planning unit status", self.iface.mainWindow())
        self.IdentifyAction = QAction(QIcon(path.dirname(__file__) + "/icons/cluz_identify.png"), "Identify features in planning unit", self.iface.mainWindow())

        if path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        self.SetupDialog = None
        self.startDialog = None
        self.createDialog = None
        self.zonesTransformDialog = None
        self.convertVecDialog = None
        self.convert_raster_dialog = None
        self.convert_csv_dialog = None
        self.removeDialog = None
        self.distributionDialog = None
        self.Ui_identifySelectedDialog = None
        self.richnessDialog = None
        self.portfolioDialog = None
        self.inputsDialog = None
        self.zonesInputsDialog = None
        self.marxanDialog = None
        self.zonesMarxanDialog = None
        self.loadDialog = None
        self.zonesLoadDialog = None
        self.calibrateDialog = None
        self.minpatchDialog = None
        self.aboutDialog = None
        self.abundSelectDialog = None
        self.targetDialog = None
        self.zonesDialog = None
        self.metDialog = None
        self.changeStatusDialog = None
        self.zonesChangeStatusDialog = None

    def initGui(self):
        cluz_menu_bar = self.iface.mainWindow().menuBar()
        cluz_menu_bar.insertMenu(self.iface.firstRightStandardMenu().menuAction(), self.cluz_menu)

        # Create the Setup Object
        setup_object = CluzSetupObject()
        setup_object.TargetsMetAction = self.TargetsMetAction
        setup_object.ZonesAction = self.ZonesAction
        setup_object.ConvertVecAction = self.ConvertVecAction
        setup_object.ConvertRasterAction = self.ConvertRasterAction
        setup_object.ConvertCsvAction = self.ConvertCsvAction
        setup_object.MinPatchAction = self.MinPatchAction

        # connect the action to the run method
        self.SetupAction.triggered.connect(lambda: self.run_setup_dialog(setup_object))

        self.CreateAction.triggered.connect(self.run_create_dialog)
        self.ZonesTransformAction.triggered.connect(lambda: self.run_zones_transform(setup_object))
        self.ConvertVecAction.triggered.connect(lambda: self.convert_polyline_polygon_to_abundance_data(setup_object))
        self.ConvertRasterAction.triggered.connect(lambda: self.convert_raster_to_abundance_data(setup_object))
        self.ConvertCsvAction.triggered.connect(lambda: self.convert_csv_to_abundance_data(setup_object))

        self.RemoveAction.triggered.connect(lambda: self.run_remove_features(setup_object))
        self.RecalcAction.triggered.connect(lambda: self.recalc_target_table(setup_object))
        self.TroubleAction.triggered.connect(lambda: self.run_trouble_shoot(setup_object))

        self.DistributionAction.triggered.connect(lambda: self.run_show_distribution_features(setup_object))
        self.IdentifySelectedAction.triggered.connect(lambda: self.run_identify_features_in_selected(setup_object))
        self.RichnessAction.triggered.connect(lambda: self.calc_richness(setup_object))
        self.PortfolioAction.triggered.connect(lambda: self.calc_portfolio_details(setup_object))

        self.InputsAction.triggered.connect(lambda: self.run_create_marxan_input_files(setup_object))
        self.MarxanAction.triggered.connect(lambda: self.run_marxan(setup_object))
        self.LoadAction.triggered.connect(lambda: self.load_prev_marxan_results(setup_object))
        self.CalibrateAction.triggered.connect(lambda: self.run_calibrate(setup_object))

        self.MinPatchAction.triggered.connect(lambda: self.run_minpatch(setup_object))

        self.AboutAction.triggered.connect(lambda: self.run_show_about_dialog(setup_object))

        self.TargetAction.triggered.connect(lambda: self.run_target_dialog(setup_object))
        self.AbundAction.triggered.connect(lambda: self.run_abund_select_dialog(setup_object))
        self.ZonesAction.triggered.connect(lambda: self.run_zones_dialog(setup_object))

        self.EarmarkedToAvailableAction.triggered.connect(lambda: self.change_earmarked_to_available(setup_object))
        self.BestToEarmarkedAction.triggered.connect(lambda: self.change_best_to_earmarked(setup_object))
        self.TargetsMetAction.triggered.connect(lambda: self.targets_met_dialog(setup_object))
        self.ChangeAction.triggered.connect(lambda: self.run_change_status_dialog(setup_object))
        self.IdentifyAction.triggered.connect(lambda: self.show_features_in_pu(setup_object))

        # Add actions to CLUZ menu
        self.cluz_menu.addAction(self.SetupAction)
        self.cluz_menu.addSeparator()
        self.cluz_menu.addAction(self.CreateAction)
        self.cluz_menu.addAction(self.ZonesTransformAction)
        self.cluz_menu.addAction(self.ConvertVecAction)
        self.cluz_menu.addAction(self.ConvertRasterAction)
        self.cluz_menu.addAction(self.ConvertCsvAction)
        self.cluz_menu.addSeparator()
        self.cluz_menu.addAction(self.RemoveAction)
        self.cluz_menu.addAction(self.RecalcAction)
        self.cluz_menu.addAction(self.TroubleAction)
        self.cluz_menu.addSeparator()
        self.cluz_menu.addAction(self.DistributionAction)
        self.cluz_menu.addAction(self.IdentifySelectedAction)
        self.cluz_menu.addAction(self.RichnessAction)
        self.cluz_menu.addAction(self.PortfolioAction)
        self.cluz_menu.addSeparator()
        self.cluz_menu.addAction(self.InputsAction)
        self.cluz_menu.addAction(self.MarxanAction)
        self.cluz_menu.addAction(self.LoadAction)
        self.cluz_menu.addAction(self.CalibrateAction)
        self.cluz_menu.addSeparator()
        self.cluz_menu.addAction(self.MinPatchAction)
        self.cluz_menu.addSeparator()
        self.cluz_menu.addAction(self.AboutAction)

        # Add actions as buttons on menu bar
        self.cluz_toolbar.addAction(self.TargetAction)
        self.cluz_toolbar.addAction(self.AbundAction)
        self.cluz_toolbar.addAction(self.ZonesAction)
        self.cluz_toolbar.addSeparator()
        self.cluz_toolbar.addAction(self.EarmarkedToAvailableAction)
        self.cluz_toolbar.addAction(self.TargetsMetAction)
        self.cluz_toolbar.addAction(self.BestToEarmarkedAction)
        self.cluz_toolbar.addSeparator()
        self.cluz_toolbar.addAction(self.ChangeAction)
        self.cluz_toolbar.addAction(self.IdentifyAction)
        self.cluz_toolbar.addSeparator()

    def unload(self):
        # Remove the plugin menu item and icon
        self.iface.removePluginMenu(u"&CLUZ", self.SetupAction)
        del self.cluz_toolbar

    def run_start_dialog(self, setup_object):
        self.startDialog = StartDialog(self, setup_object)
        self.startDialog.show()
        self.startDialog.exec_()

    def run_setup_dialog(self, setup_object):
        self.SetupDialog = SetupDialog(self, setup_object)
        self.SetupDialog.show()
        self.SetupDialog.exec_()

    def run_create_dialog(self):
        self.createDialog = CreateDialog(self)
        self.createDialog.show()
        self.createDialog.exec_()

    def run_zones_transform(self, setup_object):
        check_all_relevant_files(self, setup_object, StartDialog, SetupDialog)
        if setup_object.setup_status == 'files_checked':
            self.zonesTransformDialog = ZonesTransformDialog(self, setup_object)
            self.zonesTransformDialog.show()
            self.zonesTransformDialog.exec_()

    def convert_polyline_polygon_to_abundance_data(self, setup_object):
        check_all_relevant_files(self, setup_object, StartDialog, SetupDialog)
        if setup_object.setup_status == 'files_checked':
            if setup_object.abund_pu_key_dict == 'blank':
                setup_object.abund_pu_key_dict = make_abundance_pu_key_dict(setup_object)
            self.convertVecDialog = ConvertVecDialog(self, setup_object)
            self.convertVecDialog.show()
            self.convertVecDialog.exec_()

    def convert_raster_to_abundance_data(self, setup_object):
        check_all_relevant_files(self, setup_object, StartDialog, SetupDialog)
        if setup_object.setup_status == 'files_checked':
            if setup_object.abund_pu_key_dict == 'blank':
                setup_object.abund_pu_key_dict = make_abundance_pu_key_dict(setup_object)
            self.convert_raster_dialog = ConvertRasterDialog(self, setup_object)
            self.convert_raster_dialog.show()
            self.convert_raster_dialog.exec_()

    def convert_csv_to_abundance_data(self, setup_object):
        check_all_relevant_files(self, setup_object, StartDialog, SetupDialog)
        if setup_object.setup_status == 'files_checked':
            if setup_object.abund_pu_key_dict == 'blank':
                setup_object.abund_pu_key_dict = make_abundance_pu_key_dict(setup_object)
            self.convert_csv_dialog = ConvertCsvDialog(self, setup_object)
            self.convert_csv_dialog.show()
            self.convert_csv_dialog.exec_()

    def run_remove_features(self, setup_object):
        check_all_relevant_files(self, setup_object, StartDialog, SetupDialog)
        if setup_object.setup_status == 'files_checked':
            if setup_object.abund_pu_key_dict == 'blank':
                setup_object.abund_pu_key_dict = make_abundance_pu_key_dict(setup_object)
            self.removeDialog = RemoveDialog(self, setup_object)
            self.removeDialog.show()
            self.removeDialog.exec_()

    def recalc_target_table(self, setup_object):
        check_all_relevant_files(self, setup_object, StartDialog, SetupDialog)
        if setup_object.setup_status == 'files_checked':
            if setup_object.analysis_type != 'MarxanWithZones':
                recalc_update_target_table_details(setup_object)
            else:
                recalc_update_zones_target_table_details(setup_object)

    def run_trouble_shoot(self, setup_object):
        check_all_relevant_files(self, setup_object, StartDialog, SetupDialog)
        if setup_object.setup_status == 'files_checked':
            if setup_object.abund_pu_key_dict == 'blank':
                setup_object.abund_pu_key_dict = make_abundance_pu_key_dict(setup_object)
            trouble_shoot_cluz_files(setup_object)

    def run_show_distribution_features(self, setup_object):
        check_all_relevant_files(self, setup_object, StartDialog, SetupDialog)
        if setup_object.setup_status == 'files_checked':
            if setup_object.abund_pu_key_dict == 'blank':
                setup_object.abund_pu_key_dict = make_abundance_pu_key_dict(setup_object)
            self.distributionDialog = DistributionDialog(self, setup_object)
            self.distributionDialog.show()
            self.distributionDialog.exec_()

    def run_identify_features_in_selected(self, setup_object):
        check_all_relevant_files(self, setup_object, StartDialog, SetupDialog)
        if setup_object.setup_status == 'files_checked':
            if setup_object.abund_pu_key_dict == 'blank':
                setup_object.abund_pu_key_dict = make_abundance_pu_key_dict(setup_object)
            if setup_object.analysis_type != 'MarxanWithZones':
                self.Ui_identifySelectedDialog = IdentifySelectedDialog(self, setup_object)
                self.Ui_identifySelectedDialog.show()
                self.Ui_identifySelectedDialog.exec_()
            else:
                self.Ui_identifySelectedDialog = ZonesIdentifySelectedDialog(self, setup_object)
                self.Ui_identifySelectedDialog.show()
                self.Ui_identifySelectedDialog.exec_()

    def calc_richness(self, setup_object):
        check_all_relevant_files(self, setup_object, StartDialog, SetupDialog)
        if setup_object.setup_status == 'files_checked':
            if setup_object.abund_pu_key_dict == 'blank':
                setup_object.abund_pu_key_dict = make_abundance_pu_key_dict(setup_object)
            self.richnessDialog = RichnessDialog(self, setup_object)
            self.richnessDialog.show()
            self.richnessDialog.exec_()

    def calc_portfolio_details(self, setup_object):
        check_all_relevant_files(self, setup_object, StartDialog, SetupDialog)
        if setup_object.setup_status == 'files_checked':
            self.portfolioDialog = PortfolioDialog(self, setup_object)
            self.portfolioDialog.show()
            self.portfolioDialog.exec_()

    def run_create_marxan_input_files(self, setup_object):
        check_all_relevant_files(self, setup_object, StartDialog, SetupDialog)
        if setup_object.setup_status == 'files_checked':
            if setup_object.analysis_type != 'MarxanWithZones':
                self.inputsDialog = InputsDialog(self, setup_object)
                self.inputsDialog.show()
                self.inputsDialog.exec_()
            else:
                self.zonesInputsDialog = ZonesInputsDialog(self, setup_object)
                self.zonesInputsDialog.show()
                self.zonesInputsDialog.exec_()

    def run_marxan(self, setup_object):
        check_all_relevant_files(self, setup_object, StartDialog, SetupDialog)
        if setup_object.setup_status == 'files_checked':
            marxan_bool = check_cluz_is_not_running_on_mac()
            if setup_object.analysis_type != 'MarxanWithZones':
                if marxan_bool:
                    marxan_bool = check_marxan_path(setup_object, marxan_bool)
                    if marxan_bool:
                        self.marxanDialog = MarxanDialog(self, setup_object)
                        self.marxanDialog.show()
                        self.marxanDialog.exec_()
                    else:
                        self.SetupDialog = SetupDialog(self, setup_object)
                        self.SetupDialog.show()
                        self.SetupDialog.exec_()
            else:
                if marxan_bool:
                    marxan_bool = check_marxan_path(setup_object, marxan_bool)
                    if marxan_bool:
                        self.zonesMarxanDialog = ZonesMarxanDialog(self, setup_object)
                        self.zonesMarxanDialog.show()
                        self.zonesMarxanDialog.exec_()
                    else:
                        self.SetupDialog = SetupDialog(self, setup_object)
                        self.SetupDialog.show()
                        self.SetupDialog.exec_()

    def load_prev_marxan_results(self, setup_object):
        check_all_relevant_files(self, setup_object, StartDialog, SetupDialog)
        if setup_object.setup_status == 'files_checked':
            if setup_object.analysis_type != 'MarxanWithZones':
                self.loadDialog = LoadDialog(self, setup_object)
                self.loadDialog.show()
                self.loadDialog.exec_()
            else:
                self.zonesLoadDialog = ZonesLoadDialog(self, setup_object)
                self.zonesLoadDialog.show()
                self.zonesLoadDialog.exec_()

    def run_calibrate(self, setup_object):
        check_all_relevant_files(self, setup_object, StartDialog, SetupDialog)
        if setup_object.setup_status == 'files_checked':
            marxan_bool = check_cluz_is_not_running_on_mac()
            if marxan_bool:
                self.calibrateDialog = CalibrateDialog(self, setup_object)
                self.calibrateDialog.show()
                self.calibrateDialog.exec_()
            else:
                self.SetupDialog = SetupDialog(self, setup_object)
                self.SetupDialog.show()
                self.SetupDialog.exec_()

    def run_minpatch(self, setup_object):
        check_all_relevant_files(self, setup_object, StartDialog, SetupDialog)
        if setup_object.setup_status == 'files_checked':
            self.minpatchDialog = MinpatchDialog(self, setup_object)
            self.minpatchDialog.show()
            self.minpatchDialog.exec_()

    def run_show_about_dialog(self, setup_object):
        self.aboutDialog = AboutDialog(self, setup_object)
        self.aboutDialog.show()
        self.aboutDialog.exec_()

    def run_target_dialog(self, setup_object):
        check_all_relevant_files(self, setup_object, StartDialog, SetupDialog)
        if setup_object.setup_status == 'files_checked':
            self.targetDialog = TargetDialog(self, setup_object)
            self.targetDialog.show()
            self.targetDialog.exec_()

    def run_abund_select_dialog(self, setup_object):
        check_all_relevant_files(self, setup_object, StartDialog, SetupDialog)
        if setup_object.setup_status == 'files_checked':
            if setup_object.abund_pu_key_dict == 'blank':
                setup_object.abund_pu_key_dict = make_abundance_pu_key_dict(setup_object)
            self.abundSelectDialog = AbundSelectDialog(self, setup_object)
            self.abundSelectDialog.show()
            self.abundSelectDialog.exec_()

    def run_zones_dialog(self, setup_object):
        check_all_relevant_files(self, setup_object, StartDialog, SetupDialog)
        if setup_object.setup_status == 'files_checked':
            self.zonesDialog = ZonesDialog(self, setup_object)
            self.zonesDialog.show()
            self.zonesDialog.exec_()

    def change_earmarked_to_available(self, setup_object):
        check_all_relevant_files(self, setup_object, StartDialog, SetupDialog)
        if setup_object.setup_status == 'files_checked':
            if setup_object.abund_pu_key_dict == 'blank':
                setup_object.abund_pu_key_dict = make_abundance_pu_key_dict(setup_object)
            if setup_object.analysis_type != 'MarxanWithZones':
                change_earmarked_to_available_pus(setup_object)
            else:
                zones_change_earmarked_to_available_pus(setup_object)

    def targets_met_dialog(self, setup_object):
        check_all_relevant_files(self, setup_object, StartDialog, SetupDialog)
        self.metDialog = MetDialog(self, setup_object)
        self.metDialog.show()
        self.metDialog.exec_()

    def change_best_to_earmarked(self, setup_object):
        check_all_relevant_files(self, setup_object, StartDialog, SetupDialog)
        if setup_object.setup_status == 'files_checked':
            if setup_object.abund_pu_key_dict == 'blank':
                setup_object.abund_pu_key_dict = make_abundance_pu_key_dict(setup_object)
            if setup_object.analysis_type != 'MarxanWithZones':
                change_best_to_earmarked_pus(setup_object)
            else:
                zones_change_best_to_earmarked_pus(setup_object)

    def run_change_status_dialog(self, setup_object):
        check_all_relevant_files(self, setup_object, StartDialog, SetupDialog)
        if setup_object.setup_status == 'files_checked':
            if setup_object.abund_pu_key_dict == 'blank':
                setup_object.abund_pu_key_dict = make_abundance_pu_key_dict(setup_object)
            if setup_object.analysis_type != 'MarxanWithZones':
                self.changeStatusDialog = ChangeStatusDialog(self, setup_object)
                self.changeStatusDialog.show()
                self.changeStatusDialog.exec_()
            else:
                self.zonesChangeStatusDialog = ZonesChangeStatusDialog(self, setup_object)
                self.zonesChangeStatusDialog.show()
                self.zonesChangeStatusDialog.exec_()

    def show_features_in_pu(self, setup_object):
        check_all_relevant_files(self, setup_object, StartDialog, SetupDialog)
        if setup_object.setup_status == 'files_checked':
            if setup_object.abund_pu_key_dict == 'blank':
                setup_object.abund_pu_key_dict = make_abundance_pu_key_dict(setup_object)
            identify_tool = IdentifyTool(self.iface.mapCanvas(), setup_object)
            self.iface.mapCanvas().setMapTool(identify_tool)
