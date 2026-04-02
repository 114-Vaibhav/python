from collections import deque

class Node:
    def __init__(self, name, label, properties):
        self.name = name
        self.label = label
        self.properties = properties
        # print("Node created: ", label, name, properties)

class Edge:
    def __init__(self, source, target, label, properties):
        self.source = source
        self.target = target
        self.label = label
        self.properties = properties
        # print(f"Edge created: {source.name} - {label}-> {target.name}")

class Graph:
    def __init__(self, nodes=None, edges=None):
        self.nodes = nodes or []
        self.edges = edges or []
        self.adjacency_list = self._create_adjacency_list()
        self.hash_index = {}
        self.property_index = {}

        for node in self.nodes:
            self.hash_index[node.name] = node
            self.adjacency_list.setdefault(node.name, [])
            for key, value in node.properties.items():
                self.property_index.setdefault(key, {}).setdefault(value, []).append(node.name)

    def add_node(self, node):
        if node.name in self.hash_index:
            raise ValueError(f"Node {node.name} already exists")
        self.nodes.append(node)
        self.adjacency_list[node.name] = []
        self.hash_index[node.name] = node
        print(node.properties)
        for key, value in node.properties.items():
            if key not in self.property_index:
                self.property_index[key] = {}
            if value not in self.property_index[key]:
                self.property_index[key][value] = []
            self.property_index[key][value].append(node.name)
        print(f"Node added: {node.name}")

    def add_edge(self, edge):
        if edge.source.name not in self.hash_index or edge.target.name not in self.hash_index:
            raise ValueError("Both nodes must exist in graph")
        self.edges.append(edge)
        source = edge.source.name
        target = edge.target.name
        if source not in self.adjacency_list:
            self.adjacency_list[source] = []
        self.adjacency_list[source].append((target, edge))
        print(f"Edge added: {source} -> {target}")

    def _create_adjacency_list(self):
        adjacency_list = {}
        for edge in self.edges:
            source = edge.source.name
            target = edge.target.name
            if source not in adjacency_list:
                adjacency_list[source] = []
            adjacency_list[source].append((target, edge))
        return adjacency_list
    
    def search_by_property(self, key, value):
         return self.property_index.get(key, {}).get(value, [])
    
    def get_node(self, name):
        if name not in self.hash_index:
            return None
        return self.hash_index[name]

    def print_adj(self):
        for node in self.nodes:
            print(f"{node.name}: {self.adjacency_list[node.name]}")

    def get_neighbors(self, name):
        return self.adjacency_list.get(name, [])

    def shortest_path(self, start, end):
        visited = set()
        queue = deque([(start, [start])])

        while queue:
            vertex, path = queue.popleft()

            if vertex == end:
                print("Path: ", end="")
                for p in path:
                    print(p,end=" ")
                print("\nLength: ", (len(path)-1)/2)
                print("Total Weight: ", (len(path)-1)/2)
                return path

            if vertex not in visited:
                visited.add(vertex)
                for neighbor, edge in self.adjacency_list.get(vertex, []):
                    queue.append((neighbor, path + [" - " + edge.label+ " ->"] + [neighbor]))

        return None

   

# def run_tests():
#     print("\n===== START TESTS =====\n")

#     # Create nodes
#     alice = Node("alice", "Person", {"age": 25, "city": "Lucknow"})
#     bob = Node("bob", "Person", {"age": 30, "city": "Delhi"})
#     charlie = Node("charlie", "Person", {"age": 35, "city": "Delhi"})
#     company = Node("google", "Company", {"industry": "Tech"})

#     # Create graph
#     graph = Graph([alice, bob, charlie, company], [])

#     # Add edges 
#     graph.add_edge(Edge(alice, bob, "KNOWS", {"since": 2020}))
#     graph.add_edge(Edge(bob, charlie, "KNOWS", {"since": 2018}))
#     graph.add_edge(Edge(charlie, company, "WORKS_AT", {"role": "Engineer"}))


#     print("\n--- Adjacency List ---")
#     graph.print_adj()

    
#     print("\n--- Get Node ---")
#     print(graph.get_node("alice"))
#     print(graph.get_node("unknown"))  


#     print("\n--- Property Search ---")
#     print("City = Delhi:", graph.search_by_property("city", "Delhi"))
#     print("Age = 25:", graph.search_by_property("age", 25))
#     print("Invalid:", graph.search_by_property("city", "Mumbai"))

   
#     print("\n--- Neighbors ---")
#     print("Alice neighbors:", graph.get_neighbors("alice"))
#     print("Bob neighbors:", graph.get_neighbors("bob"))
#     print("Unknown neighbors:", graph.get_neighbors("unknown"))


#     print("\n--- Shortest Path ---")
#     graph.shortest_path("alice", "google")   
#     graph.shortest_path("alice", "charlie")  
#     graph.shortest_path("google", "alice")  


#     print("\n--- Duplicate Node Test ---")
#     try:
#         graph.add_node(Node("alice", "Person", {"age": 40}))
#     except ValueError as e:
#         print("Caught:", e)

    
#     print("\n--- Invalid Edge Test ---")
#     fake = Node("fake", "Person", {})
#     try:
#         graph.add_edge(Edge(fake, alice, "KNOWS", {}))
#     except ValueError as e:
#         print("Caught:", e)

    
#     print("\n--- Add Node + Index Update ---")
#     dave = Node("dave", "Person", {"age": 28, "city": "Delhi"})
#     graph.add_node(dave)

#     print("City = Delhi after adding dave:",
#           graph.search_by_property("city", "Delhi"))

#     print("\n===== END TESTS =====\n")



# run_tests()