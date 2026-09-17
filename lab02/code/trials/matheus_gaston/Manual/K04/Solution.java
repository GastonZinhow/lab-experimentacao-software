package katas.k04;

import java.util.ArrayList;
import java.util.List;

/**
 * K04 - Flower Planting With No Adjacent (issue #22).
 * https://leetcode.com/problems/flower-planting-with-no-adjacent/
 *
 * Dados n jardins (numerados de 1 a n) e uma lista paths de caminhos
 * (arestas) entre pares de jardins, atribui a cada jardim um tipo de
 * flor, representado por um inteiro entre 1 e 4, de forma que nenhum par
 * de jardins conectados por um caminho tenha o mesmo tipo de flor.
 * Qualquer atribuicao valida e aceita: o problema garante que cada jardim
 * tem no maximo 3 vizinhos, portanto sempre existe solucao.
 */

public class Solution {
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