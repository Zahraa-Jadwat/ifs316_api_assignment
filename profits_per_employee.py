import matplotlib.pyplot as plt
import requests
import numpy as np

# Fetch data from API
url = "https://oracleapex.com/ords/zahraa_individual_assignment/myapi/profits_per_employee"

headers = {
    "Accept": "application/json",
    "Host": "oracleapex.com",
    "User-Agent": "Mozilla/5.0 Firefox/149.0"
}

response = requests.get(url, headers=headers, timeout=30)

# Extract data
if response.status_code == 200:
    print("Connection successful!")
    data = response.json()

    items = data.get("items", [])

    if not items:
        print("No data returned from API")
    else:
        employees = []
        profits = []

        for item in items:
            name = item.get("employee_name")
            profit_val = item.get("total_profit")

            if name is not None and profit_val is not None:
                # Handle both string and numeric values safely
                if isinstance(profit_val, str):
                    profit_clean = profit_val.strip().replace('$', '').replace(',', '')
                    try:
                        profit = float(profit_clean)
                    except:
                        continue
                else:
                    profit = float(profit_val)

                employees.append(name)
                profits.append(profit)

        # Create horizontal bar chart
        fig, ax = plt.subplots(figsize=(10, 8))
        bars = ax.barh(employees, profits, color='steelblue', edgecolor='navy', alpha=0.8)

        # Add value labels
        for bar, profit in zip(bars, profits):
            ax.text(
                bar.get_width() + 5000,
                bar.get_y() + bar.get_height()/2,
                f'${profit:,.0f}',
                va='center',
                fontsize=9
            )

        # Customize
        ax.set_xlabel('Total Profit ($)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Employee Name', fontsize=12, fontweight='bold')
        ax.set_title('Employee Profit Performance', fontsize=14, fontweight='bold', pad=20)
        ax.grid(axis='x', alpha=0.3, linestyle='--')

        if profits:
            ax.set_xlim(0, max(profits) * 1.1)

        plt.tight_layout()
        plt.show()
else:
    print(f"Connection failed. Status code: {response.status_code}")
