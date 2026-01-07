import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import '../styles/Auth.css';

export const MainHub: React.FC = () => {
    const { user, logout } = useAuth();
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate('/');
    };

    const agents = [
        {
            id: 'analysis',
            title: 'Data Analysis',
            icon: '📊',
            description: 'Analyze your data with AI-powered insights and visualizations',
            color: '#6366f1',
            path: '/analysis'
        },
        {
            id: 'report',
            title: 'PDF Reports',
            icon: '📄',
            description: 'Generate professional PDF reports with charts and findings',
            color: '#10b981',
            path: '/report'
        },
        {
            id: 'presentation',
            title: 'Presentations',
            icon: '📑',
            description: 'Create stunning PowerPoint presentations from your data',
            color: '#f59e0b',
            path: '/presentation'
        },
        {
            id: 'dashboard',
            title: 'Dashboards',
            icon: '📈',
            description: 'Build interactive dashboards like Power BI or Tableau',
            color: '#ec4899',
            path: '/dashboard'
        }
    ];

    return (
        <div className="hub-container">
            <div className="auth-background">
                <div className="gradient-sphere sphere-1"></div>
                <div className="gradient-sphere sphere-2"></div>
                <div className="gradient-sphere sphere-3"></div>
            </div>

            <nav className="hub-nav">
                <div className="nav-left">
                    <Link to="/" className="home-link">
                        <span className="home-icon">🏠</span>
                        <span>Home</span>
                    </Link>
                    <span className="nav-divider">|</span>
                    <span className="nav-logo">📊 Data Analysis Agent</span>
                </div>
                <div className="nav-right">
                    {user && (
                        <div className="user-info">
                            <img
                                src={user.avatar || `https://api.dicebear.com/7.x/initials/svg?seed=${user.name}`}
                                alt={user.name}
                                className="user-avatar-small"
                            />
                            <span>{user.name}</span>
                        </div>
                    )}
                    <button className="logout-btn-hub" onClick={handleLogout}>
                        Logout
                    </button>
                </div>
            </nav>

            <main className="hub-main">
                <div className="hub-header">
                    <h1>Welcome back{user ? `, ${user.name.split(' ')[0]}` : ''}! 👋</h1>
                    <p>Choose what you'd like to create today</p>
                </div>

                <div className="agent-grid">
                    {agents.map((agent) => (
                        <Link
                            key={agent.id}
                            to={agent.path}
                            className="agent-card"
                            style={{ '--card-color': agent.color } as React.CSSProperties}
                        >
                            <div className="agent-icon">{agent.icon}</div>
                            <h3>{agent.title}</h3>
                            <p>{agent.description}</p>
                            <div className="agent-arrow">→</div>
                        </Link>
                    ))}
                </div>

                <div className="hub-footer">
                    <p>Or use the <Link to="/chat" className="chat-link">unified chat</Link> for all agents</p>
                </div>
            </main>
        </div>
    );
};
