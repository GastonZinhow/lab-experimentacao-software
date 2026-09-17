package katas.k05;

/**
 * K05 - Longest Cycle in a Graph (issue #22).
 * https://leetcode.com/problems/longest-cycle-in-a-graph/
 *
 * Dado um grafo direcionado em que cada vertice possui no maximo uma
 * aresta de saida, representado por edges[i] = proximo vertice ou -1,
 * retorna o tamanho do maior ciclo existente. Se nao houver ciclo,
 * retorna -1.
 */public class Solution {

    public int longestCycle(int[] edges) {
        int n = edges.length;
        int[] visitedAt = new int[n];
        int step = 1;
        int longest = -1;

        for (int i = 0; i < n; i++) {
            if (visitedAt[i] != 0) {
                continue;
            }

            int startStep = step;
            int node = i;

            while (node != -1 && visitedAt[node] == 0) {
                visitedAt[node] = step;
                step++;
                node = edges[node];
            }

            if (node != -1 && visitedAt[node] >= startStep) {
                longest = Math.max(longest, step - visitedAt[node]);
            }
        }

        return longest;
    }
}