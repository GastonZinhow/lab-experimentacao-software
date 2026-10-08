from datetime import date, datetime, timedelta

from pipeline.collector_runs import collect_repo_runs, fetch_runs_range


class FakeRunsClient:
    """Cada dia tem `per_day` runs; o total de um intervalo é a soma dos dias."""

    def __init__(self, per_day):
        self.per_day = per_day
        self.ranges = []

    @staticmethod
    def _days(created):
        a, b = (date.fromisoformat(x) for x in created.split(".."))
        return [a + timedelta(days=i) for i in range((b - a).days + 1)]

    def get_json(self, url, params=None, transform=None):
        a, b = params["created"].split("..")
        self.ranges.append((a, b))
        return {"total_count": len(self._days(params["created"])) * self.per_day}, False

    def paginate(self, url, params=None, transform_item=None):
        days = self._days(params["created"])
        runs = [{"id": f"{d}-{i}", "conclusion": "success"} for d in days for i in range(self.per_day)]
        return runs[:1000]


def test_subdivisao_nunca_gera_intervalo_invertido_e_cobre_todos_os_dias():
    client = FakeRunsClient(per_day=600)   # 2 dias já passam do teto
    runs = fetch_runs_range(client, "o", "r", "main", datetime(2025, 11, 1), datetime(2025, 11, 30))

    assert all(a <= b for a, b in client.ranges)
    assert len(runs) == 30 * 600
    assert {r["id"].split("-", 3)[2] for r in runs} == {f"{d:02d}" for d in range(1, 31)}


def test_mes_inteiro_coletado_pelo_collect_repo_runs():
    client = FakeRunsClient(per_day=10)
    df = collect_repo_runs(client, "o", "r", "main", "2025-09-30", "2025-10-31")
    assert len(df) == 32 * 10
    assert set(df["status_classificacao"]) == {"sucesso"}
