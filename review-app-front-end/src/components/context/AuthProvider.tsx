import {
  createContext,
  useContext,
  useState,
  useEffect,
  type ReactNode,
} from 'react';
import backendApi from '../api/backendApi';

type User = {
  id: string;
  username: string;
  role: string;
  created_at: string;
};

type AuthContextType = {
  user: User | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  register: (username: string, password: string) => Promise<void>;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
};

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    fetchCurrentUser();
  }, []);

  const fetchCurrentUser = async () => {
    try {
      const res = await backendApi.get('/auth/me', { withCredentials: true });

      if (res.status == 200) {
        const data: User = await res.data;
        setUser(data);
      } else {
        setUser(null);
      }
    } catch (error) {
      console.error('failed to fetch current user:', error);
      setUser(null);
    }
  };

  const login = async (username: string, password: string) => {
    try {
      const res = await backendApi.post(
        '/auth/login',
        { username, password },
        { withCredentials: true }
      );
      if (res.status !== 200) throw new Error('Login failed');
      await fetchCurrentUser();
    } catch (error: any) {
      throw new Error(error.response?.data?.message || 'Login failed');
    }
  };

  const register = async (username: string, password: string) => {
    try {
      const res = await backendApi.post(
        '/auth/register',
        { username, password },
        { withCredentials: true }
      );
      if (res.status !== 200) throw new Error('Registration failed');
      await fetchCurrentUser();
    } catch (error: any) {
      throw new Error(error.response?.data?.message || 'Registration failed');
    }
  };

  const logout = async () => {
    try {
      const res = await backendApi.post('/auth/logout', {
        withCredentials: true,
      });
      if (res.status !== 200) throw new Error('Logout failed');
      setUser(null);
    } catch (error: any) {
      throw new Error(error.response?.data?.message || 'Logout failed');
    }
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, register }}>
      {children}
    </AuthContext.Provider>
  );
};
