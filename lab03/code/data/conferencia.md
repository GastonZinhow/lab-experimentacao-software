# Conferência da coleta (Issue #52)

Gerado em 2026-10-15 por `python conferencia.py --config config.yaml`.
Janela: [2025-09-30, 2026-09-30), isto é, de 2025-09-30 a 2026-09-29. Os valores "conferência" foram baixados de novo da API,
sem cache, por um caminho diferente do pipeline (releases filtradas neste script;
runs contados pelo `total_count` com filtro `status`, mês a mês).

| Repositório | Medida | Pipeline (`metadados.csv`) | Conferência | Confere? |
|---|---|---|---|---|
| DmitriySalnikov/godot_debug_draw_3d | releases | 5 | 5 | sim |
| DmitriySalnikov/godot_debug_draw_3d | pré-releases | 0 | 0 | sim |
| DmitriySalnikov/godot_debug_draw_3d | runs válidos | 55 | 55 | sim |
| DmitriySalnikov/godot_debug_draw_3d | runs por conclusion | – | success: 53, failure: 2, timed_out: 0, startup_failure: 0 | – |
| immich-app/immich | releases | 35 | 35 | sim |
| immich-app/immich | pré-releases | 8 | 8 | sim |
| immich-app/immich | runs válidos | 18090 | 18090 | sim |
| immich-app/immich | runs por conclusion | – | success: 17707, failure: 383, timed_out: 0, startup_failure: 0 | – |

## Conferência visual (opcional)

Para conferir pela interface do GitHub, abra:

- **DmitriySalnikov/godot_debug_draw_3d**
  - releases: https://github.com/DmitriySalnikov/godot_debug_draw_3d/releases
  - runs: https://github.com/DmitriySalnikov/godot_debug_draw_3d/actions?query=branch%3Amaster+event%3Apush+created%3A2025-09-30..2026-09-29+is%3Asuccess (troque `is:success` por `is:failure`)
- **immich-app/immich**
  - releases: https://github.com/immich-app/immich/releases
  - runs: https://github.com/immich-app/immich/actions?query=branch%3Amain+event%3Apush+created%3A2025-09-30..2026-09-29+is%3Asuccess (troque `is:success` por `is:failure`)
