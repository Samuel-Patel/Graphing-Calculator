import sqlite3


def create_database():
    conn = sqlite3.connect("saved_graphs.db")   # creates database

    c = conn.cursor()   # initialises cursor
    # executes query to create Graphs table
    c.execute("""CREATE TABLE IF NOT EXISTS Graphs (
                graph_id TEXT PRIMARY KEY,
                name TEXT,
                type TEXT,
                date_created DATE,
                date_modified DATE
    )""")

    # dates are in format YYYY-MM-DD

    # executes query to create Expressions table and sets up cascade delete restriction
    c.execute("""CREATE TABLE IF NOT EXISTS Expressions (
                expression_id TEXT,
                graph_id TEXT,
                expression_text TEXT,
                FOREIGN KEY(graph_id) REFERENCES Graphs(graph_id) ON DELETE CASCADE          
    )""")

    conn.commit()   # commits the transaction
    conn.close()    # closes the database


def delete_graph(graph_id):
    conn = sqlite3.connect("saved_graphs.db")
    conn.execute("PRAGMA foreign_keys = ON")    # acknowledges foreign keys to enforce referential integrity
    c = conn.cursor()

    # gets rid of graph record with passed id
    c.execute("""DELETE FROM Graphs
                WHERE graph_id = ?
    """, (graph_id,))   # delete query using sqlite to pass in values- must be in a tuple

    conn.commit()
    conn.close()


def add_graph(graph_id, graph_title, g_type, date_created, date_modified):
    conn = sqlite3.connect("saved_graphs.db")
    c = conn.cursor()

    c.execute("""SELECT graph_id FROM Graphs
                WHERE graph_id = ?
    """, (graph_id,))   # query to see if any graphs exist with entered ID

    if len(c.fetchall()) == 0:  # validation to check if the graph already exists
        c.execute("INSERT INTO Graphs VALUES (?, ?, ?, ?, ?)", (graph_id, graph_title, g_type, date_created,
                                                                date_modified))

    conn.commit()
    conn.close()


def add_expressions(expressions):   # expressions = [(expression_id, graph_id, expression_text)...]
    conn = sqlite3.connect("saved_graphs.db")
    conn.execute("PRAGMA foreign_keys = ON")    # prevents referential integrity from being violated
    c = conn.cursor()

    c.executemany("INSERT INTO Expressions VALUES (?, ?, ?)", expressions)  # adds all expressions

    conn.commit()
    conn.close()


def save_as(graph_id, graph_title, g_type, date_created, date_modified, expressions):
    add_graph(graph_id, graph_title, g_type, date_created, date_modified)   # new graph record needs to be created
    add_expressions(expressions)    # new expressions are added


def update_graph(graph_id, graph_title, date_modified):
    conn = sqlite3.connect("saved_graphs.db")
    conn.execute("PRAGMA foreign_keys = ON")    # enforces ref integrity
    c = conn.cursor()
    c.execute("SELECT graph_id FROM Graphs WHERE graph_id = ?", (graph_id,))    # query to check if graph exists

    if len(c.fetchall()) == 0:  # checks if graph exists
        conn.commit()   # closes data base
        conn.close()
        return False

    c.execute("""UPDATE Graphs SET date_modified = ?, name = ?
                WHERE graph_id = ?
    """, (date_modified, graph_title, graph_id))    # query to update graph records with the new data

    conn.commit()
    conn.close()


def update_expressions(graph_id, expressions):
    conn = sqlite3.connect("saved_graphs.db")
    c = conn.cursor()

    # deletes all old expressions in database
    c.execute("""DELETE FROM Expressions
                WHERE graph_id = ?
        """, (graph_id,))

    conn.commit()
    conn.close()

    # adds all the new expressions
    add_expressions(expressions)


def save(graph_id, graph_title, date_modified, expressions):
    if update_graph(graph_id, graph_title, date_modified) is not None:  # updates graph and checks if it exists
        return False
    update_expressions(graph_id, expressions)


def get_graphs(search_item, sort_by, mode):
    conn = sqlite3.connect("saved_graphs.db")
    c = conn.cursor()

    search_item = "%" + search_item + "%"   # checks if search item is a substring of the name
    # gets all graphs where the search item is a substring
    if mode == "all":   # if searching from all modes then the search query does not need extra criteria
        # sort_by needs to added explicitly due to it being a field name, so it would be filtered out by SQLite3
        c.execute(f"""SELECT * FROM Graphs
                    WHERE name LIKE ?
                    ORDER BY {sort_by}
        """, (search_item,))
    else:   # otherwise the type of the graph has to be specified in the query
        c.execute(f"""SELECT * FROM Graphs
                    WHERE name LIKE ? AND type = ?
                    ORDER BY {sort_by}
        """, (search_item, mode))

    results = c.fetchall()  # gets all records that match the search criteria

    conn.commit()
    conn.close()

    return results


def get_expressions(graph_id):
    conn = sqlite3.connect("saved_graphs.db")
    c = conn.cursor()

    # gets the id and the text of all expressions belonging to the graph
    c.execute("""SELECT expression_id, expression_text
                FROM Expressions
                WHERE graph_id = ?
        """, (graph_id,))

    results = c.fetchall()  # returns a list of all expression ids and text
    conn.commit()
    conn.close()

    return results


if __name__ == "__main__":
    print(get_graphs("Test", "name", "2d"))
