# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GpxSegmentImporter
                                 A QGIS plugin
 This plugin imports an GPX file and creates short line segments between track points
                              -------------------
        begin                : 2017-12-01
        git sha              : $Format:%H$
        copyright            : (C) 2018 by Simon Gröchenig @ Salzburg Research
        email                : simon.groechenig@salzburgresearch.at
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
# Initialize Qt resources from file resources.py
# PyQt imports
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt import QtWidgets
# QGIS imports
from qgis.core import Qgis, QgsProject, QgsApplication
# Plugin classes
from ..core.segment_builder_from_gpx import SegmentBuilderFromGpx
from .attribute_table_model import AttributeTableModel
from .datatype_combo_delegate import DatatypeComboDelegate
# dialog
from .gpx_segment_importer_dialog import GpxSegmentImporterDialog
# other
import os.path


# Based on http://www.qgistutorials.com/en/docs/building_a_python_plugin.html
class GpxSegmentImporter:
    """QGIS GPX segment importer plugin. UI interaction"""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # # initialize plugin directory
        # self.plugin_dir = os.path.dirname(__file__)
        # # initialize locale
        # locale_path = os.path.join(
        #     self.plugin_dir,
        #     '../i18n',
        #     'gpx_segment_importer_{}.qm'.format(QSettings().value('locale/userLocale')[0:2]))
        #
        # if os.path.exists(locale_path):
        #     self.translator = QTranslator()
        #     self.translator.load(locale_path)
        #     QCoreApplication.installTranslator(self.translator)

        # # Declare instance attributes
        # self.actions = []
        # self.menu = self.tr(u'&GPX Segment Tools')
        # self.toolbar = self.iface.addToolBar(u'GPX Segment Toolbar')
        # self.toolbar.setObjectName(u'GPX Segment Toolbar')

        # Create the dialog (after translation) and keep reference
        self.dlg = GpxSegmentImporterDialog()

        self.dlg.btnSelectFiles.clicked.connect(self.select_gpx_files)
        self.dlg.btnOutputDirectory.clicked.connect(self.select_output_directory)

        self.gpx_files = list()
        self.output_directory = None
        self.gpx_directory_default = QSettings().value('gpx-segment-importer/default_input_dir', '')
        self.output_directory_default = QSettings().value('gpx-segment-importer/default_output_dir', '')
        self.gpx_file_reader = SegmentBuilderFromGpx()

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('gpx_segment_importer', message)

    def select_gpx_files(self):
        # Get GPX files
        self.gpx_files = QtWidgets.QFileDialog.getOpenFileNames(self.dlg, "Select GPX files ...",
                                                                self.gpx_directory_default, 'GPX tracks (*.gpx)',
                                                                options=QtWidgets.QFileDialog.ReadOnly)[0]
        if len(self.gpx_files) == 1:
            self.dlg.txtSelectedFiles.setText(str(os.path.basename(self.gpx_files[0])))
        else:
            self.dlg.txtSelectedFiles.setText(str(len(self.gpx_files)) + " files")

        # remember gpx directory path
        if len(self.gpx_files) > 0:
            self.gpx_directory_default = os.path.abspath(self.gpx_files[0])
            # save as default input directory
            QSettings().setValue("gpx-segment-importer/default_input_dir", self.gpx_directory_default)

        # load attribute data of first GPX file
        if len(self.gpx_files) >= 1:
            self.gpx_file_reader.get_table_data(self.gpx_files[0])
            self.dlg.lblFeedback.setText(self.gpx_file_reader.error_message)
            self.create_table()
            self.dlg.tableAttributes.setEnabled(True)

    def select_output_directory(self):
        if self.output_directory is None:
            self.output_directory = QtWidgets.QFileDialog.getExistingDirectory(self.dlg, "Output directory",
                                                                               self.output_directory_default,
                                                                               options=QtWidgets.QFileDialog.ReadOnly)
            if os.path.exists(self.output_directory):
                self.dlg.txtOutputDirectory.setText(str(self.output_directory))
                self.dlg.btnOutputDirectory.setText('Remove output directory')
                self.output_directory_default = self.output_directory
                # save as default output directory
                QSettings().setValue("gpx-segment-importer/default_output_dir", self.output_directory_default)
                if self.check_if_file_exists(self.output_directory, self.gpx_files):
                    self.dlg.lblFeedback.setText('Output file(s) already exist!')
            else:
                self.output_directory = None
                self.dlg.txtOutputDirectory.setText('[Create temporary layer]')
                self.dlg.btnOutputDirectory.setText('Output directory')
                self.dlg.lblFeedback.setText('')
        else:
            self.output_directory = None
            self.dlg.txtOutputDirectory.setText('[Create temporary layer]')
            self.dlg.btnOutputDirectory.setText('Output directory')

    @staticmethod
    def check_if_file_exists(directory, files):
        for f in files:
            if os.path.exists(directory + '/' + os.path.basename(f) + '.gpkg'):
                return True
        return False

    def run(self):
        """Run method that performs all the real work"""
        self.initialize()
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            self.process_gpx_files()

    def process_gpx_files(self):
        if self.gpx_files is not None and len(self.gpx_files) > 0:

            progress_message_bar = self.iface.messageBar().createMessage("Create gpx segments...")
            progress = QtWidgets.QProgressBar()
            progress.setMaximum(len(self.gpx_files))
            progress_message_bar.layout().addWidget(progress)
            self.iface.messageBar().pushWidget(progress_message_bar, Qgis.Info)

            overwrite = False
            use_wgs84 = True  # if self.dlg.chkUseWgs84.isChecked() else False
            calculate_motion_attributes = True if self.dlg.chkCalculateMotionAttributes.isChecked() else False
            attribute_select = "Both"
            if self.dlg.radioButtonFirst.isChecked():
                attribute_select = "First"
            elif self.dlg.radioButtonLast.isChecked():
                attribute_select = "Last"

            i = 0
            for gpx_file in self.gpx_files:
                layer = self.gpx_file_reader.import_gpx_file(gpx_file, self.output_directory, attribute_select,
                                                             use_wgs84, calculate_motion_attributes, overwrite)
                if layer is not None:
                    QgsProject.instance().addMapLayer(layer)

                self.dlg.lblFeedback.setText(self.gpx_file_reader.error_message)

                i += 1
                progress.setValue(i)
                if i == len(self.gpx_files):
                    self.iface.messageBar().clearWidgets()

                if self.gpx_file_reader.equal_coordinates_count > 0:
                    self.iface.messageBar().pushMessage(
                        'Error',
                        'Cannot create ' + str(self.gpx_file_reader.equal_coordinates_count) +
                        ' segments because of equal coordinates',
                        level=Qgis.Warning)

                if self.gpx_file_reader.error_message != '':
                    self.iface.messageBar().pushMessage("Error", self.gpx_file_reader.error_message,
                                                        level=Qgis.CRITICAL)

    def initialize(self):
        self.gpx_files = list()
        # self._attribute_table_data = list()
        self.dlg.tableAttributes.setEnabled(False)
        self.output_directory = None
        self.dlg.txtSelectedFiles.clear()
        self.dlg.btnOutputDirectory.setText('Output directory')
        self.dlg.txtOutputDirectory.clear()
        self.dlg.txtOutputDirectory.setText('[Create temporary layer]')
        # self.dlg.lblFeedback.setText(
        #     self.tr('This dialog will be removed in a future version. ') + self.tr(
        #         'Please use the algorithm [Import GPX segments] from the toolbox instead!'))

    def create_table(self):
        # create the view
        table_view = self.dlg.tableAttributes

        # set the table model
        header = ['Select', 'Attribute', 'Data type', 'Example data']
        tm = AttributeTableModel(self.gpx_file_reader.attribute_definitions, header, self)
        table_view.setModel(tm)

        combo_delegate = DatatypeComboDelegate(table_view)
        combo_delegate.setItems(['Boolean', 'Integer', 'Double', 'String', 'Date'])
        table_view.setItemDelegateForColumn(2, combo_delegate)

        # https://gist.github.com/Riateche/5984815
        for row in range(0, tm.rowCount()):
            table_view.openPersistentEditor(tm.index(row, 2))

        # show grid
        table_view.setShowGrid(True)
        # hide vertical header
        vertical_header = table_view.verticalHeader()
        vertical_header.setVisible(False)
        # set horizontal header properties
        horizontal_header = table_view.horizontalHeader()
        horizontal_header.setVisible(True)
        # horizontal_header.setStretchLastSection(True)
        # set column width to fit contents
        table_view.resizeColumnsToContents()
        # set row height
        for row in range(len(self.gpx_file_reader.attribute_definitions)):
            table_view.setRowHeight(row, 20)
        # disable sorting
        table_view.setSortingEnabled(False)
