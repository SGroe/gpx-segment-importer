import os
# PyQt imports
from qgis.PyQt.QtCore import QVariant
# QGIS imports
from qgis.core import QgsVectorLayer, QgsField, QgsFeature, QgsGeometry
# Plugin imports
from .datatype_definition import (DataTypeDefinition, DataTypes)
from .vector_file_writer import VectorFileWriter


class SegmentLayerBuilder:
    """ Builds segment layers and features """

    def __init__(self):
        self.attribute_definitions: list[DataTypeDefinition] = list()
        self.error_message = ''
        self.equal_coordinates_count = 0
        self.track_point_count = 0

        self.segment_layer = None
        self.data_provider = None

    def initialize_layer(self, layer_name, attribute_select='Last', crs=None):
        layer_definition: str = 'LineString'
        if crs is not None:
            layer_definition = layer_definition + "?crs=epsg:" + str(crs.postgisSrid())

        self.segment_layer = QgsVectorLayer(layer_definition, layer_name, "memory")
        self.data_provider = self.segment_layer.dataProvider()

        # Build field list
        attributes: list[QgsField] = list()
        for attribute in self.attribute_definitions:
            if not attribute.selected:  # select attribute [boolean]
                continue

            for attribute_select_option in ['First', 'Last']:
                if attribute_select_option != attribute_select and attribute_select != 'Both':
                    continue

                prefix = ''  # prefix only if attribute_select = 'Both' AND not for motion attributes
                if attribute_select == 'Both'\
                        and attribute.attribute_key_modified != '_a_index' \
                        and attribute.attribute_key_modified != '_b_index' \
                        and attribute.attribute_key_modified != '_distance' \
                        and attribute.attribute_key_modified != '_duration' \
                        and attribute.attribute_key_modified != '_speed' \
                        and attribute.attribute_key_modified != '_elevation_diff':
                    if attribute_select_option == 'First':
                        prefix = 'a_'
                    elif attribute_select_option == 'Last':
                        prefix = 'b_'

                attributes.append(attribute.build_field(prefix))

        # Enter editing mode
        self.segment_layer.startEditing()
        self.data_provider.addAttributes(attributes)
        self.segment_layer.updateFields()

    def initialize_motion_attributes(self):
        self.attribute_definitions.append(DataTypeDefinition('_a_index', DataTypes.Integer, True, ''))
        self.attribute_definitions.append(DataTypeDefinition('_b_index', DataTypes.Integer, True, ''))
        self.attribute_definitions.append(DataTypeDefinition('_distance', DataTypes.Double, True, ''))
        self.attribute_definitions.append(DataTypeDefinition('_duration', DataTypes.Double, True, ''))
        self.attribute_definitions.append(DataTypeDefinition('_speed', DataTypes.Double, True, ''))
        self.attribute_definitions.append(DataTypeDefinition('_elevation_diff', DataTypes.Double, True, ''))

    def get_attribute_definition(self, key):
        for attribute in self.attribute_definitions:
            if key == attribute.attribute_key:
                return attribute
        return None

    def add_segment_feature(self, line_coordinates, attributes):
        feature = QgsFeature()
        feature.setGeometry(QgsGeometry.fromPolyline(line_coordinates))
        feature.setFields(self.segment_layer.fields(), True)
        for attribute_key in list(attributes.keys()):
            try:
                feature.setAttribute(attribute_key, attributes[attribute_key])
            except KeyError:
                pass
        self.data_provider.addFeatures([feature])

    def save_layer(self, output_directory, overwrite):
        self.segment_layer.commitChanges()

        self.error_message = ''

        if self.segment_layer.featureCount() > 0:
            self.segment_layer.updateExtents()

            # Write vector layer to file
            if output_directory is not None:
                if os.path.isdir(output_directory):
                    vector_layer_writer = VectorFileWriter(output_directory)
                    output_file_path = vector_layer_writer.write(self.segment_layer, overwrite)

                    if output_file_path is not None:
                        return QgsVectorLayer(output_file_path, os.path.basename(output_file_path), 'ogr')
                    else:
                        self.error_message = 'Writing vector layer failed...'  # TODO throw exception
                        return None
                else:
                    self.error_message = 'Cannot find output directory'  # TODO throw exception
                    return None

        return self.segment_layer
