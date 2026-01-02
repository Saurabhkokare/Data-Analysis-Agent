const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface AnalysisResponse {
  response: string;
  image_paths?: string[];
  pdf_path?: string;
  ppt_path?: string;
  dashboard_path?: string;
}

export const api = {
  async uploadAndAnalyze(file: File, prompt: string): Promise<AnalysisResponse> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('prompt', prompt);

    const response = await fetch(`${API_BASE_URL}/analyze`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error('Analysis request failed');
    }

    return response.json();
  },

  async analyzeWithExistingData(prompt: string): Promise<AnalysisResponse> {
    const formData = new FormData();
    formData.append('prompt', prompt);

    const response = await fetch(`${API_BASE_URL}/analyze`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error('Analysis request failed');
    }

    return response.json();
  },

  async downloadReport(filename: string): Promise<Blob> {
    const response = await fetch(`${API_BASE_URL}/download/${filename}`);

    if (!response.ok) {
      throw new Error('Download failed');
    }

    return response.blob();
  },
};
