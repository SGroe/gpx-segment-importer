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
class DataTypes():
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
        if DataTypes.str_is_int(text):
            return DataTypes.Integer
        elif DataTypes.str_is_double(text):
            return DataTypes.Double
        elif DataTypes.str_is_boolean(text):
            return DataTypes.Boolean
        # elif self.str_is_date(extension.text):
        #     return DataTypes.Date
        else:
            return DataTypes.String

    @staticmethod
    def str_is_int(string):
        if string is None:
            return False
        try:
            int(string)
            return True
        except ValueError:
            return False
        # except TypeError:
        #     print "TypeError int " + str(string)
        #     return False

    @staticmethod
    def str_is_boolean(string):
        if string is None:
            return False
        if string in ['true', 'false', 'TRUE', 'FALSE', 1, 0, 't', 'f']:
            return True
        return False

    @staticmethod
    def str_is_double(string):
        if string is None:
            return False
        try:
            float(string)
            return True
        except ValueError:
            return False
        except TypeError:
            print "TypeError double " + str(string)
            return False

    @staticmethod
    def str_is_date(string):
        if string is None:
            return None
        elif DataTypes.create_date(string) is not None:
            return True
        else:
            return False

    @staticmethod
    def string_to_boolean(string):
        print string
        if string is True or string in ['true', 'TRUE', '1', 't']:
            return True
        return False

    @staticmethod
    def create_date(s):
        if s is None:
            return None
        s = re.sub(r"[+-]([0-9]{4})+", "", s)
        try:
            return datetime.strptime(s, '%Y-%m-%dT%H:%M:%SZ')
        except ValueError:
            try:
                return datetime.strptime(s, '%Y-%m-%dT%H:%M:%S.%fZ')
            except ValueError:
                try:
                    return datetime.strptime(s, '%Y-%m-%dT%H:%M:%S')
                except ValueError:
                    try:
                        return datetime.strptime(s, '%Y-%m-%dT%H:%M:%S.%f')
                    except ValueError:
                        pass
        return None
