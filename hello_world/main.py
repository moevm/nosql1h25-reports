import random

from hello_world.neo4jconn import Neo4jConnection

if __name__ == '__main__':
    conn = Neo4jConnection(uri="bolt://localhost:7687", user="neo4j", password="password")

    # clear database
    conn.query('MATCH (n) DETACH DELETE n')

    expected = random.randint(1, 100)

    print(f'Generated value: {expected}')

    # inserting value
    conn.query("CREATE(n: Node {id: %d})" % expected)

    print('Value stored')

    # selecting value
    result = conn.query('MATCH (n: Node) RETURN n.id')[0]["n.id"]

    print(f'Extracted value {result}')

    # deleting value
    conn.query("MATCH (n: Node {id: %d}) DELETE n" % expected)
    print('Value deleted')

    conn.close()

    assert expected == result
