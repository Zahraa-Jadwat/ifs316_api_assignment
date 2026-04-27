import requests
import matplotlib.pyplot as plt

# Oracle APEX API endpoint
url = "https://oracleapex.com/ords/zahraa_individual_assignment/myapi/average_order_value"

headers = {
    "Accept": "application/json",
    "Host": "oracleapex.com",
    "User-Agent": "Mozilla/5.0 Firefox/149.0"
}

# Fetch data from API
response = requests.get(url, headers=headers, timeout=30)

# Extract items
if response.status_code == 200:
    print("Connection successful!")
    data = response.json()

    # Safe access to items
    items = data.get("items", [])

    if not items:
        print("No data returned from API")
    else:
        # Safe loop extraction
        months = []
        avg_order = []

        for item in items:
            month = item.get("month_name")
            value = item.get("avg_order_value")

            if month is not None and value is not None:
                months.append(month)
                avg_order.append(float(value))

        # Create Line Chart
        plt.figure(figsize=(14, 6))

        plt.plot(
            months,
            avg_order,
            marker="o",
            linewidth=2,
            markersize=7,
            color="#2196F3",
            markerfacecolor="#FF5722"
        )

        plt.title("Average Order Value per Month (2017)")
        plt.xlabel("Month")
        plt.ylabel("Average Order Value (USD)")

        plt.xticks(rotation=45, ha="right")
        plt.grid(axis="y", linestyle="--", alpha=0.5)

        plt.tight_layout()
        plt.show()
else:
    print(f"Connection failed. Status code: {response.status_code}")
