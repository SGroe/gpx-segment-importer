# Initialize Qt resources from file resources.py
from xml.etree import ElementTree
from qgis.core import QgsVectorLayer, QgsField, QgsGeometry, QgsFeature, QgsPoint, QgsVectorLayer,\
    QgsCoordinateReferenceSystem
from .datatype_definition import DataTypeDefinition, DataTypes
from .gpx_feature_builder import GpxFeatureBuilder
from .geom_tools import GeomTools
import os


class GpxFileReader:
    """ Reads gpx files and assembles vector layers """

    def __init__(self):
        self.attribute_definitions = list()
        self.namespace = None
        self.error_message = ''

    def get_table_data(self, file_path):
        """ Reads the first GPX track point and create datatype definitions from the available attributes """

        self.attribute_definitions = list()
        self.error_message = ''

        tree = ElementTree.parse(file_path)
        root = tree.getroot()

        # https://stackoverflow.com/questions/1953761/accessing-xmlns-attribute-with-python-elementree
        if root.tag[0] == "{":
            uri, ignore, tag = root.tag[1:].partition("}")
            self.namespace = {'gpx': uri}

        track = root.find('gpx:trk', self.namespace)
        if track is not None:
            track_segment = track.find('gpx:trkseg', self.namespace)
            if track_segment is not None:
                track_point = track_segment.find('gpx:trkpt', self.namespace)
                if track_point is not None:
                    for child in track_point:
                        self._detect_attribute(child)
                else:
                    self.error_message = 'Cannot find trkpt-tag in GPX file'
            else:
                self.error_message = 'Cannot find trkseg-tag in GPX file'
        else:
            self.error_message = 'Cannot find trk-tag in GPX file'

        return True if self.error_message == '' else False

    def import_gpx_file(self, file_path, output_directory, attribute_select="Last", use_wgs84=True,
                        calculate_speed=False, overwrite=False):
        """ Imports the data from the GPX file and create the vector layer """

        self.error_message = ''

        if calculate_speed:
            self.attribute_definitions.append(DataTypeDefinition('_distance', DataTypes.Double, True, ''))
            self.attribute_definitions.append(DataTypeDefinition('_duration', DataTypes.Double, True, ''))
            self.attribute_definitions.append(DataTypeDefinition('_speed', DataTypes.Double, True, ''))

        tree = ElementTree.parse(file_path)
        root = tree.getroot()

        vector_layer_builder = GpxFeatureBuilder(os.path.basename(file_path), self.attribute_definitions,
                                                 attribute_select, use_wgs84)

        prev_track_point = None

        for track in root.findall('gpx:trk', self.namespace):
            track_segment = track.find('gpx:trkseg', self.namespace)

            for track_point in track_segment.findall('gpx:trkpt', self.namespace):
                if prev_track_point is not None:
                    previous_point = QgsPoint(float(prev_track_point.get('lon')), float(prev_track_point.get('lat')))
                    new_point = QgsPoint(float(track_point.get('lon')), float(track_point.get('lat')))

                    if self.is_equal_coordinate(previous_point, new_point):
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

                    if calculate_speed:
                        time_a = DataTypes.create_date(prev_track_point.find('gpx:time', self.namespace).text)
                        time_b = DataTypes.create_date(track_point.find('gpx:time', self.namespace).text)

                        attributes['_distance'] = GeomTools.distance(previous_point, new_point)

                        if time_a is not None or time_b is not None:
                            attributes['_duration'] = GeomTools.calculate_duration(time_a, time_b)
                            attributes['_speed'] = GeomTools.calculate_speed(time_a, time_b, previous_point, new_point)

                    vector_layer_builder.add_feature([previous_point, new_point], attributes)

                prev_track_point = track_point

        vector_layer_builder.save_file(output_directory, overwrite)
        if vector_layer_builder.error_message != '':
            self.error_message = vector_layer_builder.error_message
            print(self.error_message)

    def _detect_attribute(self, element):
        """ Either detects the attribute or recursively finds child elements """

        if len(element) == 0:  # only elements without children
            if element.get('key') is not None:
                self.attribute_definitions.append(DataTypeDefinition(
                    element.get('key'),
                    DataTypes.detect_data_type(element.get('value')),
                    element.get('value') is not None and element.get('value') != '',
                    element.get('value')))
            else:
                self.attribute_definitions.append(DataTypeDefinition(
                    self.normalize(element.tag),
                    DataTypes.detect_data_type(element.text),
                    element.text is not None and element.text != '',
                    element.text))
        for child in element:
            self._detect_attribute(child)

    def add_attributes(self, attributes, element, key_prefix):
        """ Reads and adds attributes to the feature """

        if len(element) == 0:  # only elements without children
            try:
                # check if attribute value is
                if element.get('key') is not None:
                    attribute = self._get_attribute_definition(element.get('key'))
                    attribute.example_value = element.get('value')
                else:
                    attribute = self._get_attribute_definition(self.normalize(element.tag))
                    attribute.example_value = element.text

                if attribute.datatype is DataTypes.Integer and DataTypes.str_is_int(attribute.example_value) or \
                        attribute.datatype is DataTypes.Double and DataTypes.str_is_double(attribute.example_value) or \
                        attribute.datatype is DataTypes.String:
                    attributes[key_prefix + attribute.attribute_key_modified] = attribute.example_value
                elif attribute.datatype is DataTypes.Boolean and DataTypes.str_is_boolean(attribute.example_value):
                    attributes[key_prefix + attribute.attribute_key_modified] = str(attribute.example_value)
            except KeyError:
                pass
                # print('KeyError while reading attribute ' + self.normalize(extension.tag))
        for child in element:
            self.add_attributes(attributes, child, key_prefix)

    def _get_attribute_definition(self, key):
        for attribute in self.attribute_definitions:
            if key == attribute.attribute_key:
                return attribute
        return None

    @staticmethod
    def is_equal_coordinate(previous_point, new_point):
        return previous_point.x() == new_point.x() and previous_point.y() == new_point.y()

    @staticmethod
    def normalize(name):
        if name[0] == '{':
            uri, tag = name[1:].split('}')
            return tag
        else:
            return name
