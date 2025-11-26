import { useState, useEffect, useCallback, useRef } from 'react';
import api from '../../components/api/backendApi';
import { UseInfiniteScroll } from '../../components/useInfiniteScroll';
import type { LibraryReviewType } from '../../types/ReviewType';

export default function UserLibrary() {
  const containerRef = useRef<HTMLDivElement>(null);

  const [library, setLibrary] = useState<LibraryReviewType[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState('');
  const [page, setPage] = useState<number>(1);
  const [hasNextPage, setHasNextPage] = useState<boolean>(true);
  const [selectedItem, setSelectedItem] = useState<LibraryReviewType | null>(
    null
  );

  // Sorting and filtering
  const [sortBy, setSortBy] = useState<string>('created_at');
  const [sortOrder, setSortOrder] = useState<number>(-1); // 1 = ascending, -1 = descending
  const [filters, setFilters] = useState<Record<string, any>>({});

  const fetchLibrary = useCallback(
    async (newPage = 1) => {
      try {
        setLoading(true);
        const res = await api.get('review/library/anime', {
          params: {
            page: newPage,
            per_page: 10,
            sort_by: sortBy,
            sort_order: sortOrder,
            ...filters,
          },
        });
        const data = res.data;

        setLibrary((prev) =>
          newPage === 1 ? data.results : [...prev, ...data.results]
        );

        setPage(newPage);
        setHasNextPage(data.hasNextPage);
      } catch (err: any) {
        setError(
          err.response?.data?.detail || err.message || 'Failed to load library'
        );
      } finally {
        setLoading(false);
      }
    },
    [sortBy, sortOrder, filters]
  );

  useEffect(() => {
    fetchLibrary(1);
  }, [fetchLibrary]);

  UseInfiniteScroll({
    callback: () => fetchLibrary(page + 1),
    isLoading: loading,
    hasNextPage,
    container: containerRef.current,
  });

  // Handle updating a review
  const handleUpdate = async (updated: LibraryReviewType) => {
    try {
      await api.put(`review/update/${updated.type}`, {
        review_id: updated.review_id,
        review: updated.review,
        rating: updated.rating,
      });
      setLibrary((prev) =>
        prev.map((item) =>
          item.review_id === updated.review_id ? { ...item, ...updated } : item
        )
      );
      setSelectedItem(null); // Close the modal after updating
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to update review');
    }
  };

  // Handle deleting a review
  const handleDelete = async (item: LibraryReviewType) => {
    try {
      await api.delete(`review/delete/${item.type}/${item.review_id}`);
      setLibrary((prev) => prev.filter((i) => i.review_id !== item.review_id));
      setSelectedItem(null); // Close the modal after deleting
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete review');
    }
  };

  return (
    <div className="h-screen flex flex-col">
      {/* Header */}
      <div className="p-4 bg-blue-600 text-white text-center font-bold text-xl">
        Your Library
      </div>

      {/* Sorting and filtering */}
      <div className="p-4 flex justify-between items-center bg-gray-100">
        <div className="flex items-center">
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="p-2 border rounded mr-2"
          >
            <option value="created_at">Sort by Date</option>
            <option value="rating">Sort by Rating</option>
            <option value="title">Sort by Title</option>
          </select>
          <button
            onClick={() => setSortOrder(sortOrder * -1)}
            className="p-2 bg-blue-500 text-white rounded"
          >
            {sortOrder === 1 ? 'Asc ↑' : 'Desc ↓'}
          </button>
        </div>
        <input
          type="text"
          placeholder="Filter by title"
          onKeyDown={(e) => {
            if (e.key === 'Enter') {
              const value = e.currentTarget.value;
              setFilters((f) => ({ ...f, title: value }));
              fetchLibrary(1);
            }
          }}
          className="p-2 border rounded"
        />
      </div>

      {/* Content */}
      <div ref={containerRef} className="flex-1 overflow-auto p-4">
        {error && <p className="text-red-500 text-center">{error}</p>}
        {library.length === 0 && !loading && (
          <p className="text-gray-500 text-center">No reviews found.</p>
        )}

        {/* Grid layout */}
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
          {library.map((item) => (
            <div
              key={item.review_id}
              className="relative cursor-pointer transform hover:scale-105 transition-transform"
              onClick={() => setSelectedItem(item)}
            >
              <img
                src={item.cover_image || 'https://via.placeholder.com/150'}
                alt={item.title}
                className="w-full h-48 object-cover rounded-xl shadow-lg"
              />
              <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center opacity-0 hover:opacity-100 transition-opacity rounded-xl">
                <span className="text-white text-center font-semibold">
                  {item.title}
                </span>
              </div>
            </div>
          ))}
        </div>

        {loading && <p className="text-center mt-4">Loading...</p>}
      </div>

      {/* Modal */}
      {selectedItem && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-lg p-6 w-11/12 max-w-lg">
            <h2 className="text-xl font-bold mb-4">{selectedItem.title}</h2>
            <p className="text-gray-700 mb-2">
              <strong>Type:</strong> {selectedItem.type}
            </p>
            <p className="text-gray-700 mb-2">
              <strong>Review:</strong> {selectedItem.review}
            </p>
            <p className="text-gray-700 mb-2">
              <strong>Rating:</strong> {selectedItem.rating}
            </p>
            <p className="text-gray-700 mb-4">
              <strong>Description:</strong> {selectedItem.description}
            </p>
            <div className="flex justify-end">
              <button
                className="bg-red-500 text-white px-4 py-2 rounded-lg mr-2"
                onClick={() => setSelectedItem(null)}
              >
                Close
              </button>
              <button
                className="bg-blue-500 text-white px-4 py-2 rounded-lg mr-2"
                onClick={() => {
                  const newReview = window.prompt(
                    'Edit Review:',
                    selectedItem?.review
                  );
                  if (newReview === null) return;
                  const newRatingStr = window.prompt(
                    'Edit Rating (1-10):',
                    selectedItem?.rating?.toString()
                  );
                  if (newRatingStr === null) return;
                  const newRating = parseInt(newRatingStr, 10);
                  if (isNaN(newRating) || newRating < 1 || newRating > 10) {
                    alert(
                      'Invalid rating. Please enter a number between 1 and 10.'
                    );
                    return;
                  }
                  const updated = {
                    ...selectedItem,
                    review: newReview,
                    rating: newRating,
                  };
                  handleUpdate(updated as LibraryReviewType);
                }}
              >
                Edit
              </button>
              <button
                className="bg-red-500 text-white px-4 py-2 rounded-lg"
                onClick={() => {
                  if (
                    window.confirm(
                      'Are you sure you want to delete this review?'
                    )
                  ) {
                    handleDelete(selectedItem as LibraryReviewType);
                  }
                }}
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
