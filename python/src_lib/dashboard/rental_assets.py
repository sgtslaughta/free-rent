from .unit_funcs.properties import show as show_properties
from .unit_funcs.types import show as show_types
from .unit_funcs.units import show as show_units


def show(container):
    props_tab, units_tab, types_tab = container.tabs(["Properties", "Units", "Amenity/Unit Types"])
    show_properties(props_tab)
    show_units(units_tab)
    show_types(types_tab)
