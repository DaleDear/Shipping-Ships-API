import sqlite3
import json

def update_ship(id, ship_data):
    with sqlite3.connect("./shipping.db") as conn:
        db_cursor = conn.cursor()

        db_cursor.execute(
            """
            UPDATE Ship
                SET
                    name = ?,
                    hauler_id = ?
            WHERE id = ?
            """,
            (ship_data['name'], ship_data['hauler_id'], id)
        )

        rows_affected = db_cursor.rowcount

    return True if rows_affected > 0 else False

def delete_ship(pk):
    with sqlite3.connect("./shipping.db") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        # Write the SQL query to get the information you want
        db_cursor.execute("""
        DELETE FROM Ship WHERE id = ?
        """, (pk,)
        )
        number_of_rows_deleted = db_cursor.rowcount

    return True if number_of_rows_deleted > 0 else False


def list_ships(url):
    expand_param = url["query_params"].get("_expand")
    # Open a connection to the database
    with sqlite3.connect("./shipping.db") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        if expand_param: 
            # Write the SQL query to get the information you want
            db_cursor.execute(
                """
            SELECT
                s.id,
                s.name,
                s.hauler_id,
                h.id haulerId,
                h.name haulerName,
                h.dock_id
            FROM Ship s
            JOIN Hauler h
                ON h.id = s.hauler_id
            """
            )
        else:
            db_cursor.execute(
                """
            SELECT
                s.id,
                s.name,
                s.hauler_id
            FROM Ship s              
            """)
        query_results = db_cursor.fetchall()

        # Initialize an empty list and then add each dictionary to it
        ships=[]
        for row in query_results:
            row_dict = dict(row)
            hauler_id = row_dict.get("haulerId") if "haulerId" in row_dict else None
            hauler_name = row_dict.get("haulerName") if "haulerName" in row_dict else None
            dock_id = row_dict.get("dock_id") if "dock_id" in row_dict else None

            
            hauler = {
                "id": hauler_id,
                "name": hauler_name,
                "dock_id": dock_id,
            }
            ship = {
                "id": row_dict["id"],
                "name": row_dict["name"],
                "hauler_id": row_dict["hauler_id"],
                "hauler": hauler,
            }
            ships.append(ship)

        # Serialize Python list to JSON encoded string
        serialized_ships = json.dumps(ships)

    return serialized_ships

def retrieve_ship(pk, expand=False):
    # Open a connection to the database
    with sqlite3.connect("./shipping.db") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        if expand:
            # Write the SQL query to get the information you want
            db_cursor.execute("""
            SELECT
                s.id,
                s.name,
                s.hauler_id,
                h.id haulerId,
                h.name haulerName,
                h.dock_id
            FROM Ship s
            LEFT JOIN Hauler h
                ON h.id = s.hauler_id
            WHERE s.id = ?
            """, (pk,))
        else:
            # Write the SQL query to get the information without expansion
            db_cursor.execute("""
            SELECT
                s.id,
                s.name,
                s.hauler_id
            FROM Ship s
            WHERE s.id = ?
            """, (pk,))

        query_results = db_cursor.fetchone()

        if not query_results:
            return None  # Return None if ship is not found

        # Convert the sqlite3.Row object to a dictionary
        query_results_dict = dict(query_results)

        # Build the ship dictionary
        hauler_id = query_results_dict.get("haulerId")
        hauler_name = query_results_dict.get("haulerName")
        dock_id = query_results_dict.get("dock_id")

        ship = {
            "id": query_results_dict["id"],
            "name": query_results_dict["name"],
            "hauler_id": query_results_dict["hauler_id"],
            "hauler": {
                "id": hauler_id,
                "name": hauler_name,
                "dock_id": dock_id,
            } if all(val is not None for val in [hauler_id, hauler_name, dock_id]) and expand else None
        }
        # Serialize Python list to JSON encoded string

        serialized_ship = json.dumps(ship)

    return serialized_ship


def create_ship(ship_data):
    with sqlite3.connect("./shipping.db") as conn:
        db_cursor = conn.cursor()

        db_cursor.execute(
            """
            INSERT INTO Ship (name, hauler_id)
            VALUES (?, ?)
            """,
            (ship_data["name"], ship_data["hauler_id"]),
        )

        # Get the last inserted row id to confirm the creation
        new_ship_id = db_cursor.lastrowid

    return new_ship_id
