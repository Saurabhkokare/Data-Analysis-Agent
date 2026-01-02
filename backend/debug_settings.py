from llama_index.core import Settings
from llama_index.llms.groq import Groq
import os

try:
    print("Testing Settings.llm assignment...")
    llm = Groq(model="llama3-70b-8192", api_key="fake")
    Settings.llm = llm
    print("Settings.llm assigned successfully.")
    print(f"Settings.llm type: {type(Settings.llm)}")
    
    import pandas as pd
    from llama_index.experimental.query_engine import PandasQueryEngine
    
    print("Testing PandasQueryEngine initialization...")
    df = pd.DataFrame({"a": [1, 2, 3]})
    pqe = PandasQueryEngine(df=df, llm=llm)
    print("PandasQueryEngine initialized successfully.")
    
    from llama_index.core.tools import QueryEngineTool, ToolMetadata
    data_tool = QueryEngineTool(
        query_engine=pqe,
        metadata=ToolMetadata(name="data_tool", description="test")
    )
    
    from llama_index.core.tools import FunctionTool
    def test_fn(a: int) -> int:
        return a
    viz_tool = FunctionTool.from_defaults(fn=test_fn, name="test_tool")
    
    from llama_index.core.agent import FunctionAgent
    print("Testing FunctionAgent initialization...")
    agent = FunctionAgent(
        tools=[data_tool, viz_tool],
        llm=llm,
        system_prompt="test"
    )
    print("FunctionAgent initialized successfully.")
except Exception as e:
    import traceback
    traceback.print_exc()
    print(f"FAILED with error: {e}")
