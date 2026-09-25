"use client";

import { useState } from "react";

import { ReadingTimeSlider } from "@/components/personalization/ReadingTimeSlider";
import { ToggleChip } from "@/components/personalization/ToggleChip";
import { TopicPreferenceSlider } from "@/components/personalization/TopicPreferenceSlider";
import type { ContentType, Region, Source, Topic, UserPreferences } from "@/types";
import { recordSignal } from "@/lib/analytics/signals";

interface PreferencesEditorProps {
  topics: Topic[];
  regions: Region[];
  sources: Source[];
  contentTypes: ContentType[];
  initialPreferences: UserPreferences;
}

/**
 * Holds preference state locally for this session (no backend or
 * persistence yet — see docs/PROJECT_STATE.md). Every change here is UI +
 * data-model only; nothing here ranks content with ML.
 */
export function PreferencesEditor({
  topics,
  regions,
  sources,
  contentTypes,
  initialPreferences,
}: PreferencesEditorProps) {
  const [preferences, setPreferences] = useState<UserPreferences>(initialPreferences);

  function setTopicWeight(topicId: string, weight: number) {
    setPreferences((prev) => {
      const previousWeight = prev.topics.find((t) => t.id === topicId)?.weight ?? 0;

      if (previousWeight <= 0 && weight > 0) {
        recordSignal("topic_followed", { topicId, weight });
      } else if (previousWeight > 0 && weight <= 0) {
        recordSignal("topic_ignored", { topicId });
      }

      const exists = prev.topics.some((t) => t.id === topicId);
      const nextTopics = exists
        ? prev.topics.map((t) => (t.id === topicId ? { ...t, weight } : t))
        : [...prev.topics, { id: topicId, weight }];

      return { ...prev, topics: nextTopics };
    });
  }

  function toggleInList(key: "regions" | "sources" | "contentTypes", id: string) {
    setPreferences((prev) => {
      const current = prev[key];
      const next = current.includes(id) ? current.filter((item) => item !== id) : [...current, id];
      return { ...prev, [key]: next };
    });
  }

  function weightFor(topicId: string): number {
    return preferences.topics.find((t) => t.id === topicId)?.weight ?? 0;
  }

  return (
    <div className="flex flex-col gap-12">
      <section className="flex flex-col gap-4">
        <p className="text-section-title text-accent">Your Interests</p>
        <p className="text-body text-muted">
          Adjust how much weight each topic gets in your personalized sections. Setting a topic to
          &quot;Not following&quot; removes it from Relevant to You.
        </p>
        <div className="flex flex-col">
          {topics.map((topic) => (
            <TopicPreferenceSlider
              key={topic.id}
              topic={topic}
              weight={weightFor(topic.id)}
              onChange={(weight) => setTopicWeight(topic.id, weight)}
            />
          ))}
        </div>
      </section>

      <section className="flex flex-col gap-4 border-t border-border pt-8">
        <p className="text-section-title text-accent">Regions</p>
        <p className="text-body text-muted">Prioritize coverage tied to these regions.</p>
        <div className="flex flex-wrap gap-2">
          {regions.map((region) => (
            <ToggleChip
              key={region.id}
              label={region.name}
              active={preferences.regions.includes(region.id)}
              onToggle={() => toggleInList("regions", region.id)}
            />
          ))}
        </div>
      </section>

      <section className="flex flex-col gap-4 border-t border-border pt-8">
        <p className="text-section-title text-accent">Sources</p>
        <p className="text-body text-muted">Follow specific publishers to prioritize their coverage.</p>
        <div className="flex flex-wrap gap-2">
          {sources.map((source) => (
            <ToggleChip
              key={source.id}
              label={source.name}
              description={source.country}
              active={preferences.sources.includes(source.id)}
              onToggle={() => toggleInList("sources", source.id)}
            />
          ))}
        </div>
      </section>

      <section className="flex flex-col gap-4 border-t border-border pt-8">
        <p className="text-section-title text-accent">Content Types</p>
        <p className="text-body text-muted">Choose which parts of Daily Signal to prioritize.</p>
        <div className="flex flex-wrap gap-2">
          {contentTypes.map((contentType) => (
            <ToggleChip
              key={contentType.id}
              label={contentType.name}
              description={contentType.description}
              active={preferences.contentTypes.includes(contentType.id)}
              onToggle={() => toggleInList("contentTypes", contentType.id)}
            />
          ))}
        </div>
      </section>

      <section className="flex flex-col gap-4 border-t border-border pt-8">
        <p className="text-section-title text-accent">Reading Time</p>
        <ReadingTimeSlider
          minutes={preferences.readingTime}
          onChange={(minutes) => setPreferences((prev) => ({ ...prev, readingTime: minutes }))}
        />
      </section>

      <p className="text-caption border-t border-border pt-6">
        These preferences shape what Daily Signal prioritizes for you today. They&apos;re rule-based,
        not AI-generated — automated, model-driven personalization is planned for a later module.
        Changes here aren&apos;t saved between visits yet.
      </p>
    </div>
  );
}
