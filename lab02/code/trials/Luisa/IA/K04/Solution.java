class Solution {
    public int[] gardenNoAdj(int n, int[][] paths) {
        List<List<Integer>> graph = new ArrayList<>();
        for (int i = 0; i <= n; i++) graph.add(new ArrayList<>());

        for (int[] p : paths) {
            graph.get(p[0]).add(p[1]);
            graph.get(p[1]).add(p[0]);
        }

        int[] result = new int[n + 1];

        for (int garden = 1; garden <= n; garden++) {
            boolean[] usedColors = new boolean[5];
            for (int neighbor : graph.get(garden)) {
                if (result[neighbor] != 0) {
                    usedColors[result[neighbor]] = true;
                }
            }
            for (int color = 1; color <= 4; color++) {
                if (!usedColors[color]) {
                    result[garden] = color;
                    break;
                }
            }
        }

        return Arrays.copyOfRange(result, 1, n + 1);
    }
}