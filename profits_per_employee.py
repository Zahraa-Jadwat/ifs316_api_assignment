import matplotlib.pyplot as plt
import requests
import numpy as np

# Fetch data from API
url = "https://oracleapex.com/ords/zahraa_individual_assignment/myapi/profits_per_employee"
response = requests.get(url)

# Parse JSON response
data = response.json()

# Extract employee names and profits
employees = []
profits = []

for item in data['items']:
    employees.append(item['employee_name'])
    # Clean the profit string: remove '$', commas, and whitespace, then convert to float
    profit_str = item['total_profit'].strip().replace('$', '').replace(',', '')
    profits.append(float(profit_str))

# Create horizontal bar chart
fig, ax = plt.subplots(figsize=(10, 8))
bars = ax.barh(employees, profits, color='steelblue', edgecolor='navy', alpha=0.8)

# Add value labels on the bars
for i, (bar, profit) in enumerate(zip(bars, profits)):
    ax.text(bar.get_width() + 5000, bar.get_y() + bar.get_height()/2,
            f'${profit:,.0f}', va='center', fontsize=9)

# Customize
ax.set_xlabel('Total Profit ($)', fontsize=12, fontweight='bold')
ax.set_ylabel('Employee Name', fontsize=12, fontweight='bold')
ax.set_title('Employee Profit Performance', fontsize=14, fontweight='bold', pad=20)
ax.grid(axis='x', alpha=0.3, linestyle='--')
ax.set_xlim(0, max(profits) * 1.1)

plt.tight_layout()
plt.show()