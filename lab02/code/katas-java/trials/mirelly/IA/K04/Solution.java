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
        List<List<Integer>> adjacency = new ArrayList<>();
        for (int i = 0; i < n; i++) {
            adjacency.add(new ArrayList<>());
        }
        for (int[] path : paths) {
            int a = path[0] - 1;
            int b = path[1] - 1;
            adjacency.get(a).add(b);
            adjacency.get(b).add(a);
        }

        int[] answer = new int[n];
        for (int garden = 0; garden < n; garden++) {
            boolean[] usedFlowers = new boolean[5];
            for (int neighbor : adjacency.get(garden)) {
                usedFlowers[answer[neighbor]] = true;
            }
            for (int flower = 1; flower <= 4; flower++) {
                if (!usedFlowers[flower]) {
                    answer[garden] = flower;
                    break;
                }
            }
        }

        return answer;
    }
}
