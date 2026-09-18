#!/usr/bin/env python3
"""
Load testing script for E-Cell Portal
Tests capacity for 1000+ simultaneous students
"""

import asyncio
import time
from typing import List
import httpx
import json
from datetime import datetime

# Configuration
API_URL = "http://localhost:8000"
NUM_USERS = 100  # Can increase to 1000 for full load test
REQUESTS_PER_USER = 10
CONCURRENT_USERS = 50

class LoadTester:
    def __init__(self, api_url: str):
        self.api_url = api_url
        self.results = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "response_times": [],
            "errors": [],
        }
        self.start_time = None
        self.end_time = None

    async def test_health_check(self, client: httpx.AsyncClient) -> tuple[int, float]:
        """Test health check endpoint."""
        start = time.time()
        try:
            response = await client.get(f"{self.api_url}/health", timeout=10.0)
            duration = time.time() - start
            return response.status_code, duration
        except Exception as e:
            self.results["errors"].append(str(e))
            return 500, time.time() - start

    async def test_task_list(self, client: httpx.AsyncClient, token: str) -> tuple[int, float]:
        """Test getting task list."""
        start = time.time()
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = await client.get(
                f"{self.api_url}/api/tasks/participant/all",
                headers=headers,
                timeout=10.0
            )
            duration = time.time() - start
            return response.status_code, duration
        except Exception as e:
            self.results["errors"].append(str(e))
            return 500, time.time() - start

    async def simulate_user(self, user_id: int, token: str = "dummy_token") -> None:
        """Simulate a single user making requests."""
        async with httpx.AsyncClient() as client:
            for req_num in range(REQUESTS_PER_USER):
                # Alternate between health check and task list
                if req_num % 2 == 0:
                    status, duration = await self.test_health_check(client)
                else:
                    status, duration = await self.test_task_list(client, token)

                self.results["total_requests"] += 1
                self.results["response_times"].append(duration)

                if status == 200:
                    self.results["successful_requests"] += 1
                else:
                    self.results["failed_requests"] += 1

    async def run_load_test(self) -> None:
        """Run the load test with concurrent users."""
        print(f"\n{'='*60}")
        print("E-Cell Portal Load Test")
        print(f"{'='*60}")
        print(f"Number of simulated users: {NUM_USERS}")
        print(f"Requests per user: {REQUESTS_PER_USER}")
        print(f"Concurrent users: {CONCURRENT_USERS}")
        print(f"Total requests: {NUM_USERS * REQUESTS_PER_USER}")
        print(f"{'='*60}\n")

        self.start_time = time.time()

        # Create tasks for all users
        tasks = [
            self.simulate_user(user_id)
            for user_id in range(NUM_USERS)
        ]

        # Run with limited concurrency
        for i in range(0, len(tasks), CONCURRENT_USERS):
            batch = tasks[i:i + CONCURRENT_USERS]
            await asyncio.gather(*batch)
            print(f"Completed {min(i + CONCURRENT_USERS, len(tasks))}/{len(tasks)} users...")

        self.end_time = time.time()

    def print_results(self) -> None:
        """Print test results."""
        total_time = self.end_time - self.start_time
        
        print(f"\n{'='*60}")
        print("Load Test Results")
        print(f"{'='*60}")
        
        print(f"\nTiming:")
        print(f"  Total Duration: {total_time:.2f}s")
        print(f"  Requests/Second: {self.results['total_requests'] / total_time:.2f}")

        print(f"\nRequests:")
        print(f"  Total: {self.results['total_requests']}")
        print(f"  Successful: {self.results['successful_requests']} ({self.results['successful_requests']/self.results['total_requests']*100:.1f}%)")
        print(f"  Failed: {self.results['failed_requests']} ({self.results['failed_requests']/self.results['total_requests']*100:.1f}%)")

        if self.results["response_times"]:
            times = sorted(self.results["response_times"])
            print(f"\nResponse Times (seconds):")
            print(f"  Min: {times[0]:.3f}s")
            print(f"  Max: {times[-1]:.3f}s")
            print(f"  Mean: {sum(times)/len(times):.3f}s")
            print(f"  Median: {times[len(times)//2]:.3f}s")
            print(f"  p95: {times[int(len(times)*0.95)]:.3f}s")
            print(f"  p99: {times[int(len(times)*0.99)]:.3f}s")

        if self.results["errors"]:
            print(f"\nErrors ({len(self.results['errors'])}):")
            for error in self.results["errors"][:5]:  # Show first 5
                print(f"  - {error}")
            if len(self.results["errors"]) > 5:
                print(f"  ... and {len(self.results['errors']) - 5} more")

        print(f"\n{'='*60}")
        print("Capacity Assessment:")
        print(f"{'='*60}")
        
        success_rate = self.results["successful_requests"] / self.results["total_requests"]
        avg_response_time = sum(self.results["response_times"]) / len(self.results["response_times"])
        
        if success_rate >= 0.95 and avg_response_time < 1.0:
            print(f"✓ System can handle {NUM_USERS} concurrent users")
            print(f"✓ Estimated capacity: {int(NUM_USERS * (success_rate / 0.95))} users")
        elif success_rate >= 0.80:
            print(f"⚠ System handles {NUM_USERS} users but with degradation")
            print(f"✓ Recommended max users: {int(NUM_USERS * 0.8)}")
        else:
            print(f"✗ System cannot handle {NUM_USERS} concurrent users")
            print(f"✓ Reduce to: {int(NUM_USERS * 0.5)} users max")

        print(f"\n{'='*60}\n")

async def main():
    """Main function."""
    # Check if API is running
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_URL}/health", timeout=5.0)
            if response.status_code != 200:
                print(f"❌ API not ready (status {response.status_code})")
                return
    except Exception as e:
        print(f"❌ Cannot connect to API at {API_URL}")
        print(f"   Make sure backend is running: uvicorn app.main:app --reload")
        return

    print(f"✓ Connected to API at {API_URL}")

    # Run test
    tester = LoadTester(API_URL)
    await tester.run_load_test()
    tester.print_results()

if __name__ == "__main__":
    asyncio.run(main())
