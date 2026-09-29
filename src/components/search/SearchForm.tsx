import Form from "next/form";

import type { Category, Region, SearchFilters, Source, Topic } from "@/types";

interface SearchFormProps {
  filters: SearchFilters;
  categories: Category[];
  sources: Source[];
  topics: Topic[];
  regions: Region[];
  dates: { value: string; label: string }[];
}

/**
 * A plain GET form (via next/form) — search state lives entirely in the URL
 * (?q=&date=&category=&source=&topic=&region=), not client React state.
 * That gives shareable/bookmarkable search URLs, works without JS, and
 * gets a free "searching" loading state from app/search/loading.tsx during
 * the client-side transition next/form provides.
 */
export function SearchForm({ filters, categories, sources, topics, regions, dates }: SearchFormProps) {
  return (
    <Form action="/search" className="flex flex-col gap-5">
      <input
        type="search"
        name="q"
        defaultValue={filters.query ?? ""}
        placeholder="What are you looking for?"
        aria-label="Search Daily Signal"
        className="text-headline w-full border-b-2 border-border-strong bg-transparent py-3 text-foreground placeholder:text-muted focus:border-accent focus:outline-none"
      />

      <div className="flex flex-wrap gap-3">
        <select
          name="date"
          defaultValue={filters.date ?? ""}
          aria-label="Filter by date"
          className="text-metadata border border-border bg-background px-3 py-2 text-foreground"
        >
          <option value="">Any date</option>
          {dates.map((date) => (
            <option key={date.value} value={date.value}>
              {date.label}
            </option>
          ))}
        </select>

        <select
          name="category"
          defaultValue={filters.category ?? ""}
          aria-label="Filter by category"
          className="text-metadata border border-border bg-background px-3 py-2 text-foreground"
        >
          <option value="">Any category</option>
          {categories.map((category) => (
            <option key={category.slug} value={category.slug}>
              {category.name}
            </option>
          ))}
        </select>

        <select
          name="source"
          defaultValue={filters.source ?? ""}
          aria-label="Filter by source"
          className="text-metadata border border-border bg-background px-3 py-2 text-foreground"
        >
          <option value="">Any source</option>
          {sources.map((source) => (
            <option key={source.id} value={source.id}>
              {source.name}
            </option>
          ))}
        </select>

        <select
          name="topic"
          defaultValue={filters.topic ?? ""}
          aria-label="Filter by topic"
          className="text-metadata border border-border bg-background px-3 py-2 text-foreground"
        >
          <option value="">Any topic</option>
          {topics.map((topic) => (
            <option key={topic.id} value={topic.id}>
              {topic.name}
            </option>
          ))}
        </select>

        <select
          name="region"
          defaultValue={filters.region ?? ""}
          aria-label="Filter by region"
          className="text-metadata border border-border bg-background px-3 py-2 text-foreground"
        >
          <option value="">Any region</option>
          {regions.map((region) => (
            <option key={region.id} value={region.id}>
              {region.name}
            </option>
          ))}
        </select>

        <button
          type="submit"
          className="text-metadata border border-border-strong bg-background-elevated px-4 py-2 text-accent transition-colors hover:bg-background"
        >
          Search
        </button>
      </div>
    </Form>
  );
}
