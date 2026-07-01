import streamlit as st
import requests
from snowflake.snowpark import Session
from snowflake.snowpark.functions import col

# -------------------------
# Title
# -------------------------
st.title("🥤 Customize Your Smoothie!")
st.write("Build your perfect smoothie using Snowflake + API data 🍓🍌🍍")

# -------------------------
# User input
# -------------------------
name_on_order = st.text_input("Name on Smoothie:")

# -------------------------
# Snowflake connection (SAFE)
# -------------------------
conn_params = st.secrets["snowflake"]
session = Session.builder.configs(conn_params).create()

# -------------------------
# Get fruit list from Snowflake
# -------------------------
fruit_df = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"))
fruit_list = [row["FRUIT_NAME"] for row in fruit_df.collect()]

# -------------------------
# Multi-select fruits
# -------------------------
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_list,
    max_selections=5
)

# -------------------------
# API CALL (FIXED)
# -------------------------
st.subheader("🍉 Fruit Info (API)")

selected_fruit = st.text_input("Enter a fruit to get info from API (e.g. watermelon)")

if selected_fruit:
    try:
        url = f"https://my.smoothiefroot.com/api/fruit/{selected_fruit}"

        response = requests.get(url)

        if response.status_code == 200:
            fruit_info = response.json()
            st.write("### Fruit Details")
            st.json(fruit_info)
        else:
            st.error("API returned an error.")
    except Exception as e:
        st.error(f"Request failed: {e}")

# -------------------------
# Submit order
# -------------------------
if st.button("Submit Order"):

    if not name_on_order:
        st.error("Please enter your name 😊")

    elif not ingredients_list:
        st.error("Please select at least one fruit 🍓")

    else:
        ingredients_string = ", ".join(ingredients_list)

        try:
            session.sql(f"""
                INSERT INTO smoothies.public.orders (ingredients, name_on_order)
                VALUES ('{ingredients_string}', '{name_on_order}')
            """).collect()

            st.success("🎉 Your smoothie order has been placed!")

            st.write("### Order Summary")
            st.write(f"**Name:** {name_on_order}")
            st.write(f"**Ingredients:** {ingredients_string}")

        except Exception:
            st.error("Failed to save order. Check Snowflake table & permissions.")
