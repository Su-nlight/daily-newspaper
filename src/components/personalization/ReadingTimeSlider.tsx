interface ReadingTimeSliderProps {
  minutes: number;
  onChange: (minutes: number) => void;
}

const STEPS = [5, 10, 15, 20, 30];

export function ReadingTimeSlider({ minutes, onChange }: ReadingTimeSliderProps) {
  return (
    <div className="flex flex-col gap-2">
      <div className="flex items-baseline justify-between gap-4">
        <p className="text-body text-foreground">Daily reading time budget</p>
        <span className="text-metadata text-accent">{minutes} min</span>
      </div>
      <input
        type="range"
        min={5}
        max={30}
        step={5}
        value={minutes}
        onChange={(event) => onChange(Number(event.target.value))}
        aria-label="Daily reading time budget in minutes"
        className="w-full accent-accent"
      />
      <div className="text-caption flex justify-between">
        {STEPS.map((step) => (
          <span key={step}>{step}m</span>
        ))}
      </div>
    </div>
  );
}
