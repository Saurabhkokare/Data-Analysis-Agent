import React, { useState, useRef, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { api, AnalysisResponse, ImageData, AgentType } from '../services/api';
import '../styles/Chat.css';

interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  images?: string[];
  imageData?: ImageData[];  // New: images with title and description
  pdfPath?: string;
  pptPath?: string;
  dashboardPath?: string;
}

// Helper function to clean markdown formatting and file paths from text
const cleanMarkdown = (text: string): string => {
  if (!text) return '';
  return text
    .replace(/\*\*([^*]+)\*\*/g, '$1')  // Bold **text**
    .replace(/\*([^*]+)\*/g, '$1')      // Italic *text*
    .replace(/^#{1,6}\s+/gm, '')        // Headers # ## ###
    .replace(/```[\s\S]*?```/g, '')     // Code blocks
    .replace(/`([^`]+)`/g, '$1')        // Inline code
    .replace(/^[\-\*]\s+/gm, '• ')      // Bullet points
    .replace(/^\d+\.\s+/gm, '')         // Numbered lists
    .replace(/\|/g, ' ')                // Table pipes
    .replace(/^[-=]+$/gm, '')           // Horizontal rules
    .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')  // Links
    // Clean file paths
    .replace(/[A-Za-z]:\\[^\s]+\.(png|pdf|pptx|html)/gi, '')  // Windows paths
    .replace(/\/[^\s]+\.(png|pdf|pptx|html)/gi, '')  // Unix paths
    .replace(/[\w_-]+\.(png|pdf|pptx|html)/gi, '')  // Just filenames
    .replace(/The (PDF|PPT|dashboard|report|presentation|file) (is saved at|path is|located at|created at)[^.]*\./gi, '')  // Path descriptions
    .replace(/\n{3,}/g, '\n\n')         // Multiple newlines
    .trim();
};

export const Chat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const [latestPdf, setLatestPdf] = useState<string | null>(null);
  const [latestPpt, setLatestPpt] = useState<string | null>(null);
  const [latestDashboard, setLatestDashboard] = useState<string | null>(null);
  const [showDashboard, setShowDashboard] = useState(false);
  const [selectedAgent, setSelectedAgent] = useState<AgentType>('auto');

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleDrag = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const files = e.dataTransfer.files;
    if (files && files[0]) {
      setUploadedFile(files[0]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setUploadedFile(e.target.files[0]);
    }
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!input.trim()) return;

    const userMessage: Message = {
      id: Math.random().toString(36).substring(7),
      type: 'user',
      content: uploadedFile ? `📎 ${uploadedFile.name}\n\n${input}` : input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      let response: AnalysisResponse;

      if (uploadedFile) {
        response = await api.uploadAndAnalyze(uploadedFile, input, selectedAgent);
        setUploadedFile(null);
      } else {
        response = await api.analyzeWithExistingData(input, selectedAgent);
      }

      if (response.pdf_path) setLatestPdf(response.pdf_path);
      if (response.ppt_path) setLatestPpt(response.ppt_path);
      if (response.dashboard_path) setLatestDashboard(response.dashboard_path);

      const assistantMessage: Message = {
        id: Math.random().toString(36).substring(7),
        type: 'assistant',
        content: response.response,
        timestamp: new Date(),
        images: response.image_paths,
        imageData: response.images,  // New: includes title and description
        pdfPath: response.pdf_path,
        pptPath: response.ppt_path,
        dashboardPath: response.dashboard_path,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage: Message = {
        id: Math.random().toString(36).substring(7),
        type: 'assistant',
        content: `Error: ${error instanceof Error ? error.message : 'An unexpected error occurred'}`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadReport = (path: string) => {
    const link = document.createElement('a');
    link.href = path;
    link.download = path.split('/').pop() || 'report';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleOpenDashboard = (dashboardPath: string) => {
    window.open(dashboardPath, '_blank');
  };

  const handleClearChat = () => {
    if (confirm('Are you sure you want to clear the chat history?')) {
      setMessages([]);
      setUploadedFile(null);
      setLatestPdf(null);
      setLatestPpt(null);
      setLatestDashboard(null);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <div className="chat-container">
      <div className="auth-background">
        <div className="gradient-sphere sphere-1"></div>
        <div className="gradient-sphere sphere-2"></div>
        <div className="gradient-sphere sphere-3"></div>
      </div>

      {/* Dashboard Preview Modal */}
      {showDashboard && latestDashboard && (
        <div className="dashboard-modal">
          <div className="dashboard-modal-header">
            <h2>📊 Dashboard Preview</h2>
            <div className="dashboard-modal-actions">
              <button
                className="modal-btn open-btn"
                onClick={() => window.open(latestDashboard, '_blank')}
                title="Open in new tab"
              >
                Open in New Tab
              </button>
              <button
                className="modal-btn close-btn"
                onClick={() => setShowDashboard(false)}
                title="Close"
              >
                ✕
              </button>
            </div>
          </div>
          <iframe
            src={latestDashboard}
            className="dashboard-iframe"
            title="Dashboard Preview"
          />
        </div>
      )}

      <div className="chat-header">
        <div className="header-left">
          <Link to="/" className="home-btn" title="Home">🏠</Link>
          <Link to="/hub" className="back-btn" title="Back to Hub">← Hub</Link>
          <span className="header-logo">📊</span>
          <h1>Data Analysis Agent</h1>
          <button
            className="header-action-btn dashboard-create-btn"
            onClick={() => {
              if (latestDashboard) {
                setShowDashboard(true);
              } else {
                setInput('Create an interactive dashboard for this data');
                const form = document.querySelector('.chat-input-area') as HTMLFormElement;
                if (form) form.dispatchEvent(new Event('submit', { bubbles: true }));
              }
            }}
            title={latestDashboard ? 'View Dashboard' : 'Create Dashboard'}
          >
            📈 Dashboard
          </button>
        </div>
        <div className="header-right">
          <div className="header-reports">
            {latestPdf && (
              <button
                className="header-report-btn pdf-btn"
                onClick={() => handleDownloadReport(latestPdf)}
                title="Download PDF Report"
              >
                📄 PDF
              </button>
            )}
            {latestPpt && (
              <button
                className="header-report-btn ppt-btn"
                onClick={() => handleDownloadReport(latestPpt)}
                title="Download PowerPoint"
              >
                📊 PPT
              </button>
            )}
            {latestDashboard && (
              <button
                className="header-report-btn dashboard-btn"
                onClick={() => handleOpenDashboard(latestDashboard)}
                title="Open Dashboard"
              >
                📈 Dashboard
              </button>
            )}
          </div>

          {user && (
            <div className="user-info">
              <img
                src={user.avatar || `https://api.dicebear.com/7.x/initials/svg?seed=${user.name}`}
                alt={user.name}
                className="user-avatar"
              />
              <span className="user-name">{user.name}</span>
            </div>
          )}
          <button
            className="header-btn"
            onClick={handleClearChat}
            title="Clear chat"
          >
            🗑️
          </button>
          <button
            className="header-btn logout-btn"
            onClick={handleLogout}
            title="Logout"
          >
            Logout
          </button>
        </div>
      </div>

      <div className="messages-container">
        {messages.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">📊</div>
            <h2>Welcome to Data Analysis Agent</h2>
            <p>Upload a file or ask a question to get started</p>
          </div>
        ) : (
          messages.map((message) => (
            <div key={message.id} className={`message message-${message.type}`}>
              <div className="message-avatar">
                {message.type === 'user' ? '👤' : '🤖'}
              </div>
              <div className="message-content">
                <div className="message-text" style={{ whiteSpace: 'pre-wrap' }}>
                  {message.type === 'assistant' ? cleanMarkdown(message.content) : message.content}
                </div>
                {/* Display images with titles and descriptions */}
                {message.imageData && message.imageData.length > 0 ? (
                  <div className="message-images">
                    {message.imageData.map((img, idx) => (
                      <div key={idx} className="image-card">
                        <div className="image-card-header">
                          <span className="image-title">📊 {img.title}</span>
                        </div>
                        <img
                          src={img.url}
                          alt={img.title}
                          className="analysis-image"
                        />
                        <div className="image-description">
                          {img.description}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : message.images && message.images.length > 0 && (
                  <div className="message-images">
                    {message.images.map((imgPath, idx) => (
                      <div key={idx} className="image-card">
                        <img
                          src={imgPath}
                          alt={`Analysis ${idx + 1}`}
                          className="analysis-image"
                        />
                      </div>
                    ))}
                  </div>
                )}
                {(message.pdfPath || message.pptPath || message.dashboardPath) && (
                  <div className="download-buttons">
                    {message.pdfPath && (
                      <button
                        className="download-btn download-btn-pdf"
                        onClick={() => handleDownloadReport(message.pdfPath!)}
                      >
                        📄 Download PDF
                      </button>
                    )}
                    {message.pptPath && (
                      <button
                        className="download-btn download-btn-ppt"
                        onClick={() => handleDownloadReport(message.pptPath!)}
                      >
                        📊 Download PPT
                      </button>
                    )}
                    {message.dashboardPath && (
                      <button
                        className="download-btn download-btn-dashboard"
                        onClick={() => handleOpenDashboard(message.dashboardPath!)}
                      >
                        📈 Open Dashboard
                      </button>
                    )}
                  </div>
                )}
                <span className="message-time">
                  {message.timestamp.toLocaleTimeString()}
                </span>
              </div>
            </div>
          ))
        )}
        {loading && (
          <div className="message message-assistant">
            <div className="message-avatar">🤖</div>
            <div className="message-content">
              <div className="loading-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSendMessage} className="chat-input-area">
        <div
          className={`file-upload-zone ${dragActive ? 'active' : ''}`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <input
            ref={fileInputRef}
            type="file"
            onChange={handleFileChange}
            accept=".csv,.xlsx,.xls,.txt,.json"
            style={{ display: 'none' }}
          />
          {uploadedFile ? (
            <div className="file-preview">
              <span>📎 {uploadedFile.name}</span>
              <button
                type="button"
                onClick={() => {
                  setUploadedFile(null);
                  if (fileInputRef.current) fileInputRef.current.value = '';
                }}
                className="remove-file-btn"
              >
                ✕
              </button>
            </div>
          ) : (
            <button
              type="button"
              className="upload-btn"
              onClick={() => fileInputRef.current?.click()}
            >
              📁 Upload File
            </button>
          )}
        </div>

        {/* Agent Type Selector */}
        <div className="agent-selector">
          <label className="agent-selector-label">Agent:</label>
          <select
            value={selectedAgent}
            onChange={(e) => setSelectedAgent(e.target.value as AgentType)}
            className="agent-dropdown"
            disabled={loading}
          >
            <option value="auto">🔄 Auto Detect</option>
            <option value="data_analysis">📊 Data Analysis & Graphs</option>
            <option value="pdf">📄 PDF Report</option>
            <option value="ppt">📑 PowerPoint</option>
            <option value="dashboard">📈 Dashboard</option>
          </select>
        </div>

        <div className="input-row">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => {
              setInput(e.target.value);
              // Auto-resize textarea
              if (textareaRef.current) {
                textareaRef.current.style.height = 'auto';
                textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 250) + 'px';
              }
            }}
            onKeyDown={(e) => {
              // Submit on Enter (without Shift)
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                if (input.trim() && !loading) {
                  handleSendMessage(e as any);
                  // Reset textarea height
                  if (textareaRef.current) {
                    textareaRef.current.style.height = 'auto';
                  }
                }
              }
            }}
            placeholder="Ask me anything about your data... (Shift+Enter for new line)"
            disabled={loading}
            className="chat-input chat-textarea"
            rows={1}
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="send-btn"
            onClick={() => {
              // Reset textarea height on submit
              if (textareaRef.current) {
                textareaRef.current.style.height = 'auto';
              }
            }}
          >
            {loading ? '⏳' : '➤'}
          </button>
        </div>
      </form>
    </div>
  );
};
