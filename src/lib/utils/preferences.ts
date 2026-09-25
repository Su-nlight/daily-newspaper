/** Converts a 0–1 topic weight into an editorial label rather than a raw
 *  percentage, keeping the preferences UI from reading like a dashboard. */
export function weightLabel(weight: number): string {
  if (weight <= 0) return "Not following";
  if (weight < 0.34) return "Low";
  if (weight < 0.67) return "Medium";
  if (weight < 1) return "High";
  return "Essential";
}
