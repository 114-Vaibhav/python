# PDF Report Generator with Templating

This project generates a monthly sales report from a SQLite database, builds charts with Matplotlib, renders an HTML report using Jinja2, creates a PDF version, and emails the final PDF through Gmail SMTP.

It is a small end-to-end automation project for learning how Python can combine:

- data extraction from SQLite
- chart creation with Matplotlib
- HTML templating with Jinja2
- PDF generation
- email automation with Gmail

## Features

- Reads monthly sales data from `data/sales.db`
- Calculates total revenue, total units sold, and average revenue per sale
- Groups sales by region
- Creates 4 charts:
  - daily revenue trend
  - revenue by region
  - revenue distribution pie chart
  - units sold by region
- Renders a monthly HTML report from `template_sales_monthly.html`
- Generates a PDF report in the `reports/` folder
- Sends the PDF as an email attachment using Gmail

## Project Structure

```text
.
|-- main.py
|-- html_to_pdf.py
|-- sendEmail.py
|-- template_sales_monthly.html
|-- data/
|   `-- sales.db
|-- output/
|   `-- generated charts
`-- reports/
    |-- generated HTML reports
    `-- generated PDF reports
```

## How It Works

1. `main.py` asks for a month and year.
2. It fetches matching sales rows from the SQLite database.
3. It calculates summary metrics and region-wise statistics.
4. It saves charts into the `output/` folder.
5. Jinja2 renders the report template into an HTML file inside `reports/`.
6. `html_to_pdf.py` creates a PDF version of the report.
7. `sendEmail.py` emails the generated PDF to the configured recipients.

## Requirements

- Python 3.10+
- A virtual environment is recommended
- A Gmail account for sending email
- A Gmail App Password if 2-Step Verification is enabled

Python packages used in this project:

- `matplotlib`
- `jinja2`
- `reportlab`
- `python-dotenv`

Install them with:

```bash
pip install matplotlib jinja2 reportlab python-dotenv
```

## Environment Variables

Create a `.env` file in the project root:

```env
EMAIL_USER=your_email@gmail.com
EMAIL_PASS=your_gmail_app_password
```

`sendEmail.py` loads these values with `python-dotenv` and uses them for SMTP login.

## Gmail Setup

This project sends mail using Gmail over SSL with:

- SMTP server: `smtp.gmail.com`
- Port: `465`

If your Gmail account uses 2-Step Verification, use a Google App Password instead of your normal account password. That is the safest way to make this script work reliably with Gmail SMTP.

## Database Setup

The project expects a SQLite database at:

```text
data/sales.db
```

There is also a helper file, `data/sales.py`, that shows the structure of the `sales` table and how sample records can be generated.

Expected table shape:

```sql
CREATE TABLE sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    region TEXT CHECK(region IN ('North','South','East','West')),
    revenue REAL,
    units_sold INTEGER
);
```

## Run the Project

From the project folder, run:

```bash
python main.py
```

You will be prompted for:

- month
- year

Example:

```text
Enter the month: 2
Enter the year: 2026
```

After execution, the project generates:

- charts in `output/`
- an HTML report in `reports/`
- a PDF report in `reports/`
- an email with the PDF attachment

## Important Notes

- `main.py` currently uses an absolute path for the SQLite database connection. If you move this project to another machine or folder, update that path or convert it to a relative path.
- `sendEmail.py` currently contains a hardcoded recipients list. Update the `recipients` variable if you want to send the report to different people.
- The generated filenames currently use the numeric month for the PDF and a short month name for the HTML report.

## Jinja2 Templating

The HTML report is created from `template_sales_monthly.html` using Jinja2. Template placeholders such as `{{ month }}`, `{{ total_revenue }}`, and loops like `{% for region, revenue in region_revenue.items() %}` are filled at runtime from the processed sales data.

This keeps the report layout separate from the Python logic and makes the design easier to update without changing the reporting code.

## Learning References

This project is closely related to these concepts:

- Gmail email sending with Python and SMTP:
  https://www.geeksforgeeks.org/python/send-mail-gmail-account-using-python/
- Jinja2 template rendering:
  https://swiftorial.com/tutorials/artificial_intelligence/crewai/templates/using_jinja2_with_templates/

These references are useful for understanding:

- how SMTP-based email sending works in Python
- how template variables are rendered into HTML
- why separating data and presentation makes report generation cleaner

## Summary

This project demonstrates a complete Python reporting workflow: query data, analyze it, visualize it, render it into HTML, export it to PDF, and send it by email. It is a practical beginner-to-intermediate automation project for learning data reporting and templating in Python.
