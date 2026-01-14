# 🧹 Conference Lead Cleaner Tool

A Streamlit web application designed for Nucleus Network to clean, format, and prepare conference lead lists for Salesforce import.

## Features

- **📤 File Upload**: Support for CSV and Excel files (.xlsx, .xls)
- **🧹 Smart Filtering**: Automatically excludes non-pharma/biotech companies based on customizable keywords
- **🌍 Regional Assignment**: Automatically assigns leads to Business Directors based on geographic region
  - APAC (Asia-Pacific)
  - EURO (Europe, UK, Middle East)
  - US-East (Eastern United States)
  - US-West (Western United States)
- **📋 Column Mapping**: Flexible mapping between your file columns and Salesforce fields
- **📥 Export**: Download cleaned and formatted CSV ready for Salesforce import

## Installation

### Local Development

1. Clone this repository:
```bash
git clone <your-repo-url>
cd NN-Lead-Cleaner-Tool
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the app:
```bash
streamlit run app.py
```

### Deploy to Streamlit Cloud

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Deploy!

## Usage

1. **Configure Settings** (Left sidebar):
   - Enter Salesforce Owner IDs for each region (APAC, EURO, US-East, US-West)
   - Customize exclusion keywords for filtering
   - Add campaign name (optional)

2. **Upload Lead List**:
   - Click "Browse files" and select your CSV or Excel file
   - File can contain any column names

3. **Map Columns**:
   - Match your file columns to required Salesforce fields
   - Required: First Name, Last Name, Company, Country/Region
   - Optional: Title, Email

4. **Clean & Format**:
   - Click "Clean & Format Leads" button
   - Review excluded companies and region distribution

5. **Download**:
   - Download the cleaned CSV file
   - Import directly into Salesforce

## Exclusion Logic

The tool filters out companies containing these keywords (customizable):
- Accelerator
- Academia
- CRO (Clinical Research Organization)
- Service Providers
- Investors
- Fund
- Government entities
- Consultants
- Hospitals
- CDMO
- Research institutions

## Region Assignment Logic

**APAC**: Australia, New Zealand, Singapore, Japan, China, Korea, India, Malaysia, Thailand, Vietnam, Indonesia, Philippines, Hong Kong

**EURO**: UK, Germany, France, Spain, Italy, Netherlands, Belgium, Switzerland, Austria, Sweden, Denmark, Norway, Finland, Poland, Ireland, Portugal, Greece, Czech Republic, Hungary, Romania, Israel, UAE, Saudi Arabia, Qatar, Dubai

**US-West**: California, Oregon, Washington, Nevada, Arizona, Utah, Colorado

**US-East**: All other US states (default)

## Requirements

- Python 3.8+
- streamlit
- pandas
- openpyxl (for Excel file support)

## License

See LICENSE file for details.

## Support

For questions or issues, contact your system administrator.

---

*Built for Nucleus Network | Lead Cleaner Tool v1.0*
