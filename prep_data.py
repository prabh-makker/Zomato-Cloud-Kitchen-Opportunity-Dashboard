"""Clean Zomato + Bengaluru house-price data and join on locality for Power BI."""
import re
import pandas as pd

DATA = "data"


def norm(s):
    return re.sub(r"\s+", " ", str(s)).strip().lower()


def fix_mojibake(s):
    # source CSV has names re-encoded latin-1->utf-8 several times (e.g. "Café" -> "CafÃÂÃÂ©")
    if not isinstance(s, str):
        return s
    cur = s
    for _ in range(10):
        try:
            nxt = cur.encode("latin-1").decode("utf-8")
        except (UnicodeDecodeError, UnicodeEncodeError):
            break
        if nxt == cur:
            break
        cur = nxt
    # leftover stray cp1252 bytes (e.g. right single quote) that aren't part of the utf-8 chain
    return cur.replace("\x92", "'").replace("\x91", "'").replace("\x93", '"').replace("\x94", '"')


def parse_sqft(val):
    # some rows are ranges like "2100-2850" or have units like "34.46Sq. Meter"
    s = str(val).strip()
    if "-" in s:
        parts = s.split("-")
        try:
            return (float(parts[0]) + float(parts[1])) / 2
        except ValueError:
            return None
    try:
        return float(s)
    except ValueError:
        return None


# ---- Zomato restaurants ----
zomato = pd.read_csv(f"{DATA}/zomato.csv", usecols=[
    "name", "location", "online_order", "book_table", "rate", "votes",
    "cuisines", "approx_cost(for two people)", "rest_type", "listed_in(type)",
])
before = len(zomato)

zomato["rate"] = zomato["rate"].astype(str).str.extract(r"([\d.]+)").astype(float)
zomato["approx_cost(for two people)"] = (
    zomato["approx_cost(for two people)"].astype(str).str.replace(",", "", regex=False)
)
zomato["approx_cost(for two people)"] = pd.to_numeric(
    zomato["approx_cost(for two people)"], errors="coerce"
)
zomato = zomato.dropna(subset=["rate", "approx_cost(for two people)", "location"])
zomato["name"] = zomato["name"].map(fix_mojibake)
zomato = zomato.drop_duplicates(subset=["name", "location"])
zomato["location_norm"] = zomato["location"].map(norm)
zomato = zomato.rename(columns={"approx_cost(for two people)": "cost_for_two"})

after = len(zomato)
print(f"Zomato: {before} -> {after} rows after cleaning ({before - after} dropped)")

zomato.to_csv(f"{DATA}/restaurants_clean.csv", index=False)

# ---- Bengaluru house prices (rent proxy) ----
house = pd.read_csv(f"{DATA}/bengaluru_house_prices.csv", usecols=["location", "total_sqft", "price"])
house["total_sqft"] = house["total_sqft"].map(parse_sqft)
house = house.dropna(subset=["location", "total_sqft", "price"])
house = house[house["total_sqft"] > 0]
house["price_per_sqft"] = house["price"] * 100000 / house["total_sqft"]
house["location_norm"] = house["location"].map(norm)

print(f"House prices: {len(house)} usable rows, {house['location_norm'].nunique()} unique localities")

# ---- Join: zomato locality is coarser than house-price locality, so match by substring ----
zomato_localities = sorted(zomato["location_norm"].unique())
house_grouped = house.groupby("location_norm")["price_per_sqft"].agg(["mean", "count"])

rows = []
unmatched = []
for loc in zomato_localities:
    hits = house_grouped[
        house_grouped.index.str.contains(re.escape(loc), na=False)
        | [loc in h for h in house_grouped.index]
    ]
    if len(hits) == 0:
        unmatched.append(loc)
        continue
    # weight by count of listings per matched sub-locality
    avg_price = (hits["mean"] * hits["count"]).sum() / hits["count"].sum()
    rows.append({"location_norm": loc, "avg_price_per_sqft": round(avg_price, 2), "matched_sublocalities": len(hits)})

locality_clean = pd.DataFrame(rows)
locality_clean.to_csv(f"{DATA}/locality_clean.csv", index=False)

print(f"Locality join: {len(zomato_localities)} zomato localities, {len(rows)} matched, {len(unmatched)} unmatched")
if unmatched:
    print("Unmatched (no rent data found, will be null after join in Power BI):")
    for u in unmatched:
        print(f"  - {u}")
