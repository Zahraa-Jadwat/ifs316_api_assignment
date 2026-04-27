import requests
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

# Oracle APEX API endpoint
url = "https://oracleapex.com/ords/zahraa_individual_assignment/myapi/sales_per_region"

# Fetch data from API
response = requests.get(url)
data = response.json()

# Extract items
items = data["items"]

# Build matrix
regions    = sorted(set(item["region_name"]   for item in items))
categories = sorted(set(item["category_name"] for item in items))

# Create a 2D grid of profit values
matrix = []
for region in regions:
    row = []
    for category in categories:
        value = next(
            (float(item["total_profit"]) for item in items
             if item["region_name"] == region
             and item["category_name"] == category),
            0.0
        )
        row.append(value)
    matrix.append(row)

# Create Heatmap
fig, ax = plt.subplots(figsize=(12, 6))

heatmap = ax.imshow(
    matrix,
    cmap="Blues",
    aspect="auto"
)

# Add colour bar
plt.colorbar(heatmap, ax=ax, label="Total Profit (USD)")

# Label axes
ax.set_xticks(range(len(categories)))
ax.set_yticks(range(len(regions)))
ax.set_xticklabels(categories, rotation=45, ha="right")
ax.set_yticklabels(regions)

# Annotate each cell with its value
for i, region in enumerate(regions):
    for j, category in enumerate(categories):
        ax.text(
            j, i,
            f"${matrix[i][j]:,.0f}",
            ha="center",
            va="center",
            fontsize=8,
            color="black"
        )

ax.set_title("Profit by Region and Product Category")
ax.set_xlabel("Product Category")
ax.set_ylabel("Region")

plt.tight_layout()
plt.show()