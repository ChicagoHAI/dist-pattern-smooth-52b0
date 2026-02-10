# This experiment validates the convergence rate and α-smoothness conditions for distributed pattern mining by:
1. Generating synthetic temporal patterns
2. Implementing utility functions with known α-smoothness
3. Simulating distributed mining on different graph topologies
4. Measuring empirical convergence rates
# Verified: No (simulated)

import numpy as np
from typing import List, Tuple
import random

class Node:
    def __init__(self, id: int, neighbors: List[int], patterns: List[str]):
        self.id = id
        self.neighbors = neighbors
        self.patterns = patterns
        self.best_pattern = None
        self.best_utility = -float('inf')

def hamming_distance(p1: str, p2: str) -> int:
    return sum(c1 != c2 for c1, c2 in zip(p1, p2))

def alpha_smooth_utility(pattern: str, alpha: float = 1.0) -> float:
    # Example α-smooth utility function
    return alpha * sum(c == '1' for c in pattern)

def generate_random_pattern(length: int) -> str:
    return ''.join(random.choice(['0', '1']) for _ in range(length))

def create_graph_topology(n: int, topology: str) -> List[List[int]]:
    if topology == "ring":
        return [[(i-1)%n, (i+1)%n] for i in range(n)]
    elif topology == "complete":
        return [[j for j in range(n) if j != i] for i in range(n)]
    else:  # random
        edges = [[i] for i in range(n)]
        for i in range(n):
            for j in range(i+1, n):
                if random.random() < 0.3:
                    edges[i].append(j)
                    edges[j].append(i)
        return edges

def distributed_mining(nodes: List[Node], max_rounds: int, epsilon: float) -> Tuple[int, float]:
    prev_global_best = -float('inf')
    
    for round in range(max_rounds):
        # Local computation
        for node in nodes:
            for pattern in node.patterns:
                utility = alpha_smooth_utility(pattern)
                if utility > node.best_utility:
                    node.best_utility = utility
                    node.best_pattern = pattern
        
        # Communication
        for node in nodes:
            for neighbor_id in node.neighbors:
                if nodes[neighbor_id].best_utility > node.best_utility:
                    node.best_utility = nodes[neighbor_id].best_utility
                    node.best_pattern = nodes[neighbor_id].best_pattern
        
        # Check convergence
        global_best = max(node.best_utility for node in nodes)
        if abs(global_best - prev_global_best) < epsilon:
            return round, global_best
        prev_global_best = global_best
    
    return max_rounds, prev_global_best

# Experiment parameters
n_nodes = 10
pattern_length = 8
n_patterns_per_node = 5
epsilon = 1e-6
max_rounds = 100

# Run experiments for different topologies
topologies = ["ring", "complete", "random"]
print("=== Convergence Results ===")

for topology in topologies:
    # Initialize network
    edges = create_graph_topology(n_nodes, topology)
    nodes = []
    for i in range(n_nodes):
        patterns = [generate_random_pattern(pattern_length) for _ in range(n_patterns_per_node)]
        nodes.append(Node(i, edges[i], patterns))
    
    # Run distributed mining
    rounds, final_utility = distributed_mining(nodes, max_rounds, epsilon)
    
    print(f"\nTopology: {topology}")
    print(f"Convergence rounds: {rounds}")
    print(f"Final best utility: {final_utility}")
    
    # Verify α-smoothness
    all_patterns = [p for node in nodes for p in node.patterns]
    max_diff = 0
    for p1 in all_patterns[:10]:  # Check subset for efficiency
        for p2 in all_patterns[:10]:
            utility_diff = abs(alpha_smooth_utility(p1) - alpha_smooth_utility(p2))
            h_dist = hamming_distance(p1, p2)
            max_diff = max(max_diff, utility_diff / h_dist if h_dist > 0 else 0)
    
    print(f"Empirical α bound: {max_diff:.3f}")
