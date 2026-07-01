# Import python packages
import streamlit as st
import requests
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col

# Title
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")

st.write("Choose the fruits you want in your custom Smoothie!")

# Name input
name_on_order = st.text_input("Name on Smoothie:")

# Get Snowflake session
from snowflake.snowpark import Session

conn_params = st.secrets["snowflake"]
session = Session.builder.configs(conn_params).create()

# Get fruit names
fruit_df = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"))

# Convert Snowpark DataFrame to Python list
fruit_list = [row["FRUIT_NAME"] for row in fruit_df.collect()]

# Multiselect
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_list,
    max_selections=5
)

# -------------------------
# NEW SECTION: API CALL
# -------------------------
import urllib.parse

if ingredients_list:

    selected_fruit = urllib.parse.quote(ingredients_list[0])

    try:
        smoothiefroot_response = requests.get(
    f"https://my.smoothiefroot.com/api/fruit/{selected_fruit}"
)

        st.write("🍉 SmoothieFroot Nutrition Info")
        #st.write(smoothiefroot_response.json())

        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

    except Exception as e:
        st.error(f"API error: {e}")

# -------------------------
# INSERT ORDER INTO SNOWFLAKE
# -------------------------
if ingredients_list:

    ingredients_string = " ".join(ingredients_list)

    my_insert_stmt = f"""
    INSERT INTO smoothies.public.orders
    (ingredients, name_on_order)
    VALUES
    ('{ingredients_string}', '{name_on_order}')
    """

    # Optional: Show SQL for debugging
    st.code(my_insert_stmt, language="sql")

    # Submit button
    if st.button("Submit Order"):

        session.sql(my_insert_stmt).collect()

        st.success("✅ Your Smoothie is ordered!")

        st.write(f"**Name:** {name_on_order}")
        st.write(f"**Ingredients:** {ingredients_string}")
