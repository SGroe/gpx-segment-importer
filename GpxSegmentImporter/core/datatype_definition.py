from datetime import *
import re
from qgis.PyQt.QtCore import QDateTime, QVariant
from qgis.core import QgsField


class DataTypeDefinition:
    """ Datatype definition class """

    attribute_key = None
    attribute_key_modified = None
    datatype = 'text'
    length = 0
    precision = 0
    selected = True
    example_value = None

    def __init__(self, attribute_key, datatype, selected, example_value):
        self.attribute_key = attribute_key
        self.attribute_key_modified = attribute_key
        self.datatype = datatype
        self.selected = selected
        self.example_value = example_value

    def build_field(self, prefix=''):
        key = prefix + str(self.attribute_key_modified)
        if self.datatype == DataTypes.Integer:  # data type [Integer|Double|String]
            field = QgsField(key, QVariant.Int, 'Integer')
        elif self.datatype == DataTypes.Double:
            field = QgsField(key, QVariant.Double, 'Real')
        elif self.datatype == DataTypes.Boolean:
            # QVariant.Bool is not available for QgsField
            # attributes.append(QgsField(key, QVariant.Bool, 'Boolean'))
            field = QgsField(key, QVariant.String, 'String')
        elif self.datatype == DataTypes.Date:
            field = QgsField(key, QVariant.DateTime, 'datetime')
        elif self.datatype == DataTypes.String:
            field = QgsField(key, QVariant.String, 'String')
        else:
            field = QgsField(key, QVariant.String, 'String')

        if self.length > 0:
            field.setLength(self.length)
        if self.precision > 0:
            field.setPrecision(self.length)

        return field


# https://stackoverflow.com/questions/702834/whats-the-common-practice-for-enums-in-python
class DataTypes:
    # _unused, Integer, Double, Boolean, String, Date = range(6)
    Undefined = None
    Integer = 'Integer'
    Double = 'Double'
    Boolean = 'Boolean'
    String = 'String'
    Date = 'Date'

    @classmethod
    def parse(cls, value):
        if value == 'Integer':
            return DataTypes.Integer
        elif value == 'Double':
            return DataTypes.Double
        elif value == 'Boolean':
            return DataTypes.Boolean
        elif value == 'String':
            return DataTypes.String
        elif value == 'Date':
            return DataTypes.Date
        return DataTypes.Undefined

    @staticmethod
    def detect_data_type(text):
        if DataTypes.value_is_int(text):
            return DataTypes.Integer
        elif DataTypes.value_is_float(text):
            return DataTypes.Double
        elif DataTypes.value_is_boolean(text):
            return DataTypes.Boolean
        elif DataTypes.value_is_date(text):
            return DataTypes.Date
        else:
            return DataTypes.String

    @staticmethod
    def value_is_int(value):
        if type(value) is str:
            if value is None:
                return False
            try:
                int(value)
                return True
            except ValueError:
                return False
            # except TypeError:
            #     print "TypeError int " + str(string)
            #     return False
        elif type(value) is int:
            return True
        else:
            return False

    @staticmethod
    def value_is_boolean(value):
        if type(value) is str:
            if value is None:
                return False
            if value in ['true', 'false', 'True', 'False', 'TRUE', 'FALSE', 1, 0, 't', 'f']:
                return True
            return False
        elif type(value) is bool:
            return True
        else:
            return False

    @staticmethod
    def value_is_float(value):
        if type(value) is str:
            if value is None:
                return False
            try:
                float(value)
                return True
            except ValueError:
                return False
            except TypeError:
                print("TypeError double " + str(value))
                return False
        elif type(value) is float:
            return True
        else:
            return False

    @staticmethod
    def value_is_date(value):
        if type(value) is str:
            if value is None:
                return None
            elif DataTypes.create_date(value) is not None:
                return True
            else:
                return False
        elif type(value) is datetime:
            return True
        elif type(value) is QDateTime:
            return True
        else:
            return False

    # @staticmethod
    # def string_to_boolean(string):
    #     if string is True or string in ['true', 'TRUE', '1', 't']:
    #         return True
    #     return False

    @staticmethod
    def create_date(s, custom_format=None):
        if s is None:
            return None
        # TODO explain following line
        s = re.sub(r"[+-]([0-9]{4})+", "", s)

        # https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior

        date_formats = [
            custom_format if custom_format is not None else '',
            '%Y-%m-%dT%H:%M:%S',  # 2023-10-15T14:58:34
            '%Y-%m-%dT%H:%M:%SZ',  # 2023-10-15T14:58:34Z
            '%Y-%m-%dT%H:%M:%S.%f',  # 2023-10-15T14:58:34.874
            '%Y-%m-%dT%H:%M:%S.%fZ',  # 2023-10-15T14:58:34.874Z
            '%Y-%m-%dT%H:%M:%S%z',  # 2023-10-15T14:58:34+03:00
            '%Y-%m-%dT%H:%M:%S%zZ',  # 2023-10-15T14:58:34+03:00Z
            '%Y-%m-%dT%H:%M:%S.%f%z',  # 2023-10-15T14:58:34.874+03:00
            '%Y-%m-%dT%H:%M:%S.%f%zZ'  # 2023-10-15T14:58:34.874+03:00Z
        ]
        for date_format in date_formats:
            try:
                return datetime.strptime(s, date_format)
            except ValueError:
                pass
        return None
