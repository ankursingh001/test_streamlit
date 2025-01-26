import json
import streamlit as st
import pandas as pd

# Load data from a CSV file
def load_data_from_csv(file_path):
    return pd.read_csv(file_path)

# Specify the path to your CSV file
file_path = 'data.csv'  # Update this to your actual file path
df = load_data_from_csv(file_path)

# Reset index if it is a MultiIndex
if isinstance(df.index, pd.MultiIndex):
    df = df.reset_index()



# Display the data editor for direct editing
edited_df = st.data_editor(df, num_rows="dynamic")  # Allows direct editing of the DataFrame

# Check if the edited DataFrame is different from the original DataFrame
if not edited_df.equals(df):
    if st.button("Submit Changes"):
        # Update the original DataFrame with the edited DataFrame values
        df = edited_df.copy()  # Update here or you can store it in a session state
        st.success("Changes Submitted Successfully!")
else:
    st.info("No changes made to the DataFrame.")

# Display the current state of the DataFrame
st.write("### Previous DataFrame")
st.dataframe(df)
