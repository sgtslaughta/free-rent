import streamlit as st


def get_units():
    try:
        units = st.session_state.conn.query("SELECT * FROM unit")
        if len(units) > 0:
            return units
        return None
    except Exception as e:
        st.error(f"Error: {e}")
        return None


def show(container):
    units = get_units()
    if units:
        container.table(units)
    else:
        container.warning("No units found.")
