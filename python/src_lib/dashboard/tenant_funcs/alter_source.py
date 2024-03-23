from datetime import datetime

import streamlit as st
from sqlalchemy import text


def add_tenant(container):
    def validate_tenant(tenant, container):
        errors = []
        if not tenant["first_name"]:
            errors.append("First Name")
        if not tenant["last_name"]:
            errors.append("Last Name")
        if not tenant["phone"]:
            errors.append("Phone")
        if not tenant["email"]:
            errors.append("Email")
        if not tenant["dob"]:
            errors.append("Date of Birth")
        if errors:
            container.error("REQUIRED: " + ", ".join(errors))
            return False
        return True

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
            "phone": form.text_input("Phone*"),
            "cell": form.text_input("Cell"),
            "email": form.text_input("Email*"),
            "dob": form.date_input("Date of Birth*", value=None,
                                   min_value=min,
                                   max_value=max),
            "emergency_contact": form.text_input("Emergency Contact"),
            "emergency_phone": form.text_input("Emergency Phone"),
            "emergency_relationship": form.text_input("Emergency Relationship"),
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
                    (:first_name, :middle_name, :last_name, :phone, :cell, 
                    :email, :dob, :emergency_contact, :emergency_phone, :emergency_relationship, :notes)
                    ;"""
                s.execute(text(statement), tenant)
                s.commit()

            st.session_state.adding_tenant = False
            st.rerun()
