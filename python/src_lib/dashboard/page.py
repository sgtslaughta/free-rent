"""
@Author: Richard Soto
@Title: Page
@Description: This module contains the core functions to display the main page.
"""

import streamlit as st

from .dash import show as show_dashboard
from .rental_assets import show as show_units
from .tenant import show as show_tenants
from .wo import show as show_work_orders


def show():
    if st.session_state.logged_in:
        st.title(f"FREE-RENT: Welcome {st.session_state.user}!")
        dash, tenants, units, work_orders = st.tabs(["Dashboard", "Tenants", "Properties/Units", "Work Orders"])
        show_dashboard(dash)
        show_tenants(tenants)
        show_units(units)
        show_work_orders(work_orders)
