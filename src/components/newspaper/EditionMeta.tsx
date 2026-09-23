import type { Edition } from "@/types";
import { formatDisplayDate } from "@/lib/utils/date";

interface EditionMetaProps {
  edition: Edition;
}

export function EditionMeta({ edition }: EditionMetaProps) {
  return (
    <div className="flex flex-col gap-2 border-b border-border pb-8 text-center">
      <p className="text-metadata">
        {formatDisplayDate(edition.date)} · Edition {edition.id}
      </p>
      <h1 className="text-headline">{edition.headline}</h1>
      <p className="text-body mx-auto max-w-2xl text-muted">{edition.summary}</p>
    </div>
  );
}
