export interface ReviewType {
  id: string;
  mediaId: number;
  userId: string;
  title: string;
  type: string;
  review?: string;
  rating?: string;
  isFavorite?: boolean;
  created_at?: Date; 
  updated_at?: Date;
}