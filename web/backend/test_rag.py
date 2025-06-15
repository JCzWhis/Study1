"""
Test script for Medical RAG system
"""

import asyncio
import sys
import os

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

async def test_medical_rag():
    """Test the medical RAG system"""
    
    try:
        from app.core.medical_rag import medical_rag
        from app.core.llm_service import llm_service
        
        print("🚀 Testing Medical RAG System...")
        print("=" * 50)
        
        # Test 1: Initialize knowledge base
        print("\n1. Initializing knowledge base...")
        await medical_rag.initialize_knowledge_base()
        print("✅ Knowledge base initialized")
        
        # Test 2: Test knowledge retrieval
        print("\n2. Testing knowledge retrieval...")
        
        queries = [
            ("cardiologia", "insuficiencia cardiaca tratamiento"),
            ("medicina_interna", "diabetes tipo 2 manejo"),
            ("neurologia", "accidente cerebrovascular diagnostico")
        ]
        
        for specialty, query in queries:
            print(f"\n🔍 Query: {query} (Specialty: {specialty})")
            results = await medical_rag.retrieve_relevant_knowledge(
                query=query,
                specialty=specialty,
                n_results=2
            )
            
            if results:
                for i, result in enumerate(results):
                    print(f"  Result {i+1}:")
                    print(f"    Score: {result['relevance_score']:.3f}")
                    print(f"    Source: {result['source']}")
                    print(f"    Content: {result['content'][:200]}...")
            else:
                print("  No results found")
        
        # Test 3: Test enhanced plan generation
        print("\n3. Testing enhanced plan generation...")
        
        # Check if Ollama is available
        is_available = await llm_service.ollama.check_model_availability()
        if is_available:
            print("✅ Ollama/Phi3 available - testing full plan generation")
            
            plan = await llm_service.generate_study_plan(
                specialty="cardiologia",
                level="residente", 
                target_date="2025-08-01",
                current_knowledge={"anatomia": "intermedio"},
                specific_topics=["Insuficiencia Cardíaca", "Arritmias"]
            )
            
            print(f"📋 Generated Plan Title: {plan.get('plan_title', 'No title')}")
            print(f"📚 Number of topics: {len(plan.get('topics', []))}")
            
            if plan.get('topics'):
                print("📖 Sample topic:")
                sample_topic = plan['topics'][0]
                print(f"  - Name: {sample_topic.get('name', 'No name')}")
                print(f"  - Description: {sample_topic.get('description', 'No description')[:100]}...")
        else:
            print("⚠️ Ollama/Phi3 not available - testing RAG context only")
            
            context = await medical_rag.enhance_plan_generation_prompt(
                specialty="cardiologia",
                level="residente",
                topics=["Insuficiencia Cardíaca"]
            )
            
            print(f"📝 Enhanced context length: {len(context)} characters")
            if context:
                print(f"📄 Context preview: {context[:300]}...")
        
        print("\n" + "=" * 50)
        print("🎉 RAG Test completed successfully!")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all dependencies are installed:")
        print("pip install transformers torch sentence-transformers chromadb datasets")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_medical_rag())