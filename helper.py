import base64
import uuid
from enum import Enum

import pandas as pd
import streamlit as st
from st_aggrid import GridOptionsBuilder, GridUpdateMode, AgGrid

from es_connector import wrapper
from validator import SearchQueryMetaValidator

OPERATION_LIMIT = 50


class Action(Enum):
    UPDATE = "update"
    DELETE = "delete"
    INSERT = "insert"


def get_grid_by_operation(operation):
    if not operation:
        operation = Action.UPDATE
    df = wrapper.get_df()

    gd = GridOptionsBuilder.from_dataframe(df)
    # Create a wrapper for the handle_pagination_change function to accept df

    gd.configure_pagination(enabled=False, paginationPageSize=st.session_state.page_size)
    gd.configure_default_column(editable=True, groupable=True, resizable=True, sortable=True, filter=True)
    if operation == Action.DELETE:
        gd.configure_selection(selection_mode="multiple", use_checkbox=True)
    else:
        gd.configure_selection(selection_mode="multiple", use_checkbox=False)

    grid_options = gd.build()

    update_mode = GridUpdateMode.VALUE_CHANGED if operation == Action.UPDATE else GridUpdateMode.SELECTION_CHANGED

    return AgGrid(df, gridOptions=grid_options, update_mode=update_mode, allow_unsafe_jscode=True, height=500, theme='fresh')


def handle_delete():
    st.write("### Delete data")
    grid_table = get_grid_by_operation(Action.DELETE)
    sel_row = grid_table["selected_rows"]
    st.write("### Selected rows")
    if sel_row is not None:
        if len(sel_row) > OPERATION_LIMIT:
            st.error("Operation limit exceeded. Please select fewer rows.")
            return
        st.write(sel_row)
        # Add a Delete button
        if st.button("Delete Selected Rows"):
            selected_rows = grid_table["selected_rows"]
            if not selected_rows.empty:
                st.success("Selected rows have been deleted successfully!")
                try:
                    wrapper.delete_data(selected_rows)
                    st.rerun(scope="app")
                except Exception as e:
                    st.error(f"An error occurred while deleting data from Elasticsearch: {e}")
            else:
                st.warning("No rows selected for deletion.")
    else:
        st.write("No rows selected.")  # Message if no rows are selected


def handle_update():
    def show_changed_rows(updated_rows):
        # Prepare to store the changed values
        changed_info = []
        id_column = '_id'
        for index, updated_row in updated_rows.iterrows():
            changed_row = {id_column: updated_row[id_column]}  # Get the ID
            for column in updated_rows.columns:
                # Check if the column has changed
                if changes_mask.loc[index, column]:
                    # Store the earlier and updated values
                    changed_row[column] = {
                        'earlier_value': original_df.loc[index, column],
                        'new_value': updated_rows.loc[index, column]
                    }
            failures = SearchQueryMetaValidator().validate_row(updated_row)
            for column, message in failures.items():
                changed_row["error"] = message
                st.session_state.all_valid_updates = False

            changed_info.append(changed_row)
        changed_df = pd.DataFrame(changed_info)
        st.write(changed_df)
    grid_table = get_grid_by_operation(Action.UPDATE)

    # Create columns for inline display
    col1, col2, col3 = st.columns([3, 2, 1])  # Adjust the column sizes if necessary

    with col1:
        if st.button("Next"):
            st.session_state.page += 1  # Increment page number
            st.rerun()

    with col2:
        if st.button("Prev"):
            if st.session_state.page > 1:
                st.session_state.page -= 1  # Decrement page number
                st.rerun()

    with col3:
        st.write(f"### Page {st.session_state.page}")

    # Show success message if it exists
    if 'success_message' in st.session_state:
        st.success(st.session_state.success_message)
        del st.session_state.success_message  # Optionally clear the message after displaying
    updated_df = grid_table['data'].copy()
    original_df = wrapper.get_df()

    if original_df.empty:
        st.error("No data found in Elasticsearch.")
        return
    # To ensure comparison works, reset the index of both DataFrames
    original_df = original_df.reset_index(drop=True)
    updated_df = updated_df.reset_index(drop=True)

    original_df = original_df[original_df['_id'].isin(updated_df['_id'].values)]
    # Identify rows that have been updated
    changes_mask = (updated_df.ne(original_df))  # Create a mask of changes
    updated_rows = updated_df[changes_mask.any(axis=1)]  # Select only changed rows
    if len(updated_rows) > OPERATION_LIMIT:
        st.error("Operation limit exceeded. Please update fewer rows.")
        return
    if not updated_rows.empty:
        # Style the updated rows to highlight changes
        st.write("### Updated Rows")
        show_changed_rows(updated_rows)
        # Add a Submit button
        if st.button("Submit Changes"):
            try:
                if "all_valid_updates" in st.session_state and not st.session_state.all_valid_updates:
                    st.error("Some updates are invalid. Please correct them before submitting.")
                    return
                wrapper.write_data(updated_rows)
                st.rerun(scope="app")
            except Exception as e:
                st.error(f"An error occurred while writing data to Elasticsearch: {e}")
    else:
        st.write("No rows have been updated.")

def handle_insert():
    pass


action_handler_registery = {
    Action.UPDATE.value: handle_update,
    Action.DELETE.value: handle_delete,
    Action.INSERT.value: handle_insert
}


def handle_action(action):
    handler = action_handler_registery.get(action)
    handler()
