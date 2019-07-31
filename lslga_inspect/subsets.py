from . import lslga_utils
from .db import get_db

class Subset:

    def __init__(self, id_string, pretty_string, list_create_func):
        self.id_string = id_string
        self.pretty_string = pretty_string
        self.list_create_func = list_create_func
        self.galaxy_list = self.list_create_func()

subset_list = []

def all_list():
    t = lslga_utils.get_t()
    list = [id for id, in_desi in zip(t['LSLGA_ID'], t['IN_DESI']) if in_desi]
    return list

def string_match_list(catalog):
    def inner_function():
        t = lslga_utils.get_t()
        list = [
            id for id, galaxy, in_desi in zip(t['LSLGA_ID'], t['GALAXY'], t['IN_DESI'])
            if galaxy[:len(catalog)] == catalog and in_desi
        ]
        return list
    return inner_function

subset_list.append(Subset('all', '', all_list)) # string_match_list('') would probably work as well
subset_list.append(Subset('ngc', 'NGC', string_match_list('NGC')))
subset_list.append(Subset('sdss', 'SDSS', string_match_list('SDSS')))
subset_list.append(Subset('2mas', '2MASS/2MASX', string_match_list('2MAS'))) # Change to '2MASS' for testing, only matches 4 galaxies

pretty_string_dict = {item.id_string : item.pretty_string for item in subset_list}
galaxy_list_dict = {item.id_string : item.galaxy_list for item in subset_list}

def get_inspected(user_id):
    db = get_db()
    inspections = db.execute("SELECT lslga_id FROM inspection WHERE user_id = ?", (user_id,)).fetchall()
    inspections = [row[0] for row in inspections]
    return inspections
