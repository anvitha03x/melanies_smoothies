import streamlit as st
from snowflake.snowpark import Session
from snowflake.snowpark.functions import col

# -------------------------
# Title
# -------------------------
st.title("🥤 Customize Your Smoothie! 🥤")
st.write("Pick your favorite fruits and build your smoothie 🍓🍌🍍")

# -------------------------
# Customer name input
# -------------------------
name_on_order = st.text_input("Name on Smoothie:")

# -------------------------
# Snowflake connection (SAFE via secrets)
# -------------------------
conn_params = st.secrets["snowflake"]

session = Session.builder.configs(conn_params).create()

# -------------------------
# Fetch fruit list from Snowflake
# -------------------------
fruit_df = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"))
fruit_list = [row["FRUIT_NAME"] for row in fruit_df.collect()]

# -------------------------
# Multi-select fruits (max 5)
# -------------------------
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_list,
    max_selections=5
)

# -------------------------
# Submit order
# -------------------------
if st.button("Submit Order"):

    if not name_on_order:
        st.error("Please enter your name 😊")

    elif not ingredients_list:
        st.error("Please select fruits 🍓")

    else:

        ingredients_string = ", ".join(ingredients_list)

        try:
            session.sql(f"""
                INSERT INTO smoothies.public.orders (ingredients, name_on_order)
                VALUES ('{ingredients_string}', '{name_on_order}')
            """).collect()

            st.success("Order placed successfully 🎉")

        except Exception as e:
            st.error("Something went wrong while saving your order.")
            st.write("Check Snowflake table + permissions.")

import requests  
smoothiefroot_response = requests.get("[https://my.smoothiefroot.com/api/fruit/watermelon](https://my.smoothiefroot.com/api/fruit/watermelon)")  
st.text(smoothiefroot_response)
