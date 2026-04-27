import requests
import matplotlib.pyplot as plt

# Oracle APEX API endpoint
url = "https://oracleapex.com/ords/zahraa_individual_assignment/myapi/average_order_value"

# Fetch data from API
response = requests.get(url)
data = response.json()

# Extract items
items = data["items"]

months      = [item["month_name"]       for item in items]
avg_order   = [item["avg_order_value"]  for item in items]

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