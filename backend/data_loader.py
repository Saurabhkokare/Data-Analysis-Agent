import pandas as pd
import io
import os

def load_data(file_path_or_content, file_type=None):
    """
    Loads data from a file path or string content into a Pandas DataFrame.
    
    Args:
        file_path_or_content (str): Path to the file or the content string.
        file_type (str, optional): 'csv', 'excel', or 'text'. If None, tries to infer from extension.
        
    Returns:
        pd.DataFrame: The loaded data.
    """
    try:
        if os.path.exists(file_path_or_content):
            # It's a file path
            ext = os.path.splitext(file_path_or_content)[1].lower()
            if ext == '.csv':
                return pd.read_csv(file_path_or_content)
            elif ext in ['.xlsx', '.xls']:
                return pd.read_excel(file_path_or_content)
            elif ext == '.txt':
                # Assuming tab-separated or comma-separated text file
                try:
                    return pd.read_csv(file_path_or_content, sep='\t')
                except:
                    return pd.read_csv(file_path_or_content)
            else:
                raise ValueError(f"Unsupported file extension: {ext}")
        else:
            # It's content string
            if file_type == 'csv':
                return pd.read_csv(io.StringIO(file_path_or_content))
            elif file_type == 'json':
                 return pd.read_json(io.StringIO(file_path_or_content))
            else:
                # Try to guess or default to CSV-like
                try:
                    return pd.read_csv(io.StringIO(file_path_or_content))
                except:
                    # If that fails, maybe it's just raw text lines?
                    return pd.DataFrame([x.split() for x in file_path_or_content.split('\n')])

    except Exception as e:
        print(f"Error loading data: {e}")
        return None
