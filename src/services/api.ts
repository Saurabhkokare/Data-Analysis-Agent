const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface ImageData {
  url: string;
  title: string;
  description: string;
}

export interface AnalysisResponse {
  response: string;
  images?: ImageData[];
  image_paths?: string[];
  pdf_path?: string;
  ppt_path?: string;
  dashboard_path?: string;
}

export type AgentType = 'auto' | 'pdf' | 'ppt' | 'dashboard' | 'data_analysis';

export const api = {
  async uploadAndAnalyze(file: File, prompt: string, agentType: AgentType = 'auto'): Promise<AnalysisResponse> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('prompt', prompt);
    if (agentType !== 'auto') {
      formData.append('agent_type', agentType);
    }

    const response = await fetch(`${API_BASE_URL}/analyze`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error('Analysis request failed');
    }

    return response.json();
  },

  async analyzeWithExistingData(prompt: string, agentType: AgentType = 'auto'): Promise<AnalysisResponse> {
    const formData = new FormData();
    formData.append('prompt', prompt);
    if (agentType !== 'auto') {
      formData.append('agent_type', agentType);
    }

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
