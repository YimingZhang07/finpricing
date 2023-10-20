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