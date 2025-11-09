import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from './context/AuthProvider';

interface LoginProps {
  username: string;
  password: string;
}

export default function Login({ username, password }: LoginProps) {
  const navigate = useNavigate();
  const [error, setError] = useState('');
  const [loading, setLoading] = useState<boolean>(false);
  const { login } = useAuth(); // Returns a context function to handle authentication

  useEffect(() => {
    const processLogin = async () => {
      setLoading(true);
      try {
        await login(username, password);
        setError('');
        navigate('/home');
      } catch {
        setError('Invalid Credentials');
        navigate('/login');
      } finally {
        setLoading(false);
      }
    };

    processLogin();
  }, []);

  return (
    <div className="mt-6">
      {loading && <p className="text-blue-500 mt-4">Logging in...</p>}
      {error && <p className="text-red-500 mt-4">{error}</p>}
    </div>
  );
}
