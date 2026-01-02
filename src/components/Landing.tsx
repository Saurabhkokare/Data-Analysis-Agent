import React from 'react';
import { Link } from 'react-router-dom';
import '../styles/Auth.css';

export const Landing: React.FC = () => {
    return (
        <div className="landing-container">
            <div className="auth-background">
                <div className="gradient-sphere sphere-1"></div>
                <div className="gradient-sphere sphere-2"></div>
                <div className="gradient-sphere sphere-3"></div>
            </div>

            <nav className="landing-nav animate-slide-down">
                <div className="nav-logo">
                    <span className="logo-icon"></span>
                    <span className="logo-text">Data Analysis Agent</span>
                </div>
                <div className="nav-links">
                    <Link to="/signin" className="nav-link">Sign In</Link>
                    <Link to="/signup" className="nav-button">Get Started</Link>
                </div>
            </nav>

            <main className="landing-hero">
                <div className="hero-content animate-fade-in-up">
                    <h1 className="hero-title">
                        Unlock Insights from
                        <span className="gradient-text"> Your Data</span>
                    </h1>
                    <p className="hero-subtitle">
                        Upload your data, ask questions, and get instant visualizations,
                        reports, and AI-powered insights. Transform complex data into
                        actionable intelligence.
                    </p>
                    <div className="hero-buttons">
                        <Link to="/signup" className="hero-button primary">
                            Start Free
                            <span className="button-arrow">→</span>
                        </Link>
                        <Link to="/signin" className="hero-button secondary">
                            Sign In
                        </Link>
                    </div>
                </div>

                <div className="hero-features animate-fade-in-up delay-1">
                    <div className="feature-card">
                        <div className="feature-icon">📈</div>
                        <h3>Smart Visualizations</h3>
                        <p>Auto-generate beautiful charts and graphs</p>
                    </div>
                    <div className="feature-card">
                        <div className="feature-icon">🤖</div>
                        <h3>AI Analysis</h3>
                        <p>Ask questions in natural language</p>
                    </div>
                    <div className="feature-card">
                        <div className="feature-icon">📑</div>
                        <h3>PDF & PPT Reports</h3>
                        <p>Export professional presentations</p>
                    </div>
                </div>
            </main>
        </div>
    );
};
