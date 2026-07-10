import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="E-Commerce Analytics Dashboard",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .kpi-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
    }
    .kpi-value {
        font-size: 1.8rem;
        font-weight: bold;
        color: #1f77b4;
    }
    .kpi-label {
        font-size: 0.9rem;
        color: #666;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown('<h1 class="main-header"> E-Commerce Analytics Dashboard</h1>', unsafe_allow_html=True)
st.markdown("---")

# DATA LOADING WITH CACHING
@st.cache_data
def load_data():
    """Load and cache the cleaned transaction data."""
    try:
        df = pd.read_csv('data/processed/clean_transactions.csv')
        df['date'] = pd.to_datetime(df['date'])
        return df
    except FileNotFoundError:
        try:
            df = pd.read_csv('data/raw/data.csv')
            df['date'] = pd.to_datetime(df['date'])
            if 'total_amount' not in df.columns:
                df['total_amount'] = df['quantity'] * df['unit_price']
            return df
        except Exception as e:
            st.error(f" Error loading data: {e}")
            return None

@st.cache_data
def load_rfm_data():
    """Load RFM analysis results."""
    try:
        rfm = pd.read_csv('outputs/reports/rfm_summary.csv')
        return rfm
    except:
        return None

# Load data
df = load_data()

if df is not None:

    # SIDEBAR FILTERS

    st.sidebar.header(" Filters")
    st.sidebar.markdown("---")
    
    # Date range filter
    min_date = df['date'].min().date()
    max_date = df['date'].max().date()
    
    st.sidebar.subheader(" Date Range")
    date_range = st.sidebar.date_input(
        "Select Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    st.sidebar.markdown("---")
    
    # Category filter
    st.sidebar.subheader(" Category")
    categories = ['All'] + sorted(df['category'].unique().tolist())
    selected_category = st.sidebar.selectbox("Select Category", categories)
    
    st.sidebar.markdown("---")
    

    # FIXED: Payment Method Filter

    st.sidebar.subheader(" Payment Method")
    payment_methods = ['All'] + sorted(df['payment_method'].dropna().unique().tolist())
    selected_payment = st.sidebar.selectbox("Select Payment Method", payment_methods)
    
    st.sidebar.markdown("---")
    
    # City filter
    st.sidebar.subheader(" City")
    cities = ['All'] + sorted(df['customer_city'].dropna().unique().tolist())
    selected_city = st.sidebar.selectbox("Select City", cities)
    
    st.sidebar.markdown("---")
    
    # Price range filter
    st.sidebar.subheader(" Price Range")
    min_price = float(df['total_amount'].min())
    max_price = float(df['total_amount'].max())
    price_range = st.sidebar.slider(
        "Select Price Range",
        min_value=min_price,
        max_value=max_price,
        value=(min_price, max_price),
        step=10.0
    )
    
    st.sidebar.markdown("---")
    st.sidebar.info(" Use filters to explore your data interactively!")
    
    # APPLY FILTERS WITH ERROR HANDLING

    try:
        filtered_df = df.copy()
        
        # Apply date filter
        if len(date_range) == 2:
            filtered_df = filtered_df[
                (filtered_df['date'] >= pd.to_datetime(date_range[0])) &
                (filtered_df['date'] <= pd.to_datetime(date_range[1]))
            ]
        
        # Apply category filter
        if selected_category != 'All':
            filtered_df = filtered_df[filtered_df['category'] == selected_category]
        
        # FIXED: Apply payment method filter safely

        if selected_payment != 'All' and selected_payment is not None:
            filtered_df = filtered_df[filtered_df['payment_method'] == selected_payment]
        
        # Apply city filter
        if selected_city != 'All':
            filtered_df = filtered_df[filtered_df['customer_city'] == selected_city]
        
        # Apply price range filter
        filtered_df = filtered_df[
            (filtered_df['total_amount'] >= price_range[0]) &
            (filtered_df['total_amount'] <= price_range[1])
        ]
        
        # Reset index
        filtered_df = filtered_df.reset_index(drop=True)
        
    except Exception as e:
        st.error(f" Error applying filters: {e}")
        filtered_df = df.copy()
    
    # CHECK IF DATA IS EMPTY

    if filtered_df.empty:
        st.warning(" No data matches the selected filters. Please adjust your filters.")
        filtered_df = df.copy()  # Reset to show all data
    

    # KPI CARDS

    st.header(" Key Performance Indicators")
    
    total_revenue = filtered_df['total_amount'].sum()
    total_orders = len(filtered_df)
    unique_customers = filtered_df['customer_id'].nunique()
    avg_order_value = filtered_df['total_amount'].mean() if total_orders > 0 else 0
    total_quantity = filtered_df['quantity'].sum()
    unique_products = filtered_df['product_name'].nunique()
    
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value">₹{total_revenue:,.0f}</div>
            <div class="kpi-label"> Total Revenue</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value">{total_orders:,}</div>
            <div class="kpi-label"> Total Orders</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value">{unique_customers:,}</div>
            <div class="kpi-label"> Unique Customers</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value">₹{avg_order_value:,.2f}</div>
            <div class="kpi-label"> Avg Order Value</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value">{total_quantity:,}</div>
            <div class="kpi-label"> Total Items Sold</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col6:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value">{unique_products}</div>
            <div class="kpi-label"> Unique Products</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    

    # ROW 1: Monthly Revenue & Category

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader(" Monthly Revenue Trend")
        if not filtered_df.empty and len(filtered_df) > 1:
            monthly = filtered_df.groupby(filtered_df['date'].dt.to_period('M'))['total_amount'].sum().reset_index()
            monthly['date'] = monthly['date'].astype(str)
            
            fig1 = px.line(
                monthly, 
                x='date', 
                y='total_amount',
                title='Monthly Revenue',
                labels={'date': 'Month', 'total_amount': 'Revenue (₹)'},
                markers=True
            )
            fig1.update_traces(line_color='#1f77b4', line_width=3)
            fig1.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                hovermode='x'
            )
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.info("No data available for the selected filters.")
    
    with col2:
        st.subheader(" Revenue by Category")
        if not filtered_df.empty:
            category = filtered_df.groupby('category')['total_amount'].sum().reset_index()
            category = category.sort_values('total_amount', ascending=True)
            
            fig2 = px.bar(
                category,
                x='total_amount',
                y='category',
                title='Category Revenue',
                labels={'total_amount': 'Revenue (₹)', 'category': ''},
                orientation='h',
                color='total_amount',
                color_continuous_scale='Blues'
            )
            fig2.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                coloraxis_showscale=False
            )
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No data available for the selected filters.")
    

    # ROW 2: Payment Methods & City

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader(" Payment Method Distribution")
        if not filtered_df.empty:
            payment = filtered_df['payment_method'].value_counts().reset_index()
            payment.columns = ['payment_method', 'count']
            
            fig3 = px.pie(
                payment,
                values='count',
                names='payment_method',
                title='Payment Methods',
                hole=0.3,
                color='payment_method',
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            fig3.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                showlegend=True,
                legend=dict(orientation='h', yanchor='bottom', y=-0.2)
            )
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("No data available for the selected filters.")
    
    with col2:
        st.subheader(" Revenue by City")
        if not filtered_df.empty:
            city = filtered_df.groupby('customer_city')['total_amount'].sum().reset_index()
            city = city.sort_values('total_amount', ascending=True).tail(10)
            
            fig4 = px.bar(
                city,
                x='total_amount',
                y='customer_city',
                title='Top 10 Cities by Revenue',
                labels={'total_amount': 'Revenue (₹)', 'customer_city': ''},
                orientation='h',
                color='total_amount',
                color_continuous_scale='Greens'
            )
            fig4.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                coloraxis_showscale=False
            )
            st.plotly_chart(fig4, use_container_width=True)
        else:
            st.info("No data available for the selected filters.")
    
    
    # ROW 3: Payment Method vs Revenue 

    st.subheader(" Payment Method Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if not filtered_df.empty:
            payment_revenue = filtered_df.groupby('payment_method')['total_amount'].sum().reset_index()
            payment_revenue = payment_revenue.sort_values('total_amount', ascending=True)
            
            fig10 = px.bar(
                payment_revenue,
                x='total_amount',
                y='payment_method',
                title='Revenue by Payment Method',
                labels={'total_amount': 'Revenue (₹)', 'payment_method': ''},
                orientation='h',
                color='total_amount',
                color_continuous_scale='Reds'
            )
            fig10.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                coloraxis_showscale=False
            )
            st.plotly_chart(fig10, use_container_width=True)
        else:
            st.info("No data available.")
    
    with col2:
        if not filtered_df.empty:
            payment_orders = filtered_df['payment_method'].value_counts().reset_index()
            payment_orders.columns = ['payment_method', 'order_count']
            
            fig11 = px.bar(
                payment_orders,
                x='payment_method',
                y='order_count',
                title='Orders by Payment Method',
                labels={'payment_method': '', 'order_count': 'Number of Orders'},
                color='payment_method',
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig11.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                showlegend=False
            )
            st.plotly_chart(fig11, use_container_width=True)
        else:
            st.info("No data available.")
    

    # ROW 4: Top Products & Customers

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader(" Top 10 Products by Revenue")
        if not filtered_df.empty:
            products = filtered_df.groupby('product_name')['total_amount'].sum().reset_index()
            products = products.sort_values('total_amount', ascending=False).head(10)
            
            fig5 = px.bar(
                products,
                x='total_amount',
                y='product_name',
                title='Top Products',
                labels={'total_amount': 'Revenue (₹)', 'product_name': ''},
                orientation='h',
                color='total_amount',
                color_continuous_scale='Oranges'
            )
            fig5.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                coloraxis_showscale=False,
                height=400
            )
            st.plotly_chart(fig5, use_container_width=True)
        else:
            st.info("No data available for the selected filters.")
    
    with col2:
        st.subheader(" Top 10 Customers by Spending")
        if not filtered_df.empty:
            customers = filtered_df.groupby('customer_id')['total_amount'].sum().reset_index()
            customers = customers.sort_values('total_amount', ascending=False).head(10)
            customers['customer_id'] = customers['customer_id'].str.replace('CUST', 'C-')
            
            fig6 = px.bar(
                customers,
                x='total_amount',
                y='customer_id',
                title='Top Customers',
                labels={'total_amount': 'Total Spent (₹)', 'customer_id': ''},
                orientation='h',
                color='total_amount',
                color_continuous_scale='Purples'
            )
            fig6.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                coloraxis_showscale=False,
                height=400
            )
            st.plotly_chart(fig6, use_container_width=True)
        else:
            st.info("No data available for the selected filters.")
    

    # ROW 5: Distributions

    st.subheader(" Transaction Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if not filtered_df.empty and len(filtered_df) > 1:
            fig7 = px.histogram(
                filtered_df,
                x='total_amount',
                nbins=50,
                title='Order Value Distribution',
                labels={'total_amount': 'Order Value (₹)'},
                color_discrete_sequence=['#2ecc71']
            )
            fig7.add_vline(
                x=filtered_df['total_amount'].mean(), 
                line_dash="dash", 
                line_color="red",
                annotation_text=f"Mean: ₹{filtered_df['total_amount'].mean():.2f}",
                annotation_position="top"
            )
            fig7.add_vline(
                x=filtered_df['total_amount'].median(), 
                line_dash="dash", 
                line_color="blue",
                annotation_text=f"Median: ₹{filtered_df['total_amount'].median():.2f}",
                annotation_position="bottom"
            )
            fig7.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig7, use_container_width=True)
        else:
            st.info("Not enough data for distribution.")
    
    with col2:
        if not filtered_df.empty and len(filtered_df) > 1:
            fig8 = px.histogram(
                filtered_df,
                x='quantity',
                nbins=10,
                title='Order Quantity Distribution',
                labels={'quantity': 'Quantity'},
                color_discrete_sequence=['#3498db']
            )
            fig8.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig8, use_container_width=True)
        else:
            st.info("Not enough data for distribution.")
    

    # ROW 6: Customer Age

    st.subheader("👤 Customer Demographics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if not filtered_df.empty and 'customer_age' in filtered_df.columns and len(filtered_df) > 1:
            fig9 = px.histogram(
                filtered_df,
                x='customer_age',
                nbins=20,
                title='Age Distribution',
                labels={'customer_age': 'Age'},
                color_discrete_sequence=['#e74c3c']
            )
            fig9.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig9, use_container_width=True)
        else:
            st.info("No age data available.")
    
    with col2:
        if not filtered_df.empty:
            # Payment method stats
            payment_stats = filtered_df.groupby('payment_method').agg({
                'total_amount': ['sum', 'mean', 'count']
            }).reset_index()
            payment_stats.columns = ['payment_method', 'total_revenue', 'avg_order_value', 'order_count']
            payment_stats['avg_order_value'] = payment_stats['avg_order_value'].round(2)
            payment_stats['total_revenue'] = payment_stats['total_revenue'].round(2)
            
            st.subheader("💳 Payment Method Statistics")
            st.dataframe(
                payment_stats,
                column_config={
                    'payment_method': 'Method',
                    'total_revenue': 'Total Revenue (₹)',
                    'avg_order_value': 'Avg Order (₹)',
                    'order_count': 'Orders'
                },
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No data available.")
    

    # RFM SEGMENTATION

    st.header("Customer Segmentation (RFM)")
    
    rfm_df = load_rfm_data()
    
    if rfm_df is not None and not rfm_df.empty:
        col1, col2 = st.columns([1.5, 1])
        
        with col1:
            fig11 = px.pie(
                rfm_df,
                values='customer_count',
                names='segment',
                title='RFM Customer Segments',
                hole=0.3,
                color='segment',
                color_discrete_sequence=px.colors.qualitative.Set1
            )
            fig11.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig11, use_container_width=True)
        
        with col2:
            st.subheader("Segment Summary")
            display_rfm = rfm_df.copy()
            display_rfm['customer_count'] = display_rfm['customer_count'].astype(int)
            display_rfm['percentage'] = display_rfm['percentage'].round(1)
            display_rfm['recency'] = display_rfm['recency'].round(0).astype(int)
            display_rfm['frequency'] = display_rfm['frequency'].round(1)
            display_rfm['monetary'] = display_rfm['monetary'].round(2)
            
            st.dataframe(
                display_rfm,
                column_config={
                    'segment': 'Segment',
                    'customer_count': 'Customers',
                    'percentage': '%',
                    'recency': 'Recency (days)',
                    'frequency': 'Frequency',
                    'monetary': 'Monetary (₹)',
                    'rfm_score': 'RFM Score'
                },
                use_container_width=True,
                hide_index=True
            )
    else:
        st.info("Run the pipeline to generate RFM analysis: `python -m src.main`")
    

    # DATA TABLE & DOWNLOAD

    st.header("Data Preview")
    
    with st.expander("Click to view data preview", expanded=False):
        st.dataframe(
            filtered_df.head(100),
            use_container_width=True,
            height=300
        )
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.download_button(
            label="Download Filtered Data (CSV)",
            data=filtered_df.to_csv(index=False).encode('utf-8'),
            file_name='filtered_data.csv',
            mime='text/csv',
            use_container_width=True
        )
    
    with col2:
        if not filtered_df.empty:
            summary_df = pd.DataFrame({
                'Metric': ['Total Revenue', 'Total Orders', 'Unique Customers', 'Avg Order Value', 'Total Items'],
                'Value': [
                    f'₹{total_revenue:,.2f}',
                    f'{total_orders:,}',
                    f'{unique_customers:,}',
                    f'₹{avg_order_value:,.2f}',
                    f'{total_quantity:,}'
                ]
            })
            st.download_button(
                label="Download Summary (CSV)",
                data=summary_df.to_csv(index=False).encode('utf-8'),
                file_name='dashboard_summary.csv',
                mime='text/csv',
                use_container_width=True
            )
    
    with col3:
        st.markdown(f"""
        <div style="text-align:center; padding:1rem; background-color:#f0f2f6; border-radius:10px;">
            <span style="font-size:1.2rem;">Showing <b>{len(filtered_df):,}</b> records</span>
        </div>
        """, unsafe_allow_html=True)
    
   
    # FOOTER
  
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.caption(f"Data Range: {filtered_df['date'].min().date()} to {filtered_df['date'].max().date()}")
    
    with col2:
        st.caption(f" Categories: {filtered_df['category'].nunique()} | Products: {filtered_df['product_name'].nunique()}")
    
    with col3:
        st.caption(f" Last Updated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")

else:
    st.error("No data found!")
    st.info("""
    ### Please run the pipeline first:
    
    1. Activate virtual environment:
    ```bash
    source venv/bin/activate""")