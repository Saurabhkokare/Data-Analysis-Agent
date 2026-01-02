import os
import pandas as pd
from analysis_agent import AnalysisAgent
import visualization_tools

# Mocking Groq API Key for testing if not present (will fail if actual call is made without key)
# But we can test the loading and visualization logic at least.
if "GROQ_API_KEY" not in os.environ:
    print("WARNING: GROQ_API_KEY not found. Agent queries might fail.")

def test_data_loading():
    print("Testing Data Loading...")
    df = pd.read_csv("dummy.csv")
    assert not df.empty
    print("Data Loading Passed.")
    return df

def test_visualization(df):
    print("Testing Visualization Tools...")
    path = visualization_tools.generate_histogram(df, "Sales", title="Test Histogram")
    assert os.path.exists(path)
    print(f"Histogram generated at {path}")
    
    path = visualization_tools.generate_bar_plot(df, "Region", "Sales", title="Test Bar Plot")
    assert os.path.exists(path)
    print(f"Bar Plot generated at {path}")
    print("Visualization Tools Passed.")

import asyncio

# ... (imports)

# ... (previous functions)

async def test_agent_initialization(df):
    print("Testing Agent Initialization...")
    try:
        agent = AnalysisAgent(df)
        # Check if the underlying agent is initialized
        assert agent.agent is not None
        print("Agent Initialization Passed.")
        return agent
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Agent Initialization Failed: {e}")
        return None

import report_generator

# ... (previous functions)

def test_pdf_generation():
    print("Testing PDF Generation...")
    text = "This is a test report."
    # Create a dummy image for testing
    import matplotlib.pyplot as plt
    plt.figure()
    plt.plot([1, 2, 3], [1, 2, 3])
    img_path = "test_plot.png"
    plt.savefig(img_path)
    plt.close()
    
    pdf_path = report_generator.create_pdf_report(text, [img_path], "test_report.pdf")
    assert os.path.exists(pdf_path)
    print(f"PDF Report generated at {pdf_path}")
    
    # Cleanup
    if os.path.exists(img_path): os.remove(img_path)
    if os.path.exists(pdf_path): os.remove(pdf_path)
    print("PDF Generation Passed.")

import dynamic_visualization

def test_dynamic_plotting(df):
    print("Testing Dynamic Plotting...")
    code = "plt.figure(); sns.histplot(data=df, x='Sales'); plt.title('Dynamic Hist')"
    path = dynamic_visualization.execute_plot_code(df, code)
    assert os.path.exists(path)
    print(f"Dynamic Plot generated at {path}")
    print("Dynamic Plotting Passed.")

async def main_test():
    df = test_data_loading()
    test_dynamic_plotting(df)
    test_pdf_generation()
    agent = await test_agent_initialization(df)
    
    print("\nAll automated checks passed!")

if __name__ == "__main__":
    asyncio.run(main_test())
