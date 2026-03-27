import sqlite3

conn = sqlite3.connect('data/woocommerce.db')
c = conn.cursor()

# Get exact numbers
c.execute("SELECT COUNT(*), SUM(total) FROM wc_orders WHERE strftime('%Y',date_paid)='2025' AND date_paid IS NOT NULL AND status IN ('completed','completoenviado','processing','porsalir')")
paid_2025 = c.fetchone()

c.execute("SELECT COUNT(*), SUM(total) FROM wc_orders WHERE strftime('%Y',date_paid)='2024' AND date_paid IS NOT NULL AND status IN ('completed','completoenviado','processing','porsalir')")
paid_2024 = c.fetchone()

c.execute("SELECT COUNT(*), SUM(total) FROM wc_orders WHERE strftime('%Y',date_created)='2025' AND status IN ('completed','completoenviado','processing','porsalir')")
created_2025 = c.fetchone()

c.execute("SELECT COUNT(*), SUM(total) FROM wc_orders WHERE strftime('%Y',date_created)='2024' AND status IN ('completed','completoenviado','processing','porsalir')")
created_2024 = c.fetchone()

conn.close()

print("2025:")
print(f"  date_created: {created_2025[0]} ped, ${created_2025[1]:,.0f}" if created_2025[1] else "  date_created: 0 ped, $0")
print(f"  date_paid:    {paid_2025[0]} ped, ${paid_2025[1]:,.0f}" if paid_2025[1] else "  date_paid:    0 ped, $0")
print(f"  WC CSV:       637 ped, $52,907,936")

print("\n2024:")
print(f"  date_created: {created_2024[0]} ped, ${created_2024[1]:,.0f}" if created_2024[1] else "  date_created: 0 ped, $0")
print(f"  date_paid:    {paid_2024[0]} ped, ${paid_2024[1]:,.0f}" if paid_2024[1] else "  date_paid:    0 ped, $0")
print(f"  WC CSV:       986 ped, $78,037,182")
