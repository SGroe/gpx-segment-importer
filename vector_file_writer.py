from qgis.core import QgsVectorFileWriter, QgsVectorLayer, QgsVectorLayer
import os.path


class VectorFileWriter:
    """ Writes vector layer to file """

    def __init__(self, output_directory):
        self.output_directory = output_directory

    def write(self, vector_layer, overwrite):  # TODO gpkg?
        """ Write vector file and return file path """

        output_file_path = self.output_directory + "/" + vector_layer.name() + '.shp'

        appendix = 0

        while True and appendix < 99:
            if os.path.exists(output_file_path) is False or overwrite is True:
                error = QgsVectorFileWriter.writeAsVectorFormat(vector_layer, output_file_path, 'utf-8', vector_layer.crs(),
                                                           'ESRI Shapefile')
                if error == QgsVectorFileWriter.NoError:
                    return output_file_path
                else:
                    return None
            else:
                appendix = appendix + 1
                output_file_path = self.output_directory + "/" + vector_layer.name() + '_' + str(appendix) + '.shp'
        return output_file_path
