import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { Check, ChevronDown, ChevronUp, Film, LoaderCircle } from "lucide-react";

import { Button } from "@/components/ui/button";
import { CommentThread } from "@/components/comment-thread";
import { InsightCard } from "@/components/insight-card";
import { apiRequest } from "@/lib/api";
import type { Episode, SeriesDetailsResponse } from "@/types/series";

function stripMarkup(value: string | null) {
  return value?.replace(/<[^>]*>/g, "") ?? "No summary available.";
}

function EpisodeRow({ episode, onWatched }: { episode: Episode; onWatched: (episode: Episode) => void }) {
  return (
    <div className="flex gap-4 border-t border-border/70 py-5 first:border-t-0">
      <div className="hidden h-16 w-24 shrink-0 overflow-hidden rounded-md bg-muted sm:block">
        {episode.poster_url ? <img src={episode.poster_url} alt="" className="h-full w-full object-cover" /> : <div className="flex h-full items-center justify-center text-muted-foreground"><Film size={20} /></div>}
      </div>
      <div className="min-w-0 flex-1">
        <div className="flex flex-wrap items-baseline gap-2">
          <span className="text-xs font-medium text-primary">E{String(episode.number).padStart(2, "0")}</span>
          <h3 className="font-medium">{episode.title}</h3>
          {episode.airdate && <span className="text-xs text-muted-foreground">{episode.airdate}</span>}
        </div>
        <p className="mt-2 text-sm leading-6 text-muted-foreground">{stripMarkup(episode.summary)}</p>
        <InsightCard targetType="episode" targetId={episode.id} />
        <CommentThread targetType="episode" targetId={episode.id} />
      </div>
      <Button variant={episode.watched ? "default" : "outline"} size="sm" aria-label={episode.watched ? `Mark ${episode.title} unwatched` : `Mark ${episode.title} watched`} onClick={() => onWatched(episode)}>
        <Check size={16} /><span className="hidden sm:inline">{episode.watched ? "Watched" : "Mark watched"}</span>
      </Button>
    </div>
  );
}

export function SeriesPage() {
  const { seriesId } = useParams();
  const [details, setDetails] = useState<SeriesDetailsResponse | null>(null);
  const [openSeasons, setOpenSeasons] = useState<number[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!seriesId) return;
    setIsLoading(true);
    apiRequest<SeriesDetailsResponse>(`/series/${seriesId}`)
      .then((data) => { setDetails(data); setOpenSeasons(data.seasons.length > 0 ? [data.seasons[0].season] : []); })
      .catch((requestError) => setError(requestError instanceof Error ? requestError.message : "Unable to load series"))
      .finally(() => setIsLoading(false));
  }, [seriesId]);

  async function toggleWatched(episode: Episode) {
    if (!details) return;
    const watched = !episode.watched;
    setDetails({ ...details, seasons: details.seasons.map((season) => ({ ...season, episodes: season.episodes.map((item) => item.id === episode.id ? { ...item, watched } : item) })), watched_episode_ids: watched ? [...details.watched_episode_ids, episode.id] : details.watched_episode_ids.filter((id) => id !== episode.id) });
    try {
      await apiRequest(`/episodes/${episode.id}/watched`, { method: "PUT", body: JSON.stringify({ watched }) });
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Unable to save watched state");
    }
  }

  function toggleSeason(season: number) {
    setOpenSeasons((current) => current.includes(season) ? current.filter((item) => item !== season) : [...current, season]);
  }

  if (isLoading) return <div className="flex items-center justify-center py-24 text-muted-foreground"><LoaderCircle className="mr-2 animate-spin" size={20} /> Loading series...</div>;
  if (error || !details) return <section className="py-12"><Link to="/" className="text-sm text-primary hover:underline">← Back to search</Link><p className="mt-10 text-red-300">{error ?? "Series not found"}</p></section>;

  const { series } = details;
  return (
    <section className="py-8">
      <Link to="/" className="text-sm text-primary hover:underline">← Back to search</Link>
      <div className="mt-8 grid gap-8 lg:grid-cols-[220px_1fr]">
        <div className="aspect-[2/3] overflow-hidden rounded-xl bg-muted">
          {series.poster_url ? <img src={series.poster_url} alt={`${series.title} poster`} className="h-full w-full object-cover" /> : <div className="flex h-full items-center justify-center text-muted-foreground"><Film size={40} /></div>}
        </div>
        <div>
          <div className="flex flex-wrap items-center gap-3"><h1 className="text-4xl font-semibold tracking-tight">{series.title}</h1>{series.year && <span className="text-muted-foreground">{series.year}</span>}</div>
          <div className="mt-4 flex flex-wrap gap-2">{series.genres.map((genre) => <span key={genre} className="rounded-full bg-muted px-3 py-1 text-xs text-muted-foreground">{genre}</span>)}</div>
          <p className="mt-6 max-w-3xl leading-7 text-muted-foreground">{stripMarkup(series.summary)}</p>
          <InsightCard targetType="series" targetId={series.id} />
          <CommentThread targetType="series" targetId={series.id} />
          {error && <p className="mt-4 text-sm text-red-300">{error}</p>}
        </div>
      </div>
      <div className="mt-12 space-y-4">
        <div><p className="text-sm font-medium uppercase tracking-[0.2em] text-primary">The watch trail</p><h2 className="mt-2 text-2xl font-semibold">Episodes by season</h2></div>
        {details.seasons.map((season) => {
          const isOpen = openSeasons.includes(season.season);
          const watchedCount = season.episodes.filter((episode) => episode.watched).length;
          return <div key={season.season} className="overflow-hidden rounded-xl border border-border bg-card">
            <button className="flex w-full items-center justify-between px-5 py-4 text-left hover:bg-muted/50" onClick={() => toggleSeason(season.season)}>
              <span className="font-medium">Season {season.season} <span className="ml-2 text-sm text-muted-foreground">{watchedCount}/{season.episodes.length} watched</span></span>
              {isOpen ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
            </button>
            {isOpen && <div className="px-5 pb-2">{season.episodes.map((episode) => <EpisodeRow key={episode.id} episode={episode} onWatched={toggleWatched} />)}</div>}
          </div>;
        })}
      </div>
    </section>
  );
}
