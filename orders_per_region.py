import requests
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

# Oracle APEX API endpoint
url = "https://oracleapex.com/ords/zahraa_individual_assignment/myapi/sales_per_region"

headers = {
    "Accept":     "application/json",
    "Host":       "oracleapex.com",
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
        regions    = []
        categories = []
        clean_items = []

        for item in items:
            region   = item.get("region_name")
            category = item.get("category_name")
            profit   = item.get("total_profit")

            if region is not None and category is not None and profit is not None:
                clean_items.append({
                    "region_name":   region,
                    "category_name": category,
                    "total_profit":  float(profit)
                })
                if region not in regions:
                    regions.append(region)
                if category not in categories:
                    categories.append(category)

        regions    = sorted(regions)
        categories = sorted(categories)

        # Build matrix
        matrix = []
        for region in regions:
            row = []
            for category in categories:
                value = next(
                    (item["total_profit"] for item in clean_items
                     if item["region_name"]   == region
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
        plt.savefig("sales_per_region.png", dpi=150, bbox_inches="tight")
        print("Chart saved!")
        plt.show()

else:
    print(f"Connection failed. Status code: {response.status_code}")
