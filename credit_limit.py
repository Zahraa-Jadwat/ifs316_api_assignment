import requests
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# Your Oracle APEX API endpoint
url = "https://oracleapex.com/ords/zahraa_individual_assignment/myapi/credit_limit"

headers = {
    "Accept": "application/json",
    "Host": "oracleapex.com",
    "User-Agent": "Mozilla/5.0 Firefox/149.0"
}

# Call the API
response = requests.get(url, headers=headers, timeout=30)

# Extract data
if response.status_code == 200:
    print("Connection successful!")
    data = response.json()
    
    # Safe access to items
    items = data.get("items", [])
    
    if not items:
        print("No data returned from API")
    else:
        # Safe loop extraction
        years = []
        customers = []

        for item in items:
            year = item.get("order_year")
            value = item.get("customers_exceeding_limit")

            if year is not None and value is not None:
                years.append(str(year))
                customers.append(float(value))

        # Plot graph
        fig, ax = plt.subplots(figsize=(10, 6))

        bars = ax.barh(years, customers, color="steelblue", edgecolor="white", height=0.6)

        # Add value labels
        for bar in bars:
            width = bar.get_width()
            if width > 0:
                ax.text(
                    width + 0.3, bar.get_y() + bar.get_height() / 2,
                    str(int(width)),
                    va="center", ha="left", fontsize=11, fontweight="bold"
                )

        # Styling
        ax.set_xlabel("Number of Customers Exceeding Credit Limit", fontsize=12, labelpad=10)
        ax.set_ylabel("Year", fontsize=12, labelpad=10)
        ax.set_title("Customers Exceeding Credit Limit Per Year", fontsize=14, fontweight="bold", pad=15)

        ax.xaxis.set_major_locator(ticker.MultipleLocator(5))
        ax.tick_params(axis="both", labelsize=11)

        if customers:
            ax.set_xlim(0, max(customers) * 1.15)  # prevent crash if empty

        # Grid and style
        ax.xaxis.grid(True, linestyle="--", alpha=0.5)
        ax.set_axisbelow(True)
        ax.spines[["top", "right"]].set_visible(False)

        plt.tight_layout()
        plt.show()
else:
    print(f"Connection failed. Status code: {response.status_code}")
