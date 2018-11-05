# -*- coding: utf-8 -*-

"""
/***************************************************************************
 a
                                 A QGIS plugin
 a
                              -------------------
        begin                : 2018-01-10
        copyright            : (C) 2018 by a
        email                : a
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
__author__ = 'Simon Gröchenig @ Salzburg Research'
__date__ = '2018-01-10'
__copyright__ = '(C) 2018 by Salzburg Research'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

# PyQt5 imports
from PyQt5.QtGui import QIcon
#qgis imports
from qgis.core import QgsProcessingProvider
# from processing.core.ProcessingConfig import Setting, ProcessingConfig
# plugin imports
from .gpx_segment_importer_algorithm import GpxSegmentImporterAlgorithm
from .track_segment_creator_algorithm import TrackSegmentCreatorAlgorithm


class GpxSegmentImporterProvider(QgsProcessingProvider):

    # MY_DUMMY_SETTING = 'MY_DUMMY_SETTING'

    def __init__(self):
        super().__init__()

    def id(self):
        return "GpxSegmentImporter"

    def name(self):
        """This is the name that will appear on the toolbox group.

        It is also used to create the command line name of all the
        algorithms from this provider.
        """
        return 'GPX Segment Importer'

    def icon(self):
        """We return the default icon.
        """
        return QIcon(':/plugins/GpxSegmentImporter/icon.svg')
        # return QgsProcessingProvider.icon(self)

    # def initializeSettings(self):
    #     """In this method we add settings needed to configure our
    #     provider.
    #
    #     Do not forget to call the parent method, since it takes care
    #     or automatically adding a setting for activating or
    #     deactivating the algorithms in the provider.
    #     """
    #     QgsProcessingProvider.initializeSettings(self)
    #     # ProcessingConfig.addSetting(Setting('Example algorithms',
    #     #                                     GpxSegmentImporterProvider.MY_DUMMY_SETTING,
    #     #                                     'Example setting', 'Default value'))

    def load(self):
        """In this method we add settings needed to configure our provider. """
        # ProcessingConfig.settingIcons[self.name()] = self.icon()
        # # Deactivate provider by default
        # ProcessingConfig.addSetting(Setting(self.name(), 'ACTIVATE_EXAMPLE',
        #                                     'Activate', False))
        # ProcessingConfig.addSetting(Setting('Example algorithms',
        #                                     GpxSegmentImporterProvider.MY_DUMMY_SETTING,
        #                                     'Example setting', 'Default value'))
        # ProcessingConfig.readSettings()
        self.refreshAlgorithms()
        return True

    def unload(self):
        """Setting should be removed here, so they do not appear anymore
        when the plugin is unloaded.
        """
        # ProcessingConfig.removeSetting('ACTIVATE_EXAMPLE')
        # ProcessingConfig.removeSetting(GpxSegmentImporterProvider.MY_DUMMY_SETTING)

    def loadAlgorithms(self):
        """This method is called whenever the list of algorithms should
        be updated. If the list of algorithms can change (for instance,
        if it contains algorithms from user-defined scripts and a new
        script might have been added), you should create the list again
        here.
        """
        # https://github.com/jdugge/BufferByPercentage/pull/14
        self.addAlgorithm(GpxSegmentImporterAlgorithm())
        self.addAlgorithm(TrackSegmentCreatorAlgorithm())
