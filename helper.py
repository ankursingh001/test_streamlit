from enum import Enum

import pandas as pd
import streamlit as st
from st_aggrid import GridOptionsBuilder, GridUpdateMode, AgGrid

OPERATION_LIMIT = 50
page_size = 20


class Action(Enum):
    UPSERT = "upsert"
    DELETE = "delete"


def on_page_changed(event):
    # Check if the new page event was triggered
    if event.newPage:
        new_page = event.api.paginationGetCurrentPage() + 1  # Get the new page number (zero-indexed)

        # # Determine whether to fetch more data
        # if len(st.session_state.grid_data) < new_page * page_size:  # If current data is less than expected
        #     fetch_result = wrapper.read_data(query)
        #
        #     if fetch_result:
        #         for hit in fetch_result:
        #             st.session_state.grid_data.append(hit['_source'])  # Append new results
        #         st.session_state.current_page = new_page  # Update the current page
        #     else:
        #         st.write("No more results found.")
        # else:
        #     st.session_state.current_page = new_page  # Update the current page


def get_grid_by_operation(df, operation):
    if not operation:
        operation = Action.UPSERT
    gd = GridOptionsBuilder.from_dataframe(df)
    sel_mode = st.radio('Selection type', options=["single", "multiple"])

    gd.configure_pagination(enabled=True)
    gd.configure_default_column(editable=True, groupable=True, resizable=True, sortable=True, filter=True)
    gd.configure_selection(selection_mode=sel_mode, use_checkbox=True)

    grid_options = gd.build()
    st.write()
    update_mode = GridUpdateMode.VALUE_CHANGED if operation == Action.UPSERT else GridUpdateMode.SELECTION_CHANGED

    return AgGrid(df, gridOptions=grid_options, update_mode=update_mode, allow_unsafe_jscode=True, height=500, theme='fresh')


def handle_delete(wrapper, df):
    st.write("### Delete data")
    grid_table = get_grid_by_operation(df, Action.DELETE)
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
                # Get the indices of the rows to delete
                indices_to_delete = selected_rows.index.tolist()
                indices_to_delete = [int(index) for index in indices_to_delete]
                df.drop(indices_to_delete, inplace=True)  # Drop rows from original DataFrame
                df.reset_index(drop=True, inplace=True)  # Reset index after deletion
                st.success("Selected rows have been deleted successfully!")
                wrapper.delete_data(df, selected_rows)
            else:
                st.warning("No rows selected for deletion.")
    else:
        st.write("No rows selected.")  # Message if no rows are selected


def handle_upsert(wrapper):
    def show_changed_rows(updated_rows):
        # Prepare to store the changed values
        changed_info = []
        id_column = '_id'
        for index in updated_rows.index:
            changed_row = {id_column: updated_rows.loc[index, id_column]}  # Get the ID
            for column in updated_rows.columns:
                # Check if the column has changed
                if changes_mask.loc[index, column]:
                    # Store the earlier and updated values
                    changed_row[column] = {
                        'earlier_value': original_df.loc[index, column],
                        'updated_value': updated_rows.loc[index, column]
                    }
            changed_info.append(changed_row)
        changed_df = pd.DataFrame(changed_info)
        st.write(changed_df)

    if "current_df" not in st.session_state:
        st.error("Current DataFrame not found. Please load data first.")
        return
    original_df = st.session_state.current_df.copy()
    grid_table = get_grid_by_operation(original_df, Action.UPSERT)
    updated_df = grid_table['data'].copy()

    # To ensure comparison works, reset the index of both DataFrames
    original_df = original_df.reset_index(drop=True)
    updated_df = updated_df.reset_index(drop=True)
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
            # Update the original DataFrame with changes from updated_rows
            for index in updated_rows.index:
                st.session_state.current_df.loc[index] = updated_rows.loc[index]  # Update original df at the index of updated rows
            wrapper.write_data(updated_rows)
    else:
        st.write("No rows have been updated.")


action_handler_registery = {
    Action.UPSERT.value: handle_upsert,
    Action.DELETE.value: handle_delete
}


def handle_action(action, wrapper):
    handler = action_handler_registery.get(action)
    handler(wrapper)
