from datetime import datetime
from time import sleep

import streamlit as st
from sqlalchemy.sql import text


def get_vehicles(tid):
    vehicles = st.session_state.conn.query(f"SELECT * FROM vehicle WHERE tenant_id = {tid}")
    return vehicles


def delete_vehicle_callback(vehicle, container):
    container.warning("Are you sure you want to delete this vehicle?")
    col1, col2 = container.columns(2)
    delete = col1.button("Delete", key="delete_vehicle",
                         use_container_width=True,
                         on_click=delete_vehicle_from_db, args=(vehicle,))
    cancel = col2.button("Cancel", key="cancel_delete", use_container_width=True)


def delete_vehicle_from_db(vehicle):
    try:
        with st.session_state.conn.session as s:
            sql = text("""
            DELETE FROM vehicle
            WHERE id = :id
            """)
            s.execute(sql, vehicle)
            s.commit()
        return True
    except Exception as e:
        st.error(f"Error: {e}")
        return False


def edit_vehicle(container, vehicle):
    st.session_state.edit_vehicle = True
    make, model, year = container.columns(3)
    color, license_plate = container.columns(2)
    vehicle_id = vehicle["id"].values[0]
    vehicle = {
        "id": vehicle_id,
        "make": make.text_input("Make", value=vehicle["make"].values[0]),
        "model": model.text_input("Model", value=vehicle["model"].values[0]),
        "year": year.number_input("Year", value=vehicle["year"].values[0],
                                  min_value=1900, max_value=datetime.now().year, step=1),
        "color": color.text_input("Color", value=vehicle["color"].values[0]),
        "license_plate": license_plate.text_input("License Plate", value=vehicle["license_plate"].values[0]),
        "notes": container.text_area("Notes", key="vehicle_notes", value=vehicle["notes"].values[0])
    }
    is_valid = vehicle_is_valid(vehicle)
    col1, col2 = container.columns(2)
    submit = col1.button("Submit", disabled=not is_valid,
                         use_container_width=True, type="primary")
    delete = col2.button("Delete", use_container_width=True,
                         on_click=delete_vehicle_callback, args=(vehicle, container))
    if submit:
        if update_vehicle_in_db(vehicle):
            container.success(":white_check_mark: Vehicle Updated...")
            sleep(3)
        else:
            container.error(":x: Error Updating Vehicle")
        st.session_state.edit_vehicle = False
        st.rerun()


def insert_vehicle_to_db(vehicle):
    try:
        with st.session_state.conn.session as s:
            sql = text("""
            INSERT INTO vehicle (tenant_id, make, model, year, color, license_plate)
            VALUES (:tenant_id, :make, :model, :year, :color, :license_plate)
            """)
            s.execute(sql, vehicle)
            s.commit()
        return True
    except Exception as e:
        st.error(f"Error: {e}")
        return False


def update_vehicle_in_db(vehicle):
    try:
        with st.session_state.conn.session as s:
            sql = text("""
            UPDATE vehicle
            SET make = :make, model = :model, year = :year, color = :color, license_plate = :license_plate
            WHERE id = :id
            """)
            s.execute(sql, vehicle)
            s.commit()
        return True
    except Exception as e:
        st.error(f"Error: {e}")
        return False


def vehicle_is_valid(vehicle):
    if vehicle["make"] and vehicle["model"] and vehicle["year"] and vehicle["color"] and vehicle["license_plate"]:
        return True
    return False


def add_vehicle(container, tenant_id):
    st.session_state.adding_vehicle = True
    make, model, year = container.columns(3)
    color, license_plate = container.columns(2)
    vehicle = {
        "tenant_id": tenant_id,
        "make": make.text_input("Make"),
        "model": model.text_input("Model"),
        "year": year.number_input("Year",
                                  min_value=1900, max_value=datetime.now().year, step=1),
        "color": color.text_input("Color"),
        "license_plate": license_plate.text_input("License Plate"),
        "notes": container.text_area("Notes", key="vehicle_notes")
    }
    is_valid = vehicle_is_valid(vehicle)
    col1, col2 = container.columns(2)
    submit = col1.button("Submit", disabled=not is_valid,
                         use_container_width=True, type="primary")
    cancel = col2.button("Cancel", use_container_width=True)
    if cancel:
        st.session_state.adding_vehicle = False
        st.rerun()
    if submit:
        if insert_vehicle_to_db(vehicle):
            container.success(":white_check_mark: Vehicle Added...")
            sleep(3)
        else:
            container.error(":x: Error Adding Vehicle")
            sleep(3)
        st.session_state.adding_vehicle = False
        st.rerun()


def show(container):
    if "adding_vehicle" not in st.session_state:
        st.session_state.adding_vehicle = False
    if "edit_vehicle" not in st.session_state:
        st.session_state.edit_vehicle = False
    if "deleting_vehicle" not in st.session_state:
        st.session_state.deleting_vehicle = False

    if st.session_state.selected_tenant:
        sel_tenant_id = st.session_state.selected_tenant
        vehicles = get_vehicles(sel_tenant_id)

        expanded = True if st.session_state.adding_vehicle or st.session_state.edit_vehicle else False
        exp = container.expander(f"Vehicles ({len(vehicles)})", expanded=expanded)

        if len(vehicles) == 0:
            exp.warning("🔎 No Vehicles Found...")
            selected = None
        else:
            exp.dataframe(vehicles[["make", "model", "year", "color", "license_plate"]],
                          hide_index=True,
                          column_config={"year": st.column_config.DateColumn(
                              format="YYYY")},
                          use_container_width=True)
            selected = exp.selectbox("Select Vehicle Plate # to View",
                                     options=vehicles["license_plate"].to_list(),
                                     index=None)
        show_add = True if selected else False
        if not show_add:
            add = exp.button("Add New Vehicle", use_container_width=True)
            if add or st.session_state.adding_vehicle:
                add_vehicle(exp, sel_tenant_id)
        else:
            vehicle = vehicles[vehicles["license_plate"] == selected]
            edit_vehicle(exp, vehicle)
