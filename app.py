import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Contact Sheet Cleaner", page_icon="🧼")
st.title("🧼 Contact & CRM Spreadsheet Cleaner")
st.write("Upload your data safely. Map your columns below to instantly clean your file.")

uploaded_file = st.file_uploader("Upload your messy spreadsheet (.csv or .xlsx)", type=["csv", "xlsx"])

if uploaded_file is not None:
    if "raw_df" not in st.session_state or st.session_state.get("file_name") != uploaded_file.name:
        if uploaded_file.name.endswith('.csv'):
            st.session_state["raw_df"] = pd.read_csv(uploaded_file)
        else:
            st.session_state["raw_df"] = pd.read_excel(uploaded_file)
        st.session_state["file_name"] = uploaded_file.name

    working_df = st.session_state["raw_df"].copy()
    all_columns = ["(Skip / None)"] + list(working_df.columns)

    # UI-First Column Mapping
    st.sidebar.header("🛠️ Map Your Columns")
    st.sidebar.write("Tell the tool which columns are which:")
    
    name_col = st.sidebar.selectbox("Name Column", all_columns)
    email_col = st.sidebar.selectbox("Email Column", all_columns)
    phone_col = st.sidebar.selectbox("Phone Column", all_columns)
    date_col = st.sidebar.selectbox("Date Column", all_columns)
    money_col = st.sidebar.selectbox("Financial/Revenue Column", all_columns)

    st.sidebar.header("⚙️ Global Rules")
    remove_dup = st.sidebar.checkbox("Delete Duplicate Rows", value=True)
    drop_empty = st.sidebar.checkbox("Drop Completely Empty Rows", value=True)

    # 4. PROCESSING PIPELINE
    if drop_empty:
        working_df = working_df.dropna(how='all')

    if remove_dup:
        working_df = working_df.drop_duplicates()

    # Dynamic Cleaning based on User UX Input
    if name_col != "(Skip / None)":
        working_df[name_col] = working_df[name_col].astype(str).str.strip().str.title().replace(['Null', 'Nan', 'nan'], None)
        
    if email_col != "(Skip / None)":
        working_df[email_col] = working_df[email_col].astype(str).str.strip().str.lower()
        
    if phone_col != "(Skip / None)":
        # Removes formatting but preserves empty/blank fields cleanly without injecting text
        working_df[phone_col] = working_df[phone_col].astype(str).str.replace(r'\D', '', regex=True)
        working_df[phone_col] = working_df[phone_col].replace(r'^\s*$', None, regex=True)

    if date_col != "(Skip / None)":
        # coerce keeps the script from crashing, turning broken dates to NaT (blank) safely
        working_df[date_col] = pd.to_datetime(working_df[date_col], errors='coerce').dt.strftime('%Y-%m-%d')
        
    if money_col != "(Skip / None)":
        working_df[money_col] = working_df[money_col].astype(str).str.replace(r'[$,\s]', '', regex=True)
        working_df[money_col] = pd.to_numeric(working_df[money_col], errors='coerce')

    st.subheader("👀 Cleaned Data Preview")
    st.dataframe(working_df.head(5))

    # Convert to CSV stream
    output_buffer = io.BytesIO()
    working_df.to_csv(output_buffer, index=False)
    output_buffer.seek(0)

    st.write("---")
    st.download_button(
        label="🚀 Download Cleaned Spreadsheet",
        data=output_buffer,
        file_name=f"cleaned_{st.session_state['file_name']}",
        mime="text/csv"
    )
