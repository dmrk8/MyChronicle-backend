import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../components/context/AuthProvider';

export default function Register() {
  const navigate = useNavigate();

  const [username, setUsername] = useState<string>('');
  const [password, setPassword] = useState<string>('');
  const [error, setError] = useState('');
  const { register } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    try {
      await register(username, password);
      navigate('/login');
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Registration failed');
    }
  };

  return (
    <div className="flex h-screen items-center justify-center bg-gradient-to-b from-gray-950 via-gray-900 to-gray-800">
      {/* Register Card */}
      <div className="w-full max-w-md p-8 bg-gray-900/80 backdrop-blur-md rounded-2xl shadow-2xl border border-gray-700 text-center">
        <h2 className="text-3xl font-bold text-white mb-6 drop-shadow-lg">
          Create Account
        </h2>
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
            className="w-full px-4 py-3 rounded-lg bg-gray-800 text-white border border-gray-600 focus:outline-none focus:border-blue-500 placeholder-gray-400"
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            className="w-full px-4 py-3 rounded-lg bg-gray-800 text-white border border-gray-600 focus:outline-none focus:border-blue-500 placeholder-gray-400"
          />
          <button
            type="submit"
            className="w-full py-3 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold rounded-lg shadow-md transition-colors"
          >
            Register
          </button>
        </form>

        {error && <p className="text-red-500 mt-4">{error}</p>}

        {/* Optional link back to login */}
        <div className="mt-6 text-gray-400 text-sm">
          <button
            type="button"
            onClick={() => navigate('/')}
            className="hover:text-white transition-colors"
          >
            Back to Login
          </button>
        </div>
      </div>
    </div>
  );
}
