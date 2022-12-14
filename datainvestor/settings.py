import os
import time
import warnings
import yaml
from munch import munchify, unmunchify


ENV_VAR_ROOT = 'DATAINVESTOR'
DEFAULT_CONFIG_FILENAME = './config.yml'


def from_env(key, default_value=None, root=ENV_VAR_ROOT):
    """Restituisce un valore (url, login, password)
    utilizzando il default_value o la variabile d'ambiente"""
    if root != "":
        ENV_VAR_KEY = root + "_" + key.upper()
    else:
        ENV_VAR_KEY = key.upper()
    if default_value == '' or default_value is None:
        try:
            return(os.environ[ENV_VAR_KEY])
        except Exception:
            warnings.warn("You should pass %s using --%s or using environment variable %r" % (key, key, ENV_VAR_KEY))
            return(default_value)
    else:
        return(default_value)


DEFAULT = munchify({
    "CSV_DATA_DIR": from_env("CSV_DATA_DIR", "~/data"),
    "OUTPUT_DIR": from_env("OUTPUT_DIR", "~/out")
})


TEST = munchify({
    "CSV_DATA_DIR": "data",
    "OUTPUT_DIR": "out"
})


SUPPORTED = {
    'CURRENCIES': [
        'USD', 'GBP', 'EUR'
    ],
    'FEE_MODEL': {
        'ZeroFeeModel': 'datainvestor.broker.fee_model.zero_fee_model'
    }
}

LOGGING = {
    'DATE_FORMAT': '%Y-%m-%d %H:%M:%S'
}

PRINT_EVENTS = True


def set_print_events(print_events=True):
    global PRINT_EVENTS
    PRINT_EVENTS = print_events


def from_file(fname=DEFAULT_CONFIG_FILENAME, testing=False):
    if testing:
        return TEST
    try:
        with open(os.path.expanduser(fname)) as fd:
            conf = yaml.load(fd, Loader=yaml.FullLoader)
        conf = munchify(conf)
        return conf
    except IOError:
        print("A configuration file named '%s' is missing" % fname)
        s_conf = yaml.dump(unmunchify(DEFAULT), explicit_start=True, indent=True, default_flow_style=False)
        print("""Creating this file %s
        \nYou still have to create directories with data and put your data in!
        """ % s_conf)
        time.sleep(3)
        try:
            with open(os.path.expanduser(fname), "w") as fd:
                fd.write(s_conf)
        except IOError:
            print("Can create '%s'" % fname)
    print("Trying anyway with default configuration")
    return DEFAULT

