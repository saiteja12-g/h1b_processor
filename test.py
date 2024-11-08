class TreeNode:
    def __init__(self, val, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right
    
    def __str__(self):
        return str(self.val)

def fn(node):
    # Pre Order Traversal: Root -> Left -> Right
    if not node:
        return

    print(node)  # Process the root node
    fn(node.left)  # Recur on the left subtree
    fn(node.right)  # Recur on the right subtree

# Constructing the tree
node = TreeNode(1)
B = TreeNode(2)
C = TreeNode(3)
D = TreeNode(4)
E = TreeNode(5)
F = TreeNode(10)

node.left = B
node.right = C
B.left = D
B.right = E
C.left = F

# Run pre-order traversal
fn(node)
