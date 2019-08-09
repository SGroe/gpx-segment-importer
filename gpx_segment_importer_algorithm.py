# qgis imports
from processing.algs.qgis.QgisAlgorithm import QgisAlgorithm
# from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (Qgis, QgsProcessingAlgorithm, QgsProcessingParameterBoolean, QgsProcessingParameterEnum,
                       QgsProcessingParameterFile, QgsProcessingParameterFeatureSink, QgsProcessing, QgsFeature,
                       QgsFeatureSink, QgsProcessingOutputNumber, QgsWkbTypes)
# plugin
from .gpx_file_reader import GpxFileReader


class GpxSegmentImporterAlgorithm(QgisAlgorithm):
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

        self.INPUT = 'INPUT'
        self.ATTRIBUTE_MODE = 'ATTRIBUTE_MODE'
        self.CALCULATE_MOTION_ATTRIBUTES = 'CALCULATE_MOTION_ATTRIBUTES'
        # self.USE_EPSG_4326 = 'USE_EPSG_4326'
        self.OUTPUT = 'OUTPUT'
        self.OUTPUT_SEGMENT_COUNT = 'OUTPUT_SEGMENT_COUNT'
        self.OUTPUT_EQUAL_COORDINATE_COUNT = 'OUTPUT_EQUAL_COORDINATE_COUNT'

        self.attribute_mode_options = ['Both', 'First', 'Last']
        self.attribute_mode_options_labels = [self.tr('Both'), self.tr('First'), self.tr('Last')]

        self.gpx_file_reader = GpxFileReader()

    def name(self):
        return self.alg_name

    def displayName(self):
        return self.alg_display_name

    def group(self):
        return self.alg_group

    def initAlgorithm(self, config=None):
        """Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # We add the input vector layer. It can have any kind of geometry
        # It is a mandatory (not optional) one, hence the False argument
        # self.addParameter(QgsProcessingParameterFeatureSource(self.INPUT, self.tr('Input gpx file'),
        #                                                       [QgsProcessing.TypeVectorLine]))
        self.addParameter(QgsProcessingParameterFile(self.INPUT,
                                                     self.tr('Input gpx file'),
                                                     # QgsProcessingParameterFile.Behavior.File, '*.gpx',
                                                     0, 'gpx',
                                                     None, False))  # [ParameterVector.VECTOR_TYPE_ANY], False))
        self.addParameter(QgsProcessingParameterEnum(self.ATTRIBUTE_MODE,
                                                     self.tr('Add attributes from which segment track point(s)'),
                                                     options=self.attribute_mode_options_labels,
                                                     allowMultiple=False, defaultValue=2, optional=False))
        self.addParameter(QgsProcessingParameterBoolean(self.CALCULATE_MOTION_ATTRIBUTES,
                                                        self.tr(
                                                            'Calculate motion attributes between track points'),
                                                        defaultValue=True, optional=True))
        # self.addParameter(QgsProcessingParameterBoolean(self.USE_EPSG_4326,
        #                                                 self.tr('Use \'EPSG:4326\' coordinate reference system'),
        #                                                 True, True))

        # We add a vector layer as output
        self.addParameter(QgsProcessingParameterFeatureSink(self.OUTPUT, self.tr('Track segments'),
                                                            QgsProcessing.TypeVectorLine))

        self.addOutput(QgsProcessingOutputNumber(self.OUTPUT_SEGMENT_COUNT, self.tr('Number of segments')))
        self.addOutput(QgsProcessingOutputNumber(self.OUTPUT_EQUAL_COORDINATE_COUNT,
                                                 self.tr('Number of segments which are not created because of equal  '
                                                         'coordinates')))

    def processAlgorithm(self, parameters, context, feedback):
        pass
        input_file = self.parameterAsFile(parameters, self.INPUT, context)
        attribute_mode = self.attribute_mode_options[self.parameterAsInt(parameters, self.ATTRIBUTE_MODE, context)]
        calculate_motion_attributes = self.parameterAsBool(parameters, self.CALCULATE_MOTION_ATTRIBUTES, context)
        use_epsg4326 = True  # self.parameterAsBool(parameters, self.USE_EPSG_4326, context)

        layer = self.gpx_file_reader.import_gpx_file(input_file, None, attribute_mode, use_epsg4326,
                                                     calculate_motion_attributes, False)

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

        return {self.OUTPUT: dest_id,
                self.OUTPUT_SEGMENT_COUNT: layer.featureCount(),
                self.OUTPUT_EQUAL_COORDINATE_COUNT: self.gpx_file_reader.equal_coordintes}
