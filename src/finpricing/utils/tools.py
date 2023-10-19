from prettytable import PrettyTable


def dict_to_obj_str(d: dict) -> str:
    """Return the string representation of a dictionary"""
    res = ""
    for k, v in d.items():
        res += "{0:<20s}: {1:<15s}\n".format(k, str(v))
    return res


def prettyTableByColumn(d: dict, float_format=".4") -> str:
    """Return the string representation of a dictionary in a pretty table format
    
    The dictionary contains the column names as keys and the list of values as values.
    """
    x = PrettyTable()
    for col in d:
        x.add_column(fieldname=col, column=d.get(col))
    x.float_format = float_format
    return x.get_string()

def prettyTableByRow(d: dict) -> str:
    """Return the string representation of a dictionary in a pretty table format
    
    The dictionary contains the row names as keys and the list of values as values.
    """
    x = PrettyTable()
    x.field_names = ["Attribute", "Value"]
    x.align["Attribute"] = "l"
    x.align["Value"] = "r"
    for row in d:
        x.add_row([row, d.get(row)])
    return x.get_string()