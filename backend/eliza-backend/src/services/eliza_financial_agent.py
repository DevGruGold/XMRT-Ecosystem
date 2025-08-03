import pandas as pd
import json
from datetime import datetime

# 🧾 Simulated DAO ledger
ledger = pd.DataFrame(
    [
        {
            "timestamp": "2025-7-1",
            "type": "income",
            "amount": 21.34,
            "source": "mobile mining",
        },
        {
            "timestamp": "2025-7-5",
            "type": "expense",
            "amount": -5.12,
            "source": "infra",
        },
        {
            "timestamp": "2025-7-10",
            "type": "income",
            "amount": 13.67,
            "source": "staking",
        },
        {
            "timestamp": "2025-7-12",
            "type": "expense",
            "amount": -3.0,
            "source": "dev bounties",
        },
        {
            "timestamp": "2025-7-28",
            "type": "income",
            "amount": 18.25,
            "source": "XMR swap profit",
        },
    ]
)


def summarize_ledger(df):
    net = df["amount"].sum()
    income = df[df["amount"] > 0]["amount"].sum()
    expense = df[df["amount"] < 0]["amount"].sum()
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "net_income": round(net, 2),
        "total_income": round(income, 2),
        "total_expenses": round(expense, 2),
        "entry_count": len(df),
    }


def staking_yield(df):
    stake_income = df[df["source"].str.contains("staking", case=False)]["amount"].sum()
    total_income = df[df["amount"] > 0]["amount"].sum()
    return {"staking_yield_pct": round((stake_income / total_income) * 100, 2)}


def generate_monthly_summary():
    summary = summarize_ledger(ledger)
    summary.update(staking_yield(ledger))
    return summary


if __name__ == "__main__":
    result = generate_monthly_summary()
    print("📊 Eliza Monthly DAO Financial Summary:")
    print(json.dumps(result, indent=2))
