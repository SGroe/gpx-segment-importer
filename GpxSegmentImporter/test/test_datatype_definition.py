import datetime
import unittest
from ..core.datatype_definition import DataTypes


class TestFeatureBuilder(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def test_parsing(self):
        definition = DataTypes()
        self.assertEqual(definition.parse("Integer"), 'Integer')
        self.assertEqual(definition.parse("Double"), 'Double')
        self.assertEqual(definition.parse("Boolean"), 'Boolean')
        self.assertEqual(definition.parse("String"), 'String')
        self.assertEqual(definition.parse("Date"), 'Date')

    def test_detect(self):
        definition = DataTypes()
        self.assertEqual(definition.detect_data_type(2), 'Integer')
        self.assertEqual(definition.detect_data_type("2"), 'Integer')
        self.assertEqual(definition.detect_data_type(2.2), 'Double')
        self.assertEqual(definition.detect_data_type("2.2"), 'Double')
        self.assertEqual(definition.detect_data_type(True), 'Boolean')
        self.assertEqual(definition.detect_data_type("True"), 'Boolean')
        self.assertEqual(definition.detect_data_type("String"), 'String')
        self.assertEqual(definition.detect_data_type("2023-11-17T21:07:54"), 'Date')

    def test_create_date(self):
        definition = DataTypes()
        self.assertEqual(definition.create_date("2023-11-17T21:07:54"), datetime.datetime(2023, 11, 17, 21, 7, 54))
        self.assertNotEqual(definition.create_date("2023-11-17T21:07:54"), datetime.datetime(2023, 11, 17, 22, 7, 54))
        self.assertEqual(definition.create_date("20231117", "%Y%m%d"), datetime.datetime(2023, 11, 17))
        self.assertEqual(definition.create_date("2023-11-17T21:07:54Z"), datetime.datetime(2023, 11, 17, 21, 7, 54))
        self.assertEqual(definition.create_date("2023-10-15T14:58:34+03:00"),
                         datetime.datetime(2023, 10, 15, 14, 58, 34,
                                           tzinfo=datetime.timezone(datetime.timedelta(seconds=3 * 60 * 60))))
        self.assertEqual(definition.create_date("2023-11-17T21:07:54.874Z"),
                         datetime.datetime(2023, 11, 17, 21, 7, 54, 874000))
        self.assertEqual(definition.create_date("2023-11-17T21:07:54.874"),
                         datetime.datetime(2023, 11, 17, 21, 7, 54, 874000))

