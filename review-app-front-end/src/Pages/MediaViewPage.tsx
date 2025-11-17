import { useLocation } from 'react-router-dom';
import type { MetadataType } from '../types/MetadataType';
import {
  MdFavorite,
  MdFavoriteBorder,
  MdLibraryAdd,
  MdLibraryAddCheck,
} from 'react-icons/md';
import { FaExternalLinkAlt } from 'react-icons/fa';
import { useEffect, useState } from 'react';
import IconButton from '../components/IconButton';
import MediaInfoPair from '../components/MediaInfoPair';
import type {
  ReviewCreate,
  ReviewType,
  ReviewUpdate,
} from '../types/ReviewType';
import { BsFillInfoSquareFill } from 'react-icons/bs';
import backendApi from '../components/api/backendApi';

export default function MediaViewPage() {
  const location = useLocation();
  const mediaInfo = location.state.media as MetadataType;
  const [reviewInfo, setReviewInfo] = useState<ReviewType | null>(null);
  const buttonSize = 40;
  const [rating, setRating] = useState<number | ''>('');
  const [review, setReview] = useState<string | ''>('');
  const mediaLink = `https://anilist.co/${mediaInfo.type}/${mediaInfo.mediaId}/${mediaInfo.title.english}`;

  useEffect(() => {
    async function fetchReview() {
      try {
        const res = await backendApi.get(
          `/review/id?mediaId=${mediaInfo.mediaId}`,
          {
            withCredentials: true,
          }
        );
        if (res.status === 200) {
          const reviewRes = await backendApi.get(`/review/${res.data}`, {
            withCredentials: true,
          });
          if (reviewRes.status === 200 && reviewRes.data) {
            setReviewInfo(reviewRes.data);
            setRating(reviewRes.data.rating ?? '');
            setReview(reviewRes.data.review ?? '');
          }
        }
      } catch (err) {
        // Log the error for debugging
        console.error('Error fetching review:', err);
      }
    }
    fetchReview();
    // Only run on first mount
    // eslint-disable-next-line
  }, []);

  const handleAddToLibrary = async () => {
    try {
      if (!reviewInfo) {
        // Add to library (create review)
        const reviewData: ReviewCreate = {
          mediaId: mediaInfo.mediaId,
          type: mediaInfo.type,
        };
        const res = await backendApi.post('/review/create', reviewData, {
          withCredentials: true,
        });
        if (res.status === 200) {
          const getRes = await backendApi.get(
            `/review/id?mediaId=${mediaInfo.mediaId}`,
            { withCredentials: true }
          );
          if (getRes.status === 200) {
            const reviewRes = await backendApi.get(`/review/${getRes.data}`, {
              withCredentials: true,
            });
            if (reviewRes.status === 200 && reviewRes.data) {
              setReviewInfo(reviewRes.data);
              setRating(reviewRes.data.rating ?? '');
              setReview(reviewRes.data.review ?? '');
            }
          }
        }
      } else if (reviewInfo.id) {
        // Remove from library (delete review)
        const res = await backendApi.delete(`/review/delete/${reviewInfo.id}`, {
          withCredentials: true,
        });
        if (res.status === 200) {
          setReviewInfo(null);
          setRating('');
          setReview('');
        }
      }
    } catch (err) {
      console.error('Failed to update library status:', err);
    }
  };

  const handleAddFavorite = async () => {
    if (!reviewInfo?.id) return;
    try {
      const reviewUpdate: ReviewUpdate = {
        id: reviewInfo.id!,
        isFavorite: !reviewInfo.isFavorite,
      };
      const res = await backendApi.put('/review/update', reviewUpdate, {
        withCredentials: true,
      });

      if (res.status === 200) {
        const reviewRes = await backendApi.get(`/review/${reviewInfo.id}`, {
          withCredentials: true,
        });
        if (reviewRes.status === 200 && reviewRes.data) {
          setReviewInfo(reviewRes.data);
          setRating(reviewRes.data.rating);
          setReview(reviewRes.data.review);
        }
      }
    } catch (err) {
      console.error('Failed to update favorite status:', err);
    }
  };

  return (
    <div>
      {/* Media Info */}
      <div className="relative min-h-[60vh] w-screen mx-0 overflow-hidden">
        {/* Blurred background image */}
        {mediaInfo.coverImage && (
          <div
            className="absolute inset-0 z-0 w-full h-full"
            style={{
              backgroundImage: `url(${mediaInfo.coverImage})`,
              backgroundSize: 'cover',
              backgroundPosition: 'center',
              filter: 'blur(16px) brightness(0.5)',
              opacity: 0.7,
            }}
          />
        )}

        {/* Color overlay on blurred image */}
        <div className="absolute inset-0 z-0 w-full h-full bg-[var(--media-view-overlay-color)] opacity-50" />

        {/* Gradient transition at the bottom */}
        <div
          className="absolute flex bottom-0 left-0 w-full h-60 z-10"
          style={{
            background:
              'linear-gradient(to bottom, transparent, var(--media-view-overlay-color) 40%)',
          }}
        >
          <div className="pointer-events-auto absolute bottom-12 left-1/2 -translate-x-1/2 flex gap-20">
            <IconButton
              icon={<MdLibraryAdd className="cursor-pointer" />}
              conditionIcon={<MdLibraryAddCheck className="cursor-pointer" />}
              buttonSize={buttonSize}
              label={reviewInfo ? 'In library' : 'Add to Library'}
              condition={!!reviewInfo}
              onClick={handleAddToLibrary}
            />
            {reviewInfo && (
              <IconButton
                icon={<MdFavoriteBorder />}
                conditionIcon={<MdFavorite />}
                label={reviewInfo?.isFavorite ? 'Favorite' : 'Add Favorite'}
                buttonSize={buttonSize}
                condition={reviewInfo?.isFavorite}
                onClick={handleAddFavorite}
              />
            )}
            <IconButton
              icon={<BsFillInfoSquareFill />}
              conditionIcon={<FaExternalLinkAlt />}
              label="More Info"
              condition={false}
              buttonSize={buttonSize}
              onClick={() => window.open(mediaLink, '_blank')}
            />
          </div>
        </div>

        {/* Foreground content */}
        <div className="relative z-10 flex flex-row items-center left-0 md:py-20 lg:pr-100 lg:px-50">
          {mediaInfo.coverImage && (
            <img
              src={mediaInfo.coverImage}
              alt={mediaInfo.title.english}
              className="w-[220px] rounded-lg object-cover shadow-lg"
            />
          )}
          <div className="text-white mx-10 flex flex-col">
            <h1 className="text-5xl">{mediaInfo.title.english}</h1>
            <p className="mt-10 text-xl text-[color:var(--media-view-primary-text-color)]">
              {mediaInfo.description}
            </p>
          </div>
        </div>
      </div>

      {/* Vertically divided content after the image and transition */}
      <div className="relative z-20 flex w-full min-h-[40vh]">
        {/* Left side */}
        <div className="w-2/8  flex flex-col items-center">
          <div className="bg-[var(--primary-front-color)] rounded-lg p-6 ml-50 w-[220px]">
            <MediaInfoPair
              label="Format"
              value={
                <>
                  {mediaInfo.type.charAt(0) +
                    mediaInfo.type.slice(1).toLowerCase()}
                  {mediaInfo.countryOfOrigin && (
                    <span className="ml-1 text-xs text-[color:var(--media-view-secondary-text-color)]">
                      ({mediaInfo.countryOfOrigin})
                    </span>
                  )}
                </>
              }
            />
            <MediaInfoPair
              label="Status"
              value={
                mediaInfo.status.charAt(0) +
                mediaInfo.status.slice(1).toLowerCase()
              }
            />
            <MediaInfoPair label="Start Date" value={mediaInfo.startYear} />
            <MediaInfoPair label="End Date" value={mediaInfo.endYear} />
            <MediaInfoPair
              label="Mean Score"
              value={`${mediaInfo.meanScore}%`}
            />
            <MediaInfoPair
              label="Genres"
              value={
                <ul>
                  {mediaInfo.genres.map((genre) => (
                    <li key={genre}>{genre}</li>
                  ))}
                </ul>
              }
            />
            <MediaInfoPair label="Romaji" value={mediaInfo.title.romaji} />
            <MediaInfoPair label="English" value={mediaInfo.title.english} />
            <MediaInfoPair label="Native" value={mediaInfo.title.native} />
            <MediaInfoPair
              label="Synonyms"
              value={
                <ul>
                  {mediaInfo.synonyms.map((synonym) => (
                    <li key={synonym}>{synonym}</li>
                  ))}
                </ul>
              }
            />
          </div>
          <div className="w-[220px] ml-50 mt-5 mb-2">
            <h2 className="text-lg text-[color:var(--media-view-primary-text-color)]">
              Tags
            </h2>
          </div>
          <div className="w-2/8 flex flex-col items-center">
            <div className="bg-[var(--primary-front-color)] rounded-lg p-6 ml-50 w-[220px] flex flex-wrap gap-2">
              {(mediaInfo.tags ?? []).map((tag) => (
                <span
                  key={tag.name}
                  className="bg-[var(--media-view-secondary-text-color)] text-[var(--primary-front-color)] px-3 py-1 rounded shadow text-sm font-semibold"
                >
                  {tag.name}
                </span>
              ))}
            </div>
          </div>
        </div>
        {/* Right side */}
        <div className="w-7/8 text-3xl flex flex-col items-center text-[color:var(--media-view-primary-text-color)]">
          <div className="flex items-center gap-4 mb-4 font-semibold">
            <h3 className="">My Review and </h3>
            {/* Rating */}
            <div className="flex items-center gap-2">
              <label htmlFor="rating" className="-ml-2">
                Rating:
              </label>
              <div className="relative">
                <input
                  id="rating"
                  type="number"
                  min={1}
                  max={10}
                  inputMode="numeric"
                  pattern="[0-9]*"
                  className="w-30 p-1 pl-4  rounded bg-[var(--primary-front-color)]"
                  placeholder="0"
                  value={rating}
                  onInput={(e) => {
                    const target = e.target as HTMLInputElement;
                    // Remove any non-digit characters immediately
                    target.value = target.value.replace(/[^0-9]/g, '');
                    // Remove leading zeros unless the value is exactly "0"
                    if (target.value.length > 1) {
                      target.value = target.value.replace(/^0+/, '');
                    }
                  }}
                  onChange={(e) => {
                    setRating(
                      e.target.value === ''
                        ? ''
                        : Math.max(0, Math.min(Number(e.target.value), 10))
                    );
                  }}
                />
                <span className="absolute right-4 top-1/2 -translate-y-1/2   text-3xl pointer-events-none">
                  / 10
                </span>
              </div>
            </div>
          </div>
          {/* Review input */}
          <form className="mb-6 flex flex-col gap-4 w-3xl text-[color:var(--media-view-primary-text-color)]">
            <textarea
              className="w-full text-lg  p-2 rounded bg-[var(--primary-front-color)] border border-zinc-700 focus:outline-none  resize-none"
              rows={9}
              placeholder="My review..."
              value={review}
              onChange={(e) => setReview(e.target.value)}
            />
            {/* Save Button */}
            <button
              type="button"
              className="self-end px-8 py-2 mt-4 rounded bg-[var(--primary-front-color)] font-semibold cursor-pointer border-zinc-700 disabled:opacity-60 disabled:cursor-not-allowed"
              onClick={async () => {
                if (!reviewInfo) return; // Only allow save if review exists
                try {
                  const reviewUpdate: ReviewUpdate = {
                    id: reviewInfo.id!,
                    review: review,
                    rating:
                      typeof rating === 'number' ? rating : Number(rating),
                  };
                  const res = await backendApi.put(
                    '/review/update',
                    reviewUpdate,
                    {
                      withCredentials: true,
                    }
                  );
                  if (res.status === 200) {
                    const reviewRes = await backendApi.get(
                      `/review/${reviewInfo.id}`,
                      { withCredentials: true }
                    );
                    if (reviewRes.status === 200 && reviewRes.data) {
                      setReviewInfo(reviewRes.data);
                      setRating(reviewRes.data.rating);
                      setReview(reviewRes.data.review);
                    }
                  }
                } catch (err) {
                  console.error('Failed to save review:', err);
                }
              }}
              disabled={
                !reviewInfo ||
                (review === (reviewInfo.review ?? '') &&
                  rating === (reviewInfo.rating ?? ''))
              }
            >
              Save
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
