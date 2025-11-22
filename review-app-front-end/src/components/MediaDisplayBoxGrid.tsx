import type { MetadataType } from '../types/MetadataType';

interface MediaDisplayBoxGridProps {
  items: MetadataType[];
  onClick?: (media: MetadataType) => void;
}

export default function MediaDisplayBoxGrid({
  items,
  onClick,
}: MediaDisplayBoxGridProps) {
  return (
    <div className="grid grid-cols-6 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-x-8 gap-y-8">
      {items.map((media) =>
        media.coverImage ? (
          <div
            key={media.mediaId}
            className="relative cursor-pointer transform hover:scale-105 transition-transform"
            onClick={() => onClick?.(media)}
          >
            <img
              src={media.coverImage}
              alt={media.title.english}
              className="w-full h-60 object-cover shadow-lg"
            />
            <div className="mt-2 text-center">
              <span className="text-white text-center font-semibold">
                {media.title.english || media.title.native || media.title.romaji}
              </span>
            </div>
          </div>
        ) : null
      )}
    </div>
  );
}
