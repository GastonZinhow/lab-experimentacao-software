package katas.k05;

public class Solution {
    private boolean[] visitados;
    private int[] profundidades;

    public int longestCycle(int[] edges) {
        int n = edges.length;
        visitados = new boolean[n];
        profundidades = new int[n];
        Arrays.fill(profundidades, -1);

        int maiorCiclo = -1;

        for (int i = 0; i < n; i++) {
            if (!visitados[i]) {
                maiorCiclo = Math.max(maiorCiclo, dfs(i, 0, edges));
            }
        }

        return maiorCiclo;
    }

    private int dfs(int no, int profundidadeAtual, int[] edges) {
        if (no == -1 || visitados[no]) {
            return -1;
        }

        if (profundidades[no] != -1) {
            return profundidadeAtual - profundidades[no];
        }

        profundidades[no] = profundidadeAtual;
        int resultado = dfs(edges[no], profundidadeAtual + 1, edges);
        visitados[no] = true;

        return resultado;
    }
}