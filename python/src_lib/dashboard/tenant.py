"""
@Author: Richard Soto
@Title: Tenant
@Description: This module contains the core functions display the tenant page.
"""

import streamlit as st

from .tenant_funcs.mod_tenant import add_tenant, edit_tenant, get_tenants
from .tenant_funcs.pets import show as show_pets
from .tenant_funcs.vechicles import show as show_vehicles


def filter_dataframe(data, query, column="first_name"):
    """Filter DataFrame based on user input."""
    if query:
        return data[data[column].str.contains(query, case=False)]
    else:
        return data


def show(container):
    if "tenants" not in st.session_state:
        st.session_state.tenants = None
        get_tenants()
    if "selected_tenant" not in st.session_state:
        st.session_state.selected_tenant = None
    if "adding_tenant" not in st.session_state:
        st.session_state.adding_tenant = False
    if "edit_tenant" not in st.session_state:
        st.session_state.edit_tenant = False
    if "deleting_tenant" not in st.session_state:
        st.session_state.deleting_tenant = False
    container.subheader("Tenants", divider="green")

    all_tab, by_unit_tab = container.tabs(["All Tenants", "By Unit"])

    get_tenants()
    show_all_tenants(all_tab, st.session_state.tenants)


def show_all_tenants(container, tenants):
    container.markdown("*Hover over table then click magnifying glass to search*")
    col1, col2 = container.columns(2)
    col_to_search = col2.selectbox("Search Column", tenants.columns, index=1)
    search_query = col1.text_input("Search Query", placeholder="Search...",
                                   autocomplete="on")

    tenants = filter_dataframe(tenants, search_query, col_to_search)
    container.data_editor(tenants, hide_index=True, key="tenants_table")
    add_b, edit_b = container.columns(2)
    if add_b.button("Add New Tenant", use_container_width=True) or st.session_state.adding_tenant:
        st.session_state.edit_tenant = False
        add_tenant(container)
    if edit_b.button("View Tenant Details", use_container_width=True) or st.session_state.edit_tenant:
        st.session_state.adding_tenant = False
        edit_c = container.container(border=True)
        edit_tenant(edit_c, tenants)
        col1, col2 = edit_c.columns(2)
        show_pets(col1)
        show_vehicles(col2)
    else:
        st.session_state.adding_tenant = False
        st.session_state.edit_tenant = False
