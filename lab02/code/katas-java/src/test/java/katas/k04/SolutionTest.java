package katas.k04;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

/**
 * Testes de aceitacao do K04 (issue #22), baseados no exemplo oficial do
 * LeetCode. Como o problema admite mais de uma atribuicao valida, os
 * testes verificam a propriedade de validade da solucao em vez de uma
 * unica saida esperada. Nao alterar durante o trial.
 */
class SolutionTest {

    private final Solution solution = new Solution();

    private void assertValidAssignment(int n, int[][] paths, int[] answer) {
        assertEquals(n, answer.length);

        for (int flower : answer) {
            assertTrue(flower >= 1 && flower <= 4, "flor fora do intervalo 1-4: " + flower);
        }

        for (int[] path : paths) {
            int a = path[0] - 1;
            int b = path[1] - 1;
            assertTrue(answer[a] != answer[b],
                "jardins adjacentes " + path[0] + " e " + path[1] + " tem a mesma flor");
        }
    }

    @Test
    void atribuiFloresValidasParaExemploOficial() {
        int n = 4;
        int[][] paths = {{1, 2}, {2, 3}, {3, 4}, {4, 1}, {1, 3}, {2, 4}};

        int[] answer = solution.gardenNoAdj(n, paths);

        assertValidAssignment(n, paths, answer);
    }

    @Test
    void atribuiFloresValidasSemCaminhos() {
        int n = 3;
        int[][] paths = {};

        int[] answer = solution.gardenNoAdj(n, paths);

        assertValidAssignment(n, paths, answer);
    }

    @Test
    void atribuiFloresValidasParaCadeiaLinear() {
        int n = 5;
        int[][] paths = {{1, 2}, {2, 3}, {3, 4}, {4, 5}};

        int[] answer = solution.gardenNoAdj(n, paths);

        assertValidAssignment(n, paths, answer);
    }

    @Test
    void atribuiFloresValidasParaJardimComTresVizinhos() {
        int n = 4;
        int[][] paths = {{1, 2}, {1, 3}, {1, 4}};

        int[] answer = solution.gardenNoAdj(n, paths);

        assertValidAssignment(n, paths, answer);
    }
}
