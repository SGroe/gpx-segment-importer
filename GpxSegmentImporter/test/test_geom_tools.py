import datetime
import unittest
from ..core.geom_tools import GeomTools
from qgis.core import QgsPoint, QgsCoordinateReferenceSystem


class TestFeatureBuilder(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def test_is_equal_coordinate(self):
        p1 = QgsPoint(45.5, 53.9)
        p2 = QgsPoint(46.6, 53.7)
        self.assertEqual(False, GeomTools.is_equal_coordinate(p1, p2))
        p1 = QgsPoint(45.2, 53.7)
        p2 = QgsPoint(45.2, 53.7)
        self.assertEqual(True, GeomTools.is_equal_coordinate(p1, p2))

    def test_duration(self):
        t1 = datetime.datetime(2024, 7, 23, 8, 28, 36)
        t2 = datetime.datetime(2024, 7, 23, 8, 28, 38)
        self.assertEqual(2, GeomTools.calculate_duration(t1, t2))
        self.assertEqual(-2, GeomTools.calculate_duration(t2, t1))

    def test_distance(self):
        p1 = QgsPoint(13.5195833, 46.8339187, 818.2)
        p2 = QgsPoint(13.5197988, 46.8339244, 819.4)
        self.assertAlmostEqual(16.453, GeomTools.distance(p1, p2), 2)
        self.assertAlmostEqual(16.453, GeomTools.distance_andoyer(p1, p2), 2)

    def test_(self):
        t1 = datetime.datetime(2024, 7, 23, 8, 28, 36)
        t2 = datetime.datetime(2024, 7, 23, 8, 28, 38)
        p1 = QgsPoint(13.5195833, 46.8339187, 818.2)
        p2 = QgsPoint(13.5197988, 46.8339244, 819.4)
        self.assertAlmostEqual(
            29.615,
            GeomTools.calculate_speed(t1, t2, p1, p2, QgsCoordinateReferenceSystem.fromEpsgId(4326)),
            2
        )
