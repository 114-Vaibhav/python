import sqlite3
from datetime import datetime, timedelta
from matplotlib import pyplot as plt
from collections import defaultdict
import os
from jinja2 import Environment, FileSystemLoader
from html_to_pdf import generate_pdf
from sendEmail import sendEmail

month = input("Enter the month: ")
year = input("Enter the year: ")
start_date = datetime(int(year), int(month), 1)
end_date = start_date.replace(month=start_date.month + 1, day=1) - timedelta(days=1)

conn = sqlite3.connect('E:/Intern Work/Python/python/13 PDF Report Generator with Templating/data/sales.db')
cursor = conn.cursor()

cursor.execute("SELECT * FROM sales WHERE date BETWEEN ? AND ?", (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
sales_data = cursor.fetchall()


total_revenue = 0
total_units = 0
daily_revenue = defaultdict(float)
region_revenue = defaultdict(float)
region_units = defaultdict(int)


for sale in sales_data:
    _, date, region, revenue, units = sale

    total_revenue += revenue
    total_units += units

    daily_revenue[date] += revenue
    region_revenue[region] += revenue
    region_units[region] += units

conn.close()


print("\n Monthly Sales Report (Feb 2026)")
print("-----------------------------------")
print("Total Revenue:", round(total_revenue, 2))
print("Total Units Sold:", total_units)
print("Average Revenue per Sale:", round(total_revenue / len(sales_data), 2))

print("\n Region-wise Revenue:")
for r in region_revenue:
    print(f"{r}: {round(region_revenue[r], 2)}")

print("\n Region-wise Units Sold:")
for r in region_units:
    print(f"{r}: {region_units[r]}")


output_dir = "output"
os.makedirs(output_dir, exist_ok=True)

# 1. Daily Revenue Trend
plt.figure(figsize=(10, 5))
dates = sorted(daily_revenue.keys())
revenues = [daily_revenue[d] for d in dates]

plt.plot(dates, revenues, marker='o')
plt.xticks(rotation=45)
plt.title(f"Daily Revenue Trend ({month}-{year})")
plt.xlabel("Date")
plt.ylabel("Revenue")
plt.tight_layout()
daily_chart_path = os.path.join(output_dir,"daily_revenue.png")
plt.savefig(daily_chart_path)
plt.close()

# 2. Region-wise Revenue
plt.figure(figsize=(6, 4))
plt.bar(region_revenue.keys(), region_revenue.values(), color='skyblue')
plt.title("Revenue by Region")
plt.xlabel("Region")
plt.ylabel("Revenue")
region_chart_path = os.path.join(output_dir, "region_revenue.png")
plt.savefig(region_chart_path)
plt.close()

# 3. Pie Chart
plt.figure(figsize=(6, 6))
plt.pie(region_revenue.values(), labels=region_revenue.keys(), autopct='%1.1f%%')
plt.title("Revenue Distribution by Region")
pie_chart_path = os.path.join(output_dir, "revenue_pie.png")
plt.savefig(pie_chart_path)
plt.close()

# 4. Units Sold
plt.figure(figsize=(6, 4))
plt.bar(region_units.keys(), region_units.values(), color='orange')
plt.title("Units Sold by Region")
plt.xlabel("Region")
plt.ylabel("Units")
units_chart_path = os.path.join(output_dir, "units.png")
plt.savefig(units_chart_path)
plt.close()

# Setup Jinja2
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

env = Environment(loader=FileSystemLoader(BASE_DIR))
template = env.get_template('template_sales_monthly.html')


html_output = template.render(
    month=month,
    year=year,
    total_revenue=round(total_revenue, 2),
    total_units=total_units,
    avg_revenue=round(total_revenue / len(sales_data), 2) if sales_data else 0,
    region_revenue=region_revenue,
    region_units=region_units,
    daily_chart="../"+daily_chart_path,
    region_chart="../"+region_chart_path,
    pie_chart="../"+pie_chart_path,
    units_chart="../"+units_chart_path
)

# Save HTML
month_name = datetime(int(year), int(month), 1).strftime("%b")

reports_dir = "reports"
os.makedirs(reports_dir, exist_ok=True)

with open(os.path.join(reports_dir, f"{month_name}_{year}_report.html"), "w", encoding="utf-8") as f:
    f.write(html_output)

print("✅ Report generated: output/report.html")


avg_revenue=round(total_revenue / len(sales_data), 2) if sales_data else 0
generate_pdf(month, year, total_revenue, total_units, avg_revenue, region_revenue, region_units, daily_chart_path, region_chart_path, pie_chart_path, units_chart_path)

output_dir = "reports"
os.makedirs(output_dir, exist_ok=True)
pdf_path = os.path.join(output_dir, f'{month}_{year}_monthly_sales_report.pdf')

sendEmail(pdf_path)