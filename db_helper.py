import psycopg2
from psycopg2 import pool
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database connection details
db_pool = None

try:
    db_pool = psycopg2.pool.SimpleConnectionPool(
        1, 10,
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        port=os.getenv("DB_PORT")
    )

    if db_pool:
        print("Connection pool created successfully")

except psycopg2.DatabaseError as e:
    print(f"Error creating connection pool: {e}")


# Function to call the PostgreSQL stored procedure and insert an order item
def insert_order_item(food_item, quantity, order_id):
    conn = None
    try:
        conn = db_pool.getconn()
        cursor = conn.cursor()

        # Calling the procedure using CALL
        cursor.execute("CALL public.insert_order_item(%s, %s, %s);", (food_item, int(quantity), order_id))

        # Committing the changes
        conn.commit()

        # Closing the cursor
        cursor.close()

        print("Order item inserted successfully!")
        return 1

    except psycopg2.Error as err:
        print(f"Error inserting order item: {err}")

        # Rollback changes if necessary
        if conn:
            conn.rollback()
        return -1

    except Exception as e:
        print(f"An error occurred: {e}")
        if conn:
            conn.rollback()
        return -1

    finally:
        if conn:
            db_pool.putconn(conn)


# Function to insert a record into the order_tracking table
def insert_order_tracking(order_id, status):
    conn = None
    try:
        conn = db_pool.getconn()
        cursor = conn.cursor()

        # Inserting the record into the order_tracking table
        insert_query = "INSERT INTO public.order_tracking (order_id, status) VALUES (%s, %s)"
        cursor.execute(insert_query, (order_id, status))

        # Committing the changes
        conn.commit()

        # Closing the cursor
        cursor.close()

        print("Order tracking inserted successfully!")

    except psycopg2.Error as err:
        print(f"Error inserting order tracking: {err}")
        if conn:
            conn.rollback()

    finally:
        if conn:
            db_pool.putconn(conn)


# Function to get the total order price using a PostgreSQL function
def get_total_order_price(order_id):
    conn = None
    try:
        conn = db_pool.getconn()
        cursor = conn.cursor()

        # Executing the SQL query to get the total order price
        cursor.execute("SELECT public.get_total_order_price(%s);", (order_id,))

        # Fetching the result
        result = cursor.fetchone()[0]

        # Closing the cursor
        cursor.close()

        return result

    except psycopg2.Error as err:
        print(f"Error fetching total order price: {err}")
        return None

    finally:
        if conn:
            db_pool.putconn(conn)


# Function to get the next available order_id
def get_next_order_id():
    conn = None
    try:
        conn = db_pool.getconn()
        cursor = conn.cursor()

        # Executing the SQL query to get the next available order_id
        cursor.execute("SELECT MAX(order_id) FROM orders;")

        # Fetching the result
        result = cursor.fetchone()[0]

        # Closing the cursor
        cursor.close()

        # Returning the next available order_id
        if result is None:
            return 1
        else:
            return result + 1

    except psycopg2.Error as err:
        print(f"Error fetching next order ID: {err}")
        return None

    finally:
        if conn:
            db_pool.putconn(conn)


# Function to fetch the order status from the order_tracking table
def get_order_status(order_id):
    conn = None
    try:
        conn = db_pool.getconn()
        cursor = conn.cursor()

        # Executing the SQL query to fetch the order status
        cursor.execute("SELECT status FROM order_tracking WHERE order_id = %s;", (order_id,))

        # Fetching the result
        result = cursor.fetchone()

        # Closing the cursor
        cursor.close()

        # Returning the order status
        if result:
            return result[0]
        else:
            return None

    except psycopg2.Error as err:
        print(f"Error fetching order status: {err}")
        return None

    finally:
        if conn:
            db_pool.putconn(conn)


if __name__ == "__main__":
    # Example usage
    next_order_id = get_next_order_id()
    print(f"Next Order ID: {next_order_id}")

    # Example to insert an order item
    insert_order_item('Masala Dosa', 1, next_order_id)
