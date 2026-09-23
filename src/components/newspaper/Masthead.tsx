import { siteConfig } from "@/lib/constants/site";
import { formatDisplayDate } from "@/lib/utils/date";

interface MastheadProps {
  editionLabel?: string;
  date?: string;
}

export function Masthead({ editionLabel, date }: MastheadProps) {
  const displayDate = date ?? new Date().toISOString();

  return (
    <div className="border-b-4 border-double border-foreground/80 pb-6 text-center">
      <p className="text-metadata mb-3">
        {formatDisplayDate(displayDate)}
        {editionLabel ? ` · ${editionLabel}` : ""}
      </p>
      <h1 className="text-display">{siteConfig.name}</h1>
      <p className="text-subheadline mt-2 text-muted">{siteConfig.tagline}</p>
    </div>
  );
}
