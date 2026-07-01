# Import python packages
import streamlit as st
import requests
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col

# ------------------------------------
# Title
# ------------------------------------
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# ------------------------------------
# Snowflake Session
# ------------------------------------
session = get_active_session()

# ------------------------------------
# Name on Smoothie
# ------------------------------------
name_on_order = st.text_input("Name on Smoothie:")

if name_on_order:
    st.write(f"The name on your Smoothie will be: {name_on_order}")

# ------------------------------------
# Get Fruit Data
# ------------------------------------
my_dataframe = session.table("smoothies.public.fruit_options").select(
    col("FRUIT_NAME"),
    col("SEARCH_ON")
)

# Convert Snowpark DataFrame to Pandas
pd_df = my_dataframe.to_pandas()

# ------------------------------------
# Fruit Multiselect
# ------------------------------------
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    pd_df["FRUIT_NAME"].tolist(),
    max_selections=5
)

# ------------------------------------
# Nutrition Information
# ------------------------------------
if ingredients_list:

    ingredients_string = " ".join(ingredients_list)

    for fruit_chosen in ingredients_list:

        # Get API search value
        search_on = pd_df.loc[
            pd_df["FRUIT_NAME"] == fruit_chosen,
            "SEARCH_ON"
        ].iloc[0]

        st.write(f"The search value for {fruit_chosen} is {search_on}.")

        st.subheader(f"{fruit_chosen} Nutrition Information")

        try:
            response = requests.get(
                f"https://my.smoothiefroot.com/api/fruit/{search_on}"
            )

            st.dataframe(
                response.json(),
                use_container_width=True
            )

        except Exception as e:
            st.error(f"Error retrieving data: {e}")

    # --------------------------------
    # Insert Order
    # --------------------------------
    my_insert_stmt = f"""
    INSERT INTO smoothies.public.orders
    (ingredients, name_on_order)
    VALUES
    ('{ingredients_string}', '{name_on_order}')
    """

    if st.button("Submit Order"):

        session.sql(my_insert_stmt).collect()

        st.success("✅ Your Smoothie is ordered!")

        st.write("**Name:**", name_on_order)
        st.write("**Ingredients:**", ingredients_string)
