# GPX Segment Importer
QGIS Plugin

This repository contains the source code for the plugin.

## Overview

The native GPS eXchange Format (GPX) file importer for the open-source geo-information software QGIS features multiple options to create vector layers. This includes the import of track points as a point dataset and the import of the whole track as a single linestring. If the GPX data contains attributes associated to the track points, only the track point option can be used to read and visualize those attributes. Visualizing them as line segments has not been possible so far. To overcome this missing feature, I have implemented the QGIS plugin “GPX Segment Importer” to visualize attributes as line segments between the track points.

![screenshot](img/screenshot.png)

## Features

* Available as QGIS dialog in toolbar and also as QGIS algorithm for usage in processing
* [dialog, algorithm] Read all attributes available from each track point at the segment start and/or end. This includes the timestamp and the elevation as well as any other attributes added to a track point.
* [dialog] Select one or multiple GPX files with the same data structure at once.
* [dialog] To gain full control over the data, you can edit the attribute table before creating the segment layer. You can exclude attributes, modify the attribute label and change the data type (integer, double, boolean or string) if the automatic type detection failed, e.g. at numeric data that contains “Null” or “None” values. Also, the plugin detects empty attributes and excludes it by default.
* [dialog, algorithm] Optionally calculate motion attributes (track points indices, distance, speed, duration and elevation_diff) between track points.
* [algorithm] Second algorithm 'Create track segments' to apply line segment creator to any point vector dataset that has a timestamp attribute.

## Use of plugin

The plugin is available in the QGIS plugin repository. Just open the plugin repository through the QGIS menu „Plugins” > „Manage and Install Plugins” and search for „GPX Segment Importer“. Select it and press „Install plugin”.

The dialog is available in the toolbar 'GPX Segment Toolbar' or via the menu 'Plugins' - 'GPX Segment Tools'.

The algorithms 'Import GPX segments' and 'Create track segments' are available in the toolbox (group 'GPX Segment Importer').

## Notes
* By default, the attributes of the latter track point are used for the line segment
* Consecutive track points with equal coordinates are skipped in order to avoid creating single vertex linestrings
