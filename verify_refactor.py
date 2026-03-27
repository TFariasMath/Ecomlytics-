
import pandas as pd
import numpy as np

# Mocking the logic found in new_main_content.py to verify it works as expected

def test_logic(df_orders_filtered, df_ga_filtered):
    print("\n---------------------------------------------------")
    print(f"Testing with: Orders={len(df_orders_filtered)}, GA={len(df_ga_filtered)}")
    
    combined_df = pd.DataFrame()
    daily_sales = pd.DataFrame()
    daily_ga = pd.DataFrame()

    if not df_orders_filtered.empty:
        daily_sales = df_orders_filtered.groupby('date_only').agg(
            Ventas=('total', 'sum'),
            Ordenes=('order_id', 'count')
        ).reset_index()
        daily_sales['date_only'] = pd.to_datetime(daily_sales['date_only'])
        
    if not df_ga_filtered.empty:
        daily_ga = df_ga_filtered.groupby('date_only').agg(
            Visitas=('UsuariosActivos', 'sum')
        ).reset_index()
        daily_ga['date_only'] = pd.to_datetime(daily_ga['date_only'])

    if not daily_sales.empty and not daily_ga.empty:
        combined_df = pd.merge(daily_sales, daily_ga, on='date_only', how='outer').fillna(0)
    elif not daily_sales.empty:
        combined_df = daily_sales.copy()
        combined_df['Visitas'] = 0
    elif not daily_ga.empty:
        combined_df = daily_ga.copy()
        combined_df['Ventas'] = 0
        combined_df['Ordenes'] = 0

    if not combined_df.empty:
        combined_df = combined_df.sort_values('date_only')
        
    print("Result combined_df:")
    if combined_df.empty:
        print("EMPTY")
    else:
        print(combined_df)
        print(f"Columns: {combined_df.columns.tolist()}")

# Scenario 1: Both present
orders1 = pd.DataFrame({'date_only': ['2023-01-01'], 'total': [100], 'order_id': [1]})
ga1 = pd.DataFrame({'date_only': ['2023-01-01'], 'UsuariosActivos': [50]})
test_logic(orders1, ga1)

# Scenario 2: Only GA (The bug case!)
orders2 = pd.DataFrame()
ga2 = pd.DataFrame({'date_only': ['2023-01-02'], 'UsuariosActivos': [60]})
test_logic(orders2, ga2)

# Scenario 3: Only Sales
orders3 = pd.DataFrame({'date_only': ['2023-01-03'], 'total': [200], 'order_id': [2]})
ga3 = pd.DataFrame()
test_logic(orders3, ga3)

# Scenario 4: Both Empty
test_logic(pd.DataFrame(), pd.DataFrame())
