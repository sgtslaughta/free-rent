import streamlit as st

from .tenant_funcs.alter_source import add_tenant, edit_tenant


def get_tenants():
    st.cache_data.clear()
    return st.session_state.conn.query("SELECT * FROM tenant")


def show(container):
    if "adding_tenant" not in st.session_state:
        st.session_state.adding_tenant = False
    if "edit_tenant" not in st.session_state:
        st.session_state.edit_tenant = False
    if "deleting_tenant" not in st.session_state:
        st.session_state.deleting_tenant = False
    container.button("Refresh Data", key="refresh_tenants")
    container.subheader("Tenants", divider="green")

    all_tab, by_unit_tab = container.tabs(["All Tenants", "By Unit"])

    tenants = get_tenants()
    show_all_tenants(all_tab, tenants)


def show_all_tenants(container, tenants):
    container.metric("Count", len(tenants))
    container.markdown("*Hover over table then click magnifying glass to search*")
    container.data_editor(tenants, hide_index=True, key="tenants")
    add_b, edit_b, del_b = container.columns(3)
    if add_b.button("Add", use_container_width=True) or st.session_state.adding_tenant:
        add_tenant(container)
    if edit_b.button("Edit Tenant", use_container_width=True) or st.session_state.edit_tenant:
        edit_tenant(container, tenants)
    if del_b.button("Delete Selected", use_container_width=True):
        pass
