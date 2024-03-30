"""
@Author: Richard Soto
@Title: Login
@Description: This module contains the core functions to display the login page, will replace with a more secure login
function in the future.
"""

import streamlit as st

from src_lib.dashboard import page as dashboard

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.set_page_config(page_title="Login", page_icon=":lock:", layout="centered")
elif st.session_state.logged_in:
    st.set_page_config(page_title="free-rent", page_icon=":chart_with_upwards_trend:", layout="wide",
                       initial_sidebar_state="collapsed")

if "user" not in st.session_state:
    st.session_state.user = None
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "conn" not in st.session_state:
    st.session_state.conn = st.connection("free-rent", type="sql", ttl=0)


def login():
    st.title("Login")
    # username = st.text_input("Username")
    # password = st.text_input("Password", type="password")
    # Change this for production
    username = "admin"
    password = "admin"
    if st.button("Login"):
        if username == "admin" and password == "admin":
            st.session_state.user = username
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Invalid username or password")


if st.session_state.logged_in:
    dashboard.show()
else:
    login()
