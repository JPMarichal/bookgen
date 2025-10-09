"""
Tests for parallel task execution.
"""
import pytest
import time
from src.parallel.task_executor import (
    ParallelTaskExecutor,
    ValidationParallelizer,
    TaskResult,
    parallel_map,
    parallel_batch_process,
)


class TestTaskResult:
    """Test TaskResult dataclass"""
    
    def test_successful_task_result(self):
        """Test creating successful task result"""
        result = TaskResult(
            success=True,
            result="output",
            duration=0.5,
            task_id="task1"
        )
        
        assert result.success is True
        assert result.result == "output"
        assert result.error is None
        assert result.duration == 0.5
    
    def test_failed_task_result(self):
        """Test creating failed task result"""
        error = ValueError("Test error")
        result = TaskResult(
            success=False,
            error=error,
            task_id="task1"
        )
        
        assert result.success is False
        assert result.result is None
        assert result.error == error


class TestParallelTaskExecutor:
    """Test ParallelTaskExecutor class"""
    
    def test_execute_parallel_success(self):
        """Test executing multiple tasks in parallel"""
        def task1():
            time.sleep(0.05)
            return "result1"
        
        def task2():
            time.sleep(0.05)
            return "result2"
        
        executor = ParallelTaskExecutor(max_workers=2)
        results = executor.execute_parallel([task1, task2])
        
        assert len(results) == 2
        assert all(r.success for r in results)
        assert {r.result for r in results} == {"result1", "result2"}
    
    def test_execute_parallel_with_failure(self):
        """Test executing tasks with one failure"""
        def success_task():
            return "success"
        
        def failure_task():
            raise ValueError("Task failed")
        
        executor = ParallelTaskExecutor(max_workers=2)
        results = executor.execute_parallel([success_task, failure_task])
        
        assert len(results) == 2
        successful = [r for r in results if r.success]
        failed = [r for r in results if not r.success]
        
        assert len(successful) == 1
        assert len(failed) == 1
        assert isinstance(failed[0].error, ValueError)
    
    def test_execute_parallel_timing(self):
        """Test that parallel execution is faster than sequential"""
        def slow_task():
            time.sleep(0.1)
            return "done"
        
        tasks = [slow_task for _ in range(4)]
        
        # Parallel execution
        executor = ParallelTaskExecutor(max_workers=4)
        start = time.time()
        results = executor.execute_parallel(tasks)
        parallel_time = time.time() - start
        
        # Should complete in ~0.1s (all parallel) not 0.4s (sequential)
        assert parallel_time < 0.3, "Parallel execution should be faster"
        assert all(r.success for r in results)
    
    def test_map_parallel(self):
        """Test parallel map operation"""
        def double(x):
            return x * 2
        
        executor = ParallelTaskExecutor(max_workers=4)
        items = [1, 2, 3, 4, 5]
        results = executor.map_parallel(double, items)
        
        assert len(results) == 5
        assert all(r.success for r in results)
        result_values = {r.result for r in results}
        assert result_values == {2, 4, 6, 8, 10}
    
    def test_task_ids(self):
        """Test task ID tracking"""
        tasks = [lambda: f"result_{i}" for i in range(3)]
        task_ids = ["task_a", "task_b", "task_c"]
        
        executor = ParallelTaskExecutor()
        results = executor.execute_parallel(tasks, task_ids=task_ids)
        
        assert len(results) == 3
        result_ids = {r.task_id for r in results}
        assert result_ids == set(task_ids)


class TestValidationParallelizer:
    """Test ValidationParallelizer class"""
    
    def test_validate_sources_parallel(self):
        """Test parallel source validation"""
        sources = [
            {"url": "http://example1.com"},
            {"url": "http://example2.com"},
            {"url": "http://example3.com"},
        ]
        
        def validator(source):
            time.sleep(0.05)
            return {"url": source["url"], "valid": True}
        
        parallelizer = ValidationParallelizer(max_workers=3)
        results = parallelizer.validate_sources_parallel(sources, validator)
        
        assert len(results) == 3
        assert all(r.success for r in results)
    
    def test_validate_chapters_parallel(self):
        """Test parallel chapter validation"""
        chapters = [
            {"title": "Chapter 1", "content": "Content 1"},
            {"title": "Chapter 2", "content": "Content 2"},
        ]
        
        def validator(chapter):
            return {"title": chapter["title"], "valid": True}
        
        parallelizer = ValidationParallelizer(max_workers=2)
        results = parallelizer.validate_chapters_parallel(chapters, validator)
        
        assert len(results) == 2
        assert all(r.success for r in results)
    
    def test_get_summary(self):
        """Test validation summary generation"""
        results = [
            TaskResult(success=True, result="ok", duration=0.1),
            TaskResult(success=True, result="ok", duration=0.2),
            TaskResult(success=False, error=ValueError("error"), duration=0.15),
        ]
        
        parallelizer = ValidationParallelizer()
        summary = parallelizer.get_summary(results)
        
        assert summary['total'] == 3
        assert summary['successful'] == 2
        assert summary['failed'] == 1
        assert summary['success_rate'] == 2/3
        # Use approximate comparison for floating point
        assert abs(summary['total_time'] - 0.45) < 0.0001
        assert summary['average_time'] == 0.15
        assert len(summary['errors']) == 1


class TestParallelMapFunction:
    """Test parallel_map function"""
    
    def test_parallel_map_simple(self):
        """Test simple parallel map"""
        def square(x):
            return x ** 2
        
        items = [1, 2, 3, 4, 5]
        results = parallel_map(square, items, max_workers=3)
        
        # Results should be in same order as input
        assert results == [1, 4, 9, 16, 25]
    
    def test_parallel_map_with_failure(self):
        """Test parallel map with failures"""
        def risky_operation(x):
            if x == 3:
                raise ValueError("Bad value")
            return x * 2
        
        items = [1, 2, 3, 4]
        results = parallel_map(risky_operation, items)
        
        # Failed items should be None
        assert results[0] == 2
        assert results[1] == 4
        assert results[2] is None  # Failed
        assert results[3] == 8


class TestParallelBatchProcess:
    """Test parallel_batch_process function"""
    
    def test_batch_processing(self):
        """Test parallel batch processing"""
        def process_batch(items):
            return [x * 2 for x in items]
        
        items = list(range(25))
        results = parallel_batch_process(
            items,
            process_batch,
            batch_size=10,
            max_workers=3
        )
        
        # All items should be processed
        assert len(results) == 25
        assert sorted(results) == [x * 2 for x in range(25)]
    
    def test_batch_processing_timing(self):
        """Test that batch processing is faster in parallel"""
        def slow_batch_processor(items):
            time.sleep(0.1)
            return [x * 2 for x in items]
        
        items = list(range(30))
        
        start = time.time()
        results = parallel_batch_process(
            items,
            slow_batch_processor,
            batch_size=10,
            max_workers=3
        )
        parallel_time = time.time() - start
        
        # With 30 items, 10 per batch = 3 batches
        # Sequential would take 0.3s, parallel ~0.1s
        assert parallel_time < 0.25
        assert len(results) == 30


class TestAcceptanceCriteria:
    """Test acceptance criteria for parallelization"""
    
    def test_validation_parallelization(self):
        """Test that validations can be parallelized"""
        # Simulate 10 validation tasks
        validations = [
            {"id": i, "data": f"item_{i}"}
            for i in range(10)
        ]
        
        def validate(item):
            # Simulate validation work
            time.sleep(0.05)
            return {"id": item["id"], "valid": True}
        
        # Measure parallel execution time
        start = time.time()
        parallelizer = ValidationParallelizer(max_workers=5)
        results = parallelizer.validate_sources_parallel(validations, validate)
        parallel_time = time.time() - start
        
        # Sequential would take ~0.5s, parallel with 5 workers ~0.1s
        assert parallel_time < 0.3, "Parallel validation should be faster"
        assert all(r.success for r in results)
        
        summary = parallelizer.get_summary(results)
        assert summary['successful'] == 10
        assert summary['failed'] == 0
    
    def test_speedup_ratio(self):
        """Test that parallelization provides significant speedup"""
        def slow_task():
            time.sleep(0.1)
            return "done"
        
        num_tasks = 8
        tasks = [slow_task for _ in range(num_tasks)]
        
        # Parallel with 4 workers
        executor = ParallelTaskExecutor(max_workers=4)
        start = time.time()
        results = executor.execute_parallel(tasks)
        parallel_time = time.time() - start
        
        # Expected: 8 tasks / 4 workers = 2 batches * 0.1s = ~0.2s
        # Sequential would be 8 * 0.1s = 0.8s
        # Speedup should be at least 2x
        expected_sequential_time = num_tasks * 0.1
        speedup = expected_sequential_time / parallel_time
        
        assert speedup > 2.0, f"Speedup should be > 2x, got {speedup:.2f}x"
        assert all(r.success for r in results)
