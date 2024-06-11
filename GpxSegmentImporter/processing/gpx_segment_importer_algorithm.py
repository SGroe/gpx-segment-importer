import os
# PyQt imports
from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtGui import QIcon
# qgis imports
from qgis.core import (QgsProcessingParameterBoolean, QgsProcessingParameterEnum, QgsProcessingParameterFile,
                       QgsProcessingParameterFeatureSink, QgsProcessing, QgsFeatureSink, QgsProcessingOutputNumber,
                       QgsWkbTypes, QgsProcessingAlgorithm)
# plugin
from ..core.segment_builder_from_gpx import SegmentBuilderFromGpx


class GpxSegmentImporterAlgorithm(QgsProcessingAlgorithm):
    """This is an example algorithm that takes a vector layer and
    creates a new one just with just those features of the input
    layer that are selected.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the GeoAlgorithm class.
    """

    def __init__(self):
        super().__init__()

        # Constants used to refer to parameters and outputs. They will be
        # used when calling the algorithm from another algorithm, or when
        # calling from the QGIS console.

        self.alg_name = self.tr("Import GPX segments")
        self.alg_display_name = self.tr("Import GPX segments")
        self.alg_group = self.tr("GPX segment tools")
        self.alg_group_id = "gpx_segment_tools"

        self.INPUT = 'INPUT'
        self.ATTRIBUTE_MODE = 'ATTRIBUTE_MODE'
        self.CALCULATE_MOTION_ATTRIBUTES = 'CALCULATE_MOTION_ATTRIBUTES'
        # self.USE_EPSG_4326 = 'USE_EPSG_4326'
        self.OUTPUT = 'OUTPUT'
        self.OUTPUT_SEGMENT_COUNT = 'OUTPUT_SEGMENT_COUNT'
        self.OUTPUT_TRACK_COUNT = 'OUTPUT_TRACK_COUNT'
        self.OUTPUT_TRACK_SEGMENT_COUNT = 'OUTPUT_TRACK_SEGMENT_COUNT'
        self.OUTPUT_TRACK_POINT_COUNT = 'OUTPUT_TRACK_POINT_COUNT'
        self.OUTPUT_EQUAL_COORDINATE_COUNT = 'OUTPUT_EQUAL_COORDINATE_COUNT'

        self.attribute_mode_options = ['Both', 'First', 'Last']
        self.attribute_mode_options_labels = [self.tr('Both'), self.tr('First'), self.tr('Last')]
        self.motion_attribute_labels = ['a_index', 'b_index', 'distance', 'duration', 'speed', 'elevation_diff']

        self.gpx_file_reader = SegmentBuilderFromGpx()

    def createInstance(self):
        return GpxSegmentImporterAlgorithm()

    def name(self):
        return self.alg_name

    def displayName(self):
        return self.alg_display_name

    def groupId(self):
        return self.alg_group_id

    def group(self):
        return self.alg_group

    def icon(self):
        """
        Returns the icon
        """
        path = os.path.join(
            os.path.dirname(__file__),
            '..',
            'icon.svg')
        return QIcon(path)

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def initAlgorithm(self, configuration=None):
        """Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        self.addParameter(QgsProcessingParameterFile(
            self.INPUT,
            self.tr('Input gpx file'),
            QgsProcessingParameterFile.Behavior.File,
            'gpx', None, False
        ))
        self.addParameter(QgsProcessingParameterEnum(
            self.ATTRIBUTE_MODE,
            self.tr('Add attributes from which segment track point(s)'),
            self.attribute_mode_options_labels,
            False, 2, False))
        self.addParameter(QgsProcessingParameterBoolean(
            self.CALCULATE_MOTION_ATTRIBUTES,
            self.tr('Calculate motion attributes between track points'),
            True, True))
        # self.addParameter(QgsProcessingParameterEnum(
        #     self.CALCULATE_MOTION_ATTRIBUTES,
        #     self.tr('Calculate motion attributes between track points'),
        #     self.motion_attribute_labels,
        #     True, [0, 1, 2, 3, 4, 5], False))
        # self.addParameter(QgsProcessingParameterBoolean(
        #     self.USE_EPSG_4326,
        #     self.tr('Use \'EPSG:4326\' coordinate reference system'),
        #     True,
        #     True)
        # )

        # We add a vector layer as output
        self.addParameter(QgsProcessingParameterFeatureSink(self.OUTPUT, self.tr('Track segments'),
                                                            QgsProcessing.TypeVectorLine))

        self.addOutput(QgsProcessingOutputNumber(self.OUTPUT_SEGMENT_COUNT, self.tr('Number of segments')))
        self.addOutput(QgsProcessingOutputNumber(self.OUTPUT_TRACK_COUNT, self.tr('Number of tracks')))
        self.addOutput(QgsProcessingOutputNumber(self.OUTPUT_TRACK_SEGMENT_COUNT, self.tr('Number of track segments')))
        self.addOutput(QgsProcessingOutputNumber(self.OUTPUT_TRACK_POINT_COUNT, self.tr('Number of track points')))
        self.addOutput(QgsProcessingOutputNumber(self.OUTPUT_EQUAL_COORDINATE_COUNT,
                                                 self.tr('Number of segments which are not created because of equal  '
                                                         'coordinates')))

    def processAlgorithm(self, parameters, context, feedback):
        input_file = self.parameterAsFile(parameters, self.INPUT, context)
        attribute_mode = self.attribute_mode_options[self.parameterAsInt(parameters, self.ATTRIBUTE_MODE, context)]
        if isinstance(parameters[self.CALCULATE_MOTION_ATTRIBUTES], bool):
            calculate_motion_attributes = self.parameterAsBool(parameters, self.CALCULATE_MOTION_ATTRIBUTES, context)
            if calculate_motion_attributes:
                calculate_motion_attributes_list = [1, 1, 1, 1, 1, 1]
            else:
                calculate_motion_attributes_list = [0, 0, 0, 0, 0, 0]
        else:
            calculate_motion_attributes_list = self.parameterAsEnums(
                parameters, self.CALCULATE_MOTION_ATTRIBUTES, context
            )
            calculate_motion_attributes = True  # TODO use attribute list

        use_epsg4326 = True  # self.parameterAsBool(parameters, self.USE_EPSG_4326, context)

        layer = self.gpx_file_reader.import_gpx_file(
            input_file, None, attribute_mode, use_epsg4326, calculate_motion_attributes, False
        )

        if self.gpx_file_reader.error_message != '':
            feedback.reportError(self.gpx_file_reader.error_message, True)

        (sink, dest_id) = self.parameterAsSink(parameters, self.OUTPUT, context,
                                               layer.fields(), QgsWkbTypes.LineString, layer.sourceCrs())

        total = 100.0 / layer.featureCount() if layer.featureCount() else 0

        for current, f in enumerate(layer.getFeatures()):
            # Stop the algorithm if cancel button has been clicked
            if feedback.isCanceled():
                break

            # Add a feature in the sink
            sink.addFeature(f, QgsFeatureSink.FastInsert)

            # Update the progress bar
            feedback.setProgress(int(current * total))

        return {
            self.OUTPUT: dest_id,
            self.OUTPUT_SEGMENT_COUNT: layer.featureCount(),
            self.OUTPUT_TRACK_COUNT: self.gpx_file_reader.track_count,
            self.OUTPUT_TRACK_SEGMENT_COUNT: self.gpx_file_reader.track_segment_count,
            self.OUTPUT_TRACK_POINT_COUNT: self.gpx_file_reader.track_point_count,
            self.OUTPUT_EQUAL_COORDINATE_COUNT: self.gpx_file_reader.equal_coordinates_count
        }
