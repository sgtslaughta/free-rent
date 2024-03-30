"""
@Author: Richard Soto
@Title: mod_tenant
@Description: This module contains the functions to add/edit/delete tenants.
"""

from datetime import datetime
from time import sleep

import streamlit as st
from sqlalchemy import text


def get_tenants():
    st.cache_data.clear()
    st.session_state.tenants = st.session_state.conn.query("SELECT * FROM tenant")


def validate_tenant(tenant, container):
    errors = []
    if not tenant["first_name"]:
        errors.append("First Name")
    if not tenant["last_name"]:
        errors.append("Last Name")
    if not tenant["phone_number"]:
        errors.append("Phone")
    if not tenant["email"]:
        errors.append("Email")
    if not tenant["date_of_birth"]:
        errors.append("Date of Birth")
    if errors:
        container.error(":eight_pointed_black_star: REQUIRED: " + ", ".join(errors))
        return False
    return True


def insert_tenant_to_db(data):
    try:
        with st.session_state.conn.session as s:
            statement = f"""
                INSERT INTO tenant
                (first_name, middle_name, last_name, phone_number, 
                cell_number, email, date_of_birth, emergency_contact_name, 
                emergency_contact_phone, emergency_contact_relationship, notes) 
                VALUES 
                (:first_name, :middle_name, :last_name, :phone_number, :cell_number, 
                :email, :date_of_birth, :emergency_contact_name, :emergency_contact_phone, 
                :emergency_contact_relationship, :notes)
                ;"""
            s.execute(text(statement), data)
            s.commit()
        return True
    except Exception as e:
        st.error(f"Error: {e}")
        return False


def add_tenant(container):
    st.session_state.adding_tenant = True
    container.subheader("New Tenant", divider="green")
    form = container.container(border=True)
    with form:
        min = datetime(1900, 1, 1)
        max = datetime.now()
        name_col1, name_col2, name_col3 = form.columns(3)
        phone_col, cell_col, email_col, dob_col = form.columns(4)
        ec_name_col, ec_phone_col, ec_rel_col = form.columns(3)
        ec_relationship = ["Spouse", "Parent", "Sibling", "Child", "Friend", "Other"]
        tenant = {
            "first_name": name_col1.text_input("First Name*"),
            "middle_name": name_col2.text_input("Middle Name"),
            "last_name": name_col3.text_input("Last Name*"),
            "phone_number": phone_col.text_input("Phone*"),
            "cell_number": cell_col.text_input("Cell"),
            "email": email_col.text_input("Email*"),
            "date_of_birth": dob_col.date_input("Date of Birth*", value=None,
                                                min_value=min,
                                                max_value=max),
            "emergency_contact": ec_name_col.text_input("Emergency Contact Name"),
            "emergency_contact_phone": ec_phone_col.text_input("Emergency Contact Phone"),
            "emergency_contact_relationship": ec_rel_col.selectbox("Emergency Contact Relationship",
                                                                   options=ec_relationship,
                                                                   index=None),
            "notes": form.text_area("Notes"),
        }
        col1, col2 = form.columns(2)
        is_valid = validate_tenant(tenant, form)
        submit = col1.button("Submit", use_container_width=True, type="primary",
                             disabled=not is_valid)
        cancel = col2.button("Cancel", use_container_width=True)
        if cancel:
            st.session_state.adding_tenant = False
            st.rerun()
        if submit:
            if insert_tenant_to_db(tenant):
                form.success(":white_check_mark: Tenant Added")
            else:
                form.error(":x: Error Adding Tenant")
            st.session_state.adding_tenant = False


def commit_changes(data):
    try:
        with st.session_state.conn.session as s:
            sql = text("""
            UPDATE tenant
            SET first_name = :first_name,
            middle_name = :middle_name,
            last_name = :last_name,
            phone_number = :phone_number,
            cell_number = :cell_number,
            email = :email,
            date_of_birth = :date_of_birth,
            emergency_contact_name = :emergency_contact_name,
            emergency_contact_phone = :emergency_contact_phone,
            emergency_contact_relationship = :emergency_contact_relationship,
            notes = :notes
            WHERE id = :id
            """)
            s.execute(sql, data)
            # data.to_dict(orient="records")[0]
            s.commit()
        st.session_state.edit_tenant = False
        return True
    except Exception as e:
        st.error(f"Error: {e}")
        return False


def delete_tenant(data, container):
    try:
        with st.session_state.conn.session as s:
            s.execute(text("DELETE FROM tenant WHERE id = :id"), {"id": data["id"].values[0]})
            s.commit()
        st.session_state.edit_tenant = False
        container.success(":white_check_mark: Tenant Deleted")
    except Exception as e:
        container.error(f"Error: {e}")


def edit_tenant(container, data):
    st.session_state.edit_tenant = True
    list_of_t_w_first_and_last = data["first_name"] + " " + data["last_name"]
    selected = container.selectbox("Select Tenant to View",
                                   options=list_of_t_w_first_and_last,
                                   index=None)

    if selected:
        selected = data[data["first_name"] + " " + data["last_name"] == selected]["id"].values[0]
        st.session_state.selected_tenant = selected
        t_container = container.container(border=True)
        t_name = data[data["id"] == selected]["first_name"].values[0] + " " + data[data["id"] == selected][
            "last_name"].values[0]
        t_container.subheader(f"{t_name}", divider="green")
        min = datetime(1900, 1, 1)
        max = datetime.now()
        name_col1, name_col2, name_col3 = t_container.columns(3)
        phone_col, cell_col, email_col, dob_col = t_container.columns(4)
        ec_name_col, ec_phone_col, ec_rel_col = t_container.columns(3)
        ec_relationship = ["Spouse", "Parent", "Sibling", "Child", "Friend", "Other"]
        tenant = {
            "first_name": name_col1.text_input("First Name*",
                                               value=data[data['id'] == selected]["first_name"].values[0]),
            "middle_name": name_col2.text_input("Middle Name",
                                                value=data[data['id'] == selected]["middle_name"].values[0]),
            "last_name": name_col3.text_input("Last Name*", value=data[data['id'] == selected]["last_name"].values[0]),
            "phone_number": phone_col.text_input("Phone*",
                                                 value=data[data['id'] == selected]["phone_number"].values[0]),
            "cell_number": cell_col.text_input("Cell", value=data[data['id'] == selected]["cell_number"].values[0]),
            "email": email_col.text_input("Email*", value=data[data['id'] == selected]["email"].values[0]),
            "date_of_birth": dob_col.date_input("Date of Birth*",
                                                min_value=min,
                                                max_value=max,
                                                value=data[data['id'] == selected]["date_of_birth"].values[0]),
            "emergency_contact_name": ec_name_col.text_input("Emergency Contact Name", value=
            data[data['id'] == selected].emergency_contact_name.values[0]),
            "emergency_contact_phone": ec_phone_col.text_input("Emergency Contact Phone",
                                                               value=data[data['id'] == selected][
                                                                   "emergency_contact_phone"].values[
                                                                   0]),
            "emergency_contact_relationship": ec_rel_col.selectbox("Emergency Contact Relationship",
                                                                   options=ec_relationship,
                                                                   index=ec_relationship.index(
                                                                       data[data['id'] == selected][
                                                                           "emergency_contact_relationship"].values[
                                                                           0]) if data[data['id'] == selected][
                                                                                      "emergency_contact_relationship"].values[
                                                                                      0] in ec_relationship else None),
            "notes": t_container.text_area("Notes",
                                           value=data[data['id'] == selected]["notes"].values[0]),
        }
        col1, col2 = t_container.columns(2)
        is_valid = validate_tenant(tenant, t_container)
        submit = col1.button("Submit Changes", use_container_width=True, type="primary",
                             disabled=not is_valid)
        delete = col2.button("Delete Tenant", use_container_width=True)
        if submit:
            tenant["id"] = data[data["id"] == selected]["id"].values[0]
            if commit_changes(tenant):
                t_container.success("Changes Submitted...")
                sleep(3)
                st.rerun()
            else:
                t_container.error("Error Submitting Changes..")
                sleep(3)
                st.rerun()
        if delete:
            container.warning("Are you sure you want to delete this tenant?")
            container.button("Confirm Delete", on_click=delete_tenant,
                             args=(data[data["id"] == selected], container))
    else:
        st.session_state.selected_tenant = None
