from datetime import datetime

import streamlit as st
from sqlalchemy import text


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
        container.error("REQUIRED: " + ", ".join(errors))
        return False
    return True


def add_tenant(container):
    st.session_state.adding_tenant = True
    container.subheader("Add Tenant", divider="green")
    form = container.form(key="add_tenant", clear_on_submit=True, border=True)
    with form:
        min = datetime(1900, 1, 1)
        max = datetime.now()
        tenant = {
            "first_name": form.text_input("First Name*"),
            "middle_name": form.text_input("Middle Name"),
            "last_name": form.text_input("Last Name*"),
            "phone_number": form.text_input("Phone*"),
            "cell_number": form.text_input("Cell"),
            "email": form.text_input("Email*"),
            "date_of_birth": form.date_input("Date of Birth*", value=None,
                                             min_value=min,
                                             max_value=max),
            "emergency_contact": form.text_input("Emergency Contact"),
            "emergency_contac_phone": form.text_input("Emergency Phone"),
            "emergency_contact_relationship": form.text_input("Emergency Relationship"),
            "notes": form.text_area("Notes"),
        }
        col1, col2 = form.columns(2)
        submit = col1.form_submit_button("Submit", use_container_width=True, type="primary")
        cancel = col2.form_submit_button("Cancel", use_container_width=True)
        if cancel:
            st.session_state.adding_tenant = False
            st.rerun()
        if submit:
            is_valid = validate_tenant(tenant, container)
            if not is_valid:
                return
            with st.session_state.conn.session as s:
                statement = """
                    INSERT INTO tenant
                    (first_name, middle_name, last_name, phone_number, 
                    cell_number, email, date_of_birth, emergency_contact_name, 
                    emergency_contact_phone, emergency_contact_relationship, notes) 
                    VALUES 
                    (:first_name, :middle_name, :last_name, :phone_number, :cell_number, 
                    :email, :date_of_birth, :emergency_contact_name, :emergency_contact_phone, 
                    :emergency_contact_relationship, :notes)
                    ;"""
                s.execute(text(statement), tenant)
                s.commit()

            st.session_state.adding_tenant = False
            st.rerun()


def commit_changes(data):
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
        s.execute(sql, data.to_dict(orient="records")[0])
        s.commit()
    st.session_state.edit_tenant = False


def edit_tenant(container, data):
    st.session_state.edit_tenant = True
    selected = container.selectbox("Select Tenant to Edit", options=data, index=None)
    if selected:
        sel_tenant = container.data_editor(data[data['id'] == selected], hide_index=True, key="selected_tenant",
                                           column_config={"id": {"disabled": True, "label": "USER ID"}})
        base_data = sel_tenant.copy()
        is_valid = validate_tenant(sel_tenant.to_dict(orient="records")[0], container)
        col1, col2 = container.columns(2)
        is_diff = True if sel_tenant.to_dict(orient="records")[0] == base_data.to_dict(orient="records")[0] else False
        make_submit = True if is_valid and not is_diff else False
        submit = col1.button("Submit", use_container_width=True, type="primary", disabled=is_diff)
        cancel = col2.button("Cancel", use_container_width=True)
        if cancel:
            selected = None
            st.session_state.edit_tenant = False
            st.rerun()
        if submit:
            st.write("Are you sure you want to commit changes?")
            container.write(sel_tenant.to_dict(orient="records")[0])
            container.button("COMMIT", on_click=commit_changes, args=(sel_tenant,))
            if container.button("CANCEL"):
                selected = None
                st.session_state.edit_tenant = False
                st.rerun()
