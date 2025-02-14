import random

from hello_world.neo4jconn import Neo4jConnection


# Function to insert a value into the database
def insert_value(conn, value):
    conn.query("CREATE (n: Node {id: %d})" % value)
    print(f'Value {value} stored')


# Function to select a value from the database
def select_value(conn):
    result = conn.query('MATCH (n: Node) RETURN n.id')[0]["n.id"]
    print(f'Extracted value {result}')
    return result


# Function to delete a value from the database
def delete_value(conn, value):
    conn.query("MATCH (n: Node {id: %d}) DELETE n" % value)
    print(f'Value {value} deleted')


if __name__ == '__main__':
    conn = Neo4jConnection(uri="bolt://localhost:7687", user="neo4j", password="password")

    # Clear database
    conn.query('MATCH (n) DETACH DELETE n')

    # Generate a random value to insert
    expected = random.randint(1, 100)
    print(f'Generated value: {expected}')

    # inserting value
    insert_value(conn, expected)
    # selecting value
    result = select_value(conn)

    # Generate a random value for deletion
    deleting = random.randint(1, 100)
    # inserting value
    insert_value(conn, deleting)

    # deleting value
    delete_value(conn, deleting)

    conn.close()

    assert expected == result
