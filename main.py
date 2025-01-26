import json
import streamlit as st
import pandas as pd

# Sample DataFrame with a JSON column
data = {
    'Name': ['Alice', 'Bob', 'Charlie'],
    'Age': [25, 30, 35],
    'Details': [
        json.dumps({"hobbies": ["reading", "hiking"], "city": "New York"}),
        json.dumps({"hobbies": ["movies", "sports"], "city": "Los Angeles"}),
        json.dumps({"hobbies": ["music", "art"], "city": "Chicago"})
    ]
}
df = pd.DataFrame(data)

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

