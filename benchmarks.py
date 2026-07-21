# -*- coding: utf-8 -*-
"""
Acoustic Alignment Benchmarks and Validation Module.
Runs execution timing profiles, precision validation checks, and stress tests
on the PronunciationEngine's dynamic programming sequence alignment algorithm.
"""

import time
from typing import Dict, List, Any
from pronunciation_engine import PronunciationEngine

# Benchmark test datasets containing expected target and actual spoken transcription scenarios
BENCHMARK_CASES = [
    {
        "name": "Perfect Match Short",
        "target": "She sells seashells by the seashore.",
        "spoken": "She sells seashells by the seashore.",
        "expected_accuracy": 100
    },
    {
        "name": "Perfect Match Long",
        "target": "Peter Piper picked a peck of pickled peppers. A peck of pickled peppers Peter Piper picked.",
        "spoken": "Peter Piper picked a peck of pickled peppers. A peck of pickled peppers Peter Piper picked.",
        "expected_accuracy": 100
    },
    {
        "name": "One Word Missed",
        "target": "Six sleek swans swam swiftly southwards.",
        "spoken": "Six swans swam swiftly southwards.", # missed 'sleek'
        "expected_accuracy": 83 # approx 5/6 matches
    },
    {
        "name": "Acoustic Slips & Extras",
        "target": "How much wood would a woodchuck chuck",
        "spoken": "How much wood wood a woodchuck shock extra", # 'would' -> 'wood' (0 cost), 'chuck' -> 'shock' (partial), + 'extra'
        "expected_accuracy": 75 # approx
    }
]

class SpeechAlignmentBenchmark:
    """
    Automated benchmark test suite.
    Runs stress tests and performance timings on sequence alignment calculations.
    """

    @classmethod
    def run_performance_benchmarks(cls) -> Dict[str, Any]:
        """
        Executes performance benchmarking.
        Measures processing speeds, alignment accuracy metrics, and returns a detailed audit log.
        """
        results = []
        total_time_ms = 0.0
        passed_cases = 0

        for case in BENCHMARK_CASES:
            start_time = time.perf_counter()
            alignment, accuracy = PronunciationEngine.calculate_alignment(case["target"], case["spoken"])
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            
            total_time_ms += duration_ms

            # Check if alignment is valid
            is_valid_alignment = len(alignment) >= max(len(case["target"].split()), len(case["spoken"].split()))
            
            # Tolerance band of 15% for heuristic matching differences
            diff = abs(accuracy - case["expected_accuracy"])
            success = is_valid_alignment and (diff <= 15)
            
            if success:
                passed_cases += 1

            results.append({
                "caseName": case["name"],
                "targetLen": len(case["target"].split()),
                "spokenLen": len(case["spoken"].split()),
                "accuracy": accuracy,
                "expectedAccuracy": case["expected_accuracy"],
                "executionTimeMs": round(duration_ms, 3),
                "success": success
            })

        avg_latency_ms = total_time_ms / len(BENCHMARK_CASES) if BENCHMARK_CASES else 0.0

        return {
            "timestamp": time.time(),
            "testCount": len(BENCHMARK_CASES),
            "passedCount": passed_cases,
            "successRate": round((passed_cases / len(BENCHMARK_CASES)) * 100, 1) if BENCHMARK_CASES else 0.0,
            "averageLatencyMs": round(avg_latency_ms, 3),
            "details": results
        }

    @classmethod
    def run_stress_test(cls, iterations: int = 1000) -> Dict[str, Any]:
        """
        Runs a heavy stress test on sequence alignment to check for memory leaks
        or algorithmic slowdowns under high volumes.
        """
        target = "Peter Piper picked a peck of pickled peppers. A peck of pickled peppers Peter Piper picked."
        spoken = "Peter Piper pecked a peck of pickles pepper. A peck of pickle peppers Peter Pipe picked."
        
        start_time = time.perf_counter()
        
        for _ in range(iterations):
            _ = PronunciationEngine.calculate_alignment(target, spoken)
            
        elapsed_seconds = time.perf_counter() - start_time
        avg_iter_ms = (elapsed_seconds / iterations) * 1000.0

        return {
            "iterations": iterations,
            "totalTimeSeconds": round(elapsed_seconds, 4),
            "averageIterationTimeMs": round(avg_iter_ms, 4),
            "throughputPerSecond": round(iterations / elapsed_seconds, 1)
        }

if __name__ == "__main__":
    print("=== STARTING SPEECH ALIGNMENT ALGORITHM BENCHMARKS ===")
    perf = SpeechAlignmentBenchmark.run_performance_benchmarks()
    print(f"Dataset Pass Rate: {perf['successRate']}%")
    print(f"Average Algorithm Latency: {perf['averageLatencyMs']} ms")
    print("\n--- Diagnostic Details ---")
    for d in perf["details"]:
        status = "PASSED" if d["success"] else "FAILED"
        print(f" - [{status}] {d['caseName']}: {d['accuracy']}% (Expected: {d['expectedAccuracy']}%) in {d['executionTimeMs']}ms")

    print("\n=== RUNNING 500 ITERATION STRESS TEST ===")
    stress = SpeechAlignmentBenchmark.run_stress_test(500)
    print(f"Throughput: {stress['throughputPerSecond']} alignments/sec")
    print(f"Average latency per alignment: {stress['averageIterationTimeMs']} ms")
    print("======================================================")
