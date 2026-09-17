class Solution {
    public int longestCycle(int[] edges) {
        int maxCycle = -1;
        Set<Integer> visited = new HashSet<>();


        for(int i=0; i<edges.length; i++){
            if(visited.contains(i) || edges[i] == -1){
                continue;
            }


            int cycle = longestCycle(i, edges, 0, visited, new HashMap<>());


            if(cycle > maxCycle) {
                maxCycle = cycle;
            }
        }
        return maxCycle;
    }


    private int longestCycle(int i, int[] edges, int step, Set<Integer> visited, Map<Integer, Integer> nodeToStep){
        if(edges[i] == -1){
            return -1;
        }
        if(nodeToStep.containsKey(i)){
            return step - nodeToStep.get(i);
        }
        if(visited.contains(i)){
            return -1;
        }


        visited.add(i);
        nodeToStep.put(i, step);


        return longestCycle(edges[i], edges, step+1, visited, nodeToStep);
    }
}
