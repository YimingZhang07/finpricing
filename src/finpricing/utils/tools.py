from prettytable import PrettyTable
import inspect
import datetime
from .date import Date


def dict_to_obj_str(d: dict) -> str:
    """Return the string representation of a dictionary"""
    res = ""
    for k, v in d.items():
        res += "{0:<20s}: {1:<15s}\n".format(k, str(v))
    return res


def prettyTableByColumn(d: dict, align="") -> str:
    """
    Return the string representation of a dictionary in a pretty table format where
    dictionary values can be either iterables for direct use or tuples where the first
    element is an iterable and the second is a format string.

    Args:
    d (dict): Dictionary with data to be displayed by the table.
    align (str): String with column alignments. Use 'l' for left, 'r' for right, and 'c' for center.

    Returns:
    str: A string representation of the table.
    """
    # Initialize table
    x = PrettyTable()

    # Add columns to the table with optional formatting
    for col, val in d.items():
        if isinstance(val, tuple):  # If the value is a tuple (iterable, format)
            iterable, fmt = val
            formatted_values = [format(v, fmt) for v in iterable]
            x.add_column(col, formatted_values)
        else:  # If the value is just an iterable
            x.add_column(col, val)
    
    # Set alignment for columns if provided
    if align:
        align = align.ljust(len(x.field_names), ' ')  # Default to left align if not enough align chars
        if len(align) != len(x.field_names):
            raise ValueError("Alignment string length must match the number of columns or be empty for default.")
        
        for field_name, alignment in zip(x.field_names, align):
            if alignment not in "lrc":
                raise ValueError("Alignment string can only contain 'l', 'r', or 'c'")
            x.align[field_name] = alignment

    # Return table string representation
    # return x.get_string()
    print(x.get_string())

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

class ClassUtil:
    def save_attributes(self, ignore=[]):
        frame = inspect.currentframe().f_back
        _, _, _, local_vars = inspect.getargvalues(frame)
        self.attributes = {k:v for k, v in local_vars.items()
                           if k not in set(ignore + ["self"]) and not k.startswith("_")}
        for k, v in self.attributes.items():
            setattr(self, k, v)
            
    def resolve_dates(self, start_date, maturity_date_or_tenor):
        self.start_date = Date.convert_from_datetime(start_date)
        if isinstance(maturity_date_or_tenor, datetime.date) or isinstance(maturity_date_or_tenor, Date):
            self.maturity_date = Date.convert_from_datetime(maturity_date_or_tenor)
        elif isinstance(maturity_date_or_tenor, str):
            self.maturity_date = self.start_date.add_tenor(maturity_date_or_tenor)
        else:
            raise ValueError("maturity_date_or_tenor must be either datetime.date or str")