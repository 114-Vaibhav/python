from Graph import Graph, Node, Edge
import ast
import re
import os, json
from datetime import datetime

file_path = "WAL.json"
WAL =[]
if os.path.exists(file_path):
    with open(file_path, "r") as f:
        WAL = json.load(f)
        

graph = Graph()



def store_command(command):
    timestamp = datetime.now().isoformat()  # ISO 8601 format
    WAL.append({
        "timestamp": timestamp,
        "command": command
    })
    save_wal()

def save_wal():
    with open(file_path, "w") as f:
        json.dump(WAL, f, indent=4)

def stats():
    print(f"Number of nodes: {len(graph.nodes)}")
    print(f"Number of edges: {len(graph.edges)}")
    print(f"Indexs of nodes: {len(graph.hash_index)} ")
    for key in graph.property_index:
        print(f"Indexs of {key}: {len(graph.property_index[key])}")
    print(f"WAL: ", len(WAL))
    if WAL:
        print("Last Disk Snapshot:", WAL[-1]['timestamp'])
    else:
        print("No WAL entries")

def commandParser(command,recovery=False):
    if "CREATE NODE" in command:
        inner = command[command.find('(')+1 : command.rfind(')')]
        before_props, prop = inner.split('{', 1)
        prop = '{' + prop
        name, label = before_props.strip().split(':')
        prop_fixed = re.sub(r'(\w+)\s*:', r'"\1":', prop)
        properties = ast.literal_eval(prop_fixed)
        # print("properties: ", properties)
        # print("prop: ", prop)
        # print("prop: ", prop_fixed)
        node = Node(name.strip(), label.strip(), properties=properties)
        if not recovery:
            store_command(command)
        graph.add_node(node)
   
    elif "CREATE EDGE" in command:
        source_name = command[command.find('(')+1 : command.find(')')]
        dest_name = command[command.rfind('(')+1 : command.rfind(')')]
        label = command[command.find(':')+1 : command.find('{')].strip()
        prop = command[command.find('{')+1 : command.rfind('}')].strip()
        prop = '{' + prop + '}'
        prop_fixed = re.sub(r'(\w+)\s*:', r'"\1":', prop)
        properties = ast.literal_eval(prop_fixed)
        # print("source: ", source, len(source))
        # print("dest: ", dest, len(dest))
        # print("label: ", label, len(label))
        # print("prop: ", prop, len(prop))
        # print("prop_fixed: ", prop_fixed, len(prop_fixed))
        # print("properties: ", properties, len(properties))
        source = graph.get_node(source_name)
        dest = graph.get_node(dest_name)
        if source is None or dest is None:
            raise ValueError("Both nodes must exist in graph")
        edge = Edge(source, dest, label, properties=properties)
        if not recovery:
            store_command(command)


        graph.add_edge(edge)

    elif "MATCH" in command:
        pattern = command[command.find("MATCH") + 5 : command.find("WHERE") if "WHERE" in command else command.find("RETURN")].strip()

        where_clause = None
        if "WHERE" in command:
            where_clause = command[command.find("WHERE") + 5 : command.find("RETURN")].strip()

        return_clause = command[command.find("RETURN") + 6 :].strip()
        node_labels = re.findall(r'\((\w*):(\w+)\)', pattern)
        edge_labels = re.findall(r'\[:(\w+)\]', pattern)
        start_var, start_label = node_labels[0]

        start_nodes = [
            node for node in graph.nodes
            if node.label == start_label
        ]

        results = []

        for start in start_nodes:
            for neighbor1, edge1 in graph.get_neighbors(start.name):
                if edge1.label != edge_labels[0]:
                    continue

                for neighbor2, edge2 in graph.get_neighbors(neighbor1):
                    if edge2.label != edge_labels[1]:
                        continue

                    end_node = graph.get_node(neighbor2)

                    if end_node.label == node_labels[-1][1]:
                        results.append({
                            start_var: start,
                            node_labels[-1][0]: end_node
                        })
        if where_clause:
            key, value = where_clause.split("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")

            var, prop = key.split(".")

            filtered = []
            for res in results:
                node = res[var]
                if str(node.properties.get(prop)) == value:
                    filtered.append(res)

            results = filtered

        fields = [f.strip() for f in return_clause.split(",")]

        print("-" * 30)
        for res in results:
            row = []
            for field in fields:
                var, prop = field.split(".")
                row.append(str(res[var].properties.get(prop)))
            print(" | ".join(row))
        print("-" * 30)
        print(f"{len(results)} rows returned")

    elif "SHORTEST PATH" in command:
        src_name = command[command.find('(')+1 : command.find(')')]
        dest_name = command[command.rfind('(')+1 : command.rfind(')')]
        src = graph.get_node(src_name)
        dest = graph.get_node(dest_name)
        if src is None or dest is None:
            raise ValueError("Both nodes must exist in graph")
        graph.shortest_path(src_name, dest_name)

    elif "STATS" in command:
        stats()
        
    else:
        raise ValueError("Invalid command")


def recover():
    print("Recovering from WAL...")
    for entry in WAL:
        commandParser(entry["command"], recovery=True)


recover()


print("=== Graph DB Shell ===")

while True:
    try:
        cmd = input("graphdb> ")
        if cmd.lower() in ["exit", "quit"]:
            break
        commandParser(cmd)
    except Exception as e:
        print("Error:", e)


# try:
#     commandParser("CREATE NODE (alice:Person {age: 25, city: 'Lucknow'})")
#     commandParser("CREATE NODE (bob:Person {age: 30, city: 'Delhi'})")
#     commandParser("CREATE NODE (Presidio:Company {Industry: 'IT'})")
#     # commandParser('''CREATE EDGE (bob)-[:WORKS_AT {role: "Engineer"}]>(acme)''')
#     commandParser("STATS")
# except Exception as e:
#     print(e)

