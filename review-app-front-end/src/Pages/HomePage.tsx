import { Link } from 'react-router-dom';

export default function HomePage() {
  return (
    <div className="flex h-screen items-center justify-center bg-gradient-to-b from-gray-950 via-gray-900 to-gray-800">
      <div className="w-full max-w-md p-8 bg-gray-900/80 backdrop-blur-md rounded-2xl shadow-2xl border border-gray-700 text-center">
        <h2 className="text-3xl font-bold text-white mb-6 drop-shadow-lg">
          Dashboard
        </h2>
        <div className="flex flex-col gap-4">
          <Link to="/search/anime">
            <button className="w-full py-3 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold rounded-lg shadow-md transition-colors">
              Search Anime
            </button>
          </Link>
          <Link to="/search/comic">
            <button className="w-full py-3 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold rounded-lg shadow-md transition-colors">
              Search Comic
            </button>
          </Link>
          <Link to="/user/library">
            <button className="w-full py-3 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold rounded-lg shadow-md transition-colors">
              Library
            </button>
          </Link>
        </div>
      </div>
    </div>
  );
}

