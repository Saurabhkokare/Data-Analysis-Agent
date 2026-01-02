import os
import sys
import asyncio
from dotenv import load_dotenv
import data_loader
from analysis_agent import AnalysisAgent

async def main():
    print("Welcome to the Data Analysis Multi-Agent System!")
    
    # Load environment variables
    load_dotenv()
    api_key = os.getenv("GROQ_API_KEY")
    
    # if not api_key:
    #     api_key = input("Please enter your Groq API Key: ").strip()
    #     if not api_key:
    #         print("API Key is required to proceed.")
    #         return

    # 1. Input Data
    print("\n--- Data Input ---")
    print("You can provide a file path (CSV, Excel, Text) or paste content directly.")
    source = input("Enter file path or 'paste' to paste content: ").strip()
    
    df = None
    if source.lower() == 'paste':
        print("Paste your data below (end with an empty line or Ctrl+D/Z):")
        lines = []
        try:
            while True:
                line = input()
                if not line: break
                lines.append(line)
        except EOFError:
            pass
        content = "\n".join(lines)
        df = data_loader.load_data(content)
    else:
        # Remove quotes if user added them
        source = source.strip('"').strip("'")
        df = data_loader.load_data(source)
        
    if df is None:
        print("Failed to load data. Exiting.")
        return
        
    print(f"\nData Loaded Successfully! Shape: {df.shape}")
    print("Columns:", list(df.columns))
    print(df.head())
    
    # 2. Initialize Agent
    agent = AnalysisAgent(df, api_key=api_key)
    
    # 3. Interaction Loop
    print("\n--- Analysis Session ---")
    print("Ask questions about your data, request graphs, or type 'exit' to quit.")
    
    session_history = []
    
    while True:
        user_input = input("\nUser: ").strip()
        if user_input.lower() in ['exit', 'quit', 'bye']:
            break
            
        if not user_input:
            continue
            
        try:
            print("Agent is thinking...")
            response = await agent.analyze(user_input)
            print(f"Agent: {response}")
            
            # Save history
            session_history.append({
                "query": user_input,
                "response": response
            })
            
        except Exception as e:
            print(f"An error occurred: {e}")
            import traceback
            traceback.print_exc()
            
    # 4. Save Session Output
    save_opt = input("\nDo you want to save this session? (y/n): ").lower()
    if save_opt == 'y':
        filename = "analysis_session_output.txt"
        with open(filename, "w", encoding='utf-8') as f:
            for entry in session_history:
                f.write(f"User: {entry['query']}\n")
                f.write(f"Agent: {entry['response']}\n")
                f.write("-" * 40 + "\n")
        print(f"Session saved to {filename}")

if __name__ == "__main__":
    asyncio.run(main())
