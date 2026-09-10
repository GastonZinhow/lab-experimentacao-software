package katas.k02;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

/**
 * Testes de aceitacao do K02 (issue #22), baseados nos exemplos oficiais
 * do LeetCode. Nao alterar durante o trial.
 */
class SolutionTest {

    private final Solution solution = new Solution();

    @Test
    void encontraCaminhoEmGrafoConectado() {
        int[][] edges = {{0, 1}, {1, 2}, {2, 0}};

        assertTrue(solution.validPath(3, edges, 0, 2));
    }

    @Test
    void naoEncontraCaminhoEntreComponentesDesconexas() {
        int[][] edges = {{0, 1}, {0, 2}, {3, 5}, {5, 4}, {4, 3}};

        assertFalse(solution.validPath(6, edges, 0, 5));
    }

    @Test
    void origemIgualDestinoSemArestasERetornaVerdadeiro() {
        assertTrue(solution.validPath(1, new int[0][0], 0, 0));
    }

    @Test
    void encontraCaminhoIndiretoEntreVertices() {
        int[][] edges = {{0, 1}, {1, 2}, {2, 3}, {3, 4}};

        assertTrue(solution.validPath(5, edges, 0, 4));
    }
}
