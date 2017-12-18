from PyQt4.QtCore import QVariant
# Initialize Qt resources from file resources.py
from xml.etree import ElementTree
from qgis.core import QgsVectorLayer, QgsMapLayerRegistry, QgsField, QgsGeometry, QgsFeature, QgsPoint, QgsVectorLayer,\
    QgsCoordinateReferenceSystem
from datatype_definition import DataTypeDefinition, DataTypes
from gpx_feature_builder import GpxFeatureBuilder
from datetime import *
import os
import math


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

    def import_gpx_file(self, file_path, output_directory, use_wgs84=True, overwrite=False):
        """ Imports the data from the GPX file and create the vector layer """

        self.error_message = ''

        tree = ElementTree.parse(file_path)
        root = tree.getroot()

        vector_layer_builder = GpxFeatureBuilder(os.path.basename(file_path), use_wgs84, self.attribute_definitions)

        previous_point = None

        for track in root.findall('gpx:trk', self.namespace):
            track_segment = track.find('gpx:trkseg', self.namespace)

            for track_point in track_segment.findall('gpx:trkpt', self.namespace):

                new_point = QgsPoint(float(track_point.get('lon')), float(track_point.get('lat')))

                if previous_point is not None:
                    if self.is_equal_coordinate(previous_point, new_point):
                        # print 'Equal coordinate at ' + track_point.find('gpx:time', self.namespace).text
                        continue

                    # add a feature
                    attributes = dict()
                    for child in track_point:
                        self._add_attribute(attributes, child)
                    vector_layer_builder.add_feature([previous_point, new_point], attributes)

                previous_point = new_point

        vector_layer_builder.save_file(output_directory, overwrite)
        self.error_message = vector_layer_builder.error_message

    def _detect_attribute(self, element):
        """ Either detects the attribute or recursively finds child elements """

        if len(element) == 0:  # only elements without children
            if element.get('key') is not None:
                self.attribute_definitions.append(DataTypeDefinition(
                    element.get('key'),
                    self._detect_data_type(element.get('value')),
                    element.get('value') is not None and element.get('value') != '',
                    element.get('value')))
            else:
                self.attribute_definitions.append(DataTypeDefinition(
                    self.normalize(element.tag),
                    self._detect_data_type(element.text),
                    element.text is not None and element.text != '',
                    element.text))
        for child in element:
            self._detect_attribute(child)

    def _add_attribute(self, attributes, element):
        """ Reads and adds attributes to the feature """

        if len(element) == 0:  # only elements without children
            try:
                # check if attribute value is
                attribute = None
                if element.get('key') is not None:
                    attribute = self._get_attribute_definition(element.get('key'))
                    attribute.example_value = element.get('value')
                else:
                    attribute = self._get_attribute_definition(self.normalize(element.tag))
                    attribute.example_value = element.text

                if attribute.datatype is DataTypes.Integer and self.str_is_int(attribute.example_value) or \
                        attribute.datatype is DataTypes.Double and self.str_is_double(attribute.example_value) or \
                        attribute.datatype is DataTypes.Boolean and self.str_is_boolean(attribute.example_value) or \
                        attribute.datatype is DataTypes.String:
                    attributes[attribute.attribute_key_modified] = attribute.example_value
            except KeyError:
                pass
                # print('KeyError while reading attribute ' + self.normalize(extension.tag))
        for child in element:
            self._add_attribute(attributes, child)

    def _get_attribute_definition(self, key):
        for attribute in self.attribute_definitions:
            if key == attribute.attribute_key:
                return attribute
        return None

    def _detect_data_type(self, text):
        if self.str_is_int(text):
            return DataTypes.Integer
        elif self.str_is_double(text):
            return DataTypes.Double
        elif self.str_is_boolean(text):
            return DataTypes.Boolean
        # elif self.str_is_date(extension.text):
        #     retrun "Date"
        else:
            return DataTypes.String

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

    @staticmethod
    def str_is_int(string):
        if string is None:
            return False
        try:
            int(string)
            return True
        except ValueError:
            return False
        # except TypeError:
        #     print "TypeError int " + str(string)
        #     return False

    @staticmethod
    def str_is_boolean(string):
        if string is None:
            return False
        if string in ['true', 'false', 'TRUE', 'FALSE']:
            # other values like 1 or t should be recognized as int or string
            return True
        return False

    @staticmethod
    def str_is_double(string):
        if string is None:
            return False
        try:
            float(string)
            return True
        except ValueError:
            return False
        except TypeError:
            print "TypeError double " + str(string)
            return False

    @staticmethod
    def str_is_date(string):
        if string is None:
            return None
        elif GpxFileReader.create_date(string) is not None:
            return True
        else:
            return False

    @staticmethod
    def string_to_boolean(string):
        print string
        if string is True or string in ['true', 'TRUE', '1', 't']:
            return True
        return False

    @staticmethod
    def create_date(s):
        if s is None:
            return None
        try:
            return datetime.strptime(s, '%Y-%m-%dT%H:%M:%SZ')
        except ValueError:
            try:
                return datetime.strptime(s, '%Y-%m-%dT%H:%M:%S.%fZ')
            except ValueError:
                pass
        return None

