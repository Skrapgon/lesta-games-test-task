from collections import Counter
from dataclasses import dataclass, field
import heapq

@dataclass(order=True)
class Node:
    count: int
    char: str = field(default=None, compare=False)
    code: str = field(default='', compare=False)
    left: 'Node' = field(default=None, compare=False)
    right: 'Node' = field(default=None, compare=False)
       
def build_tree(text: str) -> Node:
    char_count = Counter(text)
    node_list = [Node(char=char, count=count) for char, count in char_count.items()]
    heapq.heapify(node_list)

    while len(node_list) > 1:
        right = heapq.heappop(node_list)
        left = heapq.heappop(node_list)
        node = Node(count=right.count+left.count, left=left, right=right)
        right.code = '1'
        left.code = '0'
        heapq.heappush(node_list, node)

    return node_list[0]

def assign_codes(node: Node) -> dict[str, str]:
    codebook = {}
    node_list = [node]
    while node_list:
        node = node_list.pop()
        if not node.char:
            node.left.code = node.code + node.left.code
            node.right.code = node.code + node.right.code
            node_list.append(node.left)
            node_list.append(node.right)
        else:
            codebook[node.char] = node.code
    return codebook

def get_huffman_code(text: str) -> dict[str, str]:
    if not text:
        return {}
    root = build_tree(text)
    return assign_codes(root)
    
def encode(text: str, codebook: dict[str, str]) -> str:
    return ''.join(codebook[char] for char in text)