package katas.k06;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

/**
 * Testes de aceitacao do K06 (issue #22), baseados nos exemplos oficiais
 * do LeetCode. Nao alterar durante o trial.
 */
class SolutionTest {

    private final Solution solution = new Solution();

    @Test
    void tabuleiroQuatroPorQuatroTemDuasSolucoes() {
        assertEquals(2, solution.totalNQueens(4));
    }

    @Test
    void tabuleiroUmPorUmTemUmaSolucao() {
        assertEquals(1, solution.totalNQueens(1));
    }

    @Test
    void tabuleiroDoisPorDoisNaoTemSolucao() {
        assertEquals(0, solution.totalNQueens(2));
    }

    @Test
    void tabuleiroTresPorTresNaoTemSolucao() {
        assertEquals(0, solution.totalNQueens(3));
    }

    @Test
    void tabuleiroOitoPorOitoTemNoventaEDuasSolucoes() {
        assertEquals(92, solution.totalNQueens(8));
    }
}
