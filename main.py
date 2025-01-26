import streamlit as st
import pandas as pd


def add_buttons(df, columns):
    # Handle button clicks based on row index
    for index, row in df.iterrows():
        for i, column in enumerate(df.columns):
            columns[i].write(row[column])  # Show data in respective column
        if columns[-3].button('DELETE', key=f'delete_{index}'):
            st.write(f"You clicked DELETE for {row['Name']}")
        if columns[-2].button('EDIT', key=f'edit_{index}'):
            st.write(f"You clicked EDIT for {row['Name']}")
        if columns[-1].button('SHOW', key=f'show_{index}'):
            if st.button('SHOW', key=f'show_{index}'):
                st.write(f"You clicked SHOW for {row['Name']}")


# Create a DataFrame with 10 rows and additional columns
data = {
    'Column 1': range(1, 11),                          # Numbers from 1 to 10
    'First Name': [f'First {i}' for i in range(1, 11)],   # First names
    'Second Name': [f'Second {i}' for i in range(1, 11)], # Second names
    'Column 2': [f'Row {i}' for i in range(1, 11)],   # Labels for rows
}


st.title("Streamlit Table with Action Column")

df = pd.DataFrame(data)
# Number of columns to display (including buttons)
num_columns = len(df.columns) + 3 # Adding three buttons
columns = st.columns(num_columns)  # Create the columns

# Title of the app

add_buttons(df, columns)

# Display the DataFrame with actions included
st.dataframe(df)


