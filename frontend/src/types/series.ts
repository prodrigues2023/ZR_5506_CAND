export interface SeriesSummary {
  id: number;
  title: string;
  year: number | null;
  poster_url: string | null;
  summary: string | null;
  genres: string[];
}

export interface SearchResponse {
  results: SeriesSummary[];
}

export interface Episode {
  id: number;
  series_id: number;
  season: number;
  number: number;
  title: string;
  summary: string | null;
  airdate: string | null;
  poster_url: string | null;
  watched: boolean;
}

export interface Season {
  season: number;
  episodes: Episode[];
}

export interface Comment {
  id: string;
  author_id: string;
  author_label: string;
  target_type: "series" | "episode";
  target_id: number;
  content: string;
  created_at: string;
}

export interface SeriesDetailsResponse {
  series: SeriesSummary;
  seasons: Season[];
  watched_episode_ids: number[];
  comments: Comment[];
}
