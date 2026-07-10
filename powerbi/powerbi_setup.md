# Power BI Dashboard Setup Guide

## Prerequisites
- Power BI Desktop (Free download from Microsoft)

## Step-by-Step Setup

### Step 1: Load Data
1. Open Power BI Desktop
2. Click "Get Data" → "Text/CSV"
3. Load these files from `/powerbi/`:
   - `fact_transactions.csv`
   - `dim_date.csv`
   - `dim_customer.csv`
   - `dim_product.csv`
   - `inventory_metrics.csv`

### Step 2: Create Relationships
Open "Model" view and create these relationships:

| Table | Column | → | Table | Column |
|-------|--------|---|-------|--------|
| fact_transactions | date | → | dim_date | date |
| fact_transactions | customer_id | → | dim_customer | customer_id |
| fact_transactions | product_name | → | dim_product | product_name |
| fact_transactions | category | → | dim_product | category |

### Step 3: Add DAX Measures
1. Go to "Modeling" tab
2. Click "New Measure"
3. Add measures from `dax_measures.txt`

### Step 4: Build Dashboard

**Page 1: Executive Overview**
- Card visuals: Total Revenue, Total Orders, Unique Customers, Avg Order Value
- Line chart: Monthly Revenue Trend
- Pie chart: Revenue by Category
- Bar chart: Top 10 Products

**Page 2: Customer Analytics**
- Table: Customer Segments (RFM)
- Bar chart: Revenue by City
- Card: Repeat Purchase Rate

**Page 3: Product Analytics**
- Matrix: Product Performance by Category
- Bar chart: Underperforming Products

**Page 4: Time Analysis**
- Line chart: Year-over-Year Comparison
- Area chart: Cumulative Revenue

### Step 5: Add Slicers
- Date Range
- Category
- Payment Method
- City

### Step 6: Publish
1. File → Publish
2. Sign in to Power BI Service
3. Choose workspace
4. Share with stakeholders