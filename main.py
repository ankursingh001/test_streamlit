import json

import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, DataReturnMode

# Sample DataFrame
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
grid_width = '600px'

# Build the grid options
gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_default_column(editable=True)  # Allow editing
gb.configure_selection("single")  # Enable single row selection
gridOptions = gb.build()

# Display the grid and store the selection
grid_response = AgGrid(df, gridOptions=gridOptions, enable_enterprise_modules=True, allow_unsafe_jscode=True, data_return_mode=DataReturnMode.AS_INPUT, fit_columns_on_grid_load=True)

# Set the custom CSS style for the AgGrid width
st.markdown(f'<style> .ag-theme-alpine {{ width: {grid_width}; }} </style>', unsafe_allow_html=True)


# Check if a row was selected by the user
selected_rows = grid_response['selected_rows']
if selected_rows is not None and not selected_rows.empty:  # Check if the list has any elements'
    selected_row = selected_rows.iloc[0]  # Get the first selected row
    edit_mode = st.session_state.get("edit_mode", False)  # Check if we are in edit mode

    # If in edit mode or the "Edit Selected User" button is pressed, show the form
    if edit_mode or st.button("Edit Selected User"):
        st.session_state['edit_mode'] = True  # Enter edit mode
        st.session_state['new_name'] = selected_row['Name']
        st.session_state['new_age'] = selected_row['Age']
        st.session_state['new_details'] = selected_row['Details']

        with st.form("edit_user_form"):
            st.write("### Edit Selected User")

            # Create the input fields
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Name:**")
                st.session_state['new_name'] = st.text_input(" ", value=st.session_state['new_name'])

            with col2:
                st.markdown("**Age:**")
                st.session_state['new_age'] = st.number_input(" ", value=st.session_state['new_age'], min_value=0)

            st.markdown("**Details (JSON):**")
            details_json = st.json(body=st.session_state['new_details'])

            # Include a submit button for the form
            submitted = st.form_submit_button("Save Changes")
            if submitted:
                # Update the DataFrame with new values
                df.loc[df['Name'] == selected_row['Name'], 'Name'] = st.session_state['new_name']
                df.loc[df['Name'] == selected_row['Name'], 'Age'] = st.session_state['new_age']
                df.loc[df['Name'] == selected_row['Name'], 'Details'] = details_json
                st.success("User information updated successfully!")
                st.session_state['edit_mode'] = False  # Exit edit mode after saving

    # Button to show row info as JSON
    if st.button("Show Row Info as JSON"):
        # Convert the selected row to JSON format
        row_json = json.dumps(selected_row.to_dict(), indent=4)
        st.write("### Row Information in JSON format:")
        st.code(row_json, language='json')


