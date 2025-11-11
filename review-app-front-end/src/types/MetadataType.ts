export interface MetadataType {
  media_id: number;
  title: {
  english?: string;
  native?: string;
  romaji?: string;
}; 
  description?: string;
  start_year?: number;
  end_year?: number;
  type: string;
  cover_image?: string; 
  status?: string;
  meanScore?: number;
  genres?: string[];
  countryOfOrigin?: string;
  format? :string;
  tags?: { name: string }[];
  duration?: number;
  synonyms?: string[];
}