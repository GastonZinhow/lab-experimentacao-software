package katas.k05;

import katas.k05.Solution.Conflito;
import katas.k05.Solution.Disciplina;
import org.junit.jupiter.api.Test;

import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;

/**
 * Testes de aceitacao do K05 (issue #22). Nao alterar durante o trial.
 */
class SolutionTest {

    private final Solution solution = new Solution();

    @Test
    void detectaSobreposicaoParcialNoMesmoDia() {
        List<Disciplina> grade = List.of(
            new Disciplina("Calculo", "SEG", 480, 570),
            new Disciplina("Fisica", "SEG", 550, 640),
            new Disciplina("Quimica", "TER", 480, 570),
            new Disciplina("Programacao", "SEG", 570, 660)
        );

        List<Conflito> conflitos = solution.detectarConflitos(grade);

        assertEquals(
            List.of(
                new Conflito("Calculo", "Fisica"),
                new Conflito("Fisica", "Programacao")
            ),
            conflitos
        );
    }

    @Test
    void horariosQueSoSeTocamNaoSaoConflito() {
        List<Disciplina> grade = List.of(
            new Disciplina("Calculo", "SEG", 480, 570),
            new Disciplina("Programacao", "SEG", 570, 660)
        );

        assertEquals(List.of(), solution.detectarConflitos(grade));
    }

    @Test
    void diasDiferentesNuncaConflitam() {
        List<Disciplina> grade = List.of(
            new Disciplina("Calculo", "SEG", 480, 570),
            new Disciplina("Fisica", "TER", 480, 570)
        );

        assertEquals(List.of(), solution.detectarConflitos(grade));
    }

    @Test
    void gradeVaziaNaoTemConflitos() {
        assertEquals(List.of(), solution.detectarConflitos(List.of()));
    }

    @Test
    void umaUnicaDisciplinaNaoTemConflito() {
        List<Disciplina> grade = List.of(new Disciplina("Calculo", "SEG", 480, 570));

        assertEquals(List.of(), solution.detectarConflitos(grade));
    }
}
