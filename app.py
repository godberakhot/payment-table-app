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

# ---------------- IMAGE GENERATION ----------------

def generate_image(data):
    df = pd.DataFrame(data)

    rows = len(df)
    fig_height = 1.8 + rows * 0.95
    fig, ax = plt.subplots(figsize=(20, fig_height))
    ax.axis("off")

    col_widths = [0.12, 0.30, 0.14, 0.10, 0.14, 0.12, 0.08]

    table = ax.table(
        cellText=df.values,
        colLabels=df.columns,
        cellLoc="center",
        colWidths=col_widths,
        loc="center"
    )

    table.auto_set_font_size(False)
    table.set_fontsize(15)

    header_color = "#1E3A8A"
    border_color = "#D1D5DB"
    name_col = df.columns.get_loc("NAME")

    for (row, col), cell in table.get_celld().items():
        cell.set_edgecolor(border_color)

        if row == 0:
            cell.set_facecolor(header_color)
            cell.set_text_props(color="white", weight="bold")
            cell.set_height(0.13)
        else:
            cell.set_facecolor("#F9FAFB")
            cell.set_text_props(weight="bold")

            if col == name_col:
                text = cell.get_text().get_text()
                lines = max(1, len(text) // 18)
                cell.set_height(0.12 + lines * 0.06)
                cell.get_text().set_wrap(True)
            else:
                cell.set_height(0.12)

    plt.suptitle(
        "JOS ALUKKAS INDIA PRIVATE LIMITED - BELAGAVI BRANCH",
        fontsize=22,
        fontweight="bold",
        y=0.98
    )

    buf = io.BytesIO()
    plt.savefig(buf, dpi=300, bbox_inches="tight", facecolor="white")
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

# shared rate
if "shared_rate" not in st.session_state:
    st.session_state.shared_rate = ""

shared_rate = st.text_input(
    "Rate per gram (applies to all customers)",
    st.session_state.shared_rate
)
st.session_state.shared_rate = shared_rate

# apply today date
if st.button("📅 APPLY TODAY'S DATE"):
    for i in range(num_customers):
        st.session_state[f"date{i}"] = today_date()

customers = []

for i in range(num_customers):
    st.subheader(f"Customer {i+1}")

    name = st.text_input("Customer Name", key=f"name{i}")
    date = st.text_input("Date (DD-MM-YYYY)", key=f"date{i}")
    amount = st.text_input("Amount (INR)", key=f"amount{i}")
    wt = st.text_input("Weight (grams)", key=f"wt{i}")
    due = st.text_input("Due Date", key=f"due{i}")

    rate = st.text_input(
        "Rate per gram",
        value=shared_rate,
        key=f"rate{i}"
    )

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
            img,
            "payment_table.png",
            "image/png"
        )
