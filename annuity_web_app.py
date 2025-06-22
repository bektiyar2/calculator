import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Аннуитетный калькулятор", page_icon="💸")

def calculate_annuity(principal, annual_rate, months):
    monthly_rate = annual_rate / 12 / 100
    factor = (monthly_rate * (1 + monthly_rate) ** months) / ((1 + monthly_rate) ** months - 1)
    return round(principal * factor, 2)

def generate_schedule_with_prepayment(principal, rate, months, ep_month, ep_amount, option):
    monthly_rate = rate / 12 / 100
    payment = calculate_annuity(principal, rate, months)
    schedule = []
    balance = principal
    m = 1

    while balance > 0.01:
        interest = round(balance * monthly_rate, 2)
        principal_payment = round(payment - interest, 2)
        balance = round(balance - principal_payment, 2)

        # Apply prepayment
        if m == ep_month and ep_amount > 0:
            if ep_amount >= balance:
                schedule.append([m, ep_amount, ep_amount, 0, 0])
                break
            balance -= ep_amount
            if option == "Сократить срок":
                remaining = months - m
                months = m + 1 + remaining  # just recalculate from this point
            elif option == "Уменьшить платёж":
                remaining = months - m
                payment = calculate_annuity(balance, rate, remaining)

        schedule.append([m, payment, principal_payment, interest, max(balance, 0)])
        m += 1

        # fail-safe to prevent infinite loop
        if m > 500:
            break

    df = pd.DataFrame(schedule, columns=["Месяц", "Платёж", "Тело", "Проценты", "Остаток"])
    return df

# --- UI ---

st.title("💸 Аннуитетный калькулятор с досрочным погашением")

col1, col2 = st.columns(2)
with col1:
    principal = st.number_input("Сумма кредита (₸)", min_value=100000, step=100000, value=2_000_000)
    months = st.slider("Срок кредита (мес.)", 6, 360, 36)
with col2:
    rate = st.slider("Ставка (% годовых)", 1.0, 30.0, 14.0)
    st.markdown("")

st.markdown("### 🔄 Досрочное погашение (опционально)")
extra_month = st.number_input("Месяц досрочного погашения", min_value=0, max_value=months, value=0, step=1)
extra_amount = st.number_input("Сумма досрочного платежа (₸)", min_value=0.0, step=10000.0)
adjust_type = st.radio("После досрочного погашения:", ["Сократить срок", "Уменьшить платёж"])

if st.button("📊 Рассчитать"):
    df = generate_schedule_with_prepayment(principal, rate, months, extra_month, extra_amount, adjust_type)
    total_paid = df["Платёж"].sum()
    st.subheader(f"💰 Ежемесячный платёж: {df['Платёж'].iloc[0]:,.2f} ₸")
    st.write(f"📉 Переплата по процентам: {df['Проценты'].sum():,.2f} ₸")
    st.write(f"📆 Кол-во месяцев: {df.shape[0]}")
    st.write(f"💸 Всего выплачено: {total_paid:,.2f} ₸")

    st.markdown("### 🧾 График платежей")
    st.dataframe(df.style.format("{:,.2f}"))

    st.markdown("### 📈 Визуализация структуры платежа")
    fig, ax = plt.subplots()
    ax.plot(df["Месяц"], df["Тело"], label="Тело", color="green")
    ax.plot(df["Месяц"], df["Проценты"], label="Проценты", color="orange")
    ax.set_xlabel("Месяц")
    ax.set_ylabel("Сумма")
    ax.set_title("Структура аннуитетного платежа")
    ax.legend()
    st.pyplot(fig)
