package katas.k05;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

/**
 * Testes de aceitacao do K05 (issue #22), baseados nos exemplos oficiais
 * do LeetCode. Nao alterar durante o trial.
 */
class SolutionTest {

    private final Solution solution = new Solution();

    @Test
    void encontraCicloDeTresVerticesNoExemploOficial() {
        assertEquals(3, solution.longestCycle(new int[] {3, 3, 4, 2, 3}));
    }

    @Test
    void retornaMenosUmQuandoNaoExisteCiclo() {
        assertEquals(-1, solution.longestCycle(new int[] {2, -1, 3, 1}));
    }

    @Test
    void reconheceAutoCicloComoCicloDeTamanhoUm() {
        assertEquals(1, solution.longestCycle(new int[] {0}));
    }

    @Test
    void retornaMaiorCicloQuandoExistemMultiplosCiclos() {
        assertEquals(3, solution.longestCycle(new int[] {1, 2, 0, 4, 3}));
    }

    @Test
    void ignoraCaminhoQueEntraEmCicloJaContado() {
        assertEquals(3, solution.longestCycle(new int[] {1, 2, 3, 1, 2}));
    }
}
