import streamlit as st
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import io
from datetime import datetime, timezone, timedelta

# ---------------- FUNCTIONS ----------------

def today_date():
    ist = timezone(timedelta(hours=5, minutes=30))
    return datetime.now(ist).strftime("%d-%m-%Y")

def parse_number(val):
    try:
        return float(str(val).replace(",", "").strip())
    except:
        return None

def format_indian(num):
    if not num:
        return ""
    n = int(num)
    s = str(n)[::-1]
    out = s[:3]
    s = s[3:]
    while s:
        out += "," + s[:2]
        s = s[2:]
    return "₹" + out[::-1]

def generate_image(data):
    df = pd.DataFrame(data)

    fig, ax = plt.subplots(figsize=(20, 4))
    ax.axis("off")

    table = ax.table(
        cellText=df.values,
        colLabels=df.columns,
        cellLoc="center",
        loc="center",
        bbox=[0.02, 0.05, 0.96, 0.9]
    )

    table.auto_set_font_size(False)
    table.set_fontsize(15)
    table.scale(1.4, 2.4)

    header_color = "#1E3A8A"
    border_color = "#D1D5DB"

    for (row, col), cell in table.get_celld().items():
        cell.set_edgecolor(border_color)
        if row == 0:
            cell.set_facecolor(header_color)
            cell.set_text_props(color="white", weight="bold")
        else:
            cell.set_facecolor("#F9FAFB")
            cell.set_text_props(weight="bold")  # BODY TEXT BOLD

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    buf.seek(0)

    return buf.getvalue()

# ---------------- STREAMLIT UI ----------------

st.set_page_config(page_title="JOS ALUKKAS CUS ADV", layout="wide")
st.title("💎 JOS ALUKKAS CUS ADV")

num_customers = st.number_input(
    "How many customers?",
    min_value=1,
    max_value=10,
    value=1,
    step=1
)

# Button to apply today's date to ALL customers
apply_today = st.button("📅 Apply Today's Date")

customers = []

# Shared rate (auto-fill)
shared_rate = st.text_input("Rate per gram (applies to all customers)")

for i in range(num_customers):
    st.subheader(f"Customer {i+1}")

    col1, col2, col3 = st.columns(3)

    with col1:
        name = st.text_input("Name", key=f"name{i}")
        date = st.text_input(
            "Date",
            value=today_date() if apply_today else "",
            key=f"date{i}"
        )
        amount = st.text_input("Amount", key=f"amount{i}")

    with col2:
        wt = st.text_input("Weight (g)", key=f"wt{i}")
        rate = st.text_input(
            "Rate/g",
            value=shared_rate,
            key=f"rate{i}"
        )

    with col3:
        due = st.text_input("Due Date", key=f"due{i}")
        adv = st.text_input("Advance %", key=f"adv{i}")

    if name.strip():
        customers.append({
            "DATE": date,
            "NAME": name.upper(),
            "AMOUNT": format_indian(parse_number(amount)),
            "WT (g)": wt,
            "DUE DATE": due,
            "RATE": format_indian(parse_number(rate)),
            "ADV %": adv
        })

st.markdown("---")

if st.button("📊 GENERATE IMAGE"):
    if not customers:
        st.warning("Please enter at least one customer")
    else:
        img = generate_image(customers)

        st.image(img)
        st.download_button(
            "⬇️ DOWNLOAD IMAGE",
            data=img,
            file_name="payment_table.png",
            mime="image/png"
        )
