import pandas as pd
from models import get_orders

orders = get_orders()
query = """
SELECT *
FROM User
LEFT JOIN Orders
ON User.table_number == Orders.user_id
"""
orders_overview = pd.read_sql(query, db.session.bind)
orders_overview = orders_overview.sort_values(by=['table_number'], ascending=False)
        # orders_overview1 = orders_overview.groupby("table_number")
print(order_overview)

"""
for index, row in orders_df.iterrows():
    if row ["client_is_gone"] == "yes":
        nb_of_tables = 0
        """