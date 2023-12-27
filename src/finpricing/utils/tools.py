from prettytable import PrettyTable
import inspect
import datetime
import functools
import os
import yaml
import base64
import pickle
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet
from typing import Union

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

def datetimeToDates(func):
    """decorator to convert datetime.date to Date"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        new_args = [Date.from_datetime(arg) if isinstance(arg, datetime.date) else arg for arg in args]
        new_kwargs = {k: Date.from_datetime(v) if isinstance(v, datetime.date) else v for k, v in kwargs.items()}
        return func(*new_args, **new_kwargs)
    return wrapper

class ClassUtil:
    def save_attributes(self, ignore=None):
        """save all attributes of the class to self.attributes"""
        ignore = ignore or []
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
        
    def first_valid(self, *args):
        for arg in args:
            if arg is not None:
                return arg
        return None


#########################################
# Encryption Utilities
#########################################

def read_private_params_for_key(file_path):
    """read private params from file and generate key from password and salt_seed"""
    if not isinstance(file_path, str):
        raise TypeError('File path must be a string')
    
    if not os.path.exists(file_path):
        raise FileNotFoundError("private_params.yml file under project root not found. Testing data is not open source.")
    
    with open(file_path, 'r', encoding='utf-8') as file:
        private_params = yaml.safe_load(file)
    if private_params.get('testing_data_pwd', None) is None or private_params.get('testing_data_salt', None) is None:
        raise ValueError('Private params file must contain testing_data_pwd and salt_seed')
    key = generate_key_from_password(private_params['testing_data_pwd'], private_params['testing_data_salt'])
    return key
    
def pickle_encrypt_and_store_data(data, file_path, key):
    try:
        pickled_data = pickle.dumps(data)
    except Exception as e:
        raise ValueError('Data must be pickle-able') from e
    encrypted_data = encrypt_data_with_key(pickled_data, key)
    store_encrypted_data(encrypted_data, file_path)
    
def generate_key_from_password(password, salt_str):
    if not isinstance(password, str):
        raise TypeError('Password must be a string')
    if not isinstance(salt_str, str):
        raise TypeError('Salt must be a string.')
    salt = salt_str.encode()
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key

def encrypt_data_with_key(data: Union[str, bytes], key: bytes):
    if not isinstance(data, str) and not isinstance(data, bytes):
        raise TypeError('Data must be a string / bytes')
    if isinstance(data, str):
        data = data.encode()
    cipher_suite = Fernet(key)
    encrypted_data = cipher_suite.encrypt(data)
    return encrypted_data

def store_encrypted_data(encrypted_data, file_path):
    if not isinstance(encrypted_data, bytes):
        raise TypeError('Encrypted data must be bytes')
    if not isinstance(file_path, str):
        raise TypeError('File path must be a string')
    with open(file_path, 'wb') as file:
        pickle.dump(encrypted_data, file)
        
def load_and_decrypt_data(file_path, key):
    if not isinstance(file_path, str):
        raise TypeError('File path must be a string')
    if not isinstance(key, bytes):
        raise TypeError('Key must be bytes')
    with open(file_path, 'rb') as file:
        encrypted_data = pickle.load(file)
    cipher_suite = Fernet(key)
    decrypted_data = cipher_suite.decrypt(encrypted_data)
    assert isinstance(decrypted_data, bytes), "Decrypted data must be bytes, and then loaded by pickle"
    return pickle.loads(decrypted_data)
