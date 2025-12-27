# Product Sync Pipeline

A unified automation tool for synchronizing product data from Excel files to the Fatoorah API.

---

## Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Pipeline Workflow](#pipeline-workflow)
- [Input File Format](#input-file-format)
- [Output Files](#output-files)
- [Error Handling](#error-handling)

---

## Overview

This tool automates the process of uploading products to the Fatoorah system. It handles:

- Sorting products by name and type
- Synchronizing units and categories with the API
- Detecting duplicate barcodes
- Uploading products with checkpoint/resume support

---

## Project Structure

```
product-sync/
    main.py                              # Entry point
    modules/
        __init__.py
        sort_products.py                 # Product sorting logic
        sync_units.py                    # Units synchronization
        sync_categories.py               # Categories synchronization
        check_duplicate_barcodes.py      # Barcode validation
        send_products.py                 # Product upload with resume support
```

---

## Prerequisites

- Python 3.8 or higher
- Required packages:
  - `pandas`
  - `requests`
  - `openpyxl`

---

## Installation

```bash
pip install pandas requests openpyxl
```

---

## Configuration

The following parameters are required at runtime:

| Parameter   | Description                          |
|-------------|--------------------------------------|
| `API Token` | Bearer token for API authentication  |
| `stock_id`  | Stock identifier in the system       |
| `tax_id`    | Tax configuration identifier         |
| `Base Path` | Directory containing the Excel file  |

---

## Usage

Run the pipeline:

```bash
python main.py
```

The script will prompt for:

1. API Token
2. Stock ID
3. Tax ID
4. Base path (press Enter for current directory)
5. Excel file selection from available files

---

## Pipeline Workflow

```
                    +------------------+
                    |   User Input     |
                    | (Token, IDs,     |
                    |  Path, File)     |
                    +--------+---------+
                             |
                             v
                    +------------------+
                    |  Step 1: Sort    |
                    |  Products        |
                    | (by name, type)  |
                    +--------+---------+
                             |
                             v
                    +------------------+
                    |  Step 2: Sync    |
                    |  Units           |
                    | (create/lookup)  |
                    +--------+---------+
                             |
                             v
                    +------------------+
                    |  Step 3: Sync    |
                    |  Categories      |
                    | (create/lookup)  |
                    +--------+---------+
                             |
                             v
                    +------------------+
                    |  Step 4: Check   |
                    |  Duplicates      |
                    | (barcode report) |
                    +--------+---------+
                             |
                             v
                    +------------------+
                    |  Step 5: Send    |
                    |  Products        |
                    | (with resume)    |
                    +--------+---------+
                             |
                             v
                    +------------------+
                    |    Complete      |
                    +------------------+
```

### Step Details

| Step | Module                     | Description                                              |
|------|----------------------------|----------------------------------------------------------|
| 1    | `sort_products`            | Sorts products alphabetically, Type 1 before Type 5     |
| 2    | `sync_units`               | Searches for units in API, creates missing ones          |
| 3    | `sync_categories`          | Searches for categories in API, creates missing ones     |
| 4    | `check_duplicate_barcodes` | Generates report of duplicate barcodes                   |
| 5    | `send_products`            | Uploads products to API with checkpoint support          |

---

## Input File Format

The Excel file must contain the following columns:

| Column            | Type    | Required | Description                      |
|-------------------|---------|----------|----------------------------------|
| `name`            | String  | Yes      | Product name                     |
| `product_type`    | Integer | Yes      | 1 = Simple, 5 = Bundled          |
| `unit`            | String  | Yes      | Unit name                        |
| `category`        | String  | Yes      | Category name                    |
| `bar_code`        | String  | No       | Product barcode                  |
| `buy_price`       | Decimal | No       | Purchase price                   |
| `sale_price`      | Decimal | Yes      | Sale price                       |
| `first_quantity`  | Integer | No       | Initial stock quantity           |
| `Conversion_rate` | Integer | No       | For Type 5, quantity of base item|

---

## Output Files

| File                          | Description                              |
|-------------------------------|------------------------------------------|
| `_sorted_products.xlsx`       | Sorted products file                     |
| `units_mapping.json`          | Unit name to ID mapping                  |
| `categories_mapping.json`     | Category name to ID mapping              |
| `upload_cache.json`           | Checkpoint for resume support            |
| `duplicate_barcodes_report.xlsx` | Report of duplicate barcodes          |

---

## Error Handling

### Duplicate Barcodes

Products with duplicate barcodes are logged and skipped. Review `duplicate_barcodes_report.xlsx` for details.

### Resume Support

If the process is interrupted, run the script again. It will resume from the last successful upload using `upload_cache.json`.

### Missing Base Product

For Type 5 products, the corresponding Type 1 product must be uploaded first. The sorting step ensures this order.

---

## API Endpoints

| Endpoint       | Base URL                                        |
|----------------|-------------------------------------------------|
| Product        | `https://dev-api.fatoorah.sa/apiAdmin/Product`  |
| Category       | `https://dev-api.fatoorah.sa/apiAdmin/Category` |
| MajorUnit      | `https://dev-api.fatoorah.sa/apiAdmin/MajorUnit`|

---

## Notes

- Type 1 products are always processed before Type 5 to ensure dependencies are met
- The tax rate is automatically calculated as 15% of the sale price
- Rate limiting is applied (100ms delay between requests) to prevent API overload
