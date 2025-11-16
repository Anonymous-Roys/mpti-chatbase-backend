#!/usr/bin/env python3
"""
Test script for MPTI Website Scraper
Run this to test the enhanced scraping functionality
"""

import requests
import json
import time
from datetime import datetime

# Backend URL
BACKEND_URL = "http://localhost:5000"

def test_health_check():
    """Test the health check endpoint"""
    print("🔍 Testing health check...")
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Backend is healthy!")
            print(f"   Version: {data.get('version', 'unknown')}")
            print(f"   Website pages loaded: {data['components']['website_content_loaded']}")
            print(f"   Total documents: {data['components']['total_documents']}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_comprehensive_scraping():
    """Test comprehensive website scraping"""
    print("\n🚀 Testing comprehensive MPTI website scraping...")
    try:
        response = requests.post(f"{BACKEND_URL}/scrape/comprehensive", timeout=120)
        if response.status_code == 200:
            data = response.json()
            print("✅ Comprehensive scraping completed!")
            print(f"   Pages scraped: {data.get('pages_scraped', 0)}")
            print(f"   Pages added: {data.get('pages_added', 0)}")
            print(f"   Total documents: {data.get('total_documents', 0)}")
            print(f"   Scraped pages: {', '.join(data.get('scraped_pages', [])[:5])}...")
            return True
        else:
            print(f"❌ Scraping failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Scraping error: {e}")
        return False

def test_knowledge_stats():
    """Test knowledge base statistics"""
    print("\n📊 Testing knowledge base statistics...")
    try:
        response = requests.get(f"{BACKEND_URL}/knowledge/stats", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Knowledge base stats retrieved!")
            print(f"   Total documents: {data.get('total_documents', 0)}")
            print(f"   Website documents: {data.get('website_documents', 0)}")
            print(f"   Fallback documents: {data.get('fallback_documents', 0)}")
            
            # Show some document details
            if 'document_details' in data:
                for doc_type, docs in data['document_details'].items():
                    print(f"   {doc_type.title()} docs: {len(docs)}")
                    if docs:
                        print(f"     Example: {docs[0]['id']} ({docs[0]['length']} chars)")
            return True
        else:
            print(f"❌ Stats failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Stats error: {e}")
        return False

def test_chat_functionality():
    """Test chat with MPTI knowledge"""
    print("\n💬 Testing chat functionality...")
    
    test_messages = [
        "Hello, tell me about MPTI",
        "What courses does MPTI offer?",
        "How can I apply to MPTI?",
        "What are the admission requirements?",
        "How can I contact MPTI?"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n   Test {i}: '{message}'")
        try:
            response = requests.post(f"{BACKEND_URL}/chat/ai", 
                json={
                    'message': message,
                    'conversation_id': 'test_conversation',
                    'use_ai': True
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                reply = data.get('reply', '')
                source = data.get('source', 'unknown')
                sources_used = data.get('sources_used', 0)
                response_time = data.get('response_time', 0)
                
                print(f"   ✅ Response ({source}, {sources_used} sources, {response_time:.2f}s):")
                print(f"      {reply[:150]}{'...' if len(reply) > 150 else ''}")
            else:
                print(f"   ❌ Chat failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Chat error: {e}")
        
        time.sleep(1)  # Be respectful

def main():
    """Run all tests"""
    print("🧪 MPTI Chatbase Backend Test Suite")
    print("=" * 50)
    
    # Test health first
    if not test_health_check():
        print("\n❌ Backend is not running or not healthy. Please start the backend first.")
        return
    
    # Test scraping
    test_comprehensive_scraping()
    
    # Test stats
    test_knowledge_stats()
    
    # Test chat
    test_chat_functionality()
    
    print("\n" + "=" * 50)
    print("🎉 Test suite completed!")
    print("\nNext steps:")
    print("1. Check the backend logs for detailed scraping information")
    print("2. Test the WordPress plugin integration")
    print("3. Verify that responses contain accurate MPTI information")

if __name__ == "__main__":
    main()