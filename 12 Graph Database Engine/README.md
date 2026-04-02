# Graph Database Engine

A small Python-based graph database prototype with:

- in-memory node and edge storage
- hash and property indexing for nodes
- a simple query shell
- write-ahead logging (WAL) for recovery after restart
- breadth-first shortest path search

The project is designed as a learning-friendly graph engine rather than a full production database.

## Features

- Create labeled nodes with properties
- Create directed, labeled edges with properties
- Query simple multi-hop patterns using `MATCH ... WHERE ... RETURN`
- Find shortest paths between two nodes
- Inspect graph statistics and index counts
- Recover previously executed write commands from `WAL.json`

## Project Structure

- [QueryEngine.py]: interactive shell, command parsing, WAL handling, recovery
- [Graph.py]: `Node`, `Edge`, `Graph` classes, indexes, BFS shortest path, built-in test routine
- [commands.txt]: sample commands for populating and querying the graph
- [WAL.json]: persisted write-ahead log used during recovery
- [Output.txt]: captured sample session output

## Requirements

- Python 3.x
- No external dependencies

## How To Run

Start the query shell:

```powershell
python QueryEngine.py
```

You will see:

```text
=== Graph DB Shell ===
graphdb>
```

Type commands one at a time and use `exit` or `quit` to leave the shell.

## Command Syntax

### 1. Create a node

```text
CREATE NODE (alice:Person {name: "Alice", age: 30, city: "Delhi"})
```

Format:

```text
CREATE NODE (<node_id>:<Label> {key: value, key: value})
```

### 2. Create an edge

```text
CREATE EDGE (alice)-[:FRIENDS_WITH {since: 2020}]->(bob)
```

Format:

```text
CREATE EDGE (<source_id>)-[:<EDGE_LABEL> {key: value}]->(<target_id>)
```

Both source and target nodes must already exist.

### 3. Match a 2-hop pattern

```text
MATCH (p:Person)-[:FRIENDS_WITH]->()-[:WORKS_AT]->(c:Company) RETURN p.name, c.name
```

With filtering:

```text
MATCH (p:Person)-[:FRIENDS_WITH]->()-[:WORKS_AT]->(c:Company) WHERE c.name = "Acme Corp" RETURN p.name, c.name
```

This query engine currently supports:

- a start labeled node
- exactly two edge hops in the pattern
- an optional `WHERE` equality filter
- `RETURN` fields in `variable.property` form

### 4. Shortest path

```text
SHORTEST PATH (alice)->(google)
```

This uses breadth-first search over the directed graph.

### 5. Stats

```text
STATS
```

This prints:

- number of nodes
- number of edges
- hash index size
- property index sizes
- WAL entry count
- last WAL timestamp

## Example Session

```text
CREATE NODE (alice:Person {name: "Alice", age: 30, city: "Delhi"})
CREATE NODE (bob:Person {name: "Bob", age: 28, city: "Delhi"})
CREATE NODE (acme:Company {name: "Acme Corp", industry: "Tech"})
CREATE EDGE (alice)-[:FRIENDS_WITH {since: 2020}]->(bob)
CREATE EDGE (bob)-[:WORKS_AT {role: "Engineer"}]->(acme)
MATCH (p:Person)-[:FRIENDS_WITH]->()-[:WORKS_AT]->(c:Company) RETURN p.name, c.name
SHORTEST PATH (alice)->(acme)
STATS
```

## Write-Ahead Logging And Recovery

Every successful write command is appended to [WAL.json]:

- `CREATE NODE`
- `CREATE EDGE`

When [QueryEngine.py] starts, it:

1. loads the WAL from disk
2. replays each stored command
3. rebuilds the in-memory graph state

This allows the graph to recover after the terminal is closed.

## Internal Design

### Node storage

Each node stores:

- `name`
- `label`
- `properties`

### Edge storage

Each edge stores:

- `source`
- `target`
- `label`
- `properties`

### Indexes

The graph maintains:

- a hash index from node name to node object
- a property index from property key/value to matching node names
- an adjacency list for outgoing edges

## Sample Data

You can use the commands in [commands.txt] to populate the graph with people, companies, friendship edges, and employment edges.

## Notes And Current Limitations

- The query parser is string-based and supports a limited syntax.
- `MATCH` currently assumes a fixed 2-hop pattern.
- Shortest path works on directed edges only.
- WAL recovery replays writes, but there is no snapshot or checkpoint system yet.
- There is no delete or update command yet.
- [Graph.py] runs a built-in `run_tests()` routine when executed or imported directly in its current form.
- Blank lines entered in the shell are treated as invalid commands.
