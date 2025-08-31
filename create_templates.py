import pandas as pd
from datetime import datetime, timedelta
import os

# Create templates directory if it doesn't exist
templates_dir = r"C:\Users\marcu\Desktop\Marcus Folder\Project1\static\templates"
os.makedirs(templates_dir, exist_ok=True)

# 1. Create Pipeline Template (Multiple Projects)
pipeline_data = {
    'Project Code': ['DAR001', 'DAR002', 'DAR003'],
    'Project Name': ['London DC1', 'Manchester DC2', 'Birmingham DC3'],
    'Deal Type': ['Data Centre', 'Data Centre', 'Data Centre'],
    'Country': ['UK', 'UK', 'UK'],
    'Location': ['London, Docklands', 'Manchester, MediaCity', 'Birmingham, City Centre'],
    'Site Address': ['123 Thames Path', '456 Salford Quays', '789 Bull Ring'],
    'Site Size (sqm)': [50000, 45000, 40000],
    'Data Centre Capacity (MW)': [100, 80, 60],
    'Construction Start': ['2025-01-01', '2025-03-01', '2025-06-01'],
    'Construction End': ['2026-12-31', '2027-03-31', '2027-06-30'],
    'Construction Cost (£)': [120000000, 96000000, 72000000],
    'Development Cost (£)': [15000000, 12000000, 9000000],
    'Land Purchase (£)': [25000000, 20000000, 15000000],
    'Building Cost (£)': [80000000, 64000000, 48000000],
    'Infrastructure (£)': [30000000, 24000000, 18000000],
    'IT Equipment (£)': [40000000, 32000000, 24000000],
    'Professional Fees (£)': [5000000, 4000000, 3000000],
    'Contingency (£)': [10000000, 8000000, 6000000],
    'Total CapEx (£)': [325000000, 260000000, 195000000],
    'Market CapEx Estimate (£)': [350000000, 280000000, 210000000],
    'Offtaker Name': ['HyperCloud Inc', 'DataStream Ltd', 'TechColo Corp'],
    'Credit Rating': ['AA+', 'AA', 'AA-'],
    'Rent per kWh (£)': [0.15, 0.14, 0.13],
    'Annual Escalation (%)': [3.0, 2.5, 2.0],
    'Lease Term (Years)': [15, 12, 10],
    'Power Cost per kWh (£)': [0.08, 0.075, 0.07],
    'Expected PUE': [1.2, 1.25, 1.3]
}

# Additional sheets for pipeline template
capex_breakdown = {
    'Project Code': ['DAR001', 'DAR002', 'DAR003'],
    'Land & Site Prep': [25000000, 20000000, 15000000],
    'Shell & Core': [80000000, 64000000, 48000000],
    'M&E Infrastructure': [30000000, 24000000, 18000000],
    'IT Fit-out': [40000000, 32000000, 24000000],
    'Power Infrastructure': [50000000, 40000000, 30000000],
    'Cooling Systems': [35000000, 28000000, 21000000],
    'Security & BMS': [15000000, 12000000, 9000000],
    'Network Infrastructure': [25000000, 20000000, 15000000],
    'Professional Services': [5000000, 4000000, 3000000],
    'Contingency (10%)': [10000000, 8000000, 6000000],
    'Development Fees': [10000000, 8000000, 6000000],
    'Total': [325000000, 260000000, 195000000]
}

timeline_data = {
    'Project Code': ['DAR001', 'DAR002', 'DAR003'],
    'Pre-Development (Months)': [6, 6, 6],
    'Planning & Permits (Months)': [9, 8, 7],
    'Construction Phase 1 (Months)': [12, 11, 10],
    'Construction Phase 2 (Months)': [8, 7, 6],
    'Testing & Commissioning (Months)': [3, 3, 3],
    'Total Timeline (Months)': [38, 35, 32],
    'Target Completion': ['Q4 2026', 'Q1 2027', 'Q2 2027'],
    'First Revenue Date': ['2027-01-01', '2027-04-01', '2027-07-01']
}

# Create Pipeline Excel file
with pd.ExcelWriter(os.path.join(templates_dir, 'AtlasNexus_Pipeline_Template.xlsx'), engine='openpyxl') as writer:
    pd.DataFrame(pipeline_data).to_excel(writer, sheet_name='Pipeline', index=False)
    pd.DataFrame(capex_breakdown).to_excel(writer, sheet_name='CapEx Breakdown', index=False)
    pd.DataFrame(timeline_data).to_excel(writer, sheet_name='Timeline', index=False)
    
    # Add instructions sheet
    instructions = pd.DataFrame({
        'Instructions': [
            'ATLASNE XUS PROJECT PIPELINE TEMPLATE',
            '',
            '1. PIPELINE SHEET:',
            '   - List all projects in your pipeline',
            '   - Each row represents one project',
            '   - All financial figures should be in GBP (£)',
            '   - Dates should be in YYYY-MM-DD format',
            '',
            '2. CAPEX BREAKDOWN SHEET:',
            '   - Detailed breakdown of capital expenditure',
            '   - Must match Total CapEx in Pipeline sheet',
            '',
            '3. TIMELINE SHEET:',
            '   - Project development timeline',
            '   - All durations in months',
            '',
            '4. UPLOAD INSTRUCTIONS:',
            '   - Save file as .xlsx or .csv',
            '   - Upload via Project Specifications portal',
            '   - System will auto-extract and validate data',
            '',
            'For support: admin@atlasnexus.co.uk'
        ]
    })
    instructions.to_excel(writer, sheet_name='Instructions', index=False)

print("Pipeline template created successfully!")

# 2. Create Individual Project Template
individual_project = {
    'Field': [
        'Project Code', 'Project Name', 'Deal Type', 'Country', 'Location',
        'Site Address', 'Site Size (sqm)', 'Data Centre Capacity (MW)',
        'Construction Start Date', 'Construction End Date',
        'Total CapEx (£)', 'Land Purchase (£)', 'Building Cost (£)',
        'Infrastructure (£)', 'IT Equipment (£)', 'Professional Fees (£)',
        'Contingency (£)', 'Offtaker Name', 'Credit Rating',
        'Rent per kWh (£)', 'Annual Escalation (%)', 'Lease Term (Years)',
        'Power Cost per kWh (£)', 'Expected PUE', 'Notes'
    ],
    'Value': [
        'DAR001', 'Project Name Here', 'Data Centre', 'UK', 'City, Region',
        'Full Site Address', 50000, 100,
        '2025-01-01', '2026-12-31',
        325000000, 25000000, 80000000,
        30000000, 40000000, 5000000,
        10000000, 'Offtaker Company Name', 'AA+',
        0.15, 3.0, 15,
        0.08, 1.2, 'Additional notes here'
    ],
    'Description': [
        'Unique project identifier', 'Full project name', 'Type of deal (Data Centre/Renewable/etc)',
        'Country of project', 'City and region', 'Complete site address',
        'Total site area in square meters', 'IT capacity in megawatts',
        'Construction commencement date', 'Expected completion date',
        'Total capital expenditure', 'Land acquisition cost', 'Building construction cost',
        'Infrastructure development cost', 'IT equipment cost', 'Legal, consulting, design fees',
        'Risk contingency (typically 10%)', 'Name of tenant/customer', 'Credit rating of offtaker',
        'Rental rate per kilowatt-hour', 'Annual rent increase percentage', 'Length of lease in years',
        'Electricity cost per kWh', 'Power Usage Effectiveness ratio', 'Any additional information'
    ]
}

with pd.ExcelWriter(os.path.join(templates_dir, 'AtlasNexus_Individual_Project_Template.xlsx'), engine='openpyxl') as writer:
    pd.DataFrame(individual_project).to_excel(writer, sheet_name='Project Data', index=False)
    
    # Add financial breakdown
    financial = pd.DataFrame({
        'CapEx Component': [
            'Land & Site Preparation', 'Shell & Core Construction', 'M&E Infrastructure',
            'IT Fit-out', 'Power Infrastructure', 'Cooling Systems',
            'Security & BMS', 'Network Infrastructure', 'Professional Services',
            'Contingency', 'Development Fees', 'TOTAL'
        ],
        'Amount (£)': [
            25000000, 80000000, 30000000, 40000000, 50000000, 35000000,
            15000000, 25000000, 5000000, 10000000, 10000000, 325000000
        ],
        'Percentage': [
            '7.69%', '24.62%', '9.23%', '12.31%', '15.38%', '10.77%',
            '4.62%', '7.69%', '1.54%', '3.08%', '3.08%', '100%'
        ]
    })
    financial.to_excel(writer, sheet_name='Financial Breakdown', index=False)

print("Individual project template created successfully!")

print("\nAll templates created successfully in:", templates_dir)