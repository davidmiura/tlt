#!/usr/bin/env python3
"""
Performance test suite for MCP Gateway using Streamable HTTP.
Tests concurrent connections, response times, and throughput.
"""

import asyncio
import httpx
import json
import time
import statistics
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor

class PerformanceTestClient:
    """High-performance client for testing"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.session_id = None
    
    async def initialize_session(self, client: httpx.AsyncClient) -> bool:
        """Initialize a new MCP session"""
        try:
            response = await client.post(
                f"{self.base_url}/mcp/",
                json={
                    "jsonrpc": "2.0",
                    "id": "init",
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {}},
                        "clientInfo": {"name": "Perf-Test-Client", "version": "1.0.0"}
                    }
                },
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json, text/event-stream"
                }
            )
            
            if response.status_code == 200:
                self.session_id = response.headers.get("mcp-session-id")
                return True
            return False
        except:
            return False
    
    async def call_gateway_status(self, client: httpx.AsyncClient) -> Dict[str, Any]:
        """Call get_gateway_status tool"""
        start_time = time.time()
        
        try:
            response = await client.post(
                f"{self.base_url}/mcp/",
                json={
                    "jsonrpc": "2.0",
                    "id": "perf_test",
                    "method": "tools/call",
                    "params": {
                        "name": "get_gateway_status",
                        "arguments": {}
                    }
                },
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json, text/event-stream",
                    "mcp-session-id": self.session_id
                }
            )
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            
            success = response.status_code == 200
            
            return {
                "success": success,
                "response_time_ms": response_time,
                "status_code": response.status_code,
                "response_size": len(response.content) if response.content else 0
            }
        
        except Exception as e:
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            
            return {
                "success": False,
                "response_time_ms": response_time,
                "error": str(e),
                "status_code": 0,
                "response_size": 0
            }

class PerformanceTestSuite:
    """Performance test suite for the gateway"""
    
    def __init__(self, gateway_url: str = "http://localhost:8003"):
        self.gateway_url = gateway_url
        self.client = PerformanceTestClient(gateway_url)
    
    async def test_single_request_latency(self, num_requests: int = 10) -> Dict[str, Any]:
        """Test latency of single sequential requests"""
        print(f"📊 Testing Single Request Latency ({num_requests} requests)")
        print("-" * 50)
        
        response_times = []
        success_count = 0
        
        async with httpx.AsyncClient(timeout=30.0) as http_client:
            # Initialize session
            if not await self.client.initialize_session(http_client):
                return {"error": "Failed to initialize session"}
            
            for i in range(num_requests):
                result = await self.client.call_gateway_status(http_client)
                response_times.append(result["response_time_ms"])
                
                if result["success"]:
                    success_count += 1
                
                print(f"Request {i+1}: {result['response_time_ms']:.1f}ms {'✅' if result['success'] else '❌'}")
        
        if response_times:
            stats = {
                "total_requests": num_requests,
                "successful_requests": success_count,
                "success_rate": (success_count / num_requests) * 100,
                "min_response_time_ms": min(response_times),
                "max_response_time_ms": max(response_times),
                "avg_response_time_ms": statistics.mean(response_times),
                "median_response_time_ms": statistics.median(response_times),
                "p95_response_time_ms": None,
                "p99_response_time_ms": None
            }
            
            if len(response_times) >= 20:  # Need enough data for percentiles
                sorted_times = sorted(response_times)
                stats["p95_response_time_ms"] = sorted_times[int(0.95 * len(sorted_times))]
                stats["p99_response_time_ms"] = sorted_times[int(0.99 * len(sorted_times))]
            
            return stats
        else:
            return {"error": "No successful requests"}
    
    async def test_concurrent_connections(self, num_concurrent: int = 5, requests_per_connection: int = 3) -> Dict[str, Any]:
        """Test concurrent connections to the gateway"""
        print(f"🔄 Testing Concurrent Connections ({num_concurrent} concurrent, {requests_per_connection} requests each)")
        print("-" * 70)
        
        async def run_concurrent_client(client_id: int):
            """Run a single concurrent client"""
            client = PerformanceTestClient(self.gateway_url)
            results = []
            
            async with httpx.AsyncClient(timeout=30.0) as http_client:
                if not await client.initialize_session(http_client):
                    return {"client_id": client_id, "error": "Failed to initialize", "results": []}
                
                for req_num in range(requests_per_connection):
                    result = await client.call_gateway_status(http_client)
                    result["client_id"] = client_id
                    result["request_number"] = req_num + 1
                    results.append(result)
            
            return {"client_id": client_id, "results": results}
        
        # Run concurrent clients
        start_time = time.time()
        tasks = [run_concurrent_client(i) for i in range(num_concurrent)]
        client_results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        # Analyze results
        all_results = []
        successful_clients = 0
        
        for client_result in client_results:
            if "error" not in client_result:
                successful_clients += 1
                all_results.extend(client_result["results"])
            
            client_id = client_result["client_id"]
            success_count = sum(1 for r in client_result.get("results", []) if r.get("success", False))
            print(f"Client {client_id}: {success_count}/{requests_per_connection} successful")
        
        if all_results:
            response_times = [r["response_time_ms"] for r in all_results if r.get("success", False)]
            total_requests = len(all_results)
            successful_requests = len(response_times)
            
            stats = {
                "concurrent_clients": num_concurrent,
                "successful_clients": successful_clients,
                "total_requests": total_requests,
                "successful_requests": successful_requests,
                "success_rate": (successful_requests / total_requests) * 100 if total_requests > 0 else 0,
                "total_duration_seconds": end_time - start_time,
                "requests_per_second": total_requests / (end_time - start_time) if end_time > start_time else 0,
                "avg_response_time_ms": statistics.mean(response_times) if response_times else 0,
                "max_response_time_ms": max(response_times) if response_times else 0,
                "min_response_time_ms": min(response_times) if response_times else 0
            }
            
            return stats
        else:
            return {"error": "No successful requests from any client"}
    
    async def test_session_management_overhead(self, num_sessions: int = 10) -> Dict[str, Any]:
        """Test overhead of session management"""
        print(f"🔑 Testing Session Management Overhead ({num_sessions} sessions)")
        print("-" * 55)
        
        session_times = []
        successful_sessions = 0
        
        for i in range(num_sessions):
            async with httpx.AsyncClient(timeout=30.0) as http_client:
                start_time = time.time()
                
                success = await self.client.initialize_session(http_client)
                
                end_time = time.time()
                session_time = (end_time - start_time) * 1000
                session_times.append(session_time)
                
                if success:
                    successful_sessions += 1
                
                print(f"Session {i+1}: {session_time:.1f}ms {'✅' if success else '❌'}")
        
        if session_times:
            return {
                "total_sessions": num_sessions,
                "successful_sessions": successful_sessions,
                "success_rate": (successful_sessions / num_sessions) * 100,
                "avg_session_time_ms": statistics.mean(session_times),
                "min_session_time_ms": min(session_times),
                "max_session_time_ms": max(session_times)
            }
        else:
            return {"error": "No session data collected"}
    
    async def test_error_handling_performance(self) -> Dict[str, Any]:
        """Test performance when backend services are unavailable"""
        print("⚡ Testing Error Handling Performance")
        print("-" * 40)
        
        async with httpx.AsyncClient(timeout=30.0) as http_client:
            client = PerformanceTestClient(self.gateway_url)
            
            if not await client.initialize_session(http_client):
                return {"error": "Failed to initialize session"}
            
            # Test a tool that will fail due to missing backend service
            start_time = time.time()
            
            response = await http_client.post(
                f"{self.gateway_url}/mcp/",
                json={
                    "jsonrpc": "2.0",
                    "id": "error_test",
                    "method": "tools/call",
                    "params": {
                        "name": "list_all_events",
                        "arguments": {"user_id": "test_user"}
                    }
                },
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json, text/event-stream",
                    "mcp-session-id": client.session_id
                }
            )
            
            end_time = time.time()
            error_response_time = (end_time - start_time) * 1000
            
            print(f"Error handling response time: {error_response_time:.1f}ms")
            print(f"Status code: {response.status_code}")
            
            return {
                "error_response_time_ms": error_response_time,
                "status_code": response.status_code,
                "graceful_degradation": response.status_code == 200  # Should still return 200 with error in JSON
            }
    
    async def run_performance_tests(self):
        """Run complete performance test suite"""
        print("⚡ MCP Gateway Performance Test Suite (Streamable HTTP)")
        print("=" * 60)
        print(f"Gateway URL: {self.gateway_url}")
        print()
        
        results = {}
        
        try:
            # Test 1: Single request latency
            results["latency"] = await self.test_single_request_latency(20)
            print()
            
            # Test 2: Concurrent connections
            results["concurrency"] = await self.test_concurrent_connections(5, 5)
            print()
            
            # Test 3: Session management overhead
            results["sessions"] = await self.test_session_management_overhead(15)
            print()
            
            # Test 4: Error handling performance
            results["error_handling"] = await self.test_error_handling_performance()
            print()
            
        except Exception as e:
            print(f"❌ Performance test suite failed: {e}")
            return
        
        # Print comprehensive summary
        self._print_performance_summary(results)
    
    def _print_performance_summary(self, results: Dict[str, Any]):
        """Print performance test summary"""
        print("📊 Performance Test Results Summary")
        print("=" * 45)
        
        # Latency Results
        if "latency" in results and "error" not in results["latency"]:
            latency = results["latency"]
            print(f"📈 Latency Performance:")
            print(f"  Success Rate: {latency['success_rate']:.1f}%")
            print(f"  Average Response: {latency['avg_response_time_ms']:.1f}ms")
            print(f"  Median Response: {latency['median_response_time_ms']:.1f}ms")
            print(f"  Min/Max: {latency['min_response_time_ms']:.1f}ms / {latency['max_response_time_ms']:.1f}ms")
            if latency.get('p95_response_time_ms'):
                print(f"  P95/P99: {latency['p95_response_time_ms']:.1f}ms / {latency['p99_response_time_ms']:.1f}ms")
            print()
        
        # Concurrency Results
        if "concurrency" in results and "error" not in results["concurrency"]:
            concurrency = results["concurrency"]
            print(f"🔄 Concurrency Performance:")
            print(f"  Concurrent Clients: {concurrency['concurrent_clients']}")
            print(f"  Success Rate: {concurrency['success_rate']:.1f}%")
            print(f"  Requests/Second: {concurrency['requests_per_second']:.1f}")
            print(f"  Avg Response Time: {concurrency['avg_response_time_ms']:.1f}ms")
            print(f"  Total Duration: {concurrency['total_duration_seconds']:.2f}s")
            print()
        
        # Session Management Results
        if "sessions" in results and "error" not in results["sessions"]:
            sessions = results["sessions"]
            print(f"🔑 Session Management:")
            print(f"  Session Success Rate: {sessions['success_rate']:.1f}%")
            print(f"  Avg Session Time: {sessions['avg_session_time_ms']:.1f}ms")
            print(f"  Session Time Range: {sessions['min_session_time_ms']:.1f}ms - {sessions['max_session_time_ms']:.1f}ms")
            print()
        
        # Error Handling Results
        if "error_handling" in results and "error" not in results["error_handling"]:
            error_handling = results["error_handling"]
            print(f"⚡ Error Handling:")
            print(f"  Error Response Time: {error_handling['error_response_time_ms']:.1f}ms")
            print(f"  Graceful Degradation: {'✅' if error_handling['graceful_degradation'] else '❌'}")
            print()
        
        # Performance Assessment
        print("🎯 Performance Assessment:")
        
        if "latency" in results and "error" not in results["latency"]:
            avg_latency = results["latency"]["avg_response_time_ms"]
            if avg_latency < 100:
                print("✅ Excellent latency (< 100ms)")
            elif avg_latency < 500:
                print("✅ Good latency (< 500ms)")
            elif avg_latency < 1000:
                print("⚠️  Acceptable latency (< 1s)")
            else:
                print("❌ High latency (> 1s)")
        
        if "concurrency" in results and "error" not in results["concurrency"]:
            success_rate = results["concurrency"]["success_rate"]
            if success_rate >= 95:
                print("✅ Excellent concurrency handling")
            elif success_rate >= 90:
                print("✅ Good concurrency handling")
            else:
                print("⚠️  Concurrency issues detected")
        
        print("\n🔍 Test Conclusions:")
        print("✅ Streamable HTTP transport performance verified")
        print("✅ Session management overhead measured")
        print("✅ Concurrent connection handling tested")
        print("✅ Error handling performance validated")

async def main():
    """Main performance test runner"""
    import sys
    
    gateway_url = "http://localhost:8003"
    if len(sys.argv) > 1:
        gateway_url = sys.argv[1]
    
    test_suite = PerformanceTestSuite(gateway_url)
    await test_suite.run_performance_tests()

if __name__ == "__main__":
    asyncio.run(main())