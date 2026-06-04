import streamlit as st
import pandas as pd
import requests
import re
import io

# 1. Page Frame Configuration
st.set_page_config(page_title="Universal Sheet Cleaner", page_icon="🧼", layout="wide")
st.title("🧼 Universal Spreadsheet Data Cleaner")
st.write("Upload your data once. Your file will remain safely cached in system memory while you modify formatting options.")


# 2. GUMROAD AUTOMATED LICENSE VERIFICATION ENGINE
def verify_gumroad_license(license_key):
    # ⚠️ CRITICAL STEP: Replace 'your_product_id' with your actual Gumroad permalink slug!
    product_permalink = "your_product_id" 
    
    url = "https://gumroad.com"
    data = {
        "product_permalink": product_permalink,
        "license_key": license_key
    }
    
    try:
        # Secure background request checking Gumroad's database with a 5-second max timeout guard
        response = requests.post(url, data=data, timeout=5)
        result = response.json()
        
        # Access check: Key must exist, be active, and not leaked/shared extensively
        if result.get("success") == True and result.get("uses", 0) <= 3:
            return True
    except:
        return False
    return False


# 3. SIDEBAR SECURITY GATING UI
st.sidebar.header("🔑 Premium Activation")
# ⚠️ Replace this placeholder link with your actual public Gumroad store link!
gumroad_link = "https://gumroad.com"
st.sidebar.markdown(f"[💳 Click Here to Buy Premium Access Key]({gumroad_link})")

user_key = st.sidebar.text_input("Enter Gumroad License Key", type="password")

# Process state verification dynamically
is_premium_active = False
if user_key.strip():
    with st.sidebar.spinner("Verifying key..."):
        is_premium_active = verify_gumroad_license(user_key)


# 4. CONDITIONAL SYSTEM LAYOUT GATES
if not is_premium_active:
    # ==========================================
    # MODE A: THE FREE LIVE SANDBOX DEMO
    # ==========================================
    st.info("🔒 App is currently running in Read-Only Demo Mode. Enter a valid Gumroad License Key in the sidebar to unlock custom file uploads.")
    
    # 1. Fixed Mock Data Set for Visitors
    if "demo_df" not in st.session_state:
        mock_raw = {
            "Name": ["JOHN DOE", "jane smith", "NULL", "Bob Ross"],
            "Email": ["john@example.com ", "JANE@EXAMPLE.COM", "info@company.com", "bob@bob.com"],
            "Phone": ["123-456-7890", "   ", "9876543210", "555.555.5555"],
            "Signup Date": ["2026/01/15", "15-Jan-26", "2026-01-16", "2026/01/17"],
            "Revenue": ["$1,250.00", "$950", "", "$3,400.50"]
        }
        st.session_state["demo_df"] = pd.DataFrame(mock_raw)
        
    demo_working_df = st.session_state["demo_df"].copy()
    
    # 2. Free Interface Demonstration Checkboxes
    st.sidebar.subheader("🛠️ Sandbox Demo Options")
    demo_remove_dup = st.sidebar.checkbox("Delete Duplicate Rows", value=True, key="d_dup")
    demo_clean_contacts = st.sidebar.checkbox("Clean Contact Info", value=True, key="d_con")
    demo_fix_dates = st.sidebar.checkbox("Standardize Dates & Revenue", value=True, key="d_dat")

    # 3. Running your processing engine over mock memory rows
    if demo_remove_dup:
        demo_working_df = demo_working_df.drop_duplicates()
    if demo_clean_contacts:
        demo_working_df['Name'] = demo_working_df['Name'].astype(str).str.strip().str.title().replace('Null', None)
        demo_working_df['Email'] = demo_working_df['Email'].astype(str).str.strip().str.lower()
        demo_working_df['Phone'] = demo_working_df['Phone'].astype(str).str.replace(r'\D', '', regex=True).replace('', 'MISSING')
    if demo_fix_dates:
        demo_working_df['Signup Date'] = pd.to_datetime(demo_working_df['Signup Date'], errors='coerce').dt.strftime('%Y-%m-%d')
        demo_working_df['Revenue'] = demo_working_df['Revenue'].astype(str).str.replace(r'[$,]', '', regex=True)
        demo_working_df['Revenue'] = pd.to_numeric(demo_working_df['Revenue'], errors='coerce').fillna(0.0)

    # 4. Display Split Panels for Visual Proof
    col_left, col_right = st.columns(2)
    with col_left:
        st.subheader("❌ Input: Original Messy Data")
        st.dataframe(st.session_state["demo_df"], use_container_width=True)
    with col_right:
        st.subheader("✨ Output: Automated Clean View")
        st.dataframe(demo_working_df, use_container_width=True)

else:
    # ==========================================
    # MODE B: THE FULL PREMIUM PAID APPLICATION ENGINE
    # ==========================================
    st.sidebar.success("✅ Premium Access Granted")
    st.success("🎉 Welcome back! The full file processing pipe is completely unlocked.")
    
    # Expose the real custom upload widget to your paying customer
    uploaded_file = st.file_uploader("Upload your messy spreadsheet here", type=["csv", "xlsx"])

    if uploaded_file is not None:
        # Save raw file state into permanent memory cache if it isn't there yet
        if "raw_df" not in st.session_state or st.session_state.get("file_name") != uploaded_file.name:
            if uploaded_file.name.endswith('.csv'):
                st.session_state["raw_df"] = pd.read_csv(uploaded_file)
            else:
                st.session_state["raw_df"] = pd.read_excel(uploaded_file)
            st.session_state["file_name"] = uploaded_file.name

        # Always clone a fresh working copy from our saved backup memory data
        working_df = st.session_state["raw_df"].copy()
        
        # 3. SIDEBAR CONTROLS (Toggling these will now smoothly trigger live calculation changes)
        st.sidebar.header("🛠️ Cleaning Options")
        remove_dup = st.sidebar.checkbox("Delete Duplicate Rows", value=True)
        drop_empty = st.sidebar.checkbox("Drop Completely Empty Rows", value=True)
        clean_contacts = st.sidebar.checkbox("Clean Contact Info (Names, Emails, Phones)", value=True)
        fix_dates_money = st.sidebar.checkbox("Standardize Dates & Repair Financial Data", value=True)

        # 4. PROCESSING PIPELINE (Executes on your active working layout)
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

        if fix_dates_money:
            if 'Signup Date' in working_df.columns:
                working_df['Signup Date'] = pd.to_datetime(working_df['Signup Date'], errors='coerce').dt.strftime('%Y-%m-%d')
            if 'Revenue' in working_df.columns:
                working_df['Revenue'] = working_df['Revenue'].astype(str).str.replace(r'[$,]', '', regex=True)
                working_df['Revenue'] = pd.to_numeric(working_df['Revenue'], errors='coerce').fillna(0.0)

        # 5. UI PREVIEW RENDER (Updates instantly when checkboxes are flipped)
        st.subheader("👀 Cleaned Data Preview")
        st.dataframe(working_df.head(5))

        # 6. CONVERT CLEAN DATA INTO LIVE DOWNLOAD STREAM
        output_buffer = io.BytesIO()
        working_df.to_csv(output_buffer, index=False)
        output_buffer.seek(0)

        # 7. DOWNLOAD BUTTON (Now works natively on click without dropping data)
        st.write("---")
        st.download_button(
            label="🚀 Download Cleaned Spreadsheet",
            data=output_buffer,
            file_name=f"cleaned_{st.session_state['file_name']}",
            mime="text/csv"
        )
