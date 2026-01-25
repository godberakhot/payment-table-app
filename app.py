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
    table.set_fontsize(14)
    table.scale(1.4, 2.2)

    header_color = "#1E3A8A"

    for col in range(len(df.columns)):
        cell = table[(0, col)]
        cell.set_facecolor(header_color)
        cell.set_text_props(color="white", weight="bold")

    plt.suptitle(
        "JOS ALUKKAS INDIA PRIVATE LIMITED - BELAGAVI BRANCH",
        fontsize=20,
        fontweight="bold",
        y=0.98
    )

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)

    return buf.getvalue()

# ---------------- STREAMLIT UI ----------------

st.set_page_config(page_title="Payment Table Generator", layout="wide")
st.title("💎 Payment Table Generator")

num_customers = st.number_input(
    "How many customers?",
    min_value=1,
    max_value=10,
    value=1,
    step=1
)

customers = []

for i in range(num_customers):
    st.subheader(f"Customer {i+1}")

    col1, col2, col3 = st.columns(3)

    with col1:
        name = st.text_input("Name", key=f"name{i}")
        date = st.text_input("Date", value=today_date(), key=f"date{i}")
        amount = st.text_input("Amount", key=f"amount{i}")

    with col2:
        wt = st.text_input("Weight (g)", key=f"wt{i}")
        rate = st.text_input("Rate/g", key=f"rate{i}")

    with col3:
        adv = st.text_input("Advance %", key=f"adv{i}")
        due = st.text_input("Due Date", key=f"due{i}")

    customers.append({
        "DATE": date,
        "NAME": name.upper(),
        "AMOUNT": format_indian(parse_number(amount)),
        "WT (g)": wt,
        "RATE": format_indian(parse_number(rate)),
        "ADV %": adv,
        "DUE DATE": due
    })

st.markdown("---")

if st.button("📊 GENERATE IMAGE"):
    img = generate_image(customers)

    st.image(img)
    st.download_button(
        "⬇️ DOWNLOAD IMAGE",
        data=img,
        file_name="payment_table.png",
        mime="image/png"
    )
