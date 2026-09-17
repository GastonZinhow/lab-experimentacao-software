import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Queue;
import java.util.Set;

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
        Map<Integer, List<Integer>> graph = new HashMap<>();
        for(int[] edge: edges){
            int x = edge[0];
            int y = edge[1];
            graph.putIfAbsent(x, new ArrayList<>());
            graph.putIfAbsent(y, new ArrayList<>());
            graph.get(x).add(y);
            graph.get(y).add(x);
        }

        Queue<Integer> bfs = new ArrayDeque<>();
        bfs.add(source);
        Set<Integer> visited = new HashSet<>();
        visited.add(source);

        while(!bfs.isEmpty()){
            int node = bfs.poll();
            if(node == destination){
                return true;
            }
            if(!graph.containsKey(node)){
                continue;
            }
            for(int child: graph.get(node)){
                if(!visited.contains(child)){
                    visited.add(child);
                    bfs.add(child);
                }
            }
        }
        return false;
    }
}
