import { FormEvent, useEffect, useState } from "react";
import { LoaderCircle, MessageSquare, Send } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { apiRequest } from "@/lib/api";
import type { Comment } from "@/types/series";

interface CommentThreadProps {
  targetType: "series" | "episode";
  targetId: number;
}

export function CommentThread({ targetType, targetId }: CommentThreadProps) {
  const [comments, setComments] = useState<Comment[]>([]);
  const [content, setContent] = useState("");
  const [isOpen, setIsOpen] = useState(targetType === "series");
  const [isLoading, setIsLoading] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isOpen) return;
    const query = targetType === "series" ? `series_id=${targetId}` : `episode_id=${targetId}`;
    setIsLoading(true);
    apiRequest<Comment[]>(`/comments?${query}`)
      .then(setComments)
      .catch((requestError) => setError(requestError instanceof Error ? requestError.message : "Unable to load comments"))
      .finally(() => setIsLoading(false));
  }, [isOpen, targetId, targetType]);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!content.trim()) return;
    setIsSending(true);
    setError(null);
    try {
      const comment = await apiRequest<Comment>("/comments", {
        method: "POST",
        body: JSON.stringify({
          content,
          ...(targetType === "series" ? { series_id: targetId } : { episode_id: targetId }),
        }),
      });
      setComments((current) => [...current, comment]);
      setContent("");
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Unable to add comment");
    } finally {
      setIsSending(false);
    }
  }

  return (
    <div className={targetType === "series" ? "mt-10 rounded-xl border border-border bg-card p-5" : "mt-4 rounded-lg bg-muted/50 p-4"}>
      <button className="flex items-center gap-2 text-sm font-medium hover:text-primary" onClick={() => setIsOpen((value) => !value)}>
        <MessageSquare size={16} /> {targetType === "series" ? "Community notes" : "Episode comments"}
        {targetType === "episode" && <span className="text-muted-foreground">({comments.length})</span>}
      </button>
      {isOpen && <div className="mt-4">
        {isLoading && <p className="flex items-center text-sm text-muted-foreground"><LoaderCircle className="mr-2 animate-spin" size={15} /> Loading comments...</p>}
        {!isLoading && comments.length === 0 && <p className="text-sm text-muted-foreground">No notes yet. Start the conversation.</p>}
        <div className="space-y-3">{comments.map((comment) => <div key={comment.id} className="rounded-md border border-border/70 p-3"><div className="flex items-center justify-between gap-3"><p className="text-xs font-medium text-primary">{comment.author_label}</p><p className="text-xs text-muted-foreground">{new Date(comment.created_at).toLocaleString()}</p></div><p className="mt-2 text-sm leading-6">{comment.content}</p></div>)}</div>
        <form className="mt-4 flex gap-2" onSubmit={submit}>
          <Input value={content} onChange={(event) => setContent(event.target.value)} placeholder="Add a note..." maxLength={2000} aria-label="Comment" />
          <Button type="submit" size="icon" disabled={isSending || !content.trim()} aria-label="Send comment"><Send size={16} /></Button>
        </form>
        {error && <p className="mt-2 text-xs text-red-300">{error}</p>}
      </div>}
    </div>
  );
}
