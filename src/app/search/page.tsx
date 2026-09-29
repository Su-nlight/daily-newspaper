import { PageContainer } from "@/components/layout/PageContainer";
import { SectionHeading } from "@/components/layout/SectionHeading";
import { SearchForm } from "@/components/search/SearchForm";
import { SearchResultCard } from "@/components/search/SearchResultCard";
import type { SearchFilters } from "@/types";
import {
  getArchive,
  getCategories,
  getRegions,
  getSources,
  getTopics,
  isStorySaved,
  searchStories,
} from "@/lib/api/client";
import { formatDisplayDate } from "@/lib/utils/date";

function firstParam(value: string | string[] | undefined): string | undefined {
  const raw = Array.isArray(value) ? value[0] : value;
  return raw && raw.trim() ? raw : undefined;
}

export default async function SearchPage({ searchParams }: PageProps<"/search">) {
  const params = await searchParams;

  const filters: SearchFilters = {
    query: firstParam(params.q),
    date: firstParam(params.date),
    category: firstParam(params.category),
    source: firstParam(params.source),
    topic: firstParam(params.topic),
    region: firstParam(params.region),
  };

  const hasActiveSearch = Object.values(filters).some((value) => value !== undefined);

  const [categories, sources, topics, regions, archive] = await Promise.all([
    getCategories(),
    getSources(),
    getTopics(),
    getRegions(),
    getArchive(),
  ]);

  const dates = archive
    .flatMap((group) => group.editions)
    .map((entry) => ({ value: entry.date, label: formatDisplayDate(entry.date) }));

  const results = hasActiveSearch ? await searchStories(filters) : [];
  const savedFlags = await Promise.all(results.map((article) => isStorySaved(article.id)));

  return (
    <PageContainer narrow>
      <SectionHeading eyebrow="Search" title="Search the Archive" />
      <SearchForm
        filters={filters}
        categories={categories}
        sources={sources}
        topics={topics}
        regions={regions}
        dates={dates}
      />

      {!hasActiveSearch ? (
        <p className="text-body border-t border-border pt-8 text-muted">
          Enter a search term or choose a filter to search across every Daily Signal story.
        </p>
      ) : results.length === 0 ? (
        <div className="flex flex-col items-center gap-2 border-t border-border pt-10 pb-4 text-center">
          <p className="text-headline">No results found.</p>
          <p className="text-body max-w-md text-muted">
            Try a different search term, or clear a filter to broaden your search.
          </p>
        </div>
      ) : (
        <div className="flex flex-col border-t border-border pt-2">
          <p className="text-caption pt-4">
            {results.length} {results.length === 1 ? "result" : "results"}
          </p>
          {results.map((article, index) => (
            <SearchResultCard key={article.id} article={article} initialSaved={savedFlags[index]} />
          ))}
        </div>
      )}
    </PageContainer>
  );
}
