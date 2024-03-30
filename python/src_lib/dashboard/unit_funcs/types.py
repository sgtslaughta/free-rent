import streamlit as st
from sqlalchemy.sql import text


def get_unit_types():
    try:
        unit_types = st.session_state.conn.query("SELECT * FROM unit_type")
        if len(unit_types) > 0:
            return unit_types
        return None
    except Exception as e:
        st.error(f"Error: {e}")
        return None


def get_amenity_types():
    try:
        amenities = st.session_state.conn.query("SELECT * FROM amenity")
        if len(amenities) > 0:
            return amenities
        return None
    except Exception as e:
        st.error(f"Error: {e}")
        return None


def unit_type_is_valid(unit_type, container):
    errors = []
    if not unit_type["unit_style_name"]:
        errors.append("Unit Style Name")
    if not unit_type["bedroom_count"]:
        errors.append("Bedroom Count")
    if not unit_type["bathroom_count"]:
        errors.append("Bathroom Count")
    if errors:
        all = ", ".join(errors)
        container.error(f"Required fields: {all}")
        return False
    return True


def insert_unit_type_into_db(unit_type):
    try:
        with st.session_state.conn.session as s:
            sql = """
            INSERT INTO 
                unit_type 
                    (unit_style_name, 
                    bedroom_count, 
                    bathroom_count, 
                    sq_footage, 
                    has_balcony, 
                    has_vaulted, 
                    exterior_type, 
                    has_washer, 
                    has_dryer, 
                    range_type, 
                    furnace_type, 
                    is_furnished, 
                    date_renovated, 
                    other_info) 
            VALUES 
                (:unit_style_name, 
                :bedroom_count, 
                :bathroom_count, 
                :sq_footage, 
                :has_balcony, 
                :has_vaulted, 
                :exterior_type, 
                :has_washer, 
                :has_dryer, 
                :range_type, 
                :furnace_type, 
                :is_furnished, 
                :date_renovated, 
                :other_info)
            """
            s.execute(text(sql), unit_type)
            s.commit()
        return True
    except Exception as e:
        st.error(f"Error: {e}")
        return False


def add_unit_type(container):
    """
    +-----------------+------------------------+------+-----+---------+----------------+
    | Field           | Type                   | Null | Key | Default | Extra          |
    +-----------------+------------------------+------+-----+---------+----------------+
    | id              | int(11)                | NO   | PRI | NULL    | auto_increment |
    | unit_style_name | text                   | NO   | UNI | NULL    |                |
    | bedroom_count   | int(11)                | NO   |     | NULL    |                |
    | bathroom_count  | int(11)                | NO   |     | NULL    |                |
    | sq_footage      | int(11)                | YES  |     | NULL    |                |
    | has_balcony     | tinyint(1)             | YES  |     | NULL    |                |
    | has_vaulted     | tinyint(1)             | YES  |     | NULL    |                |
    | exterior_type   | varchar(100)           | YES  |     | NULL    |                |
    | has_washer      | tinyint(1)             | YES  |     | NULL    |                |
    | has_dryer       | tinyint(1)             | YES  |     | NULL    |                |
    | range_type      | enum('gas','electric') | YES  |     | NULL    |                |
    | furnace_type    | enum('gas','electric') | YES  |     | NULL    |                |
    | is_furnished    | tinyint(1)             | YES  |     | 0       |                |
    | date_renovated  | date                   | YES  |     | NULL    |                |
    | other_info      | text                   | YES  |     | NULL    |                |
    +-----------------+------------------------+------+-----+---------+----------------+
    :param container:
    :return:
    """
    st.session_state.adding_unit_type = True
    sub_c = container.container(border=True)
    sub_c.subheader("Add Unit Type")
    name = sub_c.text_input("Unit Style Name", key="unit_style_name")
    col1, col2, col3 = sub_c.columns([.4, .4, .2])
    unit_type = {
        "unit_style_name": name,
        "bedroom_count": col1.number_input("Bedroom Count", key="bedroom_count", min_value=1, step=1),
        "bathroom_count": col1.number_input("Bathroom Count", key="bathroom_count", min_value=1, step=1),
        "sq_footage": col2.number_input("Square Footage", key="sq_footage", min_value=0, step=1),
        "has_balcony": col3.checkbox("Has Balcony", key="has_balcony"),
        "has_vaulted": col3.checkbox("Has Vaulted Ceiling", key="has_vaulted"),
        "exterior_type": col2.text_input("Exterior Type", key="exterior_type"),
        "has_washer": col3.checkbox("Has Washer", key="has_washer"),
        "has_dryer": col3.checkbox("Has Dryer", key="has_dryer"),
        "range_type": col1.selectbox("Range Type", ["Gas", "Electric"], key="range_type"),
        "furnace_type": col2.selectbox("Furnace Type", ["Gas", "Electric"], key="furnace_type"),
        "is_furnished": col3.checkbox("Is Furnished", key="is_furnished"),
        "date_renovated": col3.date_input("Date Renovated", key="date_renovated"),
        "other_info": sub_c.text_area("Other Info", key="other_info")
    }
    is_valid = unit_type_is_valid(unit_type, container)
    if is_valid:
        col1, col2 = container.columns(2)
        add_u_type = col1.button("Submit", key="submit_unit_type", type="primary",
                                 use_container_width=True, disabled=not is_valid)
        cancel_u_type = col2.button("Cancel", key="cancel_unit_type",
                                    use_container_width=True)
        if add_u_type:
            if insert_unit_type_into_db(unit_type):
                st.success("Unit Type added successfully.")
                st.session_state.adding_unit_type = False
                st.rerun()
        if cancel_u_type:
            st.session_state.adding_unit_type = False
            st.rerun()


def show_unit_types(container):
    unit_types = get_unit_types()
    container.subheader(f"Unit Types ({len(unit_types)})", divider="green")
    if len(unit_types) > 0:
        container.dataframe(unit_types,
                            hide_index=True,
                            use_container_width=True)
    else:
        container.warning("No unit types found.")
    add_b, edit_b = container.columns(2)
    if add_b.button("Add New Unit Type", use_container_width=True) or st.session_state.adding_unit_type:
        st.session_state.edit_unit_type = False
        add_unit_type(container)


def show(container):
    if "adding_unit_type" not in st.session_state:
        st.session_state.adding_unit_type = False
    if "edit_unit_type" not in st.session_state:
        st.session_state.edit_unit_type = False
    if "deleting_unit_type" not in st.session_state:
        st.session_state.deleting_unit_type = False
    if "adding_amenity_type" not in st.session_state:
        st.session_state.adding_amenity_type = False
    if "edit_amenity_type" not in st.session_state:
        st.session_state.edit_amenity_type = False
    if "deleting_amenity_type" not in st.session_state:
        st.session_state.deleting_amenity_type = False
    unit_types_tab, amenity_types_tab = container.tabs(["Unit Types", "Amenity Types"])
    show_unit_types(unit_types_tab)
