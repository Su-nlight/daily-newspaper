export function formatDisplayDate(isoDate: string): string {
  return new Intl.DateTimeFormat("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  }).format(new Date(isoDate));
}

export function formatDisplayDateTime(isoDate: string): string {
  return new Intl.DateTimeFormat("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(isoDate));
}

export function formatRelativeTime(isoDate: string, now: Date = new Date()): string {
  const diffMs = now.getTime() - new Date(isoDate).getTime();
  const diffMinutes = Math.round(diffMs / 60000);

  if (diffMinutes < 1) return "just now";
  if (diffMinutes < 60) return `${diffMinutes}m ago`;

  const diffHours = Math.round(diffMinutes / 60);
  if (diffHours < 24) return `${diffHours}h ago`;

  const diffDays = Math.round(diffHours / 24);
  if (diffDays < 7) return `${diffDays}d ago`;

  return formatDisplayDate(isoDate);
}

/** "22 — Today" for the current edition date, otherwise "21 — Monday". Date
 *  strings are bare YYYY-MM-DD, so formatting is pinned to UTC to avoid an
 *  off-by-one day shift in timezones behind UTC. */
export function archiveDayLabel(isoDate: string, todayIsoDate: string): string {
  const day = new Date(`${isoDate}T00:00:00Z`).getUTCDate();
  if (isoDate === todayIsoDate) return `${day} — Today`;

  const weekday = new Intl.DateTimeFormat("en-IN", { weekday: "long", timeZone: "UTC" }).format(
    new Date(`${isoDate}T00:00:00Z`),
  );
  return `${day} — ${weekday}`;
}

/** "September 2026" for a bare YYYY-MM-DD date, pinned to UTC. */
export function monthYearLabel(isoDate: string): string {
  return new Intl.DateTimeFormat("en-IN", {
    month: "long",
    year: "numeric",
    timeZone: "UTC",
  }).format(new Date(`${isoDate}T00:00:00Z`));
}
