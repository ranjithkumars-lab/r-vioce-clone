import json
from typing import Dict, Any

class ReportGenerator:
    def __init__(self, metrics_summary: Dict[str, Any], gpu_summary: Dict[str, Any], scenario_config: Dict[str, Any]):
        self.metrics = metrics_summary
        self.gpu = gpu_summary
        self.config = scenario_config

    def generate_json(self, output_path: str):
        report = {
            "scenario": self.config,
            "metrics": self.metrics,
            "gpu": self.gpu
        }
        with open(output_path, "w") as f:
            json.dump(report, f, indent=2)

    def generate_markdown(self, output_path: str):
        md = [
            f"# Benchmark Report: {self.config.get('name', 'Custom Run')}",
            "",
            "## Scenario Configuration",
            f"- **Engine**: {self.config.get('engine')}",
            f"- **Total Jobs**: {self.config.get('jobs')}",
            f"- **Concurrency**: {self.config.get('concurrency')}",
            "",
            "## Overall Metrics",
            f"- **Completed Jobs**: {self.metrics.get('completed')} / {self.metrics.get('total_jobs')}",
            f"- **Failed Jobs**: {self.metrics.get('failed')}",
            f"- **Total Duration**: {self.metrics.get('total_duration_sec')}s",
            f"- **Throughput**: {self.metrics.get('throughput_jobs_per_sec')} jobs/sec",
            "",
            "## Latency Breakdown",
            "| Metric | Average (sec) | P95 (sec) |",
            "|--------|---------------|-----------|",
            f"| Queue Wait Time | {self.metrics.get('queue_wait_time_sec', {}).get('avg', 0)} | {self.metrics.get('queue_wait_time_sec', {}).get('p95', 0)} |",
            f"| Execution Time | {self.metrics.get('execution_time_sec', {}).get('avg', 0)} | {self.metrics.get('execution_time_sec', {}).get('p95', 0)} |",
            f"| Total Latency | {self.metrics.get('total_latency_sec', {}).get('avg', 0)} | {self.metrics.get('total_latency_sec', {}).get('p95', 0)} |",
            "",
            "## GPU Utilization",
            "| Device | Avg Util (%) | Peak Util (%) | Peak VRAM (MB) | Avg Temp (°C) |",
            "|--------|--------------|---------------|----------------|---------------|"
        ]

        if not self.gpu:
            md.append("| N/A | N/A | N/A | N/A | N/A |")
        else:
            for gpu_id, stats in self.gpu.items():
                md.append(
                    f"| {gpu_id} | {stats.get('avg_utilization_pct', 0)} | "
                    f"{stats.get('peak_utilization_pct', 0)} | "
                    f"{stats.get('peak_memory_mb', 0)} | "
                    f"{stats.get('avg_temperature_c', 0)} |"
                )

        with open(output_path, "w") as f:
            f.write("\n".join(md))
