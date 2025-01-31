from enum import Enum
import streamlit as st
from st_aggrid import GridOptionsBuilder, GridUpdateMode, AgGrid


class Action(Enum):
    UPSERT = "upsert"
    DELETE = "delete"


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
        st.write(sel_row)
        # Add a Delete button
        if st.button("Delete Selected Rows"):
            selected_rows = grid_table["selected_rows"]
            if not selected_rows.empty:
                # Get the indices of the rows to delete
                indices_to_delete = selected_rows.index_alias.tolist()
                indices_to_delete = [int(index) for index in indices_to_delete]
                df.drop(indices_to_delete, inplace=True)  # Drop rows from original DataFrame
                df.reset_index(drop=True, inplace=True)  # Reset index after deletion
                st.success("Selected rows have been deleted successfully!")
                st.write("### Updated dataframe")
                st.dataframe(df)  # Display the updated DataFrame
            else:
                st.warning("No rows selected for deletion.")
    else:
        st.write("No rows selected.")  # Message if no rows are selected


def handle_upsert(wrapper, df):
    print("handle upsert")
    original_df = df.copy()
    grid_table = get_grid_by_operation(df, Action.UPSERT)
    updated_df = grid_table['data']

    # To ensure comparison works, reset the index of both DataFrames
    original_df = original_df.reset_index(drop=True)
    updated_df = updated_df.reset_index(drop=True)
    # Identify rows that have been updated
    changes_mask = (updated_df.ne(original_df))  # Create a mask of changes
    print(f"updated df dtypes: {updated_df.dtypes} and original df dtypes: {original_df.dtypes}")
    updated_rows = updated_df[changes_mask.any(axis=1)]  # Select only changed rows
    print(f"updated rows {updated_rows}")
    if not updated_rows.empty:
        # Style the updated rows to highlight changes
        st.write("### Updated Rows")
        st.dataframe(updated_rows)  # Display the updated rows with highlighted changes
        # Add a Submit button
        if st.button("Submit Changes"):
            # Update the original DataFrame with changes from updated_rows
            for index in updated_rows.index:
                df.loc[index] = updated_rows.loc[index]  # Update original df at the index of updated rows
            st.success("Changes have been submitted successfully!")

            wrapper.write_data(df)
    else:
        st.write("No rows have been updated.")


action_handler_registery = {
    Action.UPSERT.value: handle_upsert,
    Action.DELETE.value: handle_delete
}


def handle_action(action, wrapper, df):
    handler = action_handler_registery.get(action)
    handler(wrapper, df)
