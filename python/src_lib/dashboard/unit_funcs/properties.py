import streamlit as st
from sqlalchemy.sql import text


def get_props():
    try:
        props = st.session_state.conn.query("SELECT * FROM property")
        if len(props) > 0:
            return props
        return None
    except Exception as e:
        st.error(f"Error: {e}")
        return None


def filter_dataframe(data, query, column="property_name"):
    if query:
        return data[data[column].str.contains(query, case=False)]
    else:
        return data


def prop_is_valid(prop, container):
    errors = []
    if not prop["property_name"]:
        errors.append("Property Name")
    if not prop["address"]:
        errors.append("Address")
    if not prop["city"]:
        errors.append("City")
    if not prop["state"]:
        errors.append("State")
    if not prop["postal_code"]:
        errors.append("Postal Code")
    if not prop["country"]:
        errors.append("Country")
    if not prop["total_units"]:
        errors.append("Total Units")
    if errors:
        all = ", ".join(errors)
        container.error(f"Required fields: {all}")
        return False
    return True


def insert_prop_into_db(prop):
    try:
        with st.session_state.conn.session as s:
            sql = """
            INSERT INTO 
                property 
                    (property_name, 
                    address, 
                    city, 
                    state, 
                    postal_code, 
                    country, 
                    total_units, 
                    manager_name, 
                    manager_email, 
                    manager_phone, 
                    notes)
            VALUES 
                (:property_name, 
                :address, 
                :city, 
                :state, 
                :postal_code, 
                :country, 
                :total_units, 
                :manager_name, 
                :manager_email, 
                :manager_phone, 
                :notes)
            """
            s.execute(text(sql), prop)
            s.commit()
        return True
    except Exception as e:
        st.error(f"Error: {e}")
        return False


def update_prop_in_db(prop):
    try:
        with st.session_state.conn.session as s:
            sql = """
            UPDATE property
            SET property_name = :property_name, 
                address = :address, 
                city = :city, 
                state = :state, 
                postal_code = :postal_code, 
                country = :country, 
                total_units = :total_units, 
                manager_name = :manager_name, 
                manager_email = :manager_email, 
                manager_phone = :manager_phone, 
                notes = :notes
            WHERE id = :id
            """
            s.execute(text(sql), prop)
            s.commit()
        return True
    except Exception as e:
        st.error(f"Error: {e}")
        return False


def delete_property(container):
    pass


def add_property(container):
    st.session_state.adding_property = True
    add_prop_container = container.container(border=True)
    add_prop_container.text("🏡 Add Property")
    name, total_units = add_prop_container.columns(2)
    addr, city, state, postal, country = add_prop_container.columns(5)
    mgr_name, mgr_email, mgr_phone = add_prop_container.columns(3)
    prop = {
        "property_name": name.text_input("Property Name*"),
        "address": addr.text_input("Address*"),
        "city": city.text_input("City*"),
        "state": state.text_input("State*"),
        "postal_code": postal.text_input("Postal Code*"),
        "country": country.text_input("Country*"),
        "total_units": total_units.number_input("Total Units*", min_value=1),
        "manager_name": mgr_name.text_input("Manager Name"),
        "manager_email": mgr_email.text_input("Manager Email"),
        "manager_phone": mgr_phone.text_input("Manager Phone"),
        "notes": add_prop_container.text_area("Notes")
    }
    is_valid = prop_is_valid(prop, add_prop_container)
    col1, col2 = add_prop_container.columns(2)
    add = col1.button("Add Property",
                      key="add_property",
                      disabled=not is_valid,
                      use_container_width=True,
                      type="primary")
    cancel = col2.button("Cancel", use_container_width=True)
    if add:
        if insert_prop_into_db(prop):
            st.success("Property added successfully.")
            st.session_state.adding_property = False
            st.rerun()
    if cancel:
        st.session_state.adding_property = False
        st.rerun()


def edit_property(container):
    st.session_state.editing_property = True
    edit_prop_container = container.container(border=True)
    selected = edit_prop_container.selectbox("Select Property",
                                             st.session_state.properties["property_name"])
    if not selected:
        return
    prop = st.session_state.properties[st.session_state.properties["property_name"] == selected]
    st.session_state.selected_property = prop
    edit_prop_container.divider()
    edit_prop_container.text("🏡 Edit Property")
    name, total_units = edit_prop_container.columns(2)
    addr, city, state, postal, country = edit_prop_container.columns(5)
    mgr_name, mgr_email, mgr_phone = edit_prop_container.columns(3)
    prop = {
        "id": prop["id"].values[0],
        "property_name": name.text_input("Property Name*", value=prop["property_name"].values[0]),
        "address": addr.text_input("Address*", value=prop["address"].values[0]),
        "city": city.text_input("City*", value=prop["city"].values[0]),
        "state": state.text_input("State*", value=prop["state"].values[0]),
        "postal_code": postal.text_input("Postal Code*", value=prop["postal_code"].values[0]),
        "country": country.text_input("Country*", value=prop["country"].values[0]),
        "total_units": total_units.number_input("Total Units*", value=prop["total_units"].values[0]),
        "manager_name": mgr_name.text_input("Manager Name", value=prop["manager_name"].values[0]),
        "manager_email": mgr_email.text_input("Manager Email", value=prop["manager_email"].values[0]),
        "manager_phone": mgr_phone.text_input("Manager Phone", value=prop["manager_phone"].values[0]),
        "notes": edit_prop_container.text_area("Notes", value=prop["notes"].values[0])
    }
    is_valid = prop_is_valid(prop, edit_prop_container)
    col1, col2 = edit_prop_container.columns(2)
    update = col1.button("Update Property",
                         key="update_property",
                         disabled=not is_valid,
                         use_container_width=True,
                         type="primary")
    cancel = col2.button("Cancel", use_container_width=True)
    if update:
        if update_prop_in_db(prop):
            st.success("Property updated successfully.")
            st.session_state.editing_property = False
            st.rerun()
    if cancel:
        st.session_state.editing_property = False
        st.rerun()


def show(container):
    if "properties" not in st.session_state:
        st.session_state.properties = None
    if "selected_property" not in st.session_state:
        st.session_state.selected_property = None
    if "adding_property" not in st.session_state:
        st.session_state.adding_property = False
    if "editing_property" not in st.session_state:
        st.session_state.editing_property = False
    if "deleting_property" not in st.session_state:
        st.session_state.deleting_property = False
    st.session_state.properties = get_props()

    props = st.session_state.properties

    p_container = container.container(border=True)
    p_container.subheader(f"Properties ({len(props)})", divider="violet")

    if props is not None:
        col1, col2 = p_container.columns(2)
        display_props = props[
            ["property_name", "address", "city", "state", "postal_code", "country", "total_units", "manager_name",
             "manager_email"]]
        col_to_search = col2.selectbox("Search Column",
                                       display_props.columns,
                                       index=1,
                                       key="prop_search_col")
        search_query = col1.text_input("Search Query",
                                       placeholder="Search...",
                                       key="prop_search_query")
        if search_query:
            display_props = filter_dataframe(display_props,
                                             search_query,
                                             col_to_search)
        if len(display_props) > 0:
            p_container.dataframe(display_props,
                                  hide_index=True,
                                  use_container_width=True,
                                  )
        else:
            p_container.warning("🔎 No properties found. Try a different search.")
    else:
        p_container.warning("🔎 No properties found.")

    add_c, edit_c = container.columns(2)
    if add_c.button("Add New Property", use_container_width=True) or \
            st.session_state.adding_property:
        add_property(container)
    elif edit_c.button("Edit Property", use_container_width=True) or \
            st.session_state.editing_property:
        edit_property(container)
    else:
        st.session_state.adding_property = False
        st.session_state.editing_property = False
        st.session_state.selected_property = None
