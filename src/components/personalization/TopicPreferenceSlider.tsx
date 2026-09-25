import type { Topic } from "@/types";
import { weightLabel } from "@/lib/utils/preferences";

interface TopicPreferenceSliderProps {
  topic: Topic;
  weight: number;
  onChange: (weight: number) => void;
}

export function TopicPreferenceSlider({ topic, weight, onChange }: TopicPreferenceSliderProps) {
  return (
    <div className="flex flex-col gap-2 border-b border-border py-4 last:border-b-0">
      <div className="flex items-baseline justify-between gap-4">
        <div>
          <p className="text-body font-medium text-foreground">{topic.name}</p>
          <p className="text-caption">{topic.description}</p>
        </div>
        <span className="text-metadata shrink-0 text-accent">{weightLabel(weight)}</span>
      </div>
      <input
        type="range"
        min={0}
        max={1}
        step={0.05}
        value={weight}
        onChange={(event) => onChange(Number(event.target.value))}
        aria-label={`Importance of ${topic.name}`}
        className="w-full accent-accent"
      />
    </div>
  );
}
