import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface User {
    id: string;
    name: string;
    email: string;
    avatar?: string;
}

interface AuthContextType {
    user: User | null;
    isAuthenticated: boolean;
    login: (email: string, password: string) => Promise<boolean>;
    signup: (name: string, email: string, password: string) => Promise<boolean>;
    logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};

interface AuthProviderProps {
    children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
    const [user, setUser] = useState<User | null>(null);

    useEffect(() => {
        // Check for existing session
        const storedUser = localStorage.getItem('user');
        if (storedUser) {
            setUser(JSON.parse(storedUser));
        }
    }, []);

    const login = async (email: string, password: string): Promise<boolean> => {
        // Get stored users
        const users = JSON.parse(localStorage.getItem('users') || '[]');
        const foundUser = users.find((u: any) => u.email === email && u.password === password);

        if (foundUser) {
            const userData: User = {
                id: foundUser.id,
                name: foundUser.name,
                email: foundUser.email,
                avatar: foundUser.avatar,
            };
            setUser(userData);
            localStorage.setItem('user', JSON.stringify(userData));
            return true;
        }
        return false;
    };

    const signup = async (name: string, email: string, password: string): Promise<boolean> => {
        const users = JSON.parse(localStorage.getItem('users') || '[]');

        // Check if email already exists
        if (users.find((u: any) => u.email === email)) {
            return false;
        }

        const newUser = {
            id: crypto.randomUUID(),
            name,
            email,
            password,
            avatar: `https://api.dicebear.com/7.x/initials/svg?seed=${encodeURIComponent(name)}`,
        };

        users.push(newUser);
        localStorage.setItem('users', JSON.stringify(users));

        // Auto-login after signup
        const userData: User = {
            id: newUser.id,
            name: newUser.name,
            email: newUser.email,
            avatar: newUser.avatar,
        };
        setUser(userData);
        localStorage.setItem('user', JSON.stringify(userData));
        return true;
    };

    const logout = () => {
        setUser(null);
        localStorage.removeItem('user');
    };

    return (
        <AuthContext.Provider value={{ user, isAuthenticated: !!user, login, signup, logout }}>
            {children}
        </AuthContext.Provider>
    );
};
