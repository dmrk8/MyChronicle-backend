import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Register from './pages/LoginPage/Register';
import SearchComicPage from './pages/SearchComicPage';
import SearchAnime from './pages/SearchAnimePage';
import UserLibrary from './pages/UserLibrary/UserLibrary';
import LoginPage from './pages/LoginPage';
import HomePage from './pages/HomePage';
import { AuthProvider } from './components/context/AuthProvider';
import MediaViewPage from './pages/MediaViewPage';

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/home" element={<HomePage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<Register />} />
          <Route path="/search/anime" element={<SearchAnime />} />
          <Route path="/search/comic" element={<SearchComicPage />} />
          <Route path="/user/library" element={<UserLibrary />} />
          <Route path="/:mediatype/:id/:title" element={<MediaViewPage />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
