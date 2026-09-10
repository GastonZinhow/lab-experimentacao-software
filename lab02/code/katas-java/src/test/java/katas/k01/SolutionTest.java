package katas.k01;

import org.junit.jupiter.api.Test;

import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;

/**
 * Testes de aceitacao do K01 (issue #22). Nao alterar durante o trial.
 */
class SolutionTest {

    private final Solution solution = new Solution();

    @Test
    void atendePrioritariosAntesDosDemaisMantendoOrdemDeChegada() {
        List<String> nomes = List.of("Ana", "Bruno", "Carla", "Diego");
        List<Boolean> prioridade = List.of(false, true, false, true);

        List<String> resultado = solution.ordemDeAtendimento(nomes, prioridade);

        assertEquals(List.of("Bruno", "Diego", "Ana", "Carla"), resultado);
    }

    @Test
    void semPrioritariosMantemOrdemDeChegada() {
        List<String> nomes = List.of("Ana", "Bruno", "Carla");
        List<Boolean> prioridade = List.of(false, false, false);

        List<String> resultado = solution.ordemDeAtendimento(nomes, prioridade);

        assertEquals(List.of("Ana", "Bruno", "Carla"), resultado);
    }

    @Test
    void todosPrioritariosMantemOrdemDeChegada() {
        List<String> nomes = List.of("Ana", "Bruno", "Carla");
        List<Boolean> prioridade = List.of(true, true, true);

        List<String> resultado = solution.ordemDeAtendimento(nomes, prioridade);

        assertEquals(List.of("Ana", "Bruno", "Carla"), resultado);
    }

    @Test
    void listaVaziaRetornaListaVazia() {
        List<String> resultado = solution.ordemDeAtendimento(List.of(), List.of());

        assertEquals(List.of(), resultado);
    }

    @Test
    void unicoPrioritarioNoFimVaiParaOInicio() {
        List<String> nomes = List.of("Ana", "Bruno", "Carla", "Diego", "Elis");
        List<Boolean> prioridade = List.of(false, false, false, false, true);

        List<String> resultado = solution.ordemDeAtendimento(nomes, prioridade);

        assertEquals(List.of("Elis", "Ana", "Bruno", "Carla", "Diego"), resultado);
    }
}
