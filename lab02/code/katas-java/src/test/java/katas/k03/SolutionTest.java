package katas.k03;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

/**
 * Testes de aceitacao do K03 (issue #22), baseados nos exemplos oficiais
 * do LeetCode. Nao alterar durante o trial.
 */
class SolutionTest {

    private final Solution solution = new Solution();

    @Test
    void escolheCasasNaoAdjacentesDeMaiorValor() {
        assertEquals(4, solution.rob(new int[]{1, 2, 3, 1}));
    }

    @Test
    void puloDeDuasCasasParaMaximizarOValor() {
        assertEquals(12, solution.rob(new int[]{2, 7, 9, 3, 1}));
    }

    @Test
    void umaUnicaCasaRetornaSeuProprioValor() {
        assertEquals(5, solution.rob(new int[]{5}));
    }

    @Test
    void duasCasasRetornaAMaior() {
        assertEquals(7, solution.rob(new int[]{3, 7}));
    }

    @Test
    void vetorVazioRetornaZero() {
        assertEquals(0, solution.rob(new int[]{}));
    }
}
