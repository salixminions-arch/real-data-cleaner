import streamlit as st
import pandas as pd
import re
import io

# 1. Page Configuration
st.set_page_config(page_title="Universal Sheet Cleaner Pro", page_icon="🧼", layout="wide")
st.title("🧼 Universal Spreadsheet Data Cleaner Pro")
st.write("The ultimate stateless pipeline to clean, format, validate, and secure your business files.")

# 2. File Upload Box (Cached via Session State memory)
uploaded_file = st.file_uploader("Upload your messy spreadsheet here", type=["csv", "xlsx"])

if uploaded_file is not None:
    # Cache raw data block to handle Streamlit re-runs smoothly
    if "raw_df" not in st.session_state or st.session_state.get("file_name") != uploaded_file.name:
        if uploaded_file.name.endswith('.csv'):
            st.session_state["raw_df"] = pd.read_csv(uploaded_file)
        else:
            st.session_state["raw_df"] = pd.read_excel(uploaded_file)
        st.session_state["file_name"] = uploaded_file.name

    # Always make a fresh copy to process
    working_df = st.session_state["raw_df"].copy()
    
    # 3. SIDEBAR CONTROLS
    st.sidebar.header("🛠️ Standard Operations")
    remove_dup = st.sidebar.checkbox("Delete Duplicate Rows", value=True)
    drop_empty = st.sidebar.checkbox("Drop Completely Empty Rows", value=True)
    clean_contacts = st.sidebar.checkbox("Standardize Text & Phone Casing", value=True)
    fix_dates_money = st.sidebar.checkbox("Format Dates & Currency Fields", value=True)
    
    st.sidebar.subheader("🚀 Advanced Cleaning Modules")
    validate_emails = st.sidebar.checkbox("Validate Email Integrity", value=True)
    enable_splitter = st.sidebar.checkbox("Split Full Names (First/Last)", value=False)
    enable_imputation = st.sidebar.checkbox("Auto-Fill Empty/Blank Cells", value=False)
    enable_anomaly = st.sidebar.checkbox("Flag Financial Anomalies", value=False)

    # 4. PROCESSING PIPELINE
    if drop_empty:
        working_df = working_df.dropna(how='all')

    if remove_dup:
        working_df = working_df.drop_duplicates()

    if clean_contacts:
        if 'Name' in working_df.columns:
            working_df['Name'] = working_df['Name'].astype(str).str.strip().str.title().replace('Null', None)
        if 'Email' in working_df.columns:
            working_df['Email'] = working_df['Email'].astype(str).str.strip().str.lower()
        if 'Phone' in working_df.columns:
            working_df['Phone'] = working_df['Phone'].astype(str).str.replace(r'\D', '', regex=True)
            working_df['Phone'] = working_df['Phone'].replace('', 'MISSING')

    if validate_emails:
        email_cols = [c for c in working_df.columns if 'email' in c.lower() or 'e-mail' in c.lower()]
        email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        for c in email_cols:
            working_df[c] = working_df[c].astype(str).str.strip().str.lower()
            working_df[f'{c}_Status'] = working_df[c].apply(
                lambda x: "✅ Valid" if re.match(email_pattern, str(x)) else "❌ Invalid Format"
            )

    # FEATURE 1: SMART NAME SPLITTER
    if enable_splitter:
        name_cols = [c for c in working_df.columns if 'name' in c.lower() and 'first' not in c.lower() and 'last' not in c.lower()]
        for c in name_cols:
            # Splits string at the first white space into a max of 2 columns
            split_data = working_df[c].astype(str).str.strip().str.split(' ', n=1, expand=True)
            working_df['First Name'] = split_data[0].str.title()
            working_df['Last Name'] = split_data[1].str.title().fillna('')

    # FEATURE 2: MISSING DATA AUTO-FILLER
    if enable_imputation:
        # Separate text strings columns from numeric/math columns
        text_cols = working_df.select_dtypes(include=['object']).columns
        num_cols = working_df.select_dtypes(include=['number']).columns
        # Apply data typing default values cleanly to clear missing values
        working_df[text_cols] = working_df[text_cols].fillna("Unknown")
        working_df[num_cols] = working_df[num_cols].fillna(0.0)

    if fix_dates_money:
        if 'Signup Date' in working_df.columns:
            working_df['Signup Date'] = pd.to_datetime(working_df['Signup Date'], errors='coerce').dt.strftime('%Y-%m-%d')
        if 'Revenue' in working_df.columns:
            working_df['Revenue'] = working_df['Revenue'].astype(str).str.replace(r'[$,]', '', regex=True)
            working_df['Revenue'] = pd.to_numeric(working_df['Revenue'], errors='coerce').fillna(0.0)

    # FEATURE 3: FINANCIAL ANOMALY GUARD
    if enable_anomaly:
        num_cols = working_df.select_dtypes(include=['number']).columns
        for c in num_cols:
            # Scan columns for impossible negative valuations
            working_df[f'{c}_Alert'] = working_df[c].apply(
                lambda x: "🚨 Negative Error" if x < 0 else "Clear"
            )

    # 5. USER INTERFACE DISPLAY
    st.subheader("👀 Cleaned Data Preview")
    st.dataframe(working_df.head(10))

    # 6. EXPORT PREPARATION
    output_buffer = io.BytesIO()
    working_df.to_csv(output_buffer, index=False)
    output_buffer.seek(0)

    st.write("---")
    st.download_button(
        label="🚀 Download Premium Cleaned Spreadsheet",
        data=output_buffer,
        file_name=f"cleaned_pro_{st.session_state['file_name']}",
        mime="text/csv"
    )