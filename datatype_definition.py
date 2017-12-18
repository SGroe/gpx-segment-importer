

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
