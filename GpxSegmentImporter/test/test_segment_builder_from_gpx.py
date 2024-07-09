import datetime
import unittest
# PyQt imports
from qgis.PyQt.QtCore import QVariant, QDateTime
# QGIS imports
from qgis.core import (QgsVectorLayer, QgsField, QgsFeature, QgsPoint)
# Plugin imports
from ..core.segment_builder_from_gpx import SegmentBuilderFromGpx
from ..core.segment_layer_builder import SegmentLayerBuilder


class TestSegmentBuilder(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.segment_builder = SegmentBuilderFromGpx()
        self.point_layer = None

    def test_build_segments(self):
        file = '././data/testdata.gpx'
        segment_layer = self.segment_builder.import_gpx_file(
            file, None, attribute_select=SegmentLayerBuilder.ATTRIBUTE_SELECT_LAST, use_wgs84=True,
            calculate_motion_attributes=False, overwrite=False
        )
        self.assertEqual(len(self.segment_builder.attribute_definitions), 5)
        self.assertEqual(self.segment_builder.attribute_definitions[0].attribute_key, "ele")
        self.assertEqual(self.segment_builder.attribute_definitions[0].datatype, "Double")
        self.assertEqual(self.segment_builder.attribute_definitions[0].selected, True)
        self.assertEqual(self.segment_builder.attribute_definitions[1].attribute_key, "time")
        self.assertEqual(self.segment_builder.attribute_definitions[1].selected, True)
        self.assertEqual(self.segment_builder.attribute_definitions[2].attribute_key, "link")
        self.assertEqual(self.segment_builder.attribute_definitions[2].selected, False)
        self.assertEqual(self.segment_builder.attribute_definitions[3].attribute_key, "data1")
        self.assertEqual(self.segment_builder.attribute_definitions[3].selected, True)
        self.assertEqual(self.segment_builder.attribute_definitions[3].datatype, "String")
        self.assertEqual(self.segment_builder.attribute_definitions[4].attribute_key, "data2")
        self.assertEqual(self.segment_builder.attribute_definitions[4].selected, True)
        self.assertEqual(self.segment_builder.attribute_definitions[4].datatype, "Integer")
        # self.assertEqual(self.segment_builder.attribute_definitions[0].example_value,
        #                  datetime.datetime(2023, 11, 17, 21, 30, 4))
        # self.assertEqual(self.segment_builder.attribute_definitions[0].selected,
        #                  datetime.datetime(2023, 11, 17, 21, 30, 4))

        self.assertEqual(segment_layer.featureCount(), 5)

    def test_build_segments_with_motion_attributes(self):
        file = '././data/testdata.gpx'
        segment_layer = self.segment_builder.import_gpx_file(
            file, None, attribute_select=SegmentLayerBuilder.ATTRIBUTE_SELECT_LAST, use_wgs84=True,
            calculate_motion_attributes=True, overwrite=False
        )
        self.assertEqual(11, len(self.segment_builder.attribute_definitions))
        self.assertEqual(self.segment_builder.attribute_definitions[0].attribute_key, "ele")
        self.assertEqual(self.segment_builder.attribute_definitions[0].datatype, "Double")
        self.assertEqual(self.segment_builder.attribute_definitions[1].attribute_key, "time")
        self.assertEqual(self.segment_builder.attribute_definitions[2].attribute_key, "link")
        self.assertEqual(self.segment_builder.attribute_definitions[3].attribute_key, "data1")
        self.assertEqual(self.segment_builder.attribute_definitions[3].datatype, "String")
        self.assertEqual(self.segment_builder.attribute_definitions[4].attribute_key, "data2")
        self.assertEqual(self.segment_builder.attribute_definitions[5].attribute_key, "_a_index")
        self.assertEqual(self.segment_builder.attribute_definitions[6].attribute_key, "_b_index")
        self.assertEqual(self.segment_builder.attribute_definitions[7].attribute_key, "_distance")
        self.assertEqual(self.segment_builder.attribute_definitions[8].attribute_key, "_duration")
        self.assertEqual(self.segment_builder.attribute_definitions[9].attribute_key, "_speed")
        self.assertEqual(self.segment_builder.attribute_definitions[10].attribute_key, "_elevation_diff")

        self.assertEqual(10, segment_layer.dataProvider().fields().size())
        self.assertEqual(10, segment_layer.fields().size())
        self.assertEqual("ele", segment_layer.fields().at(0).name())
        self.assertEqual("time", segment_layer.fields().at(1).name())
        self.assertEqual("data1", segment_layer.fields().at(2).name())
        self.assertEqual("data2", segment_layer.fields().at(3).name())
        self.assertEqual("_a_index", segment_layer.fields().at(4).name())
        self.assertEqual("_b_index", segment_layer.fields().at(5).name())
        self.assertEqual("_distance", segment_layer.fields().at(6).name())
        self.assertEqual("_duration", segment_layer.fields().at(7).name())
        self.assertEqual("_speed", segment_layer.fields().at(8).name())
        self.assertEqual("_elevation_diff", segment_layer.fields().at(9).name())

        # self.assertEqual(self.segment_builder.attribute_definitions[1].example_value,
        #                  datetime.datetime(2023, 11, 17, 21, 30, 4))
        # self.assertEqual(self.segment_builder.attribute_definitions[1].selected,
        #                  datetime.datetime(2023, 11, 17, 21, 30, 4))

        self.assertEqual(segment_layer.featureCount(), 5)
        for index, feature in enumerate(segment_layer.getFeatures()):
            if index == 0:
                self.assertEqual(feature['_a_index'], 0)
                self.assertEqual(feature['_b_index'], 1)
                self.assertEqual(feature['_duration'], 1)
                self.assertAlmostEqual(feature['_distance'], 10.3, 1)
                self.assertAlmostEqual(feature['_speed'], 37.1, 1)
                self.assertAlmostEqual(feature['_elevation_diff'], 0.7, 1)
            elif index == 1:
                self.assertEqual(feature['_a_index'], 1)
                self.assertEqual(feature['_b_index'], 2)
                self.assertEqual(feature['_duration'], 1)
                self.assertAlmostEqual(feature['_distance'], 10.3, 1)
                self.assertAlmostEqual(feature['_speed'], 37.1, 1)
                self.assertAlmostEqual(feature['_elevation_diff'], 0.4, 1)

    def test_attribute_select(self):
        file = '././data/testdata.gpx'
        segment_layer = self.segment_builder.import_gpx_file(
            file, None, attribute_select=SegmentLayerBuilder.ATTRIBUTE_SELECT_LAST, use_wgs84=True,
            calculate_motion_attributes=True, overwrite=False
        )
        self.assertEqual(segment_layer.featureCount(), 5)
        for index, feature in enumerate(segment_layer.getFeatures()):
            if index == 0:
                self.assertEqual(feature['_a_index'], 0)
                self.assertEqual(feature['_b_index'], 1)
                self.assertEqual(feature['time'].toString('hh:mm:ss'), '16:49:30')
                self.assertEqual(feature['data1'], '-14c')
                self.assertEqual(feature['data2'], 233780)

        segment_layer = self.segment_builder.import_gpx_file(
            file, None, attribute_select=SegmentLayerBuilder.ATTRIBUTE_SELECT_FIRST, use_wgs84=True,
            calculate_motion_attributes=True, overwrite=False
        )
        self.assertEqual(segment_layer.featureCount(), 5)
        for index, feature in enumerate(segment_layer.getFeatures()):
            if index == 0:
                self.assertEqual(feature['_a_index'], 0)
                self.assertEqual(feature['_b_index'], 1)
                self.assertEqual(feature['data1'], '-14a')
                self.assertEqual(feature['data2'], 233731)

        segment_layer = self.segment_builder.import_gpx_file(
            file, None, attribute_select=SegmentLayerBuilder.ATTRIBUTE_SELECT_BOTH, use_wgs84=True,
            calculate_motion_attributes=True, overwrite=False
        )
        self.assertEqual(segment_layer.featureCount(), 5)
        for index, feature in enumerate(segment_layer.getFeatures()):
            if index == 0:
                self.assertEqual(feature['_a_index'], 0)
                self.assertEqual(feature['_b_index'], 1)
                self.assertEqual(feature['a_data1'], '-14a')
                self.assertEqual(feature['b_data1'], '-14c')
                self.assertEqual(feature['a_data2'], 233731)
                self.assertEqual(feature['b_data2'], 233780)

