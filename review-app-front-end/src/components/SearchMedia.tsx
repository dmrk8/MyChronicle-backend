import { useCallback, useEffect, useRef, useState } from 'react';
import { UseInfiniteScroll } from './useInfiniteScroll';
import BoxGrid from './MediaDisplayBoxGrid';
import type { MetadataType } from '../types/MetadataType';
import backendApi from './api/backendApi';
import { useNavigate, useSearchParams } from 'react-router';

interface SearchMediaProps {
  mediaType: string; // e.g., "anime", "manga", "movies"
  placeholder?: string; // Placeholder for the search bar
}

function SearchMedia({ mediaType }: SearchMediaProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [page, setPage] = useState<number>(1);
  const [hasNextPage, setHasNextPage] = useState<boolean>(true);
  const [query, setQuery] = useState<string>('');
  const [results, setResults] = useState<MetadataType[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [searchParams, setSearchParams] = useSearchParams();
  const debounceRef = useRef<number | null>(null);
  const navigate = useNavigate();

  const handleMediaClick = (media: MetadataType) => {
    navigate(`/${media.type}/${media.mediaId}/${media.title.english}`, {
      state: { media },
    });
  };

  useEffect(() => {
    const urlQuery = searchParams.get('search') || '';
    setQuery(urlQuery);
  }, [searchParams]);

  const handleSearch = useCallback(
    async (newPage = 1) => {
      if (!hasNextPage && newPage !== 1) return;
      try {
        setLoading(true);

        const perPage = newPage === 1 ? 30 : 10;

        const response = await backendApi.get(
          `media/search/${mediaType}?query=${encodeURIComponent(
            query
          )}&page=${newPage}&per_page=${perPage}`
        );
        const data = await response.data;

        setResults((prev) =>
          newPage === 1 ? data.results : [...prev, ...data.results]
        );

        setPage(data.page + 1);
        setHasNextPage(data.hasNextPage);
      } catch (error) {
        console.error(error);
        if (newPage === 1) setResults([]);
      } finally {
        setLoading(false);
      }
    },
    [query, hasNextPage, mediaType]
  );

  // Auto-search when query changes, with debounce
  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => {
      setSearchParams({ search: query });
      handleSearch(1);
    }, 400); // 400ms debounce
    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
    };
  }, [handleSearch, query, setSearchParams]); // Only run when query change

  UseInfiniteScroll({
    callback: () => handleSearch(page),
    isLoading: loading,
    hasNextPage: hasNextPage,
    container: containerRef.current,
  });

  return (
    <div className="h-screen flex flex-col">
      {/* Search bar */}
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        className="w-full px-4 py-2 rounded bg-gray-800 text-white focus:outline-none"
      />

      {/* Box grid */}
      <div ref={containerRef} className="flex-1 overflow-auto py-30 px-60">
        <BoxGrid items={results} onClick={handleMediaClick} />
        {loading && <p className="text-center mt-4 text-white">Loading...</p>}
      </div>
    </div>
  );
}

export default SearchMedia;
