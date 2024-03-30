"""
@Author: Richard Soto
@Title: Pets
@Description: This module contains the functions to manage the pets for a tenant.
"""

from time import sleep

import streamlit as st
from sqlalchemy.sql import text


def get_pets(tid):
    pets = st.session_state.conn.query(f"SELECT * FROM pet WHERE tenant_id = {tid}")
    return pets


def pet_is_valid(pet):
    if not pet["name"]:
        return False
    if not pet["species"]:
        return False
    if not pet["breed"]:
        return False
    if not pet["age"]:
        return False
    if not pet["weight"]:
        return False
    return True


def insert_pet_to_db(pet):
    try:
        with st.session_state.conn.session as s:
            sql = text("""
            INSERT INTO pet (tenant_id, name, species, breed,
            age, weight, notes)
            VALUES (:tenant_id, :name, :species, :breed,
            :age, :weight, :notes)
            """)
            s.execute(sql, pet)
            s.commit()
        return True
    except Exception as e:
        st.error(f"Error inserting pet: {e}")
        return False


def update_pet_in_db(pet):
    try:
        with st.session_state.conn.session as s:
            sql = text("""
            UPDATE pet
            SET name = :name, species = :species, breed = :breed,
            age = :age, weight = :weight, notes = :notes
            WHERE id = :id
            """)
            s.execute(sql, pet)
            s.commit()
        return True
    except Exception as e:
        st.error(f"Error updating pet: {e}")
        return False


def delete_pet_callback(pet, container):
    container.warning(f"Are you sure you want to delete pet: {pet['name']}?")
    col1, col2 = container.columns(2)
    confirm = col1.button("Confirm Delete", key="confirm_delete",
                          use_container_width=True,
                          on_click=delete_pet_from_db,
                          args=[pet])
    cancel = col2.button("Cancel", key="cancel_delete",
                         use_container_width=True)


def delete_pet_from_db(pet):
    try:
        with st.session_state.conn.session as s:
            sql = text("""
            DELETE FROM pet
            WHERE id = :id
            """)
            s.execute(sql, pet)
            s.commit()
        return True
    except KeyboardInterrupt as e:
        print(e)
        st.error(f"Error deleting pet: {e}")
        return False


def add_pet(container, tid):
    st.session_state.adding_pet = True
    name, species, breed = container.columns(3)
    age, weight = container.columns(2)
    notes = container.text_area("Notes")
    species_list = ["Dog", "Cat", "Bird", "Fish", "Reptile", "Other"]
    pet = {
        "tenant_id": tid,
        "name": name.text_input("Name"),
        "species": species.selectbox("Species",
                                     options=species_list,
                                     index=None),
        "breed": breed.text_input("Breed"),
        "age": age.number_input("Age",
                                min_value=0, max_value=100, step=1),
        "weight": weight.number_input("Weight",
                                      min_value=0, max_value=300, step=1),
        "notes": notes
    }
    is_valid = pet_is_valid(pet)
    col1, col2 = container.columns(2)
    submit = col1.button("Submit", disabled=not is_valid,
                         key="submit_pet",
                         use_container_width=True)
    cancel = col2.button("Cancel", key="cancel_pet",
                         use_container_width=True)
    if cancel:
        st.session_state.adding_pet = False
        st.rerun()
    if submit:
        if insert_pet_to_db(pet):
            container.success("Pet added successfully...")
            sleep(3)
        else:
            container.error("Error adding pet...")
            sleep(3)
        st.session_state.adding_pet = False
        st.rerun()


def edit_pet(container, pet):
    st.session_state.edit_pet = True
    name, species, breed = container.columns(3)
    age, weight = container.columns(2)
    pet_id = pet["id"].iloc[0]
    species_list = ["Dog", "Cat", "Bird", "Fish", "Reptile", "Other"]
    pet = {
        "id": pet_id,
        "tenant_id": pet["tenant_id"].values[0],
        "name": name.text_input("Name", value=pet["name"].values[0]),
        "species": species.selectbox("Species",
                                     options=species_list,
                                     index=species_list.index(pet["species"].values[0])),
        "breed": breed.text_input("Breed", value=pet["breed"].values[0]),
        "age": age.number_input("Age",
                                min_value=0, max_value=100, step=1,
                                value=pet["age"].values[0]),
        "weight": weight.number_input("Weight",
                                      min_value=0.0, max_value=300.0, step=1.0,
                                      value=pet["weight"].values[0]),
        "notes": container.text_area("Notes", value=pet["notes"].values[0])
    }
    is_valid = pet_is_valid(pet)
    col1, col2 = container.columns(2)
    submit = col1.button("Submit", disabled=not is_valid,
                         key="submit_pet",
                         use_container_width=True)
    col2.button("Delete", key="delete_pet",
                use_container_width=True,
                on_click=delete_pet_callback,
                args=(pet, container))
    if submit:
        if update_pet_in_db(pet):
            container.success("Pet updated successfully...")
            sleep(3)
        else:
            container.error("Error updating pet...")
            sleep(3)
        st.rerun()


def show(container):
    if "adding_pet" not in st.session_state:
        st.session_state.adding_pet = False
    if "edit_pet" not in st.session_state:
        st.session_state.edit_pet = False
    if "deleting_pet" not in st.session_state:
        st.session_state.deleting_pet = False

    if st.session_state.selected_tenant:
        sel_tenant_id = st.session_state.selected_tenant
        pets = get_pets(sel_tenant_id)
        pet_list_by_name = pets["name"].to_list()

        expanded = True if st.session_state.adding_pet or st.session_state.edit_pet else False
        exp = container.expander(f"Pets ({len(pets)})", expanded=expanded)
        if len(pets) == 0:
            exp.warning("🔎 No Pets Found...")
            selected = None
        else:
            exp.dataframe(pets[["name", "species", "breed"]],
                          hide_index=True,
                          use_container_width=True)
            selected = exp.selectbox("Select Pet", pet_list_by_name,
                                     key="selected_pet",
                                     index=None)
        show_add = True if selected else False
        if not show_add:
            add = exp.button("Add Pet", use_container_width=True)
            if add or st.session_state.adding_pet:
                add_pet(exp, sel_tenant_id)
        else:
            pet = pets[pets["name"] == selected]
            edit_pet(exp, pet)
