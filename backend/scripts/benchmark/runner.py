import argparse
import asyncio
import logging
from datetime import datetime

from .monitor import GPUMonitor
from .metrics import MetricsCollector
from .client import BenchmarkClient
from .report import ReportGenerator

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def run_scenario(scenario_name: str, engine: str, concurrency: int, jobs: int, base_url: str):
    logger.info(f"Starting Scenario: {scenario_name} (Engine: {engine}, Concurrency: {concurrency}, Jobs: {jobs})")
    
    metrics = MetricsCollector()
    monitor = GPUMonitor(interval_seconds=0.5)
    client = BenchmarkClient(base_url, metrics)
    
    await client.setup()
    monitor.start()
    metrics.start_suite()
    
    logger.info("Bombarding API...")
    await client.run_concurrent_batch(concurrency=concurrency, total_jobs=jobs, engine=engine)
    
    metrics.end_suite()
    await monitor.stop()
    await client.teardown()
    
    metrics_summary = metrics.get_summary()
    gpu_summary = monitor.get_summary()
    
    config = {
        "name": scenario_name,
        "engine": engine,
        "concurrency": concurrency,
        "jobs": jobs
    }
    
    report_gen = ReportGenerator(metrics_summary, gpu_summary, config)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    prefix = scenario_name.replace(" ", "_").lower()
    
    json_path = f"benchmark_{prefix}_{timestamp}.json"
    md_path = f"benchmark_{prefix}_{timestamp}.md"
    
    report_gen.generate_json(json_path)
    report_gen.generate_markdown(md_path)
    
    logger.info(f"Benchmark complete. Reports saved to {json_path} and {md_path}")
    
    # Print quick summary
    print("\n" + "="*50)
    print(f"BENCHMARK SUMMARY: {scenario_name}")
    print("="*50)
    print(f"Throughput: {metrics_summary.get('throughput_jobs_per_sec')} jobs/sec")
    print(f"Avg Queue Time: {metrics_summary.get('queue_wait_time_sec', {}).get('avg')}s")
    print(f"Avg Exec Time: {metrics_summary.get('execution_time_sec', {}).get('avg')}s")
    print(f"Total Completed: {metrics_summary.get('completed')} / {metrics_summary.get('total_jobs')}")
    print("="*50 + "\n")

def main():
    parser = argparse.ArgumentParser(description="DGX Hardware Benchmark Suite for Voice Studio")
    parser.add_argument("--profile", choices=["queue", "gpu", "saturation", "affinity", "custom"], default="custom")
    parser.add_argument("--engine", default="mock", help="mock or f5tts")
    parser.add_argument("--concurrency", type=int, default=10)
    parser.add_argument("--jobs", type=int, default=50)
    parser.add_argument("--url", default="http://127.0.0.1:8000")
    
    args = parser.parse_args()
    
    if args.profile == "queue":
        args.engine = "mock"
        args.concurrency = 100
        args.jobs = 1000
    elif args.profile == "gpu":
        args.engine = "f5tts"
        args.concurrency = 4
        args.jobs = 40
    elif args.profile == "saturation":
        args.engine = "f5tts"
        args.concurrency = 10
        args.jobs = 100
    elif args.profile == "affinity":
        args.engine = "f5tts"
        args.concurrency = 2
        args.jobs = 20

    asyncio.run(run_scenario(
        scenario_name=f"Profile_{args.profile.capitalize()}",
        engine=args.engine,
        concurrency=args.concurrency,
        jobs=args.jobs,
        base_url=args.url
    ))

if __name__ == "__main__":
    main()
