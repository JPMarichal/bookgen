"""
Parallel task execution utilities.

Provides utilities for parallelizing independent tasks to improve
performance, particularly for validation operations.
"""
import logging
from typing import List, Callable, Any, Dict, Optional, TypeVar
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from dataclasses import dataclass
import time

logger = logging.getLogger(__name__)

T = TypeVar('T')


@dataclass
class TaskResult:
    """Result of a parallel task execution"""
    success: bool
    result: Any = None
    error: Optional[Exception] = None
    duration: float = 0.0
    task_id: Any = None


class ParallelTaskExecutor:
    """
    Executor for running independent tasks in parallel.
    
    Features:
    - Thread-based parallelization for I/O-bound tasks
    - Process-based parallelization for CPU-bound tasks
    - Error handling and result aggregation
    - Progress tracking
    """
    
    def __init__(
        self,
        max_workers: Optional[int] = None,
        use_processes: bool = False
    ):
        """
        Initialize parallel task executor.
        
        Args:
            max_workers: Maximum number of workers (default: CPU count * 2 for threads)
            use_processes: Use process pool instead of thread pool for CPU-bound tasks
        """
        self.max_workers = max_workers
        self.use_processes = use_processes
        self.executor_class = ProcessPoolExecutor if use_processes else ThreadPoolExecutor
    
    def execute_parallel(
        self,
        tasks: List[Callable[[], T]],
        task_ids: Optional[List[Any]] = None,
    ) -> List[TaskResult]:
        """
        Execute tasks in parallel.
        
        Args:
            tasks: List of callable tasks to execute
            task_ids: Optional list of task identifiers for tracking
            
        Returns:
            List of TaskResult objects
        """
        if task_ids is None:
            task_ids = list(range(len(tasks)))
        
        results = []
        
        with self.executor_class(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_task = {}
            for task, task_id in zip(tasks, task_ids):
                future = executor.submit(self._execute_task, task, task_id)
                future_to_task[future] = task_id
            
            # Collect results as they complete
            for future in as_completed(future_to_task):
                task_id = future_to_task[future]
                try:
                    result = future.result()
                    results.append(result)
                    if result.success:
                        logger.debug(f"Task {task_id} completed in {result.duration:.2f}s")
                    else:
                        logger.error(f"Task {task_id} failed: {result.error}")
                except Exception as e:
                    logger.error(f"Task {task_id} raised exception: {e}")
                    results.append(TaskResult(
                        success=False,
                        error=e,
                        task_id=task_id
                    ))
        
        return results
    
    @staticmethod
    def _execute_task(task: Callable, task_id: Any) -> TaskResult:
        """
        Execute a single task with timing and error handling.
        
        Args:
            task: Callable to execute
            task_id: Task identifier
            
        Returns:
            TaskResult
        """
        start_time = time.time()
        try:
            result = task()
            duration = time.time() - start_time
            return TaskResult(
                success=True,
                result=result,
                duration=duration,
                task_id=task_id
            )
        except Exception as e:
            duration = time.time() - start_time
            return TaskResult(
                success=False,
                error=e,
                duration=duration,
                task_id=task_id
            )
    
    def map_parallel(
        self,
        func: Callable[[Any], T],
        items: List[Any],
    ) -> List[TaskResult]:
        """
        Apply function to items in parallel (map operation).
        
        Args:
            func: Function to apply to each item
            items: List of items to process
            
        Returns:
            List of TaskResult objects
        """
        tasks = [lambda item=item: func(item) for item in items]
        return self.execute_parallel(tasks, task_ids=items)


class ValidationParallelizer:
    """
    Specialized parallelizer for validation tasks.
    
    Optimized for running multiple independent validation operations
    concurrently to improve throughput.
    """
    
    def __init__(self, max_workers: int = 4):
        """
        Initialize validation parallelizer.
        
        Args:
            max_workers: Maximum concurrent validations (default: 4)
        """
        self.executor = ParallelTaskExecutor(max_workers=max_workers)
    
    def validate_sources_parallel(
        self,
        sources: List[Dict[str, Any]],
        validator: Callable[[Dict[str, Any]], Dict[str, Any]]
    ) -> List[TaskResult]:
        """
        Validate multiple sources in parallel.
        
        Args:
            sources: List of source dictionaries
            validator: Validation function to apply
            
        Returns:
            List of validation results
        """
        logger.info(f"Validating {len(sources)} sources in parallel")
        return self.executor.map_parallel(validator, sources)
    
    def validate_chapters_parallel(
        self,
        chapters: List[Dict[str, Any]],
        validator: Callable[[Dict[str, Any]], Dict[str, Any]]
    ) -> List[TaskResult]:
        """
        Validate multiple chapters in parallel.
        
        Args:
            chapters: List of chapter dictionaries
            validator: Validation function to apply
            
        Returns:
            List of validation results
        """
        logger.info(f"Validating {len(chapters)} chapters in parallel")
        return self.executor.map_parallel(validator, chapters)
    
    def get_summary(self, results: List[TaskResult]) -> Dict[str, Any]:
        """
        Get summary of validation results.
        
        Args:
            results: List of task results
            
        Returns:
            Summary dictionary
        """
        total = len(results)
        successful = sum(1 for r in results if r.success)
        failed = total - successful
        total_time = sum(r.duration for r in results)
        avg_time = total_time / total if total > 0 else 0.0
        
        return {
            'total': total,
            'successful': successful,
            'failed': failed,
            'success_rate': successful / total if total > 0 else 0.0,
            'total_time': total_time,
            'average_time': avg_time,
            'errors': [r.error for r in results if not r.success]
        }


def parallel_map(
    func: Callable[[Any], T],
    items: List[Any],
    max_workers: Optional[int] = None,
    use_processes: bool = False
) -> List[T]:
    """
    Simple parallel map function.
    
    Args:
        func: Function to apply
        items: Items to process
        max_workers: Maximum workers
        use_processes: Use processes instead of threads
        
    Returns:
        List of results (in same order as input)
        
    Example:
        results = parallel_map(validate_url, urls, max_workers=10)
    """
    executor = ParallelTaskExecutor(max_workers=max_workers, use_processes=use_processes)
    task_results = executor.map_parallel(func, items)
    
    # Return results in original order
    results = []
    for i, item in enumerate(items):
        task_result = next((r for r in task_results if r.task_id == item), None)
        if task_result and task_result.success:
            results.append(task_result.result)
        else:
            results.append(None)
    
    return results


def parallel_batch_process(
    items: List[Any],
    batch_processor: Callable[[List[Any]], List[T]],
    batch_size: int = 10,
    max_workers: Optional[int] = None
) -> List[T]:
    """
    Process items in parallel batches.
    
    Args:
        items: Items to process
        batch_processor: Function that processes a batch of items
        batch_size: Size of each batch
        max_workers: Maximum workers
        
    Returns:
        List of all results
        
    Example:
        def process_batch(urls):
            return [validate_url(url) for url in urls]
        
        results = parallel_batch_process(all_urls, process_batch, batch_size=20)
    """
    # Create batches
    batches = [items[i:i + batch_size] for i in range(0, len(items), batch_size)]
    
    # Process batches in parallel
    executor = ParallelTaskExecutor(max_workers=max_workers)
    tasks = [lambda b=batch: batch_processor(b) for batch in batches]
    task_results = executor.execute_parallel(tasks, task_ids=list(range(len(batches))))
    
    # Flatten results
    all_results = []
    for task_result in sorted(task_results, key=lambda r: r.task_id):
        if task_result.success and task_result.result:
            all_results.extend(task_result.result)
    
    return all_results
