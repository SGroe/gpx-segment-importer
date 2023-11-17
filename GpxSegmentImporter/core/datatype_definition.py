from datetime import *
import re


class DataTypeDefinition:
    """ Datatype definition class """

    def __init__(self, attribute_key, datatype, selected, example_value):
        self.attribute_key = attribute_key
        self.attribute_key_modified = attribute_key
        self.datatype = datatype
        self.selected = selected
        self.example_value = example_value


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
            '%Y-%m-%dT%H:%M:%SZ',
            '%Y-%m-%dT%H:%M:%S.%fZ',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%dT%H:%M:%S.%f'
        ]
        for date_format in date_formats:
            try:
                return datetime.strptime(s, date_format)
            except ValueError:
                pass
        return None
