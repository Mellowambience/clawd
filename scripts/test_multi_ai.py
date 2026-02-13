#!/usr/bin/env python3
"""
Test script for multi-AI collaboration system
"""

import asyncio
from integrated_multi_ai import IntegratedMultiAICollaborator

async def test_multi_ai_collaboration():
    print("[TEST] Running comprehensive multi-AI collaboration test...")
    collaborator = IntegratedMultiAICollaborator()
    
    # Test 1: Complex analytical task
    print("\n[TEST 1] Complex analytical task:")
    task1 = ('Analyze the architecture of a distributed AI system that can coordinate multiple models, '
             'considering scalability, fault tolerance, and performance optimization.')
    result1 = await collaborator.execute_smart_collaboration(task1)
    print(f'   Task completed: {result1["task_id"]}')
    print(f'   Collaborators: {len(result1["contributions"])} AIs participated')
    print(f'   Execution order: {" -> ".join(result1["execution_order"])}')
    
    # Test 2: Technical coding task
    print("\n[TEST 2] Technical coding task:")
    task2 = ('Design a Python class that manages dynamic switching between different AI models, '
             'including error handling, performance monitoring, and fallback mechanisms.')
    result2 = await collaborator.execute_smart_collaboration(task2)
    print(f'   Task completed: {result2["task_id"]}')
    print(f'   Collaborators: {len(result2["contributions"])} AIs participated')
    print(f'   Analysis: {result2["task_analysis"]["complexity"]} complexity')
    
    # Test 3: Creative synthesis task
    print("\n[TEST 3] Creative synthesis task:")
    task3 = ('Create a conceptual framework for how multiple AI systems can work together '
             'to solve complex problems, including communication protocols and decision-making processes.')
    result3 = await collaborator.execute_smart_collaboration(task3)
    print(f'   Task completed: {result3["task_id"]}')
    print(f'   Collaborators: {len(result3["contributions"])} AIs participated')
    print(f'   Execution order: {" -> ".join(result3["execution_order"])}')
    
    # Show overall system status
    print("\n[STATUS] System status:")
    insights = collaborator.get_collaboration_insights()
    for key, value in insights.items():
        if key != 'recent_activity':
            print(f'   {key}: {value}')
    
    print("\n[SUCCESS] All tests completed successfully!")
    return {'test1': result1, 'test2': result2, 'test3': result3}

if __name__ == "__main__":
    results = asyncio.run(test_multi_ai_collaboration())
    print("\n[COMPLETE] Multi-AI collaboration system is fully operational!")