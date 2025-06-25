import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import psycopg2
from sqlalchemy import create_engine

engine = create_engine('postgresql://admin:admin123@localhost:5432/weblogs')

def read_postgres_table(table_name):
    try:
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", engine)
        return df
    except Exception as e:
        print(f"Error reading table {table_name}: {e}")
        return pd.DataFrame()

product_views_df = read_postgres_table("product_views")
action_counts_df = read_postgres_table("action_counts")


# Biểu đồ 1: Top 5 sản phẩm được xem nhiều nhất
if not product_views_df.empty:
    top_products = product_views_df.groupby("product_id")["view_count"].sum().reset_index() \
        .sort_values("view_count", ascending=False).head(5)
    plt.figure(figsize=(10, 6))
    sns.barplot(x="product_id", y="view_count", data=top_products)
    plt.title("Top 5 sản phẩm được xem nhiều nhất")
    plt.xlabel("Mã sản phẩm")
    plt.ylabel("Số lượt xem")
    plt.xticks(rotation=45)
    plt.savefig("output/product_views.png")
    plt.close()


# Biểu đồ 3: Tỷ lệ hành động
if not action_counts_df.empty:
    action_summary = action_counts_df.groupby("action")["action_count"].sum().reset_index()
    plt.figure(figsize=(8, 8))
    plt.pie(action_summary["action_count"], labels=action_summary["action"], autopct='%1.1f%%')
    plt.title("Tỷ lệ hành động người dùng")
    plt.savefig("output/action_counts.png")
    plt.close()