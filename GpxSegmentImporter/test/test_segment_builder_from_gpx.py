import datetime
import unittest
# PyQt imports
from qgis.PyQt.QtCore import QVariant, QDateTime
# QGIS imports
from qgis.core import (QgsVectorLayer, QgsField, QgsFeature, QgsPoint)
# Plugin imports
from ..core.segment_builder_from_gpx import SegmentBuilderFromGpx


class TestSegmentBuilder(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.segment_builder = SegmentBuilderFromGpx()
        self.point_layer = None

    def test_build_segments(self):
        file = '././data/testdata.gpx'
        segment_layer = self.segment_builder.import_gpx_file(
            file, None, attribute_select="Last", use_wgs84=True, calculate_motion_attributes=False, overwrite=False
        )
        self.assertEqual(len(self.segment_builder.attribute_definitions), 5)
        self.assertEqual(self.segment_builder.attribute_definitions[0].attribute_key, "ele")
        self.assertEqual(self.segment_builder.attribute_definitions[0].datatype, "Double")
        self.assertEqual(self.segment_builder.attribute_definitions[1].attribute_key, "time")
        self.assertEqual(self.segment_builder.attribute_definitions[2].attribute_key, "link")
        self.assertEqual(self.segment_builder.attribute_definitions[3].attribute_key, "data1")
        self.assertEqual(self.segment_builder.attribute_definitions[3].datatype, "String")
        # self.assertEqual(self.segment_builder.attribute_definitions[0].example_value,
        #                  datetime.datetime(2023, 11, 17, 21, 30, 4))
        # self.assertEqual(self.segment_builder.attribute_definitions[0].selected,
        #                  datetime.datetime(2023, 11, 17, 21, 30, 4))

        self.assertEqual(segment_layer.featureCount(), 5)

    def test_build_segments_with_motion_attributes(self):
        file = '././data/testdata.gpx'
        segment_layer = self.segment_builder.import_gpx_file(
            file, None, attribute_select="Last", use_wgs84=True, calculate_motion_attributes=True, overwrite=False
        )
        self.assertEqual(len(self.segment_builder.attribute_definitions), 11)
        self.assertEqual(self.segment_builder.attribute_definitions[0].attribute_key, "ele")
        self.assertEqual(self.segment_builder.attribute_definitions[0].datatype, "Double")
        self.assertEqual(self.segment_builder.attribute_definitions[1].attribute_key, "time")
        self.assertEqual(self.segment_builder.attribute_definitions[2].attribute_key, "link")
        self.assertEqual(self.segment_builder.attribute_definitions[3].attribute_key, "data1")
        self.assertEqual(self.segment_builder.attribute_definitions[3].datatype, "String")
        # self.assertEqual(self.segment_builder.attribute_definitions[0].example_value,
        #                  datetime.datetime(2023, 11, 17, 21, 30, 4))
        # self.assertEqual(self.segment_builder.attribute_definitions[0].selected,
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
