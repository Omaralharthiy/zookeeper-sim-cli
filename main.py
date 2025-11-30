class ZNode:
    def __init__(self, name, data="", ephemeral=False, sequential=False):
        self.name = name
        self.data = data
        self.children = {}
        self.ephemeral = ephemeral
        self.sequential = sequential

class ZKTree:
    def __init__(self):
        self.root = ZNode("/")

    def resolve_path(self, path):
        if path == "/":
            return self.root
        parts = [p for p in path.split("/") if p]
        curr = self.root
        for name in parts:
            if name in curr.children:
                curr = curr.children[name]
            else:
                return None
        return curr

    def create(self, path, data="", ephemeral=False, sequential=False):
        parts = [p for p in path.split("/") if p]
        curr = self.root
        for name in parts[:-1]:
            if name not in curr.children:
                curr.children[name] = ZNode(name)
            curr = curr.children[name]
        node_name = parts[-1]
        if sequential:
            node_name = f"{node_name}{len(curr.children)+1}"
        if node_name in curr.children:
            print("[ERR] Node already exists.")
            return
        curr.children[node_name] = ZNode(node_name, data, ephemeral, sequential)
        print(f"[OK] Created {path}")

    def ls(self, path):
        node = self.resolve_path(path)
        if not node:
            print("[ERR] Path not found.")
            return
        if not node.children:
            print("[INFO] No children.")
            return
        for child in node.children.values():
            print(child.name)

    def get(self, path):
        node = self.resolve_path(path)
        if not node:
            print("[ERR] Path not found.")
            return
        print(f"[DATA] {node.data}")

    def set(self, path, data):
        node = self.resolve_path(path)
        if not node:
            print("[ERR] Path not found.")
            return
        node.data = data
        print(f"[OK] Updated {path}")

    def delete(self, path):
        if path == "/":
            print("[ERR] Cannot delete root.")
            return
        parts = [p for p in path.split("/") if p]
        curr = self.root
        for name in parts[:-1]:
            if name not in curr.children:
                print("[ERR] Path not found.")
                return
            curr = curr.children[name]
        node_name = parts[-1]
        if node_name in curr.children:
            del curr.children[node_name]
            print(f"[OK] Deleted {path}")
        else:
            print("[ERR] Path not found.")

    def print_tree(self, node=None, prefix=""):
        if node is None:
            node = self.root
            print("/")
        for name, child in node.children.items():
            flags = []
            if child.ephemeral: flags.append("E")
            if child.sequential: flags.append("S")
            flag_str = f" ({''.join(flags)})" if flags else ""
            data_str = f' "{child.data}"' if child.data else ""
            print(f"{prefix}|- {name}{flag_str}{data_str}")
            self.print_tree(child, prefix + "   ")

def main():
    tree = ZKTree()
    print("ZooKeeper Simulation CLI (Python)")
    print("Commands: create, ls, get, set, delete, tree, exit")
    print("create PATH [DATA] [-e] [-s]")

    while True:
        try:
            line = input("> ").strip()
            if not line:
                continue
            tokens = line.split()
            cmd = tokens[0]

            if cmd == "create":
                if len(tokens) < 2:
                    print("[ERR] Usage: create /path [data] [-e] [-s]")
                    continue
                path = tokens[1]
                # collect flags and data safely
                flags = {t for t in tokens[2:] if t.startswith("-")}
                data_parts = [t for t in tokens[2:] if not t.startswith("-")]
                data = " ".join(data_parts) if data_parts else ""
                ephemeral = "-e" in flags
                sequential = "-s" in flags
                tree.create(path, data, ephemeral, sequential)

            elif cmd == "ls":
                path = tokens[1] if len(tokens) > 1 else "/"
                tree.ls(path)

            elif cmd == "get":
                if len(tokens) < 2:
                    print("[ERR] Usage: get /path")
                    continue
                path = tokens[1]
                tree.get(path)

            elif cmd == "set":
                if len(tokens) < 3:
                    print("[ERR] Usage: set /path data")
                    continue
                path = tokens[1]
                data = " ".join(tokens[2:])
                tree.set(path, data)

            elif cmd == "delete":
                if len(tokens) < 2:
                    print("[ERR] Usage: delete /path")
                    continue
                path = tokens[1]
                tree.delete(path)

            elif cmd == "tree":
                tree.print_tree()

            elif cmd == "exit":
                print("[INFO] Bye.")
                break

            else:
                print("[ERR] Unknown command.")

        except KeyboardInterrupt:
            print("\n[INFO] Interrupted. Type 'exit' to quit.")
        except Exception as e:
            print(f"[ERR] {e}")

if __name__ == "__main__":
    main()
