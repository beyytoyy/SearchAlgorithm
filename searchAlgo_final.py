import tkinter as tk 
from tkinter import simpledialog, messagebox, ttk  

class Graph:
    def __init__(self):
        self.vertices = {}

    def add_node(self, vertex):
        if vertex not in self.vertices:
            self.vertices[vertex] = []

    def add_edge(self, vertex1, vertex2, directed=False):
        if vertex1 in self.vertices and vertex2 in self.vertices:
            if directed:
                self.vertices[vertex1].append(vertex2)
            else:
                self.vertices[vertex1].append(vertex2)
                self.vertices[vertex2].append(vertex1)

    def rename_vertex(self, old_name, new_name):
        if old_name in self.vertices and new_name not in self.vertices:
            self.vertices[new_name] = self.vertices.pop(old_name)

            for vertex, edges in self.vertices.items():
                self.vertices[vertex] = [new_name if edge == old_name else edge for edge in edges]

        elif new_name in self.vertices:
            print(f"Error: Node '{new_name}' already exists.")
        else: print(f"Error: Node '{old_name}' not found.")

    def dfs(self, start, visited=None, end=None):
        if visited is None:
            visited = set()
        if end is None:
            end = []

        if start not in visited:
            visited.add(start)
            end.append(start)
            for neighbor in self.vertices[start]:
                self.dfs(neighbor, visited, end)

        return end
    
    def bfs(self, start):
        if start not in self.vertices:
            print(start)
            return []
        
        visited = set()
        queue = [start]
        end = []

        while queue:
            vertex = queue.pop(0)
            if vertex not in visited:
                visited.add(vertex)
                end.append(vertex)
                queue.extend([n for n in self.vertices[vertex] if n not in visited])

        return end
    
    def iddfs(self, start):
        depth_end = []
        max_depth = len(self.vertices)

        for depth_limit in range(max_depth):
            visited = set()
            end = [] 

            self.iddfs_util(start, depth_limit, visited, end)

            if not end or (
                    depth_end and end == depth_end[-1]):
                break
            
            depth_end.append(end)

        return depth_end
    
    def iddfs_util(self, vertex, depth_limit, visited, end, current_depth=0):
        if current_depth > depth_limit or vertex in visited:
            return
        
        visited.add(vertex)
        end.append(vertex)

        for neighbor in self.vertices[vertex]:
            if neighbor not in visited:
                self.iddfs_util(neighbor, depth_limit, visited, end, current_depth + 1)

class GraphGUI:
    def __init__(self, master):
        self.master = master
        self.graph = Graph()
        self.nodes = {}  # Maps canvas node ID to node name
        self.node_menu = tk.Menu(master, tearoff=0)
        self.node_menu.add_command(label="Delete Node", command=self.delete_selected_node)
        self.node_positions = {}  # Maps canvas node ID to position (x, y)
        self.edges = {}  # Maps canvas edge ID to (node1_id, node2_id)
        self.node_edges = {}  # Maps canvas node ID to a list of connected edge IDs
        self.node_labels = {}
        self.selected_nodes = []
        self.drag_data = {"x": 0, "y": 0, "item": None}
        self.first_node = None  # Track the first node added
        self.last_node = None

        master.title("Graph GUI")

        self.canvas = tk.Canvas(master, width=600, height=400, bg='white')
        self.canvas.pack(expand=tk.YES, fill=tk.BOTH, side=tk.RIGHT)
        self.canvas.bind("<Button-1>", self.on_node_press)  # Changed to <Button-1>
        self.canvas.bind("<ButtonRelease-1>", self.on_node_release)
        self.canvas.bind("<B1-Motion>", self.on_node_move)
        self.canvas.bind("<Button-3>", self.delete_node)

        self.controls_frame = tk.Frame(master)
        self.controls_frame.pack(side=tk.TOP, anchor=tk.W, padx=10, pady=10)

        self.controls_label = tk.Label(self.controls_frame, text="Options:")
        self.controls_label.pack(anchor=tk.W)

        self._reset_button = tk.Button(self.controls_frame, text="Reset", command=self.reset)
        self._reset_button.pack(anchor=tk.W)

        self.add_edge_button = tk.Button(self.controls_frame, text="Add Edge", command=self.add_edge)
        self.add_edge_button.pack(anchor=tk.W)

        self.rename_node_button = tk.Button(self.controls_frame, text="Rename Node", command=self.rename_node)
        self.rename_node_button.pack(anchor=tk.W,)

        # Algorithm Selection
        algorithm_frame = tk.Frame(master)
        algorithm_frame.pack(side=tk.TOP, anchor=tk.W, padx=10, pady=10)

        algorithm_label = tk.Label(algorithm_frame, text="Algorithm Selection:")
        algorithm_label.pack()

        self.algorithm_var = tk.StringVar(value="DFS")

        dfs_button = tk.Radiobutton(algorithm_frame, text="DFS", variable=self.algorithm_var, value="DFS")
        dfs_button.pack(anchor=tk.W)

        bfs_button = tk.Radiobutton(algorithm_frame, text="BFS", variable=self.algorithm_var, value="BFS")
        bfs_button.pack(anchor=tk.W)

        iddfs_button = tk.Radiobutton(algorithm_frame, text="IDDFS", variable=self.algorithm_var, value="IDDFS")
        iddfs_button.pack(anchor=tk.W)
        
        self.start_search_button = tk.Button(algorithm_frame, text="Search", command=self.start_search)
        self.start_search_button.pack(anchor=tk.W, pady=5)

        # Output Box 
        self.output_frame = tk.Frame(master)
        self.output_frame.pack(side=tk.BOTTOM, padx=10, pady=10)

        self.output_label = tk.Label(self.output_frame, text="Output:")
        self.output_label.pack(anchor=tk.W)

        self.output_text = tk.Text(self.output_frame, height=20, width=70)
        self.output_text.pack()

    def canvas_click(self, event):
        print("Canvas clicked at:", event.x, event.y)  # Debugging line
        closest_node = self.get_closest_node(event.x, event.y)
        if closest_node:
            self.select_node(closest_node)
        else:
            self.create_node(event.x, event.y)

    def get_closest_node(self, x, y, threshold=15):
        closest_items = self.canvas.find_overlapping(x - threshold, y - threshold, x + threshold, y + threshold)
        for item in closest_items:
            if "node" in self.canvas.gettags(item):
                return item
        return None

    def select_node(self, node_id):
        if node_id in self.selected_nodes:
            self.selected_nodes.remove(node_id)
            self.canvas.itemconfig(node_id, fill="#ffff00")
        else:
            if len(self.selected_nodes) < 2:
                self.selected_nodes.append(node_id)
                self.canvas.itemconfig(node_id, fill="#aaaa16")

    def on_node_press(self, event):
        # Adjusted to work with 'find_overlapping' method
        closest_node = self.get_closest_node(event.x, event.y)
        if closest_node:
            self.drag_data["item"] = closest_node
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y
            self.select_node(closest_node)
        else:
            self.create_node(event.x, event.y)

    def on_node_release(self, event):
        # Reset the drag information
        self.drag_data["item"] = None
        self.drag_data["x"] = 0
        self.drag_data["y"] = 0

    def on_node_move(self, event):
        # Move both the node and its label
        if self.drag_data["item"] is not None:
            delta_x = event.x - self.drag_data["x"]
            delta_y = event.y - self.drag_data["y"] 
            node_id = self.drag_data["item"]
            label_id = self.node_labels[node_id]  # Assumes you have a dictionary mapping nodes to their labels

            self.canvas.move(node_id, delta_x, delta_y)
            self.canvas.move(label_id, delta_x, delta_y)  # Move the label as well

            # Update node position and drag_data
            self.node_positions[node_id] = (event.x, event.y)
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y

            # Move connected edges
            for edge_id in self.node_edges.get(node_id, []):
                if edge_id in self.edges:  # Check if the edge ID is valid
                    node1_id, node2_id = self.edges[edge_id]
                    x1, y1 = self.node_positions[node1_id]
                    x2, y2 = self.node_positions[node2_id]
                    self.canvas.coords(edge_id, x1, y1, x2, y2)
            # Update the drag_data for the next motion event
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y

    def reset(self):
        # Clear the canvas
        self.canvas.delete("all")

        # Reset the data structures
        self.nodes = {}
        self.node_positions = {}
        self.edges = {}
        self.node_edges = {}
        self.node_labels = {}
        self.selected_nodes = []
        self.first_node = None
        self.last_node = None

        # Reset the Graph instance
        self.graph = Graph()

        print("Nodes have been reset")

    def add_edge(self):
        if len(self.selected_nodes) == 2:
            # Retrieve the actual node names using the node IDs
            node1_id, node2_id = self.selected_nodes
            node1_name = self.nodes[node1_id]
            node2_name = self.nodes[node2_id]

            edge_type = simpledialog.askstring("Edge Type", "Enter Edge Type ('d' = directed or 'ud' = undirected):", parent=self.master)

            if edge_type and edge_type.lower() in ['d', 'ud']:
                
                # Create the edge in the graph's adjacency list
                directed = edge_type == 'd'
                self.graph.add_edge(node1_name, node2_name, directed=directed)

                # Get the positions of the nodes to draw the visual edge
                x1, y1 = self.node_positions[node1_id]
                x2, y2 = self.node_positions[node2_id]
                edge_id = self.canvas.create_line(x1, y1, x2, y2, arrow=tk.LAST if directed else None)
                self.edges[edge_id] = (node1_id, node2_id)
                self.node_edges.setdefault(node1_id, []).append(edge_id)
                self.node_edges.setdefault(node2_id, []).append(edge_id) 
                self.canvas.itemconfig(node1_id, fill="#ffff00")
                self.canvas.itemconfig(node2_id, fill="#ffff00")
                self.selected_nodes = []

            print("Edge added between:", node1_name, "and", node2_name)  # Print confirmation of edge addition

    def create_node(self, x, y):
        if not self.nodes:
            node_name = 'A'
        else:
            next_node_number = len(self.nodes) + 1
            node_name = chr(ord('A') + next_node_number - 1)

        node_id = self.canvas.create_oval(x - 20, y - 20, x + 20, y + 20, fill="#ffff00", tags=("node",))
        label_id = self.canvas.create_text(x, y, text=node_name, tags=("node",))

        # Store the node and its label's ID
        self.nodes[node_id] = node_name
        self.node_labels[node_id] = label_id
        self.node_positions[node_id] = (x, y)
        self.graph.add_node(node_name)

        # If it's the first node added, store it as the start node
        if self.first_node is None:
            self.first_node = node_name
        else:
            self.last_node = node_name

    def delete_node(self, event):
        if self.selected_nodes:
            # Display the context menu at the mouse position
            self.node_menu.post(event.x_root, event.y_root)

    def delete_selected_node(self):
        if self.selected_nodes:
            node_id = self.selected_nodes[0]
            node_name = self.nodes[node_id]
            self.canvas.delete(node_id)
            del self.graph.vertices[node_name]
            del self.nodes[node_id]
            del self.node_positions[node_id]
            label_id = self.node_labels.pop(node_id, None)
            if label_id is not None:
                self.canvas.delete(label_id)
            edges = self.node_edges.pop(node_id, [])
            for edge_id in edges:
                if edge_id in self.edges:
                    del self.edges[edge_id]

            self.selected_nodes = []

            print("Node", node_name, "deleted")

    def rename_node(self):
        if self.selected_nodes:
            node_id = self.selected_nodes[0]
            old_name = self.nodes[node_id]
            new_name = simpledialog.askstring("Rename Node", "Enter new name:", parent=self.master)
            if new_name:
                if old_name == self.first_node:
                    self.first_node = new_name
                elif old_name == self.last_node:
                    self.last_node = new_name
                self.canvas.itemconfig(self.node_labels[node_id], text=new_name)
                self.graph.rename_vertex(old_name, new_name)
                self.nodes[node_id] = new_name

    def start_search(self):
        # Automatically start traversal from the first node added
        if self.first_node:
            traversal_method = self.algorithm_var.get()

            if traversal_method == "IDDFS":
                all_depth_traversal_order = self.graph.iddfs(self.first_node)
                result = ""
                for depth, nodes_at_depth in enumerate(all_depth_traversal_order):
                    if nodes_at_depth:  # Make sure there's something to display for this depth
                        result += f"Lvl {depth}: {' -> '.join(nodes_at_depth)}\n"
                self.output_text.delete('1.0', tk.END)  # Clear previous content
                self.output_text.insert(tk.END, result.rstrip('\n'))  # Display result
            else:
                traversal_order = []
                if traversal_method == "BFS":
                    traversal_order = self.graph.bfs(self.first_node)
                elif traversal_method == "DFS":
                    traversal_order = self.graph.dfs(self.first_node)
                if traversal_order:
                    self.output_text.delete('1.0', tk.END) #clear previous content
                    self.output_text.insert(tk.END, f"Path: {' -> '.join(traversal_order)}")
                else:
                    self.output_text.delete('1.0', tk.END)
                    self.output_text.insert(tk.END, "Traversal yielded no results.")
        else:
            self.output_text.delete('1.0', tk.END)  # Clear previous content
            self.output_text.insert(tk.END, "No nodes have been added yet.")

    


root = tk.Tk()
gui = GraphGUI(root)
root.mainloop()

        