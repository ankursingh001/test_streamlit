import json
import streamlit as st
import pandas as pd
from st_aggrid import GridOptionsBuilder, JsCode, AgGrid, DataReturnMode


# Load data from a CSV file
def load_data_from_csv(file_path):
    return pd.read_csv(file_path)


# Specify the path to your CSV file
file_path = 'data.csv'  # Update this to your actual file path
df = load_data_from_csv(file_path)

# Build grid options
gb = GridOptionsBuilder.from_dataframe(df)
# Show a simple text representation of the JSON in the "Details" column
gb.configure_column("Details", cellRenderer=JsCode('''function(params) {
    const details = JSON.parse(params.value);
    return `City: ${details.city}, Hobbies: ${details.hobbies.join(', ')}`; 
}'''))  # Custom renderer for JSON

# Single delete button in the Actions column
gb.configure_column("Actions", cellRenderer=JsCode('''function(params) {
    const eDiv = document.createElement('div');

    const deleteButton = document.createElement('button');
    deleteButton.innerText = 'Delete';
    deleteButton.style.backgroundColor = 'red';
    deleteButton.style.color = 'white';
    deleteButton.onclick = function() {
        // Trigger deletion
        streamlit.setComponentValue({ action: 'DELETE', name: params.data.Name });
    };

    eDiv.appendChild(deleteButton);
    return eDiv;
}'''))  # Button in the Actions column

gridOptions = gb.build()

# Display the AgGrid
grid_response = AgGrid(df, gridOptions=gridOptions, enable_enterprise_modules=True, allow_unsafe_jscode=True,
                       data_return_mode=DataReturnMode.AS_INPUT)

# Handle events: check if delete action was triggered
if grid_response and 'componentValue' in grid_response:
    action = grid_response['componentValue'].get('action')
    name = grid_response['componentValue'].get('name')

    if action == 'DELETE':
        # Delete the selected row
        df = df[df['Name'] != name].reset_index(drop=True)
        st.success(f"{name} has been deleted.")

# Display the updated DataFrame
st.write("### Updated DataFrame")
st.dataframe(df)
