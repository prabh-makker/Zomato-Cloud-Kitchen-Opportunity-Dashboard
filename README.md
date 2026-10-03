# Zomato Cloud Kitchen Opportunity Dashboard

**Portfolio project:** Power BI dashboard identifying high-opportunity localities for cloud kitchen launches in Bangalore.

## Features
- **Data cleaning pipeline** (`prep_data.py`): Zomato restaurant + Bengaluru house-price datasets → cleaned CSVs
- **Custom metric**: Opportunity Score = (avg votes ÷ restaurants) × (100,000 ÷ rent per sq ft)
- **Interactive Power BI dashboard**: Ranks top 48 localities; includes map, bar chart, price sweet-spot analysis, top-10 table, and winner card for Hosur Road
- **Small-sample bias guard**: Localities ranked only if 10+ restaurants (avoids inflated scores from 1–2 entries)
- **Data honesty**: 77.5% of restaurants rent-matched; unmatched ones shown as null in Power BI

## Files
- `prep_data.py` — Data cleaning script (mojibake reversal, locality normalization, join)
- `powerbi_python_script.py` — Python connector for Power BI (loads cleaned CSVs)
- `data/restaurants_clean.csv` — 9,189 cleaned restaurant records
- `data/locality_clean.csv` — 60 matched localities with avg rent
- `Zomato Cloud Kitchen Opportunity Dashboard.pbix` — Power BI dashboard

## How to use
1. Run `python prep_data.py` to regenerate cleaned CSVs from raw data
2. Open the .pbix file in Power BI Desktop
3. Refresh Python data source (Data → Refresh all)
4. Explore dashboard visuals

## Key findings
**Top 3 unfiltered** (raw scores, no minimum-restaurant guard):
- Rajarajeshwari Nagar: score 1332 (2 restaurants) → excluded after 10+ guard
- Kengeri: score 910 (1 restaurant) → excluded
- Langford Town: score 747 (2 restaurants) → excluded

**Top 3 after 10+ guard** (48 valid localities):
1. Hosur Road (score 214, 10 restaurants, rent ₹5,716/sq ft)
2. Infantry Road
3. ...

**Recommendation**: Launch at Hosur Road. High demand (214 opportunity score), high foot traffic (10 restaurants, avg rating 3.81), affordable rent (₹5,716/sq ft).

## Technical notes
- Mojibake corruption fixed: 68 restaurant names were UTF-8/Latin-1 double-encoded; reversed via iterative `.encode("latin-1").decode("utf-8")` chain + cp1252 byte replacements
- Locality join: Zomato uses coarse locality names (e.g. "Hosur Road"); matched to finer house-price localities via substring matching
- Page background: Cream (#F6F1E7); map banner ("visual retiring") overlaid with white rectangle; no Azure Maps upgrade needed

---

**Author:** Prabh Singh  
**Built with:** Python (pandas, regex), Power BI Desktop  
**Data source:** Kaggle (Zomato Bangalore Restaurants, Bengaluru House Prices)
