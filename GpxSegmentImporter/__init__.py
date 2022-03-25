# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GpxSegmentImporter
                                 A QGIS plugin
 This plugin imports an GPX file and creates short line segments between track points
                             -------------------
        begin                : 2017-12-01
        copyright            : (C) 2017 by Simon Gröchenig @ Salzburg Research
        email                : simon.groechenig@salzburgresearch.at
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load GpxSegmentImporter class from file GpxSegmentImporter.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from GpxSegmentImporter.gpx_segment_importer import GpxSegmentImporter
    return GpxSegmentImporter(iface)
