import { useState } from "react";
import { Brain, LoaderCircle, Sparkles } from "lucide-react";

import { Button } from "@/components/ui/button";
import { apiRequest } from "@/lib/api";

export function InsightCard({ targetType, targetId }: { targetType: "series" | "episode"; targetId: number }) {
  const [insight, setInsight] = useState<string | null>(null);
  const [usedFallback, setUsedFallback] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function loadInsight() {
    setIsLoading(true);
    setError(null);
    const path = targetType === "series" ? `/series/${targetId}/insight` : `/episodes/${targetId}/insight`;
    try {
      const response = await apiRequest<{ insight: string; used_fallback: boolean }>(path);
      setInsight(response.insight);
      setUsedFallback(response.used_fallback);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Unable to generate insight");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="mt-4 rounded-lg border border-primary/20 bg-primary/5 p-4">
      {!insight && !isLoading && <Button variant="outline" size="sm" onClick={loadInsight}><Sparkles size={16} /> Get AI insight</Button>}
      {isLoading && <p className="flex items-center text-sm text-muted-foreground"><LoaderCircle className="mr-2 animate-spin" size={15} /> Thinking about this story...</p>}
      {insight && <div className="flex gap-3"><Brain className="mt-0.5 shrink-0 text-primary" size={18} /><div><p className="text-sm leading-6">{insight}</p><p className="mt-2 text-xs text-muted-foreground">{usedFallback ? "Local fallback insight" : "AI-generated insight"}</p></div></div>}
      {error && <p className="mt-2 text-xs text-red-300">{error}</p>}
    </div>
  );
}
