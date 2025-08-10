import os

from collections import defaultdict
from datetime import datetime
from dotenv import load_dotenv

from tricount_api import TricountAPI

# currency symbol/code to use in print output
CURRENCY = "EUR"

def _parse_date(date_str: str):
    if not date_str:
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(date_str, fmt)
        except Exception:
            pass
    return None


def _get_display_name(membership_block: dict) -> str:
    return (
        membership_block
        .get("RegistryMembershipNonUser", {})
        .get("alias", {})
        .get("display_name")
        or "Unbekannt"
    )


def _get_amount(entry_or_alloc: dict) -> float:
    """
    Prefer amount_local.value; fallback to amount.value. Return as float.
    Missing/invalid values -> 0.0
    """
    try:
        v = entry_or_alloc.get("amount_local", {}).get("value", None)
        if v is None:
            v = entry_or_alloc.get("amount", {}).get("value", 0)
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def expenses_for_month_breakdown(data, month: str):
    """
    Compute NET amounts for a given month (YYYY-MM):
      - per_category: {category: net_amount}  (signed = -amount; expense -> +, income -> -)
      - totals: {"expenses": sum of expenses +, "incomes": sum of incomes +, "net": expenses - incomes}
      - per_beneficiary: {person: net_amount}
      - per_payer: {person: net_amount}

    IMPORTANT:
      - Monthly totals are derived ONLY from per_category (not from allocations) to avoid double counting.
      - Allocations are used only to distribute amounts across people (same signed convention).
    """
    per_category = defaultdict(float)
    per_beneficiary = defaultdict(float)
    per_payer = defaultdict(float)

    response = data.get("Response", [])
    if not response:
        return {}, {"expenses": 0.0, "incomes": 0.0, "net": 0.0}, {}, {}

    entries = response[0].get("Registry", {}).get("all_registry_entry", []) or []

    for wrapper in entries:
        entry = (wrapper or {}).get("RegistryEntry", {}) or {}

        # consider ACTIVE entries only
        if entry.get("status") and entry["status"] != "ACTIVE":
            continue

        # date filter -> only target month
        dt = _parse_date(entry.get("date"))
        if not dt or dt.strftime("%Y-%m") != month:
            continue

        # amount (prefer local) and unified sign convention
        amount_val = _get_amount(entry)
        if amount_val == 0:
            continue
        signed = -amount_val  # expense (negative in data) -> + ; income (positive) -> -

        # category (prefer custom)
        category = entry.get("category_custom") or entry.get("category") or "Unbekannt"
        per_category[category] += signed

        # payer
        payer = _get_display_name(entry.get("membership_owned", {}))
        per_payer[payer] += signed

        # beneficiaries via allocations (distribution only)
        allocations = entry.get("allocations", []) or []
        if allocations:
            alloc_sum = 0.0
            for alloc in allocations:
                a = _get_amount(alloc)
                alloc_sum += a
                if a == 0:
                    continue
                per_beneficiary[_get_display_name(alloc.get("membership", {}))] += -a  # same signed convention
            # optional consistency check (does not affect totals)
            if abs(alloc_sum - amount_val) > 1e-6:
                print(f"⚠️  Warning: allocations ({alloc_sum}) != entry amount ({amount_val}) for ID={entry.get('id')}")
        else:
            # no allocations -> assign full signed amount to payer as beneficiary
            per_beneficiary[payer] += signed

    # derive monthly totals exclusively from per_category
    expenses = sum(v for v in per_category.values() if v > 0)   # expenses (positive)
    incomes  = sum(-v for v in per_category.values() if v < 0)  # incomes (positive)
    net      = sum(per_category.values())                        # net

    totals = {"expenses": float(expenses), "incomes": float(incomes), "net": float(net)}
    return dict(per_category), totals, dict(per_beneficiary), dict(per_payer)


# ------------------------
# Main
# ------------------------

if __name__ == "__main__":
    load_dotenv()
    TRICOUNT_KEY = os.getenv("TRICOUNT_KEY")
    trapi = TricountAPI(TRICOUNT_KEY)

    # refresh data if available
    try:
        trapi.update_data()
    except Exception:
        pass

    data = trapi.get_data()

    target_month = "2025-07"  # <<< set your desired month here

    per_category, totals, per_person, per_payer = expenses_for_month_breakdown(data, target_month)

    print(f"=== Net per category for {target_month} ===")
    # Note: values can be negative if incomes > expenses in a category.
    for cat, total in sorted(per_category.items(), key=lambda x: x[1], reverse=True):
        print(f"{cat}: {total:.2f} {CURRENCY}")

    print(f"\n=== Monthly totals ({target_month}) ===")
    print(f"Expenses: {totals['expenses']:.2f} {CURRENCY}")
    print(f"Incomes:  {totals['incomes']:.2f} {CURRENCY}")
    print(f"Net:      {totals['net']:.2f} {CURRENCY}")

    print(f"\n=== Net per person (Beneficiary) for {target_month} ===")
    for person, total in sorted(per_person.items(), key=lambda x: x[1], reverse=True):
        print(f"{person}: {total:.2f} {CURRENCY}")

    print(f"\n=== Net per payer (Payer) for {target_month} ===")
    for person, total in sorted(per_payer.items(), key=lambda x: x[1], reverse=True):
        print(f"{person}: {total:.2f} {CURRENCY}")
