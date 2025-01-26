import json

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
grid_response = AgGrid(df, gridOptions=gridOptions, enable_enterprise_modules=True, allow_unsafe_jscode=True, data_return_mode=DataReturnMode.AS_INPUT, fit_columns_on_grid_load=True)

# Check if a row was selected by the user
selected_rows = grid_response['selected_rows']
if not selected_rows.empty:  # Check if the list has any elements'
    selected_row = selected_rows.iloc[0]  # Get the first selected row
    edit_mode = st.session_state.get("edit_mode", False)  # Check if we are in edit mode

    if edit_mode or st.button("Edit Selected User"):
        st.write("### Edit Selected User")
        new_name = st.text_input("Name", value=selected_row['Name'])
        new_age = st.number_input("Age", value=selected_row['Age'], min_value=0)

        if st.button("Save Changes"):
            # Update the DataFrame with new values
            df.loc[df['Name'] == selected_row['Name'], 'Name'] = new_name
            df.loc[df['Name'] == selected_row['Name'], 'Age'] = new_age
            st.success("User information updated successfully!")
            st.session_state["edit_mode"] = False  # Exit edit mode after saving

    # Button to show row info as JSON
    if st.button("Show Row Info as JSON"):
        # Convert the selected row to JSON format
        row_json = json.dumps(selected_row.to_dict(), indent=4)
        st.write("### Row Information in JSON format:")
        st.code(row_json, language='json')


