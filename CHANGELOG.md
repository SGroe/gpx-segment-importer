# Changelog

## v3.2 (2024-07-09)

- [Fixed] Attribute-Select string changed to upper case

## v3.1 (2024-06-11)

- [Fixed] Correct import of QgsProcessingParameterFile.Behavior.File in import-gpx-segments alg

## v3.0 (2023-11-17)

- [Feature] More date formats (including time zone aware)
- [Improvement] Major code refactoring
- [Improvement] Tests added for better stability

## v2.5 (2019-12-20)

- Add track point indices to motion attributes
- Process all track segments if more than 1 is available in GPX file
- [Fixed] Set duration to 0 instead of None if timestamps are equal

## v2.4 (2019-08-12)

- Create 3D-geometries if elevation tag is available in GPX file or track layer
- Calculate elevation_diff attribute if elevation tag is available in GPX file or track layer

## v2.3 (2019-03-04)

- Iterate over all track points to find attributes
- Use algorithm output to show number of created and skipped segments
- German translation

## v2.2 (2018-11-27)

- Add new algorithm 'Track segment creator'
- Add warning if track points with equal coordinates prevent creating segments
- Remove option to use EPSG:4326
- Deprecate 'GPX segment importer' dialog (use algorithm instead)
- Bug fixes

## v2.1 (2018-02-20)

- Importer added as QgisAlgorithm to enable usage in processing
- QGIS3 API adjustments related to QMessageBar

## v2.0 -qgis3 (2018-02-01)

- Support for QGIS3
- Use of message and progress bar

## v1.4 -qgis2 (2018-02-01)

- Use of message and progress bar

## v1.3 (2018-01-15)

- Write track layer in GeoPackage instead of ESRI Shapefile
- Store last input/output directory in QGIS settings
- Optionally calculate duration between track points

## v1.2 (2017-12-21)

- Option to add attributes from start/end/both track point(s)
- Optionally calculate distance and speed between track points

## v1.1 (2017-12-19)

- New SVG icon
- Improved boolean handling
- 
## v1.0 (2017-12-18)

- Initial release
