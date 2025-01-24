import streamlit as st
import pandas as pd

def add_buttons(row):
    return row.append(pd.Series([st.button('Edit', key=f'edit{row.name}'), st.button('Delete', key=f'delete{row.name}')]))


# Create a DataFrame with 10 rows and additional columns
data = {
    'Column 1': range(1, 11),                          # Numbers from 1 to 10
    'First Name': [f'First {i}' for i in range(1, 11)],   # First names
    'Second Name': [f'Second {i}' for i in range(1, 11)], # Second names
    'Column 2': [f'Row {i}' for i in range(1, 11)],   # Labels for rows
}


df = pd.DataFrame(data)
df.apply(add_buttons, axis=1)

for index, row in df.iterrows():
    st.write(row)

# Title of the app
st.title("Streamlit Table with Action Column")


# Display the DataFrame with actions included
st.dataframe(df)

# Handle button clicks based on row index
for index, row in df.iterrows():
    if st.button("Show", key=f"{row.name}"):
        st.write(f"You clicked Show for Row {index + 1}")

    if st.button("Edit", key=f"{row.name}"):
        st.write(f"You clicked Edit for Row {index + 1}")

    if st.button("Delete", key=f"{row.name}"):
        st.write(f"You clicked Delete for Row {index + 1}")
