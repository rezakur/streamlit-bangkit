import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

orders_products_customers_df = pd.read_csv('main_data.csv')

city_max_price = orders_products_customers_df.groupby('customer_city')['price'].sum()

sorted_cities = city_max_price.sort_values(ascending=False)

top_20_cities = sorted_cities.head(20)

st.subheader('Top 20 Cities by Max Total Price of Items Sold')
plt.figure(figsize=(12, 8))
ax = top_20_cities.plot(kind='barh')
plt.xlabel('Max Total Price of Items Sold')
plt.ylabel('City')
plt.title('Top 20 Cities by Max Total Price of Items Sold')
plt.gca().invert_yaxis()  

for i in ax.patches:
    ax.text(i.get_width() + 50, i.get_y() + i.get_height()/2,
            '${:,.0f}'.format(i.get_width()),
            fontsize=10, color='black', ha='left', va='center')

st.pyplot(plt)

city_total_price = orders_products_customers_df.groupby('customer_city')['price'].sum()

top_15_cities = city_total_price.nlargest(15)

other_cities_total_price = city_total_price[~city_total_price.index.isin(top_15_cities.index)]
others_total_price = other_cities_total_price.sum()
top_15_cities['Others'] = others_total_price

st.subheader('Total Price Distribution per Customer City')
plt.figure(figsize=(12, 8))
plt.pie(top_15_cities, labels=top_15_cities.index, autopct='%1.1f%%', startangle=90)
plt.axis('equal')  
plt.title('Total Price Distribution per Customer City')
st.pyplot(plt)

city_max_items = orders_products_customers_df.groupby('customer_city')['order_item_id'].max()

sorted_cities = city_max_items.sort_values(ascending=False)

top_10_cities = sorted_cities.head(20)

st.subheader('Top 20 Cities by Max Number of Items Sold')
plt.figure(figsize=(12, 8))
ax = top_10_cities.plot(kind='barh')
plt.xlabel('Max Number of Items Sold')
plt.ylabel('City')
plt.title('Top 20 Cities by Max Number of Items Sold')
plt.gca().invert_yaxis() 

for i in ax.patches:
    ax.text(i.get_width() + 0.001, i.get_y() + i.get_height()/2, 
            str(int(i.get_width())), 
            fontsize=10, color='white', ha='right', va='center', weight='bold')

st.pyplot(plt)

category_total_price = orders_products_customers_df.groupby('product_category_name_english')['price'].sum()

top_10_categories = category_total_price.nlargest(20)

st.subheader('Top 20 Product Categories by Total Price')
plt.figure(figsize=(12, 8))
ax = top_10_categories.plot(kind='barh')
plt.xlabel('Total Price')
plt.ylabel('Product Category')
plt.title('Top 20 Product Categories by Total Price')
plt.gca().invert_yaxis()

for i in ax.patches:
    ax.text(i.get_width() + 100, i.get_y() + i.get_height()/2, 
            '${:,.0f}'.format(i.get_width()), 
            fontsize=10, color='white', ha='right', va='center', weight='bold')

st.pyplot(plt)

top_15_categories = category_total_price.nlargest(15)

other_categories_total_price = category_total_price[~category_total_price.index.isin(top_15_categories.index)]
others_total_price = other_categories_total_price.sum()
top_15_categories['Others'] = others_total_price

st.subheader('Total Price Distribution per Product Category')
plt.figure(figsize=(12, 8))
plt.pie(top_15_categories, labels=top_15_categories.index, autopct='%1.1f%%', startangle=90)
plt.axis('equal') 
plt.title('Total Price Distribution per Product Category')
st.pyplot(plt)

top_categories = orders_products_customers_df.groupby('product_category_name_english')['product_id'].count().nlargest(20).sort_values()

st.subheader('Top 20 Product Categories by Number of Items Sold')
plt.figure(figsize=(12, 8))
ax = top_categories.plot(kind='barh')
ax.invert_yaxis()
plt.xlabel('Number of Items')
plt.ylabel('Product Category')
plt.title('Top 20 Product Categories by Number of Items Sold')
plt.gca().invert_yaxis()

for i in ax.patches:
    ax.text(i.get_width() + 5, i.get_y() + i.get_height()/2, 
            str(round(i.get_width(), 2)), 
            fontsize=10, color='white', ha='right', va='center', weight='bold')

st.pyplot(plt)

category_counts = orders_products_customers_df['product_category_name_english'].value_counts()
top_categories = category_counts.nlargest(15)
other_categories_count = category_counts[~category_counts.index.isin(top_categories.index)].sum()

plot_data = top_categories.append(pd.Series({'Others': other_categories_count}))

st.subheader('Distribution of Product Categories by Items Sold')
plt.figure(figsize=(12, 8))
plt.pie(plot_data, labels=plot_data.index, autopct='%1.1f%%', startangle=90)
plt.axis('equal') 
plt.title('Distribution of Product Categories by Items Sold')
st.pyplot(plt)

customers_buy = orders_products_customers_df.groupby(by="customer_id").product_id.nunique().sort_values(ascending=False)
customers_pay = orders_products_customers_df.groupby('customer_id')['price'].sum().sort_values(ascending=False)
customer_buy_pay = pd.merge(customers_buy, customers_pay, on='customer_id', how='inner')
customer_buy_pay = customer_buy_pay.drop_duplicates()
customer_buy_pay = customer_buy_pay.rename(columns={'product_id': 'product_bought'})
data = customer_buy_pay
rfm = data.groupby('customer_id').agg({
    'product_bought': 'sum',
    'price': 'sum'
})

rfm.columns = ['Frequency', 'Monetary']

rfm['Frequency_score'] = pd.qcut(rfm['Frequency'].rank(method='first'), q=3, labels=False)
rfm['Monetary_score'] = pd.qcut(rfm['Monetary'], q=3, labels=False)

rfm['FM_score'] = rfm['Frequency_score'].astype(str) + rfm['Monetary_score'].astype(str)

seg_map = {
    r'[0-1][0-1]': 'Low Value',
    r'[0-1]2': 'Medium Value',
    r'2[0-1]': 'Medium Value',
    r'22': 'High Value'
}

rfm['Segment'] = rfm['Frequency_score'].astype(str) + rfm['Monetary_score'].astype(str)
rfm['Segment'] = rfm['Segment'].replace(seg_map, regex=True)

segment_counts = rfm['Segment'].value_counts()

st.subheader('RFM Analysis')
plt.figure(figsize=(8, 8))
plt.pie(segment_counts, labels=segment_counts.index, autopct='%1.1f%%')
plt.title('Customer Segmentation')
plt.axis('equal')
st.pyplot(plt)