from ton_node_control.cli.system import get_cpu_count


class TestSystem:
    def test_get_cpu_count(self) -> None:
        cpu_count: int = get_cpu_count()
        assert cpu_count is not None
        assert isinstance(cpu_count, int)
