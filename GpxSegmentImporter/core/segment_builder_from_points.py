# PyQt imports
from qgis.PyQt.QtCore import QDateTime
# Plugin imports
from .datatype_definition import (DataTypeDefinition, DataTypes)
from .segment_layer_builder import SegmentLayerBuilder
from .geom_tools import GeomTools


class SegmentBuilderFromPoints(SegmentLayerBuilder):
    """ Reads point layers and assembles segment layers """

    def __init__(self, ):
        super().__init__()

    def read_segments(self, point_layer, timestamp_field, timestamp_format, attribute_select="Last",
                      calculate_motion_attributes=False):
        """
        Imports the data from the source layer and create the vector layer
        """

        if len(self.attribute_definitions) == 0:
            self.create_attribute_definitions(point_layer)

        self.error_message = ''

        if calculate_motion_attributes:
            self.initialize_motion_attributes()

        vector_layer_builder = self.initialize_layer(point_layer.sourceName(), attribute_select,
                                                     point_layer.sourceCrs())

        prev_track_point = None
        prev_track_point_index = -1
        self.equal_coordinates = 0
        self.track_point_count = 0

        for track_point in point_layer.getFeatures():
            self.track_point_count += 1

            if prev_track_point is not None:
                if GeomTools.is_equal_coordinate(prev_track_point.geometry().asPoint(),
                                                 track_point.geometry().asPoint()):
                    self.equal_coordinates += 1
                    continue

                # add a feature with first/last/both attributes
                attributes = dict()
                if attribute_select == 'First':
                    self.add_attributes(attributes, prev_track_point, '')
                elif attribute_select == 'Last':
                    self.add_attributes(attributes, track_point, '')
                elif attribute_select == 'Both':
                    self.add_attributes(attributes, prev_track_point, 'a_')
                    self.add_attributes(attributes, track_point, 'b_')

                if calculate_motion_attributes:
                    attributes['_a_index'] = prev_track_point_index
                    attributes['_b_index'] = self.track_point_count - 1
                    attributes['_distance'] = GeomTools.distance(prev_track_point.geometry().constGet(),
                                                                 track_point.geometry().constGet(),
                                                                 point_layer.sourceCrs())

                    time_a = None
                    time_b = None
                    if type(track_point[timestamp_field]) is QDateTime:
                        # time_a = time.localtime(prev_track_point[timestamp_field].toMSecsSinceEpoch())
                        # time_b = time.localtime(track_point[timestamp_field].toMSecsSinceEpoch())
                        time_a = prev_track_point[timestamp_field]  # .toMSecsSinceEpoch()
                        time_b = track_point[timestamp_field]  # .toMSecsSinceEpoch()
                    elif type(track_point[timestamp_field]) is str:
                        time_a = DataTypes.create_date(prev_track_point[timestamp_field], timestamp_format)
                        time_b = DataTypes.create_date(track_point[timestamp_field], timestamp_format)

                    if time_a is not None and time_b is not None:
                        attributes['_duration'] = GeomTools.calculate_duration(time_a, time_b)
                        attributes['_speed'] = GeomTools.calculate_speed(time_a, time_b,
                                                                         prev_track_point.geometry().constGet(),
                                                                         track_point.geometry().constGet(),
                                                                         point_layer.sourceCrs())
                    if prev_track_point.geometry().constGet().is3D():
                        elevation_a = prev_track_point.geometry().vertexAt(0).z()
                        elevation_b = track_point.geometry().vertexAt(0).z()
                        attributes['_elevation_diff'] = elevation_b - elevation_a

                vector_layer_builder.add_feature([prev_track_point.geometry().constGet(),
                                                  track_point.geometry().constGet()], attributes)

            prev_track_point = track_point
            prev_track_point_index = self.track_point_count - 1

        vector_layer = vector_layer_builder.save_layer(None, False)
        if vector_layer_builder.error_message != '':
            self.error_message = vector_layer_builder.error_message
            print(self.error_message)

        return vector_layer

    def create_attribute_definitions(self, point_layer):
        """ Reads the first track point and create datatype definitions from the available attributes """

        self.attribute_definitions = list()
        self.error_message = ''

        if len(point_layer.getFeatures()) > 0:
            track_point = point_layer.getFeatures()[0]
            for field in track_point.fields():
                self.attribute_definitions.append(DataTypeDefinition(
                    field.name(),
                    # field.typeName(),
                    DataTypes.detect_data_type(track_point[field.name()]),
                    track_point[field.name()],
                    track_point[field.name()]))

        return True if self.error_message == '' else False

    def add_attributes(self, attributes, track_point, key_prefix):
        """ Reads and adds attributes to the feature """

        for field in track_point.fields():
            attribute = self.get_attribute_definition(field.name())
            if attribute is None:
                return
            attribute.example_value = track_point[field.name()]

            if attribute.datatype is DataTypes.Integer and DataTypes.value_is_int(attribute.example_value) or \
                    attribute.datatype is DataTypes.Double and DataTypes.value_is_double(attribute.example_value) or \
                    attribute.datatype is DataTypes.String:
                attributes[key_prefix + attribute.attribute_key_modified] = attribute.example_value
            elif attribute.datatype is DataTypes.Boolean and DataTypes.value_is_boolean(attribute.example_value):
                attributes[key_prefix + attribute.attribute_key_modified] = str(attribute.example_value)
