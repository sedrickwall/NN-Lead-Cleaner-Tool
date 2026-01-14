# Create the Lead Cleaner app
import streamlit as st
import pandas as pd
import re
from io import BytesIO

# Page config
st.set_page_config(page_title="Lead Cleaner Tool", page_icon="🧹", layout="wide")

# Title
st.title("🧹 Conference Lead Cleaner")
st.markdown("**Clean, Format, and Prepare Lead Lists for Salesforce**")

# Sidebar - Configuration
st.sidebar.header("⚙️ Configuration")

# Business Director Mapping
st.sidebar.subheader("Business Director Assignment")
bd_mapping = {
    "APAC": st.sidebar.text_input("APAC Owner ID", ""),
    "EURO": st.sidebar.text_input("EURO Owner ID", ""),
    "EMEA": st.sidebar.text_input("EMEA Owner ID", ""),
    "US-East": st.sidebar.text_input("US-East Owner ID", ""),
    "US-West": st.sidebar.text_input("US-West Owner ID", "")
}

# Pharma/Biotech Keywords
st.sidebar.subheader("Exclusion Keywords")
default_keywords = "Accelerator, Acedemia, CRO, Service Providers, Investors, Fund, Govt, clinical research organization,,Consultant, Hospital, CDMO,Research, CRO"
exclusion_keywords = st.sidebar.text_area("Keywords to exclude (comma-separated)", default_keywords)
keywords_list = [k.strip().lower() for k in exclusion_keywords.split(",")]

# Campaign Name
campaign_name = st.sidebar.text_input("Campaign Name (optional)", "")

# Main Upload Section
st.header("📤 Step 1: Upload Lead List")
uploaded_file = st.file_uploader("Upload CSV or Excel file", type=["csv", "xlsx", "xls"])

if uploaded_file:
    # Read file
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        st.success(f"✅ File uploaded: {uploaded_file.name} ({len(df)} rows)")

        # Show preview
        with st.expander("📋 Preview Uploaded Data (First 10 rows)"):
            st.dataframe(df.head(10))

        # Column Mapping
        st.header("🔗 Step 2: Map Columns")
        st.markdown("Match your file columns to Salesforce fields:")

        col1, col2, col3 = st.columns(3)

        with col1:
            first_name_col = st.selectbox("First Name Column", [""] + list(df.columns))
            last_name_col = st.selectbox("Last Name Column", [""] + list(df.columns))
            email_col = st.selectbox("Email Column", [""] + list(df.columns))

        with col2:
            company_col = st.selectbox("Company Column", [""] + list(df.columns))
            title_col = st.selectbox("Title Column (optional)", [""] + list(df.columns))
            country_col = st.selectbox("Country/Region Column", [""] + list(df.columns))

        with col3:
            st.info("**Region Assignment Logic:**\n\n- APAC: Asia, Australia, NZ\n- EURO: Europe, UK\n- EMEA: Middle East, Africa\n- US-East: Eastern US states\n- US-West: Western US states")

        # Process Button
        if st.button("🚀 Clean & Format Leads", type="primary"):
            if not first_name_col or not last_name_col or not company_col or not country_col:
                st.error("⚠️ Please map at least: First Name, Last Name, Company, and Country/Region")
            else:
                with st.spinner("Processing leads..."):
                    # Create working dataframe
                    processed_df = df.copy()

                    # --- CLEANING: Remove Pharma/Biotech ---
                    st.subheader("🧹 Step 3: Cleaning Results")

                    def is_excluded(company_name):
                        if pd.isna(company_name):
                            return False
                        company_lower = str(company_name).lower()
                        return any(keyword in company_lower for keyword in keywords_list)

                    excluded_mask = processed_df[company_col].apply(is_excluded)
                    excluded_count = excluded_mask.sum()
                    excluded_companies = processed_df[excluded_mask][company_col].unique()

                    # Remove excluded companies
                    processed_df = processed_df[~excluded_mask]

                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.metric("❌ Excluded Companies", excluded_count)
                        if excluded_count > 0:
                            with st.expander("View Excluded Companies"):
                                st.write(list(excluded_companies))

                    with col_b:
                        st.metric("✅ Remaining Leads", len(processed_df))

                    # --- FORMATTING: Create Salesforce Template ---
                    st.subheader("📋 Step 4: Salesforce Formatting")

                    def assign_region(country):
                        if pd.isna(country):
                            return "US-East"  # Default

                        country_lower = str(country).lower()

                        # APAC
                        apac_countries = ['australia', 'new zealand', 'singapore', 'japan', 'china',
                                         'korea', 'india', 'malaysia', 'thailand', 'vietnam',
                                         'indonesia', 'philippines', 'hong kong']
                        if any(c in country_lower for c in apac_countries):
                            return "APAC"

                        # EURO
                        euro_countries = ['uk', 'united kingdom', 'england', 'scotland', 'wales',
                                         'germany', 'france', 'spain', 'italy', 'netherlands',
                                         'belgium', 'switzerland', 'austria', 'sweden', 'denmark',
                                         'norway', 'finland', 'poland', 'ireland', 'portugal',
                                         'greece', 'czech', 'hungary', 'romania']
                        if any(c in country_lower for c in euro_countries):
                            return "EURO"

                        # EMEA (Middle East & Africa)
                        emea_countries = ['israel', 'uae', 'saudi', 'qatar', 'dubai', 'bahrain',
                                         'kuwait', 'oman', 'egypt', 'south africa', 'morocco',
                                         'tunisia', 'kenya', 'nigeria', 'ghana', 'ethiopia',
                                         'turkey', 'jordan', 'lebanon']
                        if any(c in country_lower for c in emea_countries):
                            return "EMEA"

                        # US-West
                        west_states = ['california', 'ca', 'oregon', 'or', 'washington', 'wa',
                                      'nevada', 'nv', 'arizona', 'az', 'utah', 'colorado', 'co']
                        if any(s in country_lower for s in west_states):
                            return "US-West"

                        # Default to US-East
                        return "US-East"

                    # Create Salesforce formatted dataframe
                    sf_df = pd.DataFrame()
                    sf_df['FirstName'] = processed_df[first_name_col]
                    sf_df['LastName'] = processed_df[last_name_col]
                    sf_df['Company'] = processed_df[company_col]
                    sf_df['Email'] = processed_df[email_col] if email_col else ""
                    sf_df['Title'] = processed_df[title_col] if title_col else ""
                    sf_df['Source__c'] = "Event"
                    sf_df['Campaign'] = campaign_name
                    sf_df['Status'] = "New"

                    # Assign regions and owner IDs
                    sf_df['Region'] = processed_df[country_col].apply(assign_region)
                    sf_df['OwnerId'] = sf_df['Region'].map(bd_mapping)

                    # Remove rows with missing critical data
                    sf_df = sf_df.dropna(subset=['FirstName', 'LastName', 'Company'])

                    st.success(f"✅ Formatted {len(sf_df)} leads for Salesforce")

                    # Show region distribution
                    region_counts = sf_df['Region'].value_counts()
                    st.markdown("**Region Distribution:**")
                    col1, col2, col3, col4, col5 = st.columns(5)
                    with col1:
                        st.metric("APAC", region_counts.get('APAC', 0))
                    with col2:
                        st.metric("EURO", region_counts.get('EURO', 0))
                    with col3:
                        st.metric("EMEA", region_counts.get('EMEA', 0))
                    with col4:
                        st.metric("US-East", region_counts.get('US-East', 0))
                    with col5:
                        st.metric("US-West", region_counts.get('US-West', 0))

                    # Preview formatted data
                    with st.expander("📋 Preview Formatted Data (First 10 rows)"):
                        st.dataframe(sf_df.head(10))

                    # --- DOWNLOAD ---
                    st.subheader("📥 Step 5: Download")

                    # Convert to CSV
                    csv_buffer = BytesIO()
                    sf_df.to_csv(csv_buffer, index=False, encoding='utf-8')
                    csv_buffer.seek(0)

                    st.download_button(
                        label="⬇️ Download Cleaned Lead List (CSV)",
                        data=csv_buffer,
                        file_name=f"cleaned_leads_{uploaded_file.name.replace('.xlsx', '').replace('.csv', '')}.csv",
                        mime="text/csv",
                        type="primary"
                    )

                    # Show stats summary
                    st.success("🎉 **Processing Complete!**")
                    st.markdown(f"""
                    **Summary:**
                    - Original leads: {len(df)}
                    - Excluded (non-pharma/biotech): {excluded_count}
                    - Final clean leads: {len(sf_df)}
                    - Ready for Salesforce import ✅
                    """)

    except Exception as e:
        st.error(f"❌ Error reading file: {str(e)}")
        st.info("Make sure your file is a valid CSV or Excel file.")

else:
    st.info("👆 Upload a lead list file to get started")

    # Show instructions
    st.markdown("""
    ### 📖 How to Use:

    1. **Configure Settings** (Left sidebar):
       - Enter Salesforce Owner IDs for each region
       - Customize exclusion keywords
       - Add campaign name (optional)

    2. **Upload Lead List**:
       - Supported formats: CSV, Excel (.xlsx, .xls)
       - Can contain any column names

    3. **Map Columns**:
       - Match your file columns to Salesforce fields
       - At minimum: First Name, Last Name, Company, Country

    4. **Clean & Format**:
       - Automatically removes non pharma/biotech companies
       - Assigns Business Director based on region
       - Formats for Salesforce import

    5. **Download**:
       - Get cleaned CSV ready for SharePoint/Salesforce

    ---

    **Need help?** Contact your system admin or check the documentation.
    """)

# Footer
st.markdown("---")
st.markdown("*Lead Cleaner Tool v1.0 | Built for Nucleus Network*")