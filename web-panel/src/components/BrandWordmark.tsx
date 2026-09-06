type BrandWordmarkProps = {
  variant?: "light" | "dark";
  className?: string;
};

export default function BrandWordmark({ variant = "light", className = "" }: BrandWordmarkProps) {
  const classes = ["nexo-wordmark", variant === "dark" ? "nexo-wordmark--dark" : "", className]
    .filter(Boolean)
    .join(" ");

  return (
    <h1 className={classes}>
      <span className="nexo-heavy">Agro</span>
      <span className="nexo-light">Plaga</span>
    </h1>
  );
}
