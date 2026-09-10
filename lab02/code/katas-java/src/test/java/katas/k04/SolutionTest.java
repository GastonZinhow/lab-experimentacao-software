package katas.k04;

import org.junit.jupiter.api.Test;

import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;

/**
 * Testes de aceitacao do K04 (issue #22). Nao alterar durante o trial.
 */
class SolutionTest {

    private final Solution solution = new Solution();
    private static final double DELTA = 0.001;

    @Test
    void obterConceitoRespeitaLimitesDeFaixa() {
        assertEquals("A", solution.obterConceito(9.0));
        assertEquals("A", solution.obterConceito(9.5));
        assertEquals("B", solution.obterConceito(7.0));
        assertEquals("B", solution.obterConceito(8.9));
        assertEquals("C", solution.obterConceito(5.0));
        assertEquals("C", solution.obterConceito(6.9));
        assertEquals("D", solution.obterConceito(4.999));
    }

    @Test
    void calcularMedianaComQuantidadeImparDeNotas() {
        List<Double> notas = List.of(9.5, 8.0, 6.0, 4.0, 9.0);

        assertEquals(8.0, solution.calcularMediana(notas), DELTA);
    }

    @Test
    void calcularMedianaComQuantidadeParDeNotas() {
        List<Double> notas = List.of(9.5, 8.0, 6.0, 4.0);

        assertEquals(7.0, solution.calcularMediana(notas), DELTA);
    }

    @Test
    void conceitoMaisFrequenteSemEmpate() {
        List<Double> notas = List.of(9.5, 8.0, 6.0, 4.0, 9.0);

        assertEquals("A", solution.conceitoMaisFrequente(notas));
    }

    @Test
    void conceitoMaisFrequenteEmEmpateRetornaOAlfabeticamenteMenor() {
        List<Double> notas = List.of(9.0, 9.0, 7.0, 7.0);

        assertEquals("A", solution.conceitoMaisFrequente(notas));
    }

    @Test
    void conceitoMaisFrequenteEmEmpateEntreCED() {
        List<Double> notas = List.of(5.0, 5.0, 3.0, 3.0);

        assertEquals("C", solution.conceitoMaisFrequente(notas));
    }
}
