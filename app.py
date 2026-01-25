import streamlit as st
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import io
from datetime import datetime, timedelta, timezone

# ---------------- HELPERS ----------------

def today_date():
    ist = timezone(timedelta(hours=5, minutes=30))
    return datetime.now(ist).strftime("%d-%m-%Y")

def parse_number(value):
    try:
        value = str(value).replace(",", "").strip()
        return float(value) if value else None
    except:
        return None

def format_indian_number(num):
    if num is None:
        return ""
    n = int(num)
    s = str(n)[::-1]
    parts = [s[:3]]
    s = s[3:]
    while s:
        parts.append(s[:2])
        s = s[2:]
    return "₹" + ",".join(parts)[::-1]

# ---------------- IMAGE GENERATION ----------------

def generate_image(name, date, amount, weight, due_date, rate, adv):
    df = pd.DataFrame([{
        "DATE": date or today_date(),
        "NAME": name.upper(),
        "AMOUNT": format_indian_number(parse_number(amount)),
        "WT (g)": weight,
        "DUE DATE": due_date,
        "RATE": format_indian_number(parse_number(rate)),
        "ADV %": adv
    }])

    fig, ax = plt.subplots(figsize=(18, 3.5))
    ax.axis("off")

    table = ax.table(
        cellText=df.values,
        colLabels=df.columns,
        cellLoc="center",
        loc="center",
        bbox=[0.02, 0.05, 0.96, 0.90]
    )

    table.auto_set_font_size(False)
    table.set_fontsize(16)
    table.scale(1.4, 2.5)

    for (row, col), cell in table.get_celld().items():
        if row == 0:
            cell.set_facecolor("#1E3A8A")
            cell.set_text_props(color="white", weight="bold")
        else:
            cell.set_facecolor("#F9FAFB")
            cell.set_text_props(weight="bold")

    plt.suptitle(
        "JOS ALUKKAS INDIA PRIVATE LIMITED - BELAGAVI BRANCH",
        fontsize=22,
        fontweight="bold",
        y=0.98
    )

    buf = io.BytesIO()
    plt.savefig(buf, dpi=300, bbox_inches="tight", format="png", facecolor="white")
    plt.close(fig)
    buf.seek(0)

    return buf.getvalue()

# ---------------- STREAMLIT UI ----------------

st.set_page_config(page_title="Payment Table Generator", layout="centered")

st.title("💰 Payment Table Generator")

name = st.text_input("Customer Name")
date = st.text_input("Date (DD-MM-YYYY)", value=today_date())
amount = st.text_input("Amount (INR)")
weight = st.text_input("Weight (grams)")
due_date = st.text_input("Due Date")
rate = st.text_input("Rate per gram")
adv = st.text_input("Advance %")

if st.button("📊 GENERATE IMAGE"):
    if not name:
        st.warning("Please enter customer name")
    else:
        image_bytes = generate_image(
            name, date, amount, weight, due_date, rate, adv
        )

        st.image(image_bytes)

        filename = f"{name.replace(' ', '_')}_payment.png"

        st.download_button(
            label="⬇️ DOWNLOAD IMAGE",
            data=image_bytes,
            file_name=filename,
            mime="image/png"
        )
