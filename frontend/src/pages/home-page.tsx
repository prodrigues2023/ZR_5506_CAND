import { useState } from "react";
import { Link } from "react-router-dom";
import { Search, Tv } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { apiRequest } from "@/lib/api";
import type { SearchResponse, SeriesSummary } from "@/types/series";

function stripMarkup(value: string | null) {
  return value?.replace(/<[^>]*>/g, "") ?? "No summary available.";
}

function SeriesCard({ series }: { series: SeriesSummary }) {
  return (
    <Link
      to={`/series/${series.id}`}
      className="group overflow-hidden rounded-xl border border-border bg-card transition-colors hover:border-primary/70"
    >
      <div className="aspect-[2/3] overflow-hidden bg-muted">
        {series.poster_url ? (
          <img
            src={series.poster_url}
            alt={`${series.title} poster`}
            className="h-full w-full object-cover transition-transform duration-300 group-hover:scale-105"
          />
        ) : (
          <div className="flex h-full items-center justify-center text-muted-foreground">
            <Tv size={32} />
          </div>
        )}
      </div>
      <div className="p-4">
        <div className="flex items-start justify-between gap-3">
          <h2 className="font-semibold group-hover:text-primary">{series.title}</h2>
          {series.year && <span className="shrink-0 text-xs text-muted-foreground">{series.year}</span>}
        </div>
        <p className="mt-2 line-clamp-3 text-sm text-muted-foreground">{stripMarkup(series.summary)}</p>
        <div className="mt-4 flex flex-wrap gap-1.5">
          {series.genres.slice(0, 3).map((genre) => (
            <span key={genre} className="rounded-full bg-muted px-2 py-1 text-xs text-muted-foreground">
              {genre}
            </span>
          ))}
        </div>
      </div>
    </Link>
  );
}

export function HomePage() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SeriesSummary[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasSearched, setHasSearched] = useState(false);

  async function handleSearch(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const value = query.trim();
    if (!value) return;
    setIsLoading(true);
    setError(null);
    setHasSearched(true);
    try {
      const response = await apiRequest<SearchResponse>(`/series/search?q=${encodeURIComponent(value)}`);
      setResults(response.results);
    } catch (requestError) {
      setResults([]);
      setError(requestError instanceof Error ? requestError.message : "Search failed");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <section className="py-12">
      <div className="mx-auto max-w-3xl text-center">
      <p className="mb-4 text-sm font-medium uppercase tracking-[0.25em] text-primary">Your next story</p>
      <h1 className="text-4xl font-semibold tracking-tight sm:text-6xl">Find a series worth watching.</h1>
      <p className="mx-auto mt-6 max-w-xl text-lg text-muted-foreground">
        Search a living catalog of TV series, explore every season, and keep your own watch trail.
      </p>
      <form className="mx-auto mt-10 flex max-w-xl gap-3" onSubmit={handleSearch}>
        <Input
          aria-label="Search series"
          placeholder="Try The Bear, Severance, or Dark"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
        />
        <Button type="submit" size="lg" disabled={isLoading}>
          <Search size={18} /> Search
        </Button>
      </form>
      </div>

      {isLoading && <p className="mt-16 text-center text-muted-foreground">Searching the catalog...</p>}
      {error && <p className="mt-16 text-center text-red-300">{error}</p>}
      {!isLoading && !error && hasSearched && results.length === 0 && (
        <p className="mt-16 text-center text-muted-foreground">No series found for “{query}”.</p>
      )}
      {!isLoading && results.length > 0 && (
        <div className="mt-16 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
          {results.map((series) => <SeriesCard key={series.id} series={series} />)}
        </div>
      )}

      {!hasSearched && (
      <div className="mt-16 grid gap-4 text-left sm:grid-cols-3">
        {["Explore", "Track", "Reflect"].map((title, index) => (
          <div key={title} className="rounded-xl border border-border bg-card p-5">
            <p className="text-sm font-medium text-primary">0{index + 1}</p>
            <h2 className="mt-4 font-semibold">{title}</h2>
            <p className="mt-2 text-sm text-muted-foreground">
              {index === 0 && "Discover shows with rich summaries and genres."}
              {index === 1 && "Mark episodes watched across visits and devices."}
              {index === 2 && "Leave notes and get concise AI-powered insights."}
            </p>
          </div>
        ))}
      </div>
      )}
    </section>
  );
}
