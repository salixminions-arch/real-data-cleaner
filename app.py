import streamlit as st
import pandas as pd
import io

# 1. Web Page Header Setup
st.set_page_config(page_title="Instant Sheet Cleaner", page_icon="🧼")
st.title("🧼 Universal Spreadsheet Data Cleaner")
st.write("Upload any messy CSV or Excel file. Clean and format it instantly.")

# 2. File Upload Box (File stays strictly in temporary system RAM)
uploaded_file = st.file_uploader("Upload your file here", type=["csv", "xlsx"])

if uploaded_file is not None:
    # Read the file directly from memory stream into a Pandas DataFrame
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
        
    st.success("File uploaded successfully!")
    
    # 3. Interactive Automated Cleaning Options
    st.sidebar.header("🛠️ Cleaning Options")
    remove_dup = st.sidebar.checkbox("Delete Duplicate Rows", value=True)
    drop_empty = st.sidebar.checkbox("Drop Completely Empty Rows", value=True)
    fix_text = st.sidebar.checkbox("Standardize Text (Trim Spaces & Title Case Names)", value=True)

    # 4. Processing the Data inside Memory Pipeline
    if drop_empty:
        df = df.dropna(how='all')

    if remove_dup:
        df = df.drop_duplicates()

    if fix_text:
        for col in df.columns:
            if df[col].dtype == 'object': # Check if column contains text strings
                df[col] = df[col].astype(str).str.strip()
                # If column name looks like a name field, apply Capitalization rules
                if 'name' in col.lower():
                    df[col] = df[col].str.title()

    # 5. Display a 5-Row Cleaned Preview Window to the User
    st.subheader("👀 Cleaned Data Preview")
    st.dataframe(df.head(5))

    # 6. Convert the clean memory DataFrame back into downloadable file bytes
    output_buffer = io.BytesIO()
    df.to_csv(output_buffer, index=False)
    output_buffer.seek(0)

    # 7. Secure Action/Download Button
    st.write("---")
    st.download_button(
        label="🚀 Download Cleaned Spreadsheet",
        data=output_buffer,
        file_name=f"cleaned_{uploaded_file.name}",
        mime="text/csv"
    )