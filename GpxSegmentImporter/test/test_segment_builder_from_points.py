import datetime
import unittest
# PyQt imports
from qgis.PyQt.QtCore import QVariant, QDateTime
# QGIS imports
from qgis.core import (QgsVectorLayer, QgsField, QgsFeature, QgsPoint)
# Plugin imports
from ..core.segment_builder_from_points import SegmentBuilderFromPoints
from ..core.segment_layer_builder import SegmentLayerBuilder


class TestSegmentBuilder(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.segment_builder = SegmentBuilderFromPoints()
        self.point_layer = None

    def test_build_point_layer(self):
        self.point_layer = QgsVectorLayer("Point?crs=epsg:31255&index=yes", "test-layer", "memory")
        self.point_layer.dataProvider().addAttributes([
            QgsField('timestamp', QVariant.DateTime),
            QgsField('description', QVariant.String)
        ])
        self.point_layer.updateFields()

        self.point_layer.startEditing()
        feature1 = QgsFeature()
        feature1.setGeometry(QgsPoint(205212, -4989, 1002))
        feature1.setAttributes([datetime.datetime(2023, 11, 17, 21, 30, 4), "start point"])
        # feature1.setAttributes([QDateTime(2023, 11, 17, 21, 30, 4), "first point"])
        feature2 = QgsFeature()
        feature2.setGeometry(QgsPoint(205470, -4239, 1006.8))
        feature2.setAttributes([datetime.datetime(2023, 11, 17, 21, 31, 34), "90 seconds later"])
        feature3 = QgsFeature()
        feature3.setGeometry(QgsPoint(205470, -4239, 1006.8))
        feature3.setAttributes([datetime.datetime(2023, 11, 17, 21, 32, 4), "equal coordinate"])
        feature4 = QgsFeature()
        feature4.setGeometry(QgsPoint(205472, -4243, 1006.2))
        feature4.setAttributes([datetime.datetime(2023, 11, 17, 21, 32, 34), "equal coordinate"])

        self.assertEqual(self.point_layer.addFeatures([feature1, feature2, feature3, feature4]), True)
        self.assertEqual(self.point_layer.featureCount(), 4)
        self.point_layer.commitChanges()

    def test_build_segments(self):
        self.test_build_point_layer()
        segment_layer = self.segment_builder.build_segments(
            self.point_layer, "timestamp", '', attribute_select=SegmentLayerBuilder.ATTRIBUTE_SELECT_LAST,
            calculate_motion_attributes=False
        )
        self.assertEqual(len(self.segment_builder.attribute_definitions), 2)
        self.assertEqual(self.segment_builder.attribute_definitions[0].attribute_key, "timestamp")
        self.assertEqual(self.segment_builder.attribute_definitions[0].attribute_key_modified, "timestamp")
        self.assertEqual(self.segment_builder.attribute_definitions[0].datatype, "Date")
        self.assertNotEqual(self.segment_builder.attribute_definitions[0].datatype, "String")
        # self.assertEqual(self.segment_builder.attribute_definitions[0].example_value,
        #                  datetime.datetime(2023, 11, 17, 21, 30, 4))
        # self.assertEqual(self.segment_builder.attribute_definitions[0].selected,
        #                  datetime.datetime(2023, 11, 17, 21, 30, 4))

        self.assertEqual(segment_layer.featureCount(), 2)
        self.assertEqual(self.segment_builder.equal_coordinates_count, 1)

    def test_build_segments_with_motion_attributes(self):
        self.test_build_point_layer()
        segment_layer = self.segment_builder.build_segments(
            self.point_layer, "timestamp", '', attribute_select=SegmentLayerBuilder.ATTRIBUTE_SELECT_LAST,
            calculate_motion_attributes=True
        )

        self.assertEqual(len(self.segment_builder.attribute_definitions), 8)
        self.assertEqual(segment_layer.featureCount(), 2)
        for index, feature in enumerate(segment_layer.getFeatures()):
            if index == 0:
                self.assertEqual(feature['_a_index'], 0)
                self.assertEqual(feature['_b_index'], 1)
                self.assertEqual(feature['_duration'], 90)
                self.assertAlmostEqual(feature['_distance'], 793, 0)
                self.assertAlmostEqual(feature['_speed'], 32, 0)
                self.assertAlmostEqual(feature['_elevation_diff'], 4.8, 1)
            elif index == 1:
                self.assertEqual(feature['_a_index'], 1)
                self.assertEqual(feature['_b_index'], 3)
                self.assertEqual(feature['_duration'], 60)
                self.assertAlmostEqual(feature['_distance'], 4, 0)
                self.assertAlmostEqual(feature['_speed'], 0, 0)
                self.assertAlmostEqual(feature['_elevation_diff'], -0.6, 1)

    def test_build_segments_with_both_attributes(self):
        self.test_build_point_layer()
        segment_layer = self.segment_builder.build_segments(
            self.point_layer, "timestamp", '',
            attribute_select=self.segment_builder.ATTRIBUTE_SELECT_BOTH,
            calculate_motion_attributes=False
        )
        self.assertEqual(len(self.segment_builder.attribute_definitions), 2)
        self.assertEqual(segment_layer.fields().size(), 4)
        self.assertEqual(segment_layer.featureCount(), 2)
        for index, feature in enumerate(segment_layer.getFeatures()):
            if index == 0:
                self.assertEqual(feature['a_description'], 'start point')
                self.assertEqual(feature['b_description'], '90 seconds later')
            elif index == 1:
                self.assertEqual(feature['a_description'], '90 seconds later')
                self.assertEqual(feature['b_description'], 'equal coordinate')
