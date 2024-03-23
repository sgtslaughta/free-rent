import streamlit as st

from .tenant_funcs.alter_source import add_tenant


def get_tenants():
    st.cache_data.clear()
    return st.session_state.conn.query("SELECT * FROM tenant")


def show(container):
    if "adding_tenant" not in st.session_state:
        st.session_state.adding_tenant = False
    if "deleting_tenant" not in st.session_state:
        st.session_state.deleting_tenant = False
    container.button("Refresh Data", key="refresh_tenants")
    container.subheader("Tenants", divider="green")

    all_tab, by_unit_tab = container.tabs(["All Tenants", "By Unit"])

    tenants = get_tenants()
    show_all_tenants(all_tab, tenants)


def show_all_tenants(container, tenants):
    headers = tenants.columns.tolist()
    headers.remove("id")
    container.metric("Count", len(tenants))
    container.markdown("*Click in table then CTL-F to search*")
    container.data_editor(tenants[headers], hide_index=True, key="tenants")
    add_t, del_t, refresh_t = container.columns(3)
    if add_t.button("Add") or st.session_state.adding_tenant:
        add_tenant(container)
