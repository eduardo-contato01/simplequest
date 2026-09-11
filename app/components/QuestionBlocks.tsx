import { visibleQuestionContentBlocks, type Question, type QuestionContentBlock, type QuestionInlineContentBlock, type TextAlignment } from "../question-model";
import { InlineMath, MathFormula } from "./MathFormula";
import { QuestionMedia } from "./QuestionMedia";

function TextBlock({ block }: { block: Extract<QuestionContentBlock, { type: "text" }> }) {
  if (!block.segments?.length) return <>{block.text}</>;
  return <>{block.segments.map((segment, index) => {
    let content = <>{segment.text}</>;
    if (segment.underline) content = <u>{content}</u>;
    if (segment.italic) content = <em>{content}</em>;
    if (segment.bold) content = <strong>{content}</strong>;
    return <span key={`${block.id}-${index}`}>{content}</span>;
  })}</>;
}

type ParsedTableCell = {
  blocks: QuestionInlineContentBlock[];
  rowSpan: number;
  colSpan: number;
  merged: boolean;
  ghost: boolean;
};

function isVerticalMergeMarker(blocks: QuestionInlineContentBlock[]) {
  return blocks.length === 1 && blocks[0].type === "text" && blocks[0].text.trim() === "^";
}

function isHorizontalMergeMarker(blocks: QuestionInlineContentBlock[]) {
  return blocks.length === 1 && blocks[0].type === "text" && blocks[0].text.trim() === ">";
}

function isGhostCellMarker(blocks: QuestionInlineContentBlock[]) {
  return blocks.length === 1 && blocks[0].type === "text" && blocks[0].text.trim() === "~";
}

function parseTableContent(block: Extract<QuestionContentBlock, { type: "table" }>): ParsedTableCell[][] {
  const source: QuestionInlineContentBlock[] = block.content?.length
    ? block.content
    : [{ id: `${block.id}-text`, type: "text", text: block.data }];
  const rows: QuestionInlineContentBlock[][][] = [[[]]];
  let part = 0;
  let quoted = false;
  const currentCell = () => rows[rows.length - 1][rows[rows.length - 1].length - 1];
  const nextCell = () => rows[rows.length - 1].push([]);
  const nextRow = () => rows.push([[]]);
  const pushText = (content: Extract<QuestionInlineContentBlock, { type: "text" }>, segment: NonNullable<typeof content.segments>[number], text: string) => {
    if (!text) return;
    const formatted = Boolean(segment.bold || segment.italic || segment.underline);
    currentCell().push({
      id: `${content.id}-table-${part++}`,
      type: "text",
      text,
      alignment: content.alignment,
      segments: formatted ? [{ ...segment, text }] : undefined,
    });
  };

  for (const content of source) {
    if (content.type !== "text") {
      currentCell().push(content);
      continue;
    }
    const segments = content.segments?.length ? content.segments : [{ text: content.text }];
    for (const segment of segments) {
      let buffer = "";
      for (const character of segment.text.replace(/\r\n/g, "\n")) {
        if (character === "`" || character === "´") {
          pushText(content, segment, buffer);
          buffer = "";
          quoted = !quoted;
        } else if (!quoted && character === "|") {
          pushText(content, segment, buffer);
          buffer = "";
          nextCell();
        } else if (!quoted && character === "\n") {
          pushText(content, segment, buffer);
          buffer = "";
          nextRow();
        } else {
          buffer += character;
        }
      }
      pushText(content, segment, buffer);
    }
  }
  const parsedRows = rows
    .filter((row) => row.some((cell) => cell.some((content) => content.type !== "text" || content.text.trim())))
    .map((row) => row.map((blocks) => ({ blocks, rowSpan: 1, colSpan: 1, merged: false, ghost: isGhostCellMarker(blocks) })));

  for (const row of parsedRows) {
    for (let cellIndex = 0; cellIndex < row.length; cellIndex += 1) {
      const cell = row[cellIndex];
      if (!isHorizontalMergeMarker(cell.blocks)) continue;
      for (let targetIndex = cellIndex - 1; targetIndex >= 0; targetIndex -= 1) {
        const target = row[targetIndex];
        if (target.merged) continue;
        if (target.ghost) break;
        target.colSpan += 1;
        cell.merged = true;
        break;
      }
    }
  }

  for (let rowIndex = 1; rowIndex < parsedRows.length; rowIndex += 1) {
    for (let cellIndex = 0; cellIndex < parsedRows[rowIndex].length; cellIndex += 1) {
      const cell = parsedRows[rowIndex][cellIndex];
      if (!isVerticalMergeMarker(cell.blocks)) continue;

      for (let targetRow = rowIndex - 1; targetRow >= 0; targetRow -= 1) {
        const target = parsedRows[targetRow][cellIndex];
        if (!target || target.merged) continue;
        target.rowSpan += 1;
        cell.merged = true;
        break;
      }
    }
  }

  return parsedRows;
}

function TableCellContent({ blocks }: { blocks: QuestionInlineContentBlock[] }) {
  return <>{blocks.map((block) => block.type === "text"
    ? <TextBlock block={block} key={block.id} />
    : block.type === "script"
      ? <span className="formatted-script" key={block.id}>{block.base}{block.position === "superscript" ? <sup>{block.value}</sup> : <sub>{block.value}</sub>}</span>
      : <InlineMath latex={block.latex} key={block.id} />)}</>;
}

function TableRow({ row, rowIndex, rowCount, columnCount, header = false, alignment }: { row: ParsedTableCell[]; rowIndex: number; rowCount: number; columnCount: number; header?: boolean; alignment: TextAlignment }) {
  return <tr>{row.map((cell, cellIndex) => {
    if (cell.merged) return null;
    const className = cell.ghost ? [
      "ghost-cell",
      rowIndex === 0 && "ghost-top",
      rowIndex + cell.rowSpan >= rowCount && "ghost-bottom",
      cellIndex === 0 && "ghost-left",
      cellIndex + cell.colSpan >= columnCount && "ghost-right",
    ].filter(Boolean).join(" ") : undefined;
    const content = cell.ghost ? null : <TableCellContent blocks={cell.blocks} />;
    return header
      ? <th key={cellIndex} className={className} aria-hidden={cell.ghost || undefined} scope={cell.colSpan > 1 ? "colgroup" : "col"} rowSpan={cell.rowSpan} colSpan={cell.colSpan} style={{ textAlign: alignment }}>{content}</th>
      : <td key={cellIndex} className={className} aria-hidden={cell.ghost || undefined} rowSpan={cell.rowSpan} colSpan={cell.colSpan} style={{ textAlign: alignment }}>{content}</td>;
  })}</tr>;
}

function TableBlock({ block }: { block: Extract<QuestionContentBlock, { type: "table" }> }) {
  const rows = parseTableContent(block);
  const columnCount = Math.max(0, ...rows.map((row) => row.length));
  const headerRows = Math.max(0, Math.min(rows.length, block.headerRows ?? (block.hasHeader === false ? 0 : 1)));
  const legacyHeaderSpansBody = block.headerRows === undefined && headerRows === 1 && rows[0]?.some((cell) => !cell.merged && cell.rowSpan > 1);
  const alignment = block.content?.find((content) => content.type === "text")?.alignment || "center";
  return (
    <div className="question-section question-table-wrap">
      <table className="question-table" style={{ fontSize: `${Math.max(8, Math.min(18, block.fontSize || 11))}px` }}>
        {headerRows > 0 && !legacyHeaderSpansBody && <thead>{rows.slice(0, headerRows).map((row, rowIndex) => <TableRow row={row} rowIndex={rowIndex} rowCount={rows.length} columnCount={columnCount} header alignment={alignment} key={rowIndex} />)}</thead>}
        <tbody>{rows.slice(legacyHeaderSpansBody ? 0 : headerRows).map((row, rowIndex) => { const sourceRowIndex = rowIndex + (legacyHeaderSpansBody ? 0 : headerRows); return <TableRow row={row} rowIndex={sourceRowIndex} rowCount={rows.length} columnCount={columnCount} header={legacyHeaderSpansBody && rowIndex === 0} alignment={alignment} key={rowIndex} />; })}</tbody>
      </table>
    </div>
  );
}

export function QuestionBlocks({ question, print = false, blocks, compact = false }: { question: Question; print?: boolean; blocks?: QuestionContentBlock[]; compact?: boolean }) {
  const orderedBlocks = blocks ? visibleQuestionContentBlocks({
    ...question,
    contentBlocks: blocks,
    hasMath: blocks.some((block) => block.type === "formula" || block.type === "script"),
    hasTable: blocks.some((block) => block.type === "table"),
    hasMedia: blocks.some((block) => block.type === "image" || block.type === "pending-media"),
  }) : visibleQuestionContentBlocks(question);
  const grouped: Array<QuestionContentBlock | { type: "inline-flow"; id: string; blocks: QuestionContentBlock[] }> = [];
  let inlineCandidates: QuestionContentBlock[] = [];
  const flushInline = () => {
    if (!inlineCandidates.length) return;
    if (inlineCandidates.length > 1 || inlineCandidates.some((block) => block.type !== "text")) grouped.push({ type: "inline-flow", id: inlineCandidates.map((block) => block.id).join("-"), blocks: inlineCandidates });
    else grouped.push(...inlineCandidates);
    inlineCandidates = [];
  };
  for (const block of orderedBlocks) {
    if (block.type === "text" && block.section) {
      flushInline();
      inlineCandidates.push(block);
      continue;
    }
    if (block.type === "text" || block.type === "script" || (block.type === "formula" && (compact || block.display === "inline"))) inlineCandidates.push(block);
    else { flushInline(); grouped.push(block); }
  }
  flushInline();

  return grouped.map((block) => {
    if (block.type === "inline-flow") return <div className="question-section question-inline-flow" style={{ textAlign: block.blocks.find((part) => part.type === "text")?.alignment || "left" }} key={block.id}>{block.blocks.map((part) => part.type === "text" ? <TextBlock block={part} key={part.id} /> : part.type === "script" ? <span className="formatted-script" key={part.id}>{part.base}{part.position === "superscript" ? <sup>{part.value}</sup> : <sub>{part.value}</sub>}</span> : part.type === "formula" ? <InlineMath latex={part.latex} key={part.id} /> : null)}</div>;
    if (block.type === "text") return <div className="question-section question-stem" style={{ textAlign: block.alignment || "left" }} key={block.id}><TextBlock block={block} /></div>;
    if (block.type === "formula") return <div className="question-section" key={block.id}><MathFormula latex={block.latex} className="question-formula" /></div>;
    if (block.type === "table") return <TableBlock block={block} key={block.id} />;
    if (block.type === "image") return <QuestionMedia key={block.id} urls={block.urls} dimensions={block.dimensions} displayScale={block.displayScale} hiddenByDefault={block.hiddenByDefault} questionNumber={question.number} print={print} />;
    return null;
  });
}
