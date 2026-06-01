# ============================================================
#       CUSTOMER BEHAVIOR ANALYSIS — DATA PREPARATION
#                     & FEATURE ENGINEERING
# ============================================================

import pandas as pd

# ------------------------------------------------------------
# 1. LOAD DATA
# ------------------------------------------------------------

df = pd.read_csv('customer_shopping_behavior.csv')


# ------------------------------------------------------------
# 2. INITIAL EXPLORATION
# ------------------------------------------------------------

df.head()

df.info()

df.describe(include='all')


# ------------------------------------------------------------
# 3. MISSING VALUES
# ------------------------------------------------------------

# Check for missing values
df.isnull().sum()

# Impute 'Review Rating' with the median value grouped by Category
df['Review Rating'] = (
    df.groupby('Category')['Review Rating']
    .transform(lambda x: x.fillna(x.median()))
)

# Confirm no missing values remain
df.isnull().sum()


# ------------------------------------------------------------
# 4. COLUMN NAME CLEANING
# ------------------------------------------------------------

# Standardize column names: lowercase + underscores
df.columns = df.columns.str.lower().str.replace(' ', '_')

# Rename purchase amount column for clarity
df = df.rename(columns={'purchase_amount_(usd)': 'purchase_amount_usd'})

df.columns


# ------------------------------------------------------------
# 5. FEATURE ENGINEERING
# ------------------------------------------------------------

# --- Feature 1: Age Group ---
labels = ['Young Adult', 'Adult', 'Middle-aged', 'Senior']
df['age_group'] = pd.qcut(df['age'], q=4, labels=labels)

df[['age', 'age_group']].head(30)


# --- Feature 2: Purchase Frequency (in Days) ---
df['frequency_of_purchases'].unique()

frequency_mapping = {
    'Weekly'        : 7,
    'Fortnightly'   : 14,
    'Bi-Weekly'     : 14,
    'Monthly'       : 30,
    'Quarterly'     : 90,
    'Every 3 Months': 90,
    'Annually'      : 365,
}
df['purchase_frequency_days'] = df['frequency_of_purchases'].map(frequency_mapping)

df[['frequency_of_purchases', 'purchase_frequency_days']].head(20)


# ------------------------------------------------------------
# 6. REDUNDANT COLUMN REMOVAL
# ------------------------------------------------------------

# Check if 'discount_applied' and 'promo_code_used' are identical
df[['discount_applied', 'promo_code_used']].head(20)

(df['discount_applied'] == df['promo_code_used']).all()

# Drop 'promo_code_used' since it's redundant
df = df.drop(columns=['promo_code_used'])


# ------------------------------------------------------------
# 7. EXPORT TO SQL SERVER
# ------------------------------------------------------------

import pyodbc
from sqlalchemy import create_engine

# Connection configuration
server   = 'DESKTOP-ED4GA26\\SQLEXPRESS'
database = 'customer_behavior_analysis'
driver   = 'ODBC Driver 17 for SQL Server'

conn_str = (
    f'DRIVER={driver};'
    f'SERVER={server};'
    f'DATABASE={database};'
    f'Trusted_Connection=yes;'
)

engine = create_engine(f'mssql+pyodbc:///?odbc_connect={conn_str}')

with engine.connect() as conn:
    print("✓ Connection Successful!")

# Write DataFrame to SQL Server
table = 'customers'
df.to_sql(table, con=engine, if_exists='replace', index=False)
print(f"✓ DataFrame successfully written to the '{table}' table in SQL Server!")