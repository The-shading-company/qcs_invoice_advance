## QCS Invoice Advance

QCS Invoice Advance

#### License

MIT

# QCS Invoice Advance App

A custom Frappe app designed for The Shading Company UAE to enhance invoice and product bundle management capabilities.

## Overview

This app extends Frappe/ERPNext with specialized functionality for managing product bundles, cost calculations, and invoice processing tailored for the shading and window treatment industry.

## Key Features

### Product Bundle Cost Management
- **Automatic Cost Calculation**: Calculates total component costs for product bundles
- **Dual Cost Sources**: Supports both `custom_average_cost` and standard `valuation_rate`
- **Real-time Updates**: Automatically refreshes cost data when items are changed
- **Error Handling**: Robust handling of corrupted data and missing items

### Cost Calculation Logic
1. **Primary Source**: Uses `Item.custom_average_cost` when available (> 0)
2. **Fallback Source**: Uses `Item.valuation_rate` when average cost is not available
3. **Bundle Total**: Calculates `qty × item_cost` for each component
4. **Retail Margin**: Automatically calculates retail price margins when available

### Data Integrity Features
- **String Concatenation Fix**: Handles corrupted cost values like `'12.26080464512.260804645'`
- **Missing Item Handling**: Graceful continuation when items are not found
- **Comprehensive Logging**: Detailed logs for debugging and monitoring

## Installation

```bash
# Navigate to your Frappe bench
cd /path/to/frappe-bench

# Install the app
bench get-app qcs_invoice_advance https://github.com/your-org/qcs_invoice_advance.git

# Install dependencies and migrate
bench install-app qcs_invoice_advance
bench migrate
