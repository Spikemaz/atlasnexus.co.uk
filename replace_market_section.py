#!/usr/bin/env python3
"""Replace the market section in dashboard.html with the original layout from market_news_content.html"""

# Read the market_news_content.html file
with open('templates/market_news_content.html', 'r', encoding='utf-8') as f:
    original_market_content = f.read()

# Read the current dashboard.html
with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    dashboard_content = f.read()

# Find the market section in dashboard.html
market_start = dashboard_content.find('<!-- Market News Section')
if market_start == -1:
    print("Error: Could not find market section start")
    exit(1)

# Find the end of the market section (next major section)
analytics_start = dashboard_content.find('<!-- Analytics Section -->', market_start)
data_start = dashboard_content.find('<!-- Data Section -->', market_start)

# Use whichever comes first
market_end = min(x for x in [analytics_start, data_start] if x > market_start)

if market_end == -1:
    print("Error: Could not find market section end")
    exit(1)

# Create the new market section with proper structure
new_market_section = f'''    <!-- Market News Section - Original Layout with Bullish/Bearish Indicators -->
    <div id="market-section" style="display: none; padding: 185px 2rem 2rem; min-height: 100vh; transition: padding-top 0.3s ease;">
{original_market_content}
    </div>

'''

# Replace the market section
new_dashboard = dashboard_content[:market_start] + new_market_section + dashboard_content[market_end:]

# Write the updated dashboard
with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(new_dashboard)

print("Successfully replaced market section with original layout!")
print(f"Market section: lines {dashboard_content[:market_start].count(chr(10)) + 1} to {dashboard_content[:market_end].count(chr(10)) + 1}")