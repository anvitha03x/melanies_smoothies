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
        st.error("Please select at least one fruit 🍎")
    else:

        ingredients_string = ", ".join(ingredients_list)

        # Safe insert using Snowpark DataFrame API (no SQL injection risk)
        order_df = session.create_dataframe(
            [[ingredients_string, name_on_order]],
            schema=["INGREDIENTS", "NAME_ON_ORDER"]
        )

        order_df.write.mode("append").save_as_table("smoothies.public.orders")

        # Success message
        st.success("Your smoothie order has been placed! 🎉")

        st.write("### Order Summary")
        st.write(f"**Name:** {name_on_order}")
        st.write(f"**Ingredients:** {ingredients_string}")
