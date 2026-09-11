import katex from "katex";

export function MathFormula({ latex, className = "" }: { latex: string; className?: string }) {
  if (!latex.trim()) return null;
  const html = katex.renderToString(latex, {
    displayMode: true,
    throwOnError: false,
    strict: "ignore",
    trust: false,
    output: "htmlAndMathml",
  });
  return <div className={`math-formula ${className}`} dangerouslySetInnerHTML={{ __html: html }} />;
}

export function InlineMath({ latex, className = "" }: { latex: string; className?: string }) {
  if (!latex.trim()) return null;
  const html = katex.renderToString(`\\displaystyle ${latex}`, {
    displayMode: false,
    throwOnError: false,
    strict: "ignore",
    trust: false,
    output: "htmlAndMathml",
  });
  return <span className={`inline-math ${className}`} dangerouslySetInnerHTML={{ __html: html }} />;
}
