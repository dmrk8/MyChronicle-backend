export interface MetadataType {
  mediaId: number;
  title: {
  english?: string;
  native?: string;
  romaji?: string;
}; 
  description?: string;
  startYear?: number;
  endYear?: number;
  type: string;
  coverImage?: string; 
  status?: string;
  meanScore?: number;
  genres?: string[];
  countryOfOrigin?: string;
  format? :string;
  tags?: { name: string }[];
  duration?: number;
  synonyms?: string[];
}