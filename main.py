import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, DataReturnMode

# Sample DataFrame
data = {
    'Name': ['Alice', 'Bob', 'Charlie'],
    'Age': [25, 30, 35]
}
df = pd.DataFrame(data)

# Build the grid options
gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_default_column(editable=True)  # Allow editing
gb.configure_selection("single")  # Enable single row selection
gridOptions = gb.build()

# Display the grid and store the selection
grid_response = AgGrid(df, gridOptions=gridOptions, enable_enterprise_modules=True, allow_unsafe_jscode=True, data_return_mode=DataReturnMode.AS_INPUT)

# Check if a row was selected by the user
selected_rows = grid_response['selected_rows']
print(grid_response)
if not selected_rows.empty:  # Check if the list has any elements'
    print(selected_rows)
    selected_row = selected_rows.iloc[0]  # Get the first selected row


