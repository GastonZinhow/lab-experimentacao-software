package katas.k02;

/**
 * K02 - Find if Path Exists in Graph (issue #22).
 * https://leetcode.com/problems/find-if-path-exists-in-graph/
 *
 * Dado um grafo nao direcionado com n vertices (numerados de 0 a n-1) e
 * uma lista de arestas, determina se existe um caminho entre o vertice
 * source e o vertice destination.
 */
public class Solution {

    public boolean validPath(int n, int[][] edges, int source, int destination) {
        int[] parent = new int[n];
        for (int i = 0; i < n; i++) {
            parent[i] = i;
        }

        for (int[] edge : edges) {
            union(parent, edge[0], edge[1]);
        }

        return find(parent, source) == find(parent, destination);
    }

    private int find(int[] parent, int node) {
        while (parent[node] != node) {
            parent[node] = parent[parent[node]];
            node = parent[node];
        }
        return node;
    }

    private void union(int[] parent, int a, int b) {
        int rootA = find(parent, a);
        int rootB = find(parent, b);
        if (rootA != rootB) {
            parent[rootA] = rootB;
        }
    }
}
