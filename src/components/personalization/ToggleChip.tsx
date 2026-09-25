interface ToggleChipProps {
  label: string;
  description?: string;
  active: boolean;
  onToggle: () => void;
}

export function ToggleChip({ label, description, active, onToggle }: ToggleChipProps) {
  return (
    <button
      type="button"
      onClick={onToggle}
      aria-pressed={active}
      title={description}
      className={`text-metadata flex items-center gap-1.5 rounded-full border px-3 py-1.5 transition-colors ${
        active
          ? "border-accent bg-accent text-accent-foreground"
          : "border-border text-foreground hover:border-border-strong hover:bg-background-elevated"
      }`}
    >
      {active ? <span aria-hidden="true">✓</span> : null}
      {label}
    </button>
  );
}
