import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import calendar

# ==========================================
# 1. PAGE CONFIGURATION & CUSTOM CSS
# ==========================================
st.set_page_config(
    page_title="FinanceFlow | Budget Tracker",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 0. TRANSLATIONS & THEME STATE
# ==========================================
TRANSLATIONS = {
    "English": {
        "tagline": "Your personal wealth dashboard.",
        "nav_caption": "Navigation is handled via the tabs in the main window.",
        "dashboard": "📊 Dashboard",
        "transactions": "💸 Transactions",
        "budgeting": "🎯 Budgeting",
        "settings": "⚙️ Settings",
        "overview": "📊 Dashboard Overview",
        "welcome": "👋 Welcome! It looks like you don't have any transactions yet. Head over to the **Transactions** tab to add some data.",
        "total_balance": "Total Balance",
        "monthly_income": "Monthly Income",
        "monthly_expenses": "Monthly Expenses",
        "savings_rate": "Savings Rate (Month)",
        "expense_dist": "Expense Distribution (All Time)",
        "income_vs_expense": "Income vs Expenses (Monthly Trend)",
        "no_expenses": "No expenses recorded yet.",
        "not_enough_data": "Not enough data for trend analysis.",
        "manage_transactions": "💸 Manage Transactions",
        "add_new": "Add New Transaction",
        "type": "Type",
        "expense": "Expense",
        "income": "Income",
        "date": "Date",
        "category": "Category",
        "amount": "Amount ($)",
        "notes": "Notes (Optional)",
        "add_btn": "Add Transaction",
        "recent": "Recent Transactions",
        "no_transactions": "No transactions found.",
        "budget_goals": "🎯 Budgeting & Goals",
        "set_monthly": "Set Monthly Budget",
        "exp_cat": "Expense Category",
        "monthly_limit": "Monthly Limit ($)",
        "save_budget": "Save Budget",
        "tracking": "Current Month Budget Tracking",
        "no_budgets": "You haven't set any budgets yet. Use the form on the left to set limits for your expense categories.",
        "spent": "Spent",
        "limit": "Limit",
        "used": "used",
        "exceeded": "⚠️ You have exceeded your budget for **{}** by {}!",
        "settings_export": "⚙️ Settings & Data Export",
        "export_data": "Export Data",
        "download_csv": "⬇️ Download All Transactions as CSV",
        "no_data_export": "No data available to export.",
        "danger_zone": "Danger Zone",
        "delete_warning": "Deleting your data is permanent and cannot be undone.",
        "clear_all": "🗑️ Clear All Data (Reset Database)",
        "data_deleted": "All data has been deleted.",
        "toast_success": "Transaction added successfully!",
        "toast_budget": "Budget updated for {}!",
        # Categories
        "cat_salary": "Salary",
        "cat_freelance": "Freelance",
        "cat_invest": "Investments",
        "cat_gifts": "Gifts",
        "cat_other_inc": "Other Income",
        "cat_housing": "Housing/Rent",
        "cat_food": "Food/Groceries",
        "cat_util": "Utilities",
        "cat_transp": "Transportation",
        "cat_ent": "Entertainment",
        "cat_shop": "Shopping",
        "cat_health": "Healthcare",
        "cat_debt": "Debt/Loans",
        "cat_other_exp": "Other Expense"
    },
    "Turkish": {
        "tagline": "Kişisel servet paneliniz.",
        "nav_caption": "Navigasyon ana penceredeki sekmeler üzerinden yapılır.",
        "dashboard": "📊 Gösterge Paneli",
        "transactions": "💸 İşlemler",
        "budgeting": "🎯 Bütçeleme",
        "settings": "⚙️ Ayarlar",
        "overview": "📊 Genel Bakış",
        "welcome": "👋 Hoş geldiniz! Henüz hiç işleminiz yok gibi görünüyor. Veri eklemek için **İşlemler** sekmesine gidin.",
        "total_balance": "Toplam Bakiye",
        "monthly_income": "Aylık Gelir",
        "monthly_expenses": "Aylık Giderler",
        "savings_rate": "Tasarruf Oranı (Ay)",
        "expense_dist": "Gider Dağılımı (Tüm Zamanlar)",
        "income_vs_expense": "Gelir vs Gider (Aylık Trend)",
        "no_expenses": "Henüz kaydedilmiş gider yok.",
        "not_enough_data": "Trend analizi için yeterli veri yok.",
        "manage_transactions": "💸 İşlemleri Yönet",
        "add_new": "Yeni İşlem Ekle",
        "type": "Tür",
        "expense": "Gider",
        "income": "Gelir",
        "date": "Tarih",
        "category": "Kategori",
        "amount": "Tutar ($)",
        "notes": "Notlar (Opsiyonel)",
        "add_btn": "İşlem Ekle",
        "recent": "Son İşlemler",
        "no_transactions": "İşlem bulunamadı.",
        "budget_goals": "🎯 Bütçeleme & Hedefler",
        "set_monthly": "Aylık Bütçe Belirle",
        "exp_cat": "Gider Kategorisi",
        "monthly_limit": "Aylık Limit ($)",
        "save_budget": "Bütçeyi Kaydet",
        "tracking": "Bu Ayki Bütçe Takibi",
        "no_budgets": "Henüz bütçe belirlemediniz. Gider kategorileriniz için limit belirlemek üzere soldaki formu kullanın.",
        "spent": "Harcanan",
        "limit": "Limit",
        "used": "kullanıldı",
        "exceeded": "⚠️ **{}** için bütçenizi {} aştınız!",
        "settings_export": "⚙️ Ayarlar & Veri Dışa Aktarma",
        "export_data": "Veriyi Dışa Aktar",
        "download_csv": "⬇️ Tüm İşlemleri CSV Olarak İndir",
        "no_data_export": "Dışa aktarılacak veri yok.",
        "danger_zone": "Tehlikeli Bölge",
        "delete_warning": "Verilerinizi silmek kalıcıdır ve geri alınamaz.",
        "clear_all": "🗑️ Tüm Verileri Temizle (Veritabanını Sıfırla)",
        "data_deleted": "Tüm veriler silindi.",
        "toast_success": "İşlem başarıyla eklendi!",
        "toast_budget": "{} için bütçe güncellendi!",
        # Categories
        "cat_salary": "Maaş",
        "cat_freelance": "Freelance",
        "cat_invest": "Yatırımlar",
        "cat_gifts": "Hediyeler",
        "cat_other_inc": "Diğer Gelir",
        "cat_housing": "Konut/Kira",
        "cat_food": "Gıda/Market",
        "cat_util": "Faturalar",
        "cat_transp": "Ulaşım",
        "cat_ent": "Eğlence",
        "cat_shop": "Alışveriş",
        "cat_health": "Sağlık",
        "cat_debt": "Borçlar",
        "cat_other_exp": "Diğer Gider"
    }
}

if "lang" not in st.session_state:
    st.session_state.lang = "Turkish"
if "theme" not in st.session_state:
    st.session_state.theme = "Dark"

def t(key):
    return TRANSLATIONS[st.session_state.lang].get(key, key)

THEME = {
    "Light": {
        "bg": "#f8fafc",
        "card_bg": "#ffffff",
        "text": "#1e293b",
        "muted": "#64748b",
        "border": "#f0f2f6",
        "shadow": "rgba(0, 0, 0, 0.05)"
    },
    "Dark": {
        "bg": "#0f172a",
        "card_bg": "#1e293b",
        "text": "#f8fafc",
        "muted": "#e2e8f0",
        "border": "#334155",
        "shadow": "rgba(0, 0, 0, 0.4)"
    }
}

def inject_custom_css():
    colors = THEME[st.session_state.theme]
    st.markdown(f"""
        <style>
        /* Main Font and Background */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
        
        .stApp {{
            background-color: {colors['bg']};
            color: {colors['text']};
        }}
        
        html, body, [class*="css"] {{
            font-family: 'Inter', sans-serif;
        }}
        
        /* Sidebar and Header Fixes */
        [data-testid="stSidebar"] {{
            background-color: {colors['card_bg']} !important;
            border-right: 1px solid {colors['border']};
        }}
        [data-testid="stHeader"] {{
            background-color: {colors['bg']} !important;
            border-bottom: 1px solid {colors['border']};
        }}
        [data-testid="stSidebar"] .stMarkdown h1, 
        [data-testid="stSidebar"] .stMarkdown h2, 
        [data-testid="stSidebar"] .stMarkdown h3,
        [data-testid="stSidebar"] [data-testid="stHeader"] h1,
        [data-testid="stSidebar"] h1 {{
            color: {colors['text']} !important;
        }}
        [data-testid="stSidebar"] .stMarkdown p,
        [data-testid="stSidebar"] .stCaption,
        [data-testid="stSidebar"] span {{
            color: {colors['muted']} !important;
            opacity: 1 !important;
        }}
        
        /* Metric Cards */
        .metric-card {{
            background-color: {colors['card_bg']};
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px {colors['shadow']};
            border: 1px solid {colors['border']};
            text-align: center;
        }}
        .metric-title {{
            color: {colors['muted']};
            font-size: 14px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 10px;
        }}
        .metric-value {{
            font-size: 28px;
            font-weight: 700;
            color: {colors['text']};
        }}
        .value-positive {{ color: #10b981; }}
        .value-negative {{ color: #ef4444; }}
        
        /* Progress Bar Customization */
        .budget-bar-container {{
            width: 100%;
            background-color: {colors['border']};
            border-radius: 8px;
            height: 12px;
            margin-top: 8px;
            overflow: hidden;
        }}
        .budget-bar-fill {{
            height: 100%;
            border-radius: 8px;
            transition: width 0.4s ease;
        }}
        .budget-safe {{ background-color: #10b981; }}
        .budget-warning {{ background-color: #f59e0b; }}
        .budget-danger {{ background-color: #ef4444; }}
        
        /* Contrast Improvements for Forms and Inputs */
        .stTextInput label, .stSelectbox label, .stNumberInput label, .stRadio label, .stDateInput label {{
            color: {colors['text']} !important;
            font-weight: 600 !important;
        }}
        
        /* Radio Button items visibility */
        div[data-testid="stRadio"] [data-testid="stWidgetLabel"] p,
        div[data-testid="stRadio"] label p {{
            color: {colors['text']} !important;
        }}
        
        /* Submit Button Styling */
        .stButton button, .stFormSubmitButton button {{
            background-color: #10b981 !important;
            color: white !important;
            font-weight: 700 !important;
            border: none !important;
            padding: 10px 24px !important;
            border-radius: 8px !important;
            transition: all 0.3s ease !important;
        }}
        .stButton button:hover, .stFormSubmitButton button:hover {{
            background-color: #059669 !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3) !important;
        }}
        
        /* Aggressive Selectbox Styling */
        div[data-baseweb="select"] > div,
        div[data-baseweb="select"] {{
            background-color: {colors['bg']} !important;
            color: {colors['text']} !important;
        }}
        
        .stSelectbox [data-baseweb="select"] {{
            border: 1px solid {colors['border']} !important;
            background-color: {colors['bg']} !important;
        }}

        /* Fix for selectbox placeholder and value visibility */
        div[data-baseweb="select"] * {{
            color: {colors['text']} !important;
        }}
        
        /* Popup Menu Styling (BaseWeb) */
        [data-baseweb="popover"], [data-baseweb="menu"], [role="listbox"] {{
            background-color: {colors['card_bg']} !important;
        }}
        
        [data-baseweb="popover"] *, [role="listbox"] * {{
            background-color: {colors['card_bg']} !important;
            color: {colors['text']} !important;
        }}

        [role="option"]:hover, [role="option"]:hover * {{
            background-color: {colors['bg']} !important;
            color: #10b981 !important;
        }}

        /* Input Fields */
        .stTextInput input, .stNumberInput input, .stDateInput input {{
            background-color: {colors['bg']} !important;
            color: {colors['text']} !important;
            border: 1px solid {colors['border']} !important;
        }}
        
        /* Streamlit Element Overrides */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 24px;
        }}
        .stTabs [data-baseweb="tab"] {{
            height: 50px;
            white-space: pre-wrap;
            background-color: transparent;
            border-radius: 4px 4px 0 0;
            gap: 1px;
            padding-top: 10px;
            padding-bottom: 10px;
            color: {colors['muted']};
        }}
        .stTabs [aria-selected="true"] {{
            background-color: transparent;
            color: #10b981 !important;
            border-bottom: 2px solid #10b981 !important;
            font-weight: 700 !important;
        }}
        
        /* Hide Default Sidebar Elements */
        footer {{visibility: hidden;}}
        </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. DATABASE MANAGEMENT (SQLite)
# ==========================================
DB_NAME = "finance_tracker.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Transactions Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            type TEXT,
            category TEXT,
            amount REAL,
            notes TEXT
        )
    ''')
    # Budgets Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS budgets (
            category TEXT PRIMARY KEY,
            limit_amount REAL
        )
    ''')
    conn.commit()
    conn.close()

def get_transactions():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM transactions ORDER BY date DESC, id DESC", conn)
    conn.close()
    if not df.empty:
        df['date'] = pd.to_datetime(df['date'])
    return df

def add_transaction(date, type, category, amount, notes):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO transactions (date, type, category, amount, notes) VALUES (?, ?, ?, ?, ?)",
              (date.strftime("%Y-%m-%d"), type, category, amount, notes))
    conn.commit()
    conn.close()

def get_budgets():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM budgets", conn)
    conn.close()
    return df

def set_budget(category, limit_amount):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO budgets (category, limit_amount) VALUES (?, ?)", 
              (category, limit_amount))
    conn.commit()
    conn.close()

def clear_database():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM transactions")
    c.execute("DELETE FROM budgets")
    conn.commit()
    conn.close()

# ==========================================
# 3. HELPER FUNCTIONS & CONSTANTS
# ==========================================
def get_categories():
    inc = [t("cat_salary"), t("cat_freelance"), t("cat_invest"), t("cat_gifts"), t("cat_other_inc")]
    exp = [t("cat_housing"), t("cat_food"), t("cat_util"), t("cat_transp"), 
           t("cat_ent"), t("cat_shop"), t("cat_health"), t("cat_debt"), t("cat_other_exp")]
    return inc, exp

def format_currency(amount):
    return f"${amount:,.2f}"

def render_metric_card(title, value, type="neutral"):
    color_class = "value-positive" if type == "positive" else "value-negative" if type == "negative" else ""
    # Add +/- sign for visual clarity if it's explicitly typed
    prefix = "+" if type == "positive" and value > 0 else ""
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">{title}</div>
            <div class="metric-value {color_class}">{prefix}{format_currency(value)}</div>
        </div>
    """, unsafe_allow_html=True)

# ==========================================
# 4. UI COMPONENTS (TABS)
# ==========================================
def render_dashboard(df):
    st.header(t("overview"))
    
    if df.empty:
        st.info(t("welcome"))
        return

    # Filter for current month
    current_month = datetime.now().replace(day=1)
    df_current_month = df[df['date'] >= current_month]

    # Calculate Metrics
    total_income = df[df['type'] == 'Income']['amount'].sum()
    total_expense = df[df['type'] == 'Expense']['amount'].sum()
    total_balance = total_income - total_expense

    monthly_income = df_current_month[df_current_month['type'] == 'Income']['amount'].sum()
    monthly_expense = df_current_month[df_current_month['type'] == 'Expense']['amount'].sum()
    
    savings_rate = 0
    if monthly_income > 0:
        savings_rate = ((monthly_income - monthly_expense) / monthly_income) * 100

    # Render Metric Cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_metric_card(t("total_balance"), total_balance, "positive" if total_balance >= 0 else "negative")
    with col2:
        render_metric_card(t("monthly_income"), monthly_income, "positive")
    with col3:
        render_metric_card(t("monthly_expenses"), monthly_expense, "negative")
    with col4:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">{t("savings_rate")}</div>
                <div class="metric-value" style="color: {'#10b981' if savings_rate >= 20 else '#f59e0b' if savings_rate > 0 else '#ef4444'};">
                    {savings_rate:.1f}%
                </div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Visualizations
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.subheader(t("expense_dist"))
        df_exp = df[df['type'] == 'Expense']
        if not df_exp.empty:
            exp_by_cat = df_exp.groupby('category')['amount'].sum().reset_index()
            fig = px.pie(exp_by_cat, values='amount', names='category', hole=0.6,
                         color_discrete_sequence=px.colors.qualitative.Pastel)
            fig.update_layout(margin=dict(t=30, b=0, l=0, r=0), showlegend=True,
                             paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                             font=dict(color=THEME[st.session_state.theme]['text']))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.write(t("no_expenses"))

    with col_chart2:
        st.subheader(t("income_vs_expense"))
        # Group by Year-Month
        df['Month'] = df['date'].dt.to_period('M').astype(str)
        monthly_trend = df.groupby(['Month', 'type'])['amount'].sum().reset_index()
        
        if not monthly_trend.empty:
            fig2 = px.bar(monthly_trend, x='Month', y='amount', color='type', barmode='group',
                          color_discrete_map={'Income': '#10B981', 'Expense': '#EF4444'})
            fig2.update_layout(margin=dict(t=30, b=0, l=0, r=0), 
                               xaxis_title="", yaxis_title=t("amount").replace("($)", ""),
                               legend_title_text='',
                               paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                               font=dict(color=THEME[st.session_state.theme]['text']))
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.write(t("not_enough_data"))

def render_transactions(df):
    st.header(t("manage_transactions"))
    
    col1, col2 = st.columns([1, 2])
    
    inc_cats, exp_cats = get_categories()
    
    with col1:
        st.subheader(t("add_new"))
        with st.form("transaction_form", clear_on_submit=True):
            t_type = st.radio(t("type"), [t("expense"), t("income")], horizontal=True)
            t_date = st.date_input(t("date"), datetime.today())
            
            # Dynamic category selection based on type
            if t_type == t("income"):
                t_category = st.selectbox(t("category"), inc_cats)
                db_type = "Income"
            else:
                t_category = st.selectbox(t("category"), exp_cats)
                db_type = "Expense"
                
            t_amount = st.number_input(t("amount"), min_value=0.01, format="%.2f", step=10.0)
            t_notes = st.text_input(t("notes"))
            
            submitted = st.form_submit_button(t("add_btn"), use_container_width=True)
            if submitted:
                add_transaction(t_date, db_type, t_category, t_amount, t_notes)
                st.toast(t("toast_success"), icon="✅")
                st.rerun()

    with col2:
        st.subheader(t("recent"))
        if df.empty:
            st.write(t("no_transactions"))
        else:
            # Display formatted dataframe
            display_df = df.copy()
            display_df['date'] = display_df['date'].dt.strftime('%Y-%m-%d')
            display_df['amount'] = display_df.apply(
                lambda x: f"+${x['amount']:.2f}" if x['type'] == 'Income' else f"-${x['amount']:.2f}", axis=1
            )
            # Drop ID for cleaner display
            display_df = display_df[['date', 'type', 'category', 'amount', 'notes']]
            
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
                height=400
            )

def render_budgeting(df, budgets_df):
    st.header(t("budget_goals"))
    
    col1, col2 = st.columns([1, 2])
    _, exp_cats = get_categories()
    
    with col1:
        st.subheader(t("set_monthly"))
        with st.form("budget_form"):
            b_category = st.selectbox(t("exp_cat"), exp_cats)
            
            # Pre-fill current budget if exists
            current_limit = 0.0
            if not budgets_df.empty and b_category in budgets_df['category'].values:
                current_limit = float(budgets_df[budgets_df['category'] == b_category]['limit_amount'].iloc[0])
                
            b_limit = st.number_input(t("monthly_limit"), min_value=0.0, value=current_limit, step=50.0)
            
            b_submitted = st.form_submit_button(t("save_budget"), use_container_width=True)
            if b_submitted:
                set_budget(b_category, b_limit)
                st.toast(t("toast_budget").format(b_category), icon="🎯")
                st.rerun()

    with col2:
        st.subheader(t("tracking"))
        if budgets_df.empty:
            st.info(t("no_budgets"))
            return

        # Calculate current month's expenses per category
        current_month = datetime.now().replace(day=1)
        df_current_month_exp = df[(df['type'] == 'Expense') & (df['date'] >= current_month)]
        
        for index, row in budgets_df.iterrows():
            cat = row['category']
            limit = row['limit_amount']
            
            if limit <= 0:
                continue
                
            spent = df_current_month_exp[df_current_month_exp['category'] == cat]['amount'].sum()
            progress = min(spent / limit, 1.0)
            percentage = (spent / limit) * 100
            
            # Determine color based on progress
            if progress < 0.75:
                status_color = "budget-safe"
            elif progress < 1.0:
                status_color = "budget-warning"
            else:
                status_color = "budget-danger"
                
            st.markdown(f"**{cat}** ({t('spent')}: {format_currency(spent)} / {t('limit')}: {format_currency(limit)})")
            st.markdown(f"""
                <div class="budget-bar-container">
                    <div class="budget-bar-fill {status_color}" style="width: {progress * 100}%;"></div>
                </div>
                <div style="font-size: 12px; color: {THEME[st.session_state.theme]['muted']}; margin-top: 4px; margin-bottom: 15px; text-align: right;">
                    {percentage:.1f}% {t('used')}
                </div>
            """, unsafe_allow_html=True)
            
            if percentage > 100:
                st.error(t("exceeded").format(cat, format_currency(spent - limit)))

def render_settings(df):
    st.header(t("settings_export"))
    
    st.subheader(t("export_data"))
    if not df.empty:
        csv = df.to_csv(index=False)
        st.download_button(
            label=t("download_csv"),
            data=csv,
            file_name=f"finance_export_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=False
        )
    else:
        st.write(t("no_data_export"))
        
    st.markdown("---")
    
    st.subheader(t("danger_zone"))
    st.warning(t("delete_warning"))
    if st.button(t("clear_all"), type="primary"):
        clear_database()
        st.success(t("data_deleted"))
        st.rerun()

# ==========================================
# 5. MAIN APPLICATION FLOW
# ==========================================
def main():
    init_db()
    
    # Sidebar
    with st.sidebar:
        st.title("💸 FinanceFlow")
        st.markdown(t("tagline"))
        st.markdown("---")
        
        # New Selectors
        st.session_state.lang = st.selectbox("🌐 Language / Dil", ["English", "Turkish"], 
                                          index=0 if st.session_state.lang == "English" else 1)
        
        st.session_state.theme = st.select_slider("🌗 Theme / Tema", options=["Light", "Dark"], 
                                               value=st.session_state.theme)
        
        st.markdown("---")
        st.caption(t("nav_caption"))

    inject_custom_css()

    # Load Data
    df = get_transactions()
    budgets_df = get_budgets()

    # Layout using Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        t("dashboard"), 
        t("transactions"), 
        t("budgeting"), 
        t("settings")
    ])

    with tab1:
        render_dashboard(df)
        
    with tab2:
        render_transactions(df)
        
    with tab3:
        render_budgeting(df, budgets_df)
        
    with tab4:
        render_settings(df)

if __name__ == "__main__":
    main()