package katas.k01;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

/**
 * Testes de aceitacao do K01 (issue #22), baseados nos exemplos oficiais
 * do LeetCode. Nao alterar durante o trial.
 */
class SolutionTest {

    private final Solution solution = new Solution();

    @Test
    void aceitaSubsequenciaValida() {
        assertTrue(solution.isSubsequence("abc", "ahbgdc"));
    }

    @Test
    void rejeitaQuandoNaoESubsequencia() {
        assertFalse(solution.isSubsequence("axc", "ahbgdc"));
    }

    @Test
    void stringVaziaESubsequenciaDeQualquerString() {
        assertTrue(solution.isSubsequence("", "ahbgdc"));
    }

    @Test
    void stringIgualETSubsequenciaDeSiMesma() {
        assertTrue(solution.isSubsequence("abc", "abc"));
    }

    @Test
    void rejeitaQuandoSEMaiorQueT() {
        assertFalse(solution.isSubsequence("abcd", "abc"));
    }
}
