interface StorySummaryProps {
  text: string;
}

export function StorySummary({ text }: StorySummaryProps) {
  return (
    <p className="text-subheadline font-normal text-foreground" style={{ lineHeight: 1.4 }}>
      {text}
    </p>
  );
}
