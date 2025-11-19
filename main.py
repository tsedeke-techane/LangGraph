from graph_builder import graph
from langgraph.types import Command
import traceback
import time
from datetime import datetime

def main():
    try:
        print("🤖 AI Content Generation Bot")
        print("📊 Execution Tracking: ENABLED")
        print("=" * 50)
        
        config = {'configurable': {"thread_id": 'buy-thread'}}
        session_stats = []

        while True:
            user_input = input("\n💬 You: ").strip()
            
            if user_input.lower() in ["exit", "quit"]:
                print(f"\n📈 Session Summary - {len(session_stats)} requests:")
                for i, stat in enumerate(session_stats, 1):
                    print(f"  {i}. {stat}")
                print("👋 Goodbye!")
                break

            if not user_input:
                print("⚠️  Please enter a message")
                continue

            # Track workflow execution
            print(f"\n🚀 Starting workflow at {datetime.now().strftime('%H:%M:%S')}")
            workflow_start = time.time()
            
            try:
                response = graph.invoke(
                    {"messages": [{"role": "user", "content": user_input}]}, 
                    config=config
                )
                
                workflow_elapsed = time.time() - workflow_start
                
                # Display response
                print(f"\n🤖 Bot Response:")
                print("=" * 40)
                
                # Print the last message (Summary)
                print(f"📝 FINAL SUMMARY:\n{response['messages'][-1].content}\n")

                # Print the Refined Article (usually the 3rd to last message, depending on flow)
                # We iterate backwards to find the last AI message before the summary/seo steps
                for msg in reversed(response["messages"]):
                    if msg.type == "ai" and "Keywords:" not in msg.content and len(msg.content) > 100:
                        print(f"📄 GENERATED CONTENT:\n{msg.content}")
                        break
                
                print("=" * 40)
                
                # Execution summary
                print(f"\n📊 Workflow Complete:")
                print(f"  ⏱️  Total time: {workflow_elapsed:.2f}s")
                print(f"  📝 Input: '{user_input[:30]}{'...' if len(user_input) > 30 else ''}'")
                
                # Store session stats
                session_stats.append(f"{workflow_elapsed:.2f}s - '{user_input[:20]}...'")

            except Exception as e:
                workflow_elapsed = time.time() - workflow_start
                print(f"❌ Workflow failed after {workflow_elapsed:.2f}s: {e}")

            # Approval handling with tracking
            if not response["messages"][-1].content:
                
                print(f"\n⏳ Approval required at {datetime.now().strftime('%H:%M:%S')}")
                approval_start = time.time()
                
                decision = input("✅ Approve (yes/no): ").strip().lower()
                
                try:
                    result = graph.invoke(Command(resume=decision), config=config)
                    approval_elapsed = time.time() - approval_start
                    
                    print(f"\n🤖 Bot: {result['messages'][-1].content}")
                    print(f"⏱️  Approval processed in: {approval_elapsed:.2f}s")
                    
                except Exception as e:
                    print(f"❌ Approval processing failed: {e}")

    except Exception:
        print("\n💥 Fatal error:")
        print(traceback.format_exc())

if __name__ == "__main__":
    main()