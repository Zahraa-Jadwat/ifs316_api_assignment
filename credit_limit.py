import requests
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# Your Oracle APEX API endpoint
url = "https://oracleapex.com/ords/zahraa_individual_assignment/myapi/credit_limit"

# Call the API
response = requests.get(url)

# Convert to JSON
data = response.json()

# Extract data
items = data["items"]

years = [str(item["order_year"]) for item in items]
customers = [item["customers_exceeding_limit"] for item in items]

# Plot graph
fig, ax = plt.subplots(figsize=(10, 6))

bars = ax.barh(years, customers, color="steelblue", edgecolor="white", height=0.6)

# Add value labels at the end of each bar
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
ax.set_xlim(0, max(customers) * 1.15)  # Extra space for labels

# Light grid on x-axis only for readability
ax.xaxis.grid(True, linestyle="--", alpha=0.5)
ax.set_axisbelow(True)
ax.spines[["top", "right"]].set_visible(False)

plt.tight_layout()
plt.show()