import React, { useState, useRef, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { api, AnalysisResponse, ImageData, AgentType } from '../services/api';
import '../styles/Chat.css';

interface AgentPageProps {
    agentType: AgentType;
    title: string;
    icon: string;
    description: string;
    accentColor: string;
}

interface Message {
    id: string;
    type: 'user' | 'assistant';
    content: string;
    timestamp: Date;
    images?: string[];
    imageData?: ImageData[];
    pdfPath?: string;
    pptPath?: string;
    dashboardPath?: string;
}

const cleanMarkdown = (text: string): string => {
    if (!text) return '';
    return text
        .replace(/\*\*([^*]+)\*\*/g, '$1')
        .replace(/\*([^*]+)\*/g, '$1')
        .replace(/^#{1,6}\s+/gm, '')
        .replace(/```[\s\S]*?```/g, '')
        .replace(/`([^`]+)`/g, '$1')
        .replace(/^[\-\*]\s+/gm, '• ')
        .replace(/^\d+\.\s+/gm, '')
        .replace(/\|/g, ' ')
        .replace(/^[-=]+$/gm, '')
        .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
        .replace(/[A-Za-z]:\\[^\s]+\.(png|pdf|pptx|html)/gi, '')
        .replace(/\/[^\s]+\.(png|pdf|pptx|html)/gi, '')
        .replace(/[\w_-]+\.(png|pdf|pptx|html)/gi, '')
        .replace(/\n{3,}/g, '\n\n')
        .trim();
};

export const AgentPage: React.FC<AgentPageProps> = ({
    agentType,
    title,
    icon,
    description,
    accentColor
}) => {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [uploadedFile, setUploadedFile] = useState<File | null>(null);
    const [dragActive, setDragActive] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);
    const { user, logout } = useAuth();
    const navigate = useNavigate();

    const [latestPdf, setLatestPdf] = useState<string | null>(null);
    const [latestPpt, setLatestPpt] = useState<string | null>(null);
    const [latestDashboard, setLatestDashboard] = useState<string | null>(null);

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
                response = await api.uploadAndAnalyze(uploadedFile, input, agentType);
                setUploadedFile(null);
            } else {
                response = await api.analyzeWithExistingData(input, agentType);
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
                imageData: response.images,
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

    const handleLogout = () => {
        logout();
        navigate('/');
    };

    return (
        <div className="chat-container agent-page" style={{ '--agent-color': accentColor } as React.CSSProperties}>
            <div className="auth-background">
                <div className="gradient-sphere sphere-1"></div>
                <div className="gradient-sphere sphere-2"></div>
                <div className="gradient-sphere sphere-3"></div>
            </div>

            <div className="chat-header">
                <div className="header-left">
                    <Link to="/" className="home-btn" title="Home">🏠</Link>
                    <Link to="/hub" className="back-btn" title="Back to Hub">← Hub</Link>
                    <span className="header-logo">{icon}</span>
                    <h1>{title}</h1>
                </div>
                <div className="header-right">
                    <div className="header-reports">
                        {latestPdf && (
                            <button className="header-report-btn pdf-btn" onClick={() => handleDownloadReport(latestPdf)}>
                                📄 Download PDF
                            </button>
                        )}
                        {latestPpt && (
                            <button className="header-report-btn ppt-btn" onClick={() => handleDownloadReport(latestPpt)}>
                                📊 Download PPT
                            </button>
                        )}
                        {latestDashboard && (
                            <button className="header-report-btn dashboard-btn" onClick={() => window.open(latestDashboard, '_blank')}>
                                📈 Open Dashboard
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
                    <button className="header-btn logout-btn" onClick={handleLogout}>Logout</button>
                </div>
            </div>

            <div className="messages-container">
                {messages.length === 0 ? (
                    <div className="empty-state">
                        <div className="empty-icon">{icon}</div>
                        <h2>{title}</h2>
                        <p>{description}</p>
                        <p className="hint">Upload a data file to get started</p>
                    </div>
                ) : (
                    messages.map((message) => (
                        <div key={message.id} className={`message message-${message.type}`}>
                            <div className="message-avatar">
                                {message.type === 'user' ? '👤' : icon}
                            </div>
                            <div className="message-content">
                                <div className="message-text" style={{ whiteSpace: 'pre-wrap' }}>
                                    {message.type === 'assistant' ? cleanMarkdown(message.content) : message.content}
                                </div>
                                {message.imageData && message.imageData.length > 0 && (
                                    <div className="message-images">
                                        {message.imageData.map((img, idx) => (
                                            <div key={idx} className="image-card">
                                                <div className="image-card-header">
                                                    <span className="image-title">📊 {img.title}</span>
                                                </div>
                                                <img src={img.url} alt={img.title} className="analysis-image" />
                                                <div className="image-description">{img.description}</div>
                                            </div>
                                        ))}
                                    </div>
                                )}
                                {message.images && message.images.length > 0 && !message.imageData && (
                                    <div className="message-images">
                                        {message.images.map((imgPath, idx) => (
                                            <div key={idx} className="image-card">
                                                <img src={imgPath} alt={`Chart ${idx + 1}`} className="analysis-image" />
                                            </div>
                                        ))}
                                    </div>
                                )}
                                {(message.pdfPath || message.pptPath || message.dashboardPath) && (
                                    <div className="download-buttons">
                                        {message.pdfPath && (
                                            <button className="download-btn download-btn-pdf" onClick={() => handleDownloadReport(message.pdfPath!)}>
                                                📄 Download PDF Report
                                            </button>
                                        )}
                                        {message.pptPath && (
                                            <button className="download-btn download-btn-ppt" onClick={() => handleDownloadReport(message.pptPath!)}>
                                                📊 Download PPT
                                            </button>
                                        )}
                                        {message.dashboardPath && (
                                            <button className="download-btn download-btn-dashboard" onClick={() => window.open(message.dashboardPath, '_blank')}>
                                                📈 Open Dashboard
                                            </button>
                                        )}
                                    </div>
                                )}
                                <div className="message-time">
                                    {message.timestamp.toLocaleTimeString()}
                                </div>
                            </div>
                        </div>
                    ))
                )}
                {loading && (
                    <div className="message message-assistant">
                        <div className="message-avatar">{icon}</div>
                        <div className="message-content">
                            <div className="typing-indicator">
                                <span></span><span></span><span></span>
                            </div>
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            <form
                className={`chat-input-area ${dragActive ? 'drag-active' : ''}`}
                onSubmit={handleSendMessage}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
            >
                <div className="input-wrapper">
                    <input
                        type="file"
                        ref={fileInputRef}
                        onChange={handleFileChange}
                        accept=".csv,.xlsx,.xls,.json,.txt"
                        style={{ display: 'none' }}
                    />
                    <button type="button" className="upload-btn" onClick={() => fileInputRef.current?.click()}>
                        📎
                    </button>
                    {uploadedFile && (
                        <div className="file-badge">
                            <span>{uploadedFile.name}</span>
                            <button type="button" onClick={() => setUploadedFile(null)}>✕</button>
                        </div>
                    )}
                    <textarea
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder={`Ask about ${title.toLowerCase()}...`}
                        rows={1}
                        onKeyDown={(e) => {
                            if (e.key === 'Enter' && !e.shiftKey) {
                                e.preventDefault();
                                handleSendMessage(e);
                            }
                        }}
                    />
                    <button type="submit" className="send-btn" disabled={loading || !input.trim()}>
                        {loading ? '⏳' : '➤'}
                    </button>
                </div>
            </form>
        </div>
    );
};

// Export specific agent pages
export const DataAnalysisPage: React.FC = () => (
    <AgentPage
        agentType="data_analysis"
        title="Data Analysis"
        icon="📊"
        description="Analyze your data with AI-powered insights and beautiful visualizations"
        accentColor="#6366f1"
    />
);

export const ReportPage: React.FC = () => (
    <AgentPage
        agentType="pdf"
        title="PDF Reports"
        icon="📄"
        description="Generate professional PDF reports with charts, findings, and recommendations"
        accentColor="#10b981"
    />
);

export const PresentationPage: React.FC = () => (
    <AgentPage
        agentType="ppt"
        title="Presentations"
        icon="📑"
        description="Create stunning PowerPoint presentations from your data or content"
        accentColor="#f59e0b"
    />
);

export const DashboardPage: React.FC = () => (
    <AgentPage
        agentType="dashboard"
        title="Dashboards"
        icon="📈"
        description="Build interactive dashboards like Power BI or Tableau"
        accentColor="#ec4899"
    />
);
