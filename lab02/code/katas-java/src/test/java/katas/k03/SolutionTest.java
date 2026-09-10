package katas.k03;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

/**
 * Testes de aceitacao do K03 (issue #22). Nao alterar durante o trial.
 */
class SolutionTest {

    private final Solution solution = new Solution();

    @Test
    void aceitaCodigoComDigitoVerificadorCorreto() {
        // digitos: 2,3,0,0,4,5,6 -> soma 20 -> D = 0
        assertTrue(solution.isValido("CC2300456-0"));
    }

    @Test
    void aceitaOutroCodigoComDigitoVerificadorCorreto() {
        // digitos: 2,4,0,1,2,3,4 -> soma 16 -> D = 6
        assertTrue(solution.isValido("ES2401234-6"));
    }

    @Test
    void rejeitaDigitoVerificadorIncorreto() {
        assertFalse(solution.isValido("CC2300456-1"));
    }

    @Test
    void rejeitaSiglaDeCursoMinuscula() {
        assertFalse(solution.isValido("cc2300456-0"));
    }

    @Test
    void rejeitaNumeroSequencialComTamanhoErrado() {
        assertFalse(solution.isValido("CC230456-6"));
    }

    @Test
    void rejeitaFormatoSemHifen() {
        assertFalse(solution.isValido("CC23004560"));
    }

    @Test
    void rejeitaCodigoVazio() {
        assertFalse(solution.isValido(""));
    }
}
