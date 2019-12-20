# Initialize Qt resources from file resources.py
from qgis.core import (QgsVectorLayer, QgsField, QgsGeometry, QgsFeature, QgsPointXY, QgsVectorLayer)
from .datatype_definition import (DataTypeDefinition, DataTypes)
from .gpx_feature_builder import GpxFeatureBuilder
from .geom_tools import GeomTools
from PyQt5.QtCore import QDateTime


class PointLayerReader:
    """ Reads gpx files and assembles vector layers """

    def __init__(self):
        self.attribute_definitions = list()
        self.error_message = ''
        self.equal_coordinates = 0
        self.track_point_count = 0

    def get_table_data(self, point_layer):
        """ Reads the first GPX track point and create datatype definitions from the available attributes """

        self.attribute_definitions = list()
        self.error_message = ''

        for track_point in point_layer.getFeatures():
            self.detect_attributes(track_point)
            break

        return True if self.error_message == '' else False

    def import_gpx_file(self, point_layer, timestamp_field, timestamp_format, attribute_select="Last",
                        calculate_motion_attributes=False):
        """ Imports the data from the GPX file and create the vector layer """

        if len(self.attribute_definitions) == 0:
            self.get_table_data(point_layer)

        self.error_message = ''

        if calculate_motion_attributes:
            self.attribute_definitions.append(DataTypeDefinition('_a_index', DataTypes.Integer, True, ''))
            self.attribute_definitions.append(DataTypeDefinition('_b_index', DataTypes.Integer, True, ''))
            self.attribute_definitions.append(DataTypeDefinition('_distance', DataTypes.Double, True, ''))
            self.attribute_definitions.append(DataTypeDefinition('_duration', DataTypes.Double, True, ''))
            self.attribute_definitions.append(DataTypeDefinition('_speed', DataTypes.Double, True, ''))
            self.attribute_definitions.append(DataTypeDefinition('_elevation_diff', DataTypes.Double, True, ''))

        vector_layer_builder = GpxFeatureBuilder(point_layer.sourceName(), self.attribute_definitions,
                                                 attribute_select, point_layer.sourceCrs())

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

    def detect_attributes(self, track_point):
        """ Either detects the attribute or recursively finds child elements """

        for field in track_point.fields():
            self.attribute_definitions.append(DataTypeDefinition(
                field.name(),
                # field.typeName(),
                DataTypes.detect_data_type(track_point[field.name()]),
                track_point[field.name()],
                track_point[field.name()]))

    def add_attributes(self, attributes, track_point, key_prefix):
        """ Reads and adds attributes to the feature """

        for field in track_point.fields():
            attribute = self._get_attribute_definition(field.name())
            if attribute is None:
                return
            attribute.example_value = track_point[field.name()]

            if attribute.datatype is DataTypes.Integer and DataTypes.value_is_int(attribute.example_value) or \
                    attribute.datatype is DataTypes.Double and DataTypes.value_is_double(attribute.example_value) or \
                    attribute.datatype is DataTypes.String:
                attributes[key_prefix + attribute.attribute_key_modified] = attribute.example_value
            elif attribute.datatype is DataTypes.Boolean and DataTypes.value_is_boolean(attribute.example_value):
                attributes[key_prefix + attribute.attribute_key_modified] = str(attribute.example_value)

    def _get_attribute_definition(self, key):
        for attribute in self.attribute_definitions:
            if key == attribute.attribute_key:
                return attribute
        return None
