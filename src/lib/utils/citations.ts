/**
 * Turns inline citation markers like [1] into Markdown links to an in-page
 * anchor (#cite-1) so the renderer can style them as superscript links to
 * the source list. Skips fenced and inline code so `arr[1]` is untouched,
 * and leaves real Markdown links like [text](url) alone.
 */
export function linkifyCitations(markdown: string): string {
  const parts = markdown.split(/(```[\s\S]*?```|`[^`\n]*`)/g);
  return parts
    .map((part, index) =>
      index % 2 === 1 ? part : part.replace(/\[(\d{1,2})\](?!\()/g, "[[$1]](#cite-$1)"),
    )
    .join("");
}
