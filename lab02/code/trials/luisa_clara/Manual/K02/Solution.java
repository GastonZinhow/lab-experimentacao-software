class Solution {
    public int[] gardenNoAdj(int n, int[][] paths) {
        int[] answer = new int[n];


        List<Integer>[] graph = new ArrayList[n];


        for (int i = 0; i < n; i++) {
            graph[i] = new ArrayList<>();
        }


        for (int[] path : paths) {
            int a = path[0] - 1;
            int b = path[1] - 1;


            graph[a].add(b);
            graph[b].add(a);
        }


        for (int i = 0; i < n; i++) {
            boolean[] used = new boolean[5];


            for (int adjacent : graph[i]) {
                int flower = answer[adjacent];
                if (flower != 0) {
                    used[flower] = true;
                }
            }


            for (int flower = 1; flower <= 4; flower++) {
                if (!used[flower]) {
                    answer[i] = flower;
                    break;
                }
            }
        }


        return answer;
    }
}
