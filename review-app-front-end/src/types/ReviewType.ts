export interface ReviewType {
  id?: string;
  mediaId: number;
  userId: string;
  title: string;
  type: string;
  review?: string;
  rating?: number;
  isFavorite: boolean;
  createdAt: Date;
  updatedAt: Date;
}

export interface ReviewCreate {
  mediaId: number;
  type: string;
  review?: string;
  rating?: number;
  isFavorite?: boolean;
}

export interface ReviewUpdate {
  id: string;
  review?: string;
  rating?: number;
  isFavorite?: boolean;
}