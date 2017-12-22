from PyQt4.QtCore import QVariant
# Initialize Qt resources from file resources.py
from qgis.core import QgsVectorLayer, QgsField, QgsMapLayerRegistry, QgsFeature, QgsGeometry
from datatype_definition import DataTypes
from vector_file_writer import VectorFileWriter
import os


class GpxFeatureBuilder:
    """ Builds gpx layers and features """

    def __init__(self, layer_name, attribute_definitions, attribute_select='Last', use_wgs84=True):
        self.error_message = ''

        layer_definition = 'LineString?crs=epsg:4326' if use_wgs84 else 'LineString'
        self.vector_layer = QgsVectorLayer(layer_definition, layer_name, "memory")
        self.data_provider = self.vector_layer.dataProvider()

        # Enter editing mode
        self.vector_layer.startEditing()
        attributes = list()
        for attribute in attribute_definitions:
            if attribute.selected:  # select attribute [boolean]
                for attribute_select_option in ['First', 'Last']:
                    if attribute_select_option != attribute_select and attribute_select != 'Both':
                        continue

                    key = str(attribute.attribute_key_modified)
                    if attribute_select == 'Both' and attribute.attribute_key_modified != '_distance' \
                            and attribute.attribute_key_modified != '_duration' \
                            and attribute.attribute_key_modified != '_speed':
                        if attribute_select_option == 'First':
                            key = 'a_' + key
                        elif attribute_select_option == 'Last':
                            key = 'b_' + key

                    if attribute.datatype == DataTypes.Integer:  # data type [Integer|Double|String]
                        attributes.append(QgsField(key, QVariant.Int, 'Integer'))
                    elif attribute.datatype == DataTypes.Double:
                        attributes.append(QgsField(key, QVariant.Double, 'Real'))
                    elif attribute.datatype == DataTypes.Boolean:
                        # QVariant.Bool is not available for QgsField
                        attributes.append(QgsField(key, QVariant.String, 'String'))
                    # elif attribute.datatype == DataTypes.Date:
                    #     attributes.append(QgsField(key, QVariant.DateTime, 'String'))
                    elif attribute.datatype == DataTypes.String:
                        attributes.append(QgsField(key, QVariant.String, 'String'))
        self.data_provider.addAttributes(attributes)
        self.vector_layer.updateFields()

    def add_feature(self, line_coordinates, attributes):
        feature = QgsFeature()
        feature.setGeometry(QgsGeometry.fromPolyline(line_coordinates))
        feature.setFields(self.vector_layer.pendingFields(), True)
        for attribute_key in attributes.keys():
            try:
                feature.setAttribute(attribute_key, attributes[attribute_key])
            except KeyError:
                pass
        self.data_provider.addFeatures([feature])

    def save_file(self, output_directory, overwrite):
        self.vector_layer.commitChanges()

        self.error_message = ''

        if self.vector_layer.featureCount() > 0:
            self.vector_layer.updateExtents()

            # Write vector layer to file
            if output_directory is not None:
                if os.path.isdir(output_directory):
                    vector_layer_writer = VectorFileWriter(output_directory)
                    output_file_path = vector_layer_writer.write(self.vector_layer, overwrite)
                    if output_file_path is not None:
                        shp_layer = QgsVectorLayer(output_file_path, os.path.basename(output_file_path), 'ogr')
                        QgsMapLayerRegistry.instance().addMapLayer(shp_layer)
                    else:
                        self.error_message = 'Writing vector layer failed...'
                        return False
                else:
                    self.error_message = 'Cannot find output directory'
                    return False
            else:
                QgsMapLayerRegistry.instance().addMapLayer(self.vector_layer)
        return True
