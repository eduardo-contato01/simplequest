"use client";

import { useEffect, useLayoutEffect, useMemo, useRef, useState } from "react";
import type { FormEvent, KeyboardEvent as ReactKeyboardEvent, MouseEvent as ReactMouseEvent } from "react";
import type { QuestionContentBlock, QuestionTextSegment, TextAlignment } from "../question-model";
import { FormulaEditor } from "./FormulaEditor";
import { InlineMath } from "./MathFormula";

type InlineBlock = Extract<QuestionContentBlock, { type: "text" | "formula" | "script" }>;
type MathBlock = Exclude<InlineBlock, { type: "text" }>;
type TextBlock = Extract<InlineBlock, { type: "text" }>;
export type TextFormat = "bold" | "italic" | "underline";

type NativeSelectionSnapshot = {
  anchorNode: Node;
  anchorOffset: number;
  focusNode: Node;
  focusOffset: number;
};

type Props = {
  blocks: InlineBlock[];
  onChange: (blocks: InlineBlock[]) => void;
  onActivateFormulaInsertion?: (insert: () => void) => void;
  onActivateTextFormatting?: (apply: (format: TextFormat) => void, activeFormats: TextFormat[]) => void;
  onActivateTextAlignment?: (apply: (alignment: TextAlignment) => void, activeAlignment: TextAlignment) => void;
  onDeactivate?: () => void;
  disabled?: boolean;
  defaultAlignment?: TextAlignment;
  label: string;
};

function scriptLatex(block: Extract<InlineBlock, { type: "script" }>) {
  return `${block.base}${block.position === "superscript" ? "^" : "_"}{${block.value}}`;
}

function inlineLatex(block: InlineBlock) {
  if (block.type === "formula") return block.latex || "\u25a1";
  if (block.type === "script") return scriptLatex(block);
  return "";
}

function nextBlockId(prefix: string, blocks: InlineBlock[]) {
  const used = new Set(blocks.map((block) => block.id));
  let suffix = blocks.length + 1;
  while (used.has(`${prefix}-${suffix}`)) suffix += 1;
  return `${prefix}-${suffix}`;
}

function editorContentKey(blocks: InlineBlock[]) {
  const content = JSON.stringify(blocks);
  let hash = 2166136261;
  for (let index = 0; index < content.length; index += 1) {
    hash ^= content.charCodeAt(index);
    hash = Math.imul(hash, 16777619);
  }
  return `inline-editor-${blocks.length}-${(hash >>> 0).toString(36)}`;
}

function mergeSegments(segments: QuestionTextSegment[]) {
  const merged: QuestionTextSegment[] = [];
  for (const segment of segments) {
    if (!segment.text) continue;
    const previous = merged[merged.length - 1];
    if (previous && Boolean(previous.bold) === Boolean(segment.bold) && Boolean(previous.italic) === Boolean(segment.italic) && Boolean(previous.underline) === Boolean(segment.underline)) previous.text += segment.text;
    else merged.push({ ...segment });
  }
  return merged;
}

function segmentsFromElement(element: HTMLElement) {
  const segments: QuestionTextSegment[] = [];
  const append = (text: string, bold = false, italic = false, underline = false) => {
    if (text) segments.push({ text, bold: bold || undefined, italic: italic || undefined, underline: underline || undefined });
  };
  const visit = (node: Node, bold = false, italic = false, underline = false) => {
    if (node.nodeType === Node.TEXT_NODE) {
      append(node.textContent || "", bold, italic, underline);
      return;
    }
    if (!(node instanceof HTMLElement)) return;
    const tag = node.tagName;
    if (tag === "BR") {
      append("\n", bold, italic, underline);
      return;
    }
    const blockBreak = (tag === "DIV" || tag === "P") && segments.length > 0 && !segments[segments.length - 1].text.endsWith("\n");
    if (blockBreak) append("\n", bold, italic, underline);
    const nextBold = bold || tag === "B" || tag === "STRONG";
    const nextItalic = italic || tag === "I" || tag === "EM";
    const nextUnderline = underline || tag === "U";
    node.childNodes.forEach((child) => visit(child, nextBold, nextItalic, nextUnderline));
  };
  element.childNodes.forEach((child) => visit(child));
  return mergeSegments(segments);
}

function compositeBlocksFromElement(element: HTMLElement, currentBlocks: InlineBlock[]) {
  const currentById = new Map(currentBlocks.map((block) => [block.id, block]));
  const parsed: InlineBlock[] = [];
  let pendingId = "";
  let segments: QuestionTextSegment[] = [];
  const append = (text: string, bold = false, italic = false, underline = false) => {
    if (!text) return;
    const previous = segments[segments.length - 1];
    if (previous && Boolean(previous.bold) === bold && Boolean(previous.italic) === italic && Boolean(previous.underline) === underline) previous.text += text;
    else segments.push({ text, bold: bold || undefined, italic: italic || undefined, underline: underline || undefined });
  };
  const flushText = () => {
    const text = segments.map((segment) => segment.text).join("").replace(/\r/g, "");
    if (!text && parsed.length) {
      segments = [];
      pendingId = "";
      return;
    }
    const id = pendingId || nextBlockId("text", [...currentBlocks, ...parsed]);
    const previous = currentById.get(id);
    parsed.push({
      id,
      type: "text",
      text,
      segments: segments.some((segment) => segment.bold || segment.italic || segment.underline) ? mergeSegments(segments) : undefined,
      alignment: previous?.type === "text" ? previous.alignment : undefined,
      section: previous?.type === "text" ? previous.section : undefined,
    });
    segments = [];
    pendingId = "";
  };
  const visit = (node: Node, bold = false, italic = false, underline = false) => {
    if (node.nodeType === Node.TEXT_NODE) {
      append(node.textContent || "", bold, italic, underline);
      return;
    }
    if (!(node instanceof HTMLElement)) return;
    const mathId = node.dataset.inlineMathId;
    if (mathId) {
      flushText();
      const math = currentById.get(mathId);
      if (math && math.type !== "text") parsed.push(math);
      return;
    }
    if (node.dataset.blockId && !pendingId) pendingId = node.dataset.blockId;
    if (node.tagName === "BR") {
      append("\n", bold, italic, underline);
      return;
    }
    if ((node.tagName === "DIV" || node.tagName === "P") && (segments.length || parsed.length)) {
      const previousText = segments[segments.length - 1]?.text || "";
      if (!previousText.endsWith("\n")) append("\n", bold, italic, underline);
    }
    const nextBold = bold || node.tagName === "B" || node.tagName === "STRONG";
    const nextItalic = italic || node.tagName === "I" || node.tagName === "EM";
    const nextUnderline = underline || node.tagName === "U";
    node.childNodes.forEach((child) => visit(child, nextBold, nextItalic, nextUnderline));
  };
  element.childNodes.forEach((child) => visit(child));
  flushText();
  if (!parsed.length) return [{ id: currentBlocks.find((block) => block.type === "text")?.id || "text-1", type: "text", text: "" } satisfies TextBlock];
  if (parsed[0].type !== "text") parsed.unshift({ id: nextBlockId("text-before", [...currentBlocks, ...parsed]), type: "text", text: "" });
  if (parsed[parsed.length - 1].type !== "text") parsed.push({ id: nextBlockId("text-after", [...currentBlocks, ...parsed]), type: "text", text: "" });
  return parsed;
}

function compositeSelectionOffsets(element: HTMLElement) {
  const selection = window.getSelection();
  if (!selection?.rangeCount) return { start: 0, end: 0 };
  const selected = selection.getRangeAt(0);
  const lengthTo = (node: Node, offset: number) => {
    const range = document.createRange();
    range.selectNodeContents(element);
    try {
      range.setEnd(node, offset);
    } catch {
      return 0;
    }
    const fragment = range.cloneContents();
    fragment.querySelectorAll<HTMLElement>("[data-inline-math-id]").forEach((math) => math.replaceWith(document.createTextNode("\uFFFC")));
    fragment.querySelectorAll("br").forEach((breakElement) => breakElement.replaceWith(document.createTextNode("\n")));
    return fragment.textContent?.length || 0;
  };
  return { start: lengthTo(selected.startContainer, selected.startOffset), end: lengthTo(selected.endContainer, selected.endOffset) };
}

function placeCompositeSelection(element: HTMLElement, requestedStart: number, requestedEnd = requestedStart) {
  element.focus();
  const selection = window.getSelection();
  const range = document.createRange();
  const positionAt = (requestedOffset: number) => {
    let remaining = Math.max(0, requestedOffset);
    const visit = (node: Node): { node: Node; offset: number } | null => {
      if (node instanceof HTMLElement && node.dataset.inlineMathId) {
        const parent = node.parentNode;
        if (!parent) return null;
        const index = Array.prototype.indexOf.call(parent.childNodes, node);
        if (remaining <= 0) return { node: parent, offset: index };
        if (remaining === 1) return { node: parent, offset: index + 1 };
        remaining -= 1;
        return null;
      }
      if (node.nodeType === Node.TEXT_NODE) {
        const length = node.textContent?.length || 0;
        if (remaining <= length) return { node, offset: remaining };
        remaining -= length;
        return null;
      }
      for (const child of Array.from(node.childNodes)) {
        const result = visit(child);
        if (result) return result;
      }
      return null;
    };
    return visit(element) || { node: element as Node, offset: element.childNodes.length };
  };
  const start = positionAt(Math.min(requestedStart, requestedEnd));
  const end = positionAt(Math.max(requestedStart, requestedEnd));
  range.setStart(start.node, start.offset);
  range.setEnd(end.node, end.offset);
  selection?.removeAllRanges();
  selection?.addRange(range);
}

function splitSegments(segments: QuestionTextSegment[], offset: number) {
  const before: QuestionTextSegment[] = [];
  const after: QuestionTextSegment[] = [];
  let consumed = 0;
  for (const segment of segments) {
    const boundary = Math.max(0, Math.min(offset - consumed, segment.text.length));
    if (boundary > 0) before.push({ ...segment, text: segment.text.slice(0, boundary) });
    if (boundary < segment.text.length) after.push({ ...segment, text: segment.text.slice(boundary) });
    consumed += segment.text.length;
  }
  return [mergeSegments(before), mergeSegments(after)] as const;
}

function hasSegmentFormatting(segment: QuestionTextSegment) {
  return Boolean(segment.bold || segment.italic || segment.underline);
}

function deleteCompositeRange(blocks: InlineBlock[], requestedStart: number, requestedEnd: number) {
  const start = Math.max(0, Math.min(requestedStart, requestedEnd));
  const end = Math.max(start, Math.max(requestedStart, requestedEnd));
  const retained: InlineBlock[] = [];
  let position = 0;

  for (const block of blocks) {
    const length = block.type === "text" ? block.text.length : 1;
    const blockStart = position;
    const blockEnd = position + length;
    position = blockEnd;
    if (end <= blockStart || start >= blockEnd) {
      retained.push(block);
      continue;
    }
    if (block.type !== "text") continue;

    const localStart = Math.max(0, start - blockStart);
    const localEnd = Math.min(block.text.length, end - blockStart);
    const source = block.segments?.length ? block.segments : [{ text: block.text }];
    const [before] = splitSegments(source, localStart);
    const [, after] = splitSegments(source, localEnd);
    const segments = mergeSegments([...before, ...after]);
    retained.push({
      ...block,
      text: block.text.slice(0, localStart) + block.text.slice(localEnd),
      segments: segments.some(hasSegmentFormatting) ? segments : undefined,
    });
  }

  const merged: InlineBlock[] = [];
  for (const block of retained) {
    const previous = merged[merged.length - 1];
    if (block.type !== "text" || previous?.type !== "text" || block.alignment !== previous.alignment) {
      merged.push(block);
      continue;
    }
    const segments = mergeSegments([
      ...(previous.segments || [{ text: previous.text }]),
      ...(block.segments || [{ text: block.text }]),
    ]);
    merged[merged.length - 1] = {
      ...previous,
      text: previous.text + block.text,
      segments: segments.some(hasSegmentFormatting) ? segments : undefined,
    };
  }
  return merged.length ? merged : [{ id: "text-1", type: "text", text: "" } satisfies TextBlock];
}

function renderTextBlock(block: TextBlock) {
  if (!block.segments?.length) return block.text;
  return block.segments.map((segment, index) => {
    let content = <>{segment.text}</>;
    if (segment.underline) content = <u>{content}</u>;
    if (segment.italic) content = <em>{content}</em>;
    if (segment.bold) content = <strong>{content}</strong>;
    return <span key={`${block.id}-segment-${index}`}>{content}</span>;
  });
}

function caretOffset(element: HTMLElement) {
  const selection = window.getSelection();
  if (!selection?.rangeCount || !selection.anchorNode || !element.contains(selection.anchorNode)) return element.innerText.length;
  const range = document.createRange();
  range.selectNodeContents(element);
  range.setEnd(selection.anchorNode, selection.anchorOffset);
  return range.toString().length;
}

function selectionOffsets(element: HTMLElement) {
  const selection = window.getSelection();
  if (!selection?.rangeCount) {
    const offset = element.innerText.length;
    return { start: offset, end: offset };
  }
  const selectedRange = selection.getRangeAt(0);
  if (!element.contains(selectedRange.startContainer) || !element.contains(selectedRange.endContainer)) {
    const offset = caretOffset(element);
    return { start: offset, end: offset };
  }
  const offsetAt = (node: Node, offset: number) => {
    const range = document.createRange();
    range.selectNodeContents(element);
    range.setEnd(node, offset);
    return range.toString().length;
  };
  return {
    start: offsetAt(selectedRange.startContainer, selectedRange.startOffset),
    end: offsetAt(selectedRange.endContainer, selectedRange.endOffset),
  };
}

function selectionHasOnlyWhitespaceToBoundary(element: HTMLElement, direction: -1 | 1) {
  const selection = window.getSelection();
  if (!selection?.rangeCount) return false;
  const selectedRange = selection.getRangeAt(0);
  if (!selectedRange.collapsed || !element.contains(selectedRange.startContainer)) return false;
  const boundaryRange = document.createRange();
  boundaryRange.selectNodeContents(element);
  if (direction < 0) boundaryRange.setEnd(selectedRange.startContainer, selectedRange.startOffset);
  else boundaryRange.setStart(selectedRange.endContainer, selectedRange.endOffset);
  return boundaryRange.toString().trim().length === 0;
}

function placeSelectionAtOffsets(element: HTMLElement, requestedStart: number, requestedEnd = requestedStart) {
  element.focus();
  const selection = window.getSelection();
  const range = document.createRange();
  const positionAt = (requestedOffset: number) => {
    const walker = document.createTreeWalker(element, NodeFilter.SHOW_TEXT);
    let remaining = Math.max(0, requestedOffset);
    let node = walker.nextNode();
    while (node) {
      const length = node.textContent?.length || 0;
      if (remaining <= length) return { node, offset: remaining };
      remaining -= length;
      node = walker.nextNode();
    }
    return { node: element as Node, offset: element.childNodes.length };
  };
  const start = positionAt(Math.min(requestedStart, requestedEnd));
  const end = positionAt(Math.max(requestedStart, requestedEnd));
  range.setStart(start.node, start.offset);
  range.setEnd(end.node, end.offset);
  selection?.removeAllRanges();
  selection?.addRange(range);
}

function captureNativeSelection(element: HTMLElement) {
  const selection = window.getSelection();
  if (!selection?.anchorNode || !selection.focusNode || !element.contains(selection.anchorNode) || !element.contains(selection.focusNode)) return null;
  return {
    anchorNode: selection.anchorNode,
    anchorOffset: selection.anchorOffset,
    focusNode: selection.focusNode,
    focusOffset: selection.focusOffset,
  } satisfies NativeSelectionSnapshot;
}

function restoreNativeSelection(snapshot: NativeSelectionSnapshot) {
  if (!snapshot.anchorNode.isConnected || !snapshot.focusNode.isConnected) return false;
  const selection = window.getSelection();
  if (!selection) return false;
  selection.setBaseAndExtent(snapshot.anchorNode, snapshot.anchorOffset, snapshot.focusNode, snapshot.focusOffset);
  return true;
}

function formatTextBlock(block: TextBlock, start: number, end: number, format: TextFormat) {
  const selectionStart = Math.max(0, Math.min(start, end));
  const selectionEnd = Math.min(block.text.length, Math.max(start, end));
  if (selectionStart === selectionEnd) return block;
  const source = block.segments?.length ? block.segments : [{ text: block.text }];
  let position = 0;
  const selected = source.filter((segment) => {
    const segmentStart = position;
    position += segment.text.length;
    return position > selectionStart && segmentStart < selectionEnd;
  });
  const removeFormat = selected.length > 0 && selected.every((segment) => Boolean(segment[format]));
  const next: QuestionTextSegment[] = [];
  position = 0;
  for (const segment of source) {
    const segmentStart = position;
    const segmentEnd = position + segment.text.length;
    const overlapStart = Math.max(selectionStart, segmentStart);
    const overlapEnd = Math.min(selectionEnd, segmentEnd);
    if (overlapStart >= overlapEnd) next.push({ ...segment });
    else {
      if (overlapStart > segmentStart) next.push({ ...segment, text: segment.text.slice(0, overlapStart - segmentStart) });
      next.push({ ...segment, text: segment.text.slice(overlapStart - segmentStart, overlapEnd - segmentStart), [format]: removeFormat ? undefined : true });
      if (overlapEnd < segmentEnd) next.push({ ...segment, text: segment.text.slice(overlapEnd - segmentStart) });
    }
    position = segmentEnd;
  }
  const segments = mergeSegments(next);
  return { ...block, segments: segments.some((segment) => segment.bold || segment.italic || segment.underline) ? segments : undefined };
}

function replaceTextBlockRange(block: TextBlock, requestedStart: number, requestedEnd: number, value: string) {
  const start = Math.max(0, Math.min(requestedStart, requestedEnd));
  const end = Math.min(block.text.length, Math.max(requestedStart, requestedEnd));
  const source = block.segments?.length ? block.segments : [{ text: block.text }];
  const [before] = splitSegments(source, start);
  const [, after] = splitSegments(source, end);
  let position = 0;
  const inherited = source.find((segment) => {
    const segmentStart = position;
    position += segment.text.length;
    return start >= segmentStart && start <= position;
  });
  const inserted: QuestionTextSegment = {
    text: value,
    bold: inherited?.bold,
    italic: inherited?.italic,
    underline: inherited?.underline,
  };
  const segments = mergeSegments([...before, inserted, ...after]);
  return {
    ...block,
    text: block.text.slice(0, start) + value + block.text.slice(end),
    segments: segments.some(hasSegmentFormatting) ? segments : undefined,
  };
}

function textFormatsAt(block: TextBlock, start: number, end: number) {
  const formats: TextFormat[] = ["bold", "italic", "underline"];
  const source = block.segments?.length ? block.segments : [{ text: block.text }];
  let position = 0;
  if (start === end) {
    const segment = source.find((item) => {
      const segmentStart = position;
      position += item.text.length;
      return start > segmentStart && start < position;
    });
    return segment ? formats.filter((format) => Boolean(segment[format])) : [];
  }
  const selectionStart = Math.min(start, end);
  const selectionEnd = Math.max(start, end);
  const selected = source.filter((item) => {
    const segmentStart = position;
    position += item.text.length;
    return position > selectionStart && segmentStart < selectionEnd;
  });
  return formats.filter((format) => selected.length > 0 && selected.every((segment) => Boolean(segment[format])));
}

export function InlineMathEditor({ blocks, onChange, onActivateFormulaInsertion, onActivateTextFormatting, onActivateTextAlignment, onDeactivate, disabled = false, defaultAlignment = "left", label }: Props) {
  const blocksRef = useRef(blocks);
  const editorRef = useRef<HTMLDivElement>(null);
  const caretRestoreRef = useRef<{ id: string; start: number; end: number } | null>(null);
  const compositeRestoreRef = useRef<{ start: number; end: number } | null>(null);
  const nativeSelectionRestoreRef = useRef<NativeSelectionSnapshot | null>(null);
  const selectionSyncFrameRef = useRef<number | null>(null);
  const selectionSignatureRef = useRef("");
  const pointerGestureRef = useRef<{ x: number; y: number; moved: boolean } | null>(null);
  const clickSyncTimerRef = useRef<number | null>(null);
  const clickSequenceRef = useRef<{ x: number; y: number; at: number; count: number } | null>(null);
  const [selectedFormulaId, setSelectedFormulaId] = useState<string | null>(null);
  useEffect(() => {
    blocksRef.current = blocks;
  }, [blocks]);
  useLayoutEffect(() => {
    const nativeSelection = nativeSelectionRestoreRef.current;
    if (nativeSelection) restoreNativeSelection(nativeSelection);
    const compositeRequest = compositeRestoreRef.current;
    if (compositeRequest && editorRef.current) {
      placeCompositeSelection(editorRef.current, compositeRequest.start, compositeRequest.end);
      compositeRestoreRef.current = null;
      caretRestoreRef.current = null;
      return;
    }
    const request = caretRestoreRef.current;
    if (!request || !editorRef.current) return;
    const textPart = editorRef.current.dataset.blockId === request.id
      ? editorRef.current
      : Array.from(editorRef.current.querySelectorAll<HTMLElement>(".inline-text-part")).find((element) => element.dataset.blockId === request.id);
    if (textPart) placeSelectionAtOffsets(textPart, request.start, request.end);
    caretRestoreRef.current = null;
  });
  const selectedFormula = useMemo<MathBlock | undefined>(
    () => blocks.find((block) => block.id === selectedFormulaId && block.type !== "text") as MathBlock | undefined,
    [blocks, selectedFormulaId],
  );
  const contentKey = useMemo(() => editorContentKey(blocks), [blocks]);
  const hasEditorContent = blocks.some((block) => block.type !== "text" || block.text.length > 0);
  const blockAlignment = blocks.find((block): block is TextBlock => block.type === "text")?.alignment || defaultAlignment;

  function replace(block: InlineBlock) {
    onChange(blocks.map((item) => item.id === block.id ? block : item));
  }

  function rememberCaret(element: HTMLElement, id: string) {
    const selection = selectionOffsets(element);
    const nativeSelection = captureNativeSelection(element);
    const caretRequest = { id, ...selection };
    caretRestoreRef.current = caretRequest;
    nativeSelectionRestoreRef.current = nativeSelection;
    onActivateFormulaInsertion?.(() => insertFormulaAt(id, selection.end));
    const block = blocksRef.current.find((item): item is TextBlock => item.id === id && item.type === "text");
    onActivateTextFormatting?.((format) => applyTextFormat(id, format, selection.start, selection.end), block ? textFormatsAt(block, selection.start, selection.end) : []);
    onActivateTextAlignment?.(applyBlockAlignment, block?.alignment || defaultAlignment);
    if (selectedFormulaId !== null) setSelectedFormulaId(null);
    requestAnimationFrame(() => {
      if (nativeSelectionRestoreRef.current !== nativeSelection) return;
      if (nativeSelection) restoreNativeSelection(nativeSelection);
      nativeSelectionRestoreRef.current = null;
      if (caretRestoreRef.current === caretRequest) caretRestoreRef.current = null;
    });
  }

  function rememberCompositeCaret(element: HTMLElement) {
    const selection = window.getSelection();
    if (!selection?.focusNode || !selection.rangeCount) return;
    const nativeSelection = captureNativeSelection(element);
    const compositeRequest = compositeSelectionOffsets(element);
    compositeRestoreRef.current = compositeRequest;
    nativeSelectionRestoreRef.current = nativeSelection;
    requestAnimationFrame(() => {
      if (nativeSelectionRestoreRef.current !== nativeSelection) return;
      if (nativeSelection) restoreNativeSelection(nativeSelection);
      nativeSelectionRestoreRef.current = null;
      if (compositeRestoreRef.current === compositeRequest) compositeRestoreRef.current = null;
    });
    const focusElement = selection.focusNode.nodeType === Node.ELEMENT_NODE ? selection.focusNode as Element : selection.focusNode.parentElement;
    const textPart = focusElement?.closest<HTMLElement>(".inline-text-part[data-block-id]");
    if (!textPart || !element.contains(textPart)) return;
    const id = textPart.dataset.blockId || "";
    const block = blocksRef.current.find((item): item is TextBlock => item.id === id && item.type === "text");
    const selectedRange = selection.getRangeAt(0);
    const selectionWithinTextPart = textPart.contains(selectedRange.startContainer) && textPart.contains(selectedRange.endContainer);
    const localSelection = selectionWithinTextPart ? selectionOffsets(textPart) : { start: 0, end: 0 };
    const focusRange = document.createRange();
    focusRange.selectNodeContents(textPart);
    focusRange.setEnd(selection.focusNode, selection.focusOffset);
    const focusOffset = focusRange.toString().length;
    onActivateFormulaInsertion?.(() => insertFormulaAt(id, focusOffset));
    onActivateTextFormatting?.(
      (format) => { if (selectionWithinTextPart) applyTextFormat(id, format, localSelection.start, localSelection.end); },
      block && selectionWithinTextPart ? textFormatsAt(block, localSelection.start, localSelection.end) : [],
    );
    onActivateTextAlignment?.(applyBlockAlignment, block?.alignment || defaultAlignment);
    if (selectedFormulaId !== null) setSelectedFormulaId(null);
  }

  function editCompositeText(element: HTMLElement) {
    const selection = compositeSelectionOffsets(element);
    compositeRestoreRef.current = selection;
    const next = compositeBlocksFromElement(element, blocksRef.current);
    blocksRef.current = next;
    onChange(next);
  }

  function deleteCompositeSelection(element: HTMLElement, inputType: unknown) {
    if (typeof inputType !== "string" || !inputType.startsWith("delete")) return false;
    const selection = compositeSelectionOffsets(element);
    let { start, end } = selection;
    if (start === end) {
      if (inputType === "deleteByCut" || inputType === "deleteByDrag") return false;
      const totalLength = blocksRef.current.reduce((length, block) => length + (block.type === "text" ? block.text.length : 1), 0);
      if (inputType.toLowerCase().includes("backward")) start = Math.max(0, start - 1);
      else end = Math.min(totalLength, end + 1);
    }
    if (start === end) return false;
    const next = deleteCompositeRange(blocksRef.current, start, end);
    compositeRestoreRef.current = { start, end: start };
    blocksRef.current = next;
    onChange(next);
    setSelectedFormulaId(null);
    return true;
  }

  function scheduleCompositeCaret(start: number, end = start) {
    compositeRestoreRef.current = { start, end };
    window.setTimeout(() => {
      requestAnimationFrame(() => {
        const editor = editorRef.current;
        if (!editor?.isConnected) return;
        placeCompositeSelection(editor, start, end);
        compositeRestoreRef.current = null;
        caretRestoreRef.current = null;
        selectionSignatureRef.current = "";
      });
    }, 0);
  }

  function deleteCompositeContent(event: FormEvent<HTMLElement>) {
    const nativeEvent = event.nativeEvent as InputEvent;
    if (deleteCompositeSelection(event.currentTarget, nativeEvent.inputType)) event.preventDefault();
  }

  function deleteFormulaElement(id: string) {
    const current = blocksRef.current;
    const index = current.findIndex((block) => block.id === id);
    if (index < 0) return false;
    const start = current.slice(0, index).reduce((length, block) => length + (block.type === "text" ? block.text.length : 1), 0);
    const next = deleteCompositeRange(current, start, start + 1);
    scheduleCompositeCaret(start);
    blocksRef.current = next;
    onChange(next);
    setSelectedFormulaId(null);
    return true;
  }

  function placeCaretFromPoint(editor: HTMLElement, clientX: number, clientY: number, remember = true) {
    const caretDocument = document as Document & {
      caretPositionFromPoint?: (x: number, y: number) => { offsetNode: Node; offset: number } | null;
      caretRangeFromPoint?: (x: number, y: number) => Range | null;
    };
    const position = caretDocument.caretPositionFromPoint?.(clientX, clientY);
    const pointRange = position ? document.createRange() : caretDocument.caretRangeFromPoint?.(clientX, clientY);
    if (position && pointRange) pointRange.setStart(position.offsetNode, position.offset);
    pointRange?.collapse(true);
    const pointNode = position?.offsetNode || pointRange?.startContainer;
    const pointElement = pointNode?.nodeType === Node.ELEMENT_NODE ? pointNode as Element : pointNode?.parentElement;
    const textPart = pointElement?.closest<HTMLElement>(".inline-text-part");
    if (pointRange && textPart && editor.contains(textPart)) {
      const selection = window.getSelection();
      selection?.removeAllRanges();
      selection?.addRange(pointRange);
      textPart.focus();
      if (remember) rememberCaret(textPart, textPart.dataset.blockId || "");
      return;
    }

    const candidates = Array.from(editor.querySelectorAll<HTMLElement>(".inline-text-part"));
    let closest: { element: HTMLElement; rect: DOMRect; distance: number } | null = null;
    for (const element of candidates) {
      for (const rect of Array.from(element.getClientRects())) {
        const dx = clientX < rect.left ? rect.left - clientX : clientX > rect.right ? clientX - rect.right : 0;
        const dy = clientY < rect.top ? rect.top - clientY : clientY > rect.bottom ? clientY - rect.bottom : 0;
        const distance = dx * dx + dy * dy;
        if (!closest || distance < closest.distance) closest = { element, rect, distance };
      }
    }
    if (!closest) return;
    const useStart = clientY < closest.rect.top || (clientY <= closest.rect.bottom && clientX <= (closest.rect.left + closest.rect.right) / 2);
    placeSelectionAtOffsets(closest.element, useStart ? 0 : closest.element.innerText.length);
    if (remember) rememberCaret(closest.element, closest.element.dataset.blockId || "");
  }

  function selectTextFromPoint(editor: HTMLElement, clientX: number, clientY: number, mode: "word" | "line") {
    const caretDocument = document as Document & {
      caretPositionFromPoint?: (x: number, y: number) => { offsetNode: Node; offset: number } | null;
      caretRangeFromPoint?: (x: number, y: number) => Range | null;
    };
    const position = caretDocument.caretPositionFromPoint?.(clientX, clientY);
    const pointRange = position ? document.createRange() : caretDocument.caretRangeFromPoint?.(clientX, clientY);
    if (position && pointRange) pointRange.setStart(position.offsetNode, position.offset);
    const pointNode = position?.offsetNode || pointRange?.startContainer;
    const pointElement = pointNode?.nodeType === Node.ELEMENT_NODE ? pointNode as Element : pointNode?.parentElement;
    const textPart = pointElement?.closest<HTMLElement>(".inline-text-part");
    if (!pointRange || !pointNode || !textPart || !editor.contains(textPart)) return;
    if (mode === "line") {
      const localOffset = (() => {
        const range = document.createRange();
        range.selectNodeContents(textPart);
        range.setEnd(pointNode, position?.offset ?? pointRange.startOffset);
        return range.toString().length;
      })();
      const text = textPart.innerText.replace(/\r/g, "");
      const start = text.lastIndexOf("\n", Math.max(0, localOffset - 1)) + 1;
      const nextBreak = text.indexOf("\n", localOffset);
      placeSelectionAtOffsets(textPart, start, nextBreak < 0 ? text.length : nextBreak);
      return;
    }
    if (pointNode.nodeType !== Node.TEXT_NODE) return;
    const text = pointNode.textContent || "";
    if (!text) return;
    let start = Math.min(position?.offset ?? pointRange.startOffset, text.length - 1);
    let end = start;
    const isWord = (character: string) => /[\p{L}\p{N}_]/u.test(character);
    const targetIsWord = isWord(text[start]);
    while (start > 0 && isWord(text[start - 1]) === targetIsWord && !/\s/u.test(text[start - 1])) start--;
    while (end < text.length && isWord(text[end]) === targetIsWord && !/\s/u.test(text[end])) end++;
    const range = document.createRange();
    range.setStart(pointNode, start);
    range.setEnd(pointNode, Math.max(start + 1, end));
    const selection = window.getSelection();
    selection?.removeAllRanges();
    selection?.addRange(range);
    textPart.focus();
  }

  function editText(event: FormEvent<HTMLElement>, block: TextBlock) {
    const segments = segmentsFromElement(event.currentTarget);
    const text = segments.map((segment) => segment.text).join("").replace(/\r/g, "");
    const selection = selectionOffsets(event.currentTarget);
    caretRestoreRef.current = { id: block.id, ...selection };
    const nextBlock = { ...block, text, segments: segments.some((segment) => segment.bold || segment.italic || segment.underline) ? segments : undefined };
    replace(nextBlock);
    onActivateFormulaInsertion?.(() => insertFormulaAt(block.id, selection.end));
    onActivateTextFormatting?.((format) => applyTextFormat(block.id, format, selection.start, selection.end), textFormatsAt(nextBlock, selection.start, selection.end));
  }

  function insertLineBreakAtSelection(element: HTMLElement) {
    const selection = window.getSelection();
    if (!selection?.rangeCount || !selection.anchorNode || !selection.focusNode) return false;
    const singleBlock = blocksRef.current.length === 1 && blocksRef.current[0].type === "text" ? blocksRef.current[0] : null;
    const focusElement = selection.focusNode.nodeType === Node.ELEMENT_NODE ? selection.focusNode as Element : selection.focusNode.parentElement;
    const textPart = singleBlock ? element : focusElement?.closest<HTMLElement>(".inline-text-part[data-block-id]");
    if (!textPart || !element.contains(textPart)) return false;
    const selectedRange = selection.getRangeAt(0);
    if (!textPart.contains(selectedRange.startContainer) || !textPart.contains(selectedRange.endContainer)) return false;
    const id = singleBlock?.id || textPart.dataset.blockId || "";
    const block = blocksRef.current.find((item): item is TextBlock => item.id === id && item.type === "text");
    if (!block) return false;
    const offsets = selectionOffsets(textPart);
    const nextBlock = replaceTextBlockRange(block, offsets.start, offsets.end, "\n");
    const caret = Math.min(offsets.start, offsets.end) + 1;
    const next = blocksRef.current.map((item) => item.id === id ? nextBlock : item);
    blocksRef.current = next;
    caretRestoreRef.current = { id, start: caret, end: caret };
    selectionSignatureRef.current = "";
    onChange(next);
    onActivateFormulaInsertion?.(() => insertFormulaAt(id, caret));
    onActivateTextFormatting?.((format) => applyTextFormat(id, format, caret, caret), textFormatsAt(nextBlock, caret, caret));
    onActivateTextAlignment?.(applyBlockAlignment, nextBlock.alignment || defaultAlignment);
    setSelectedFormulaId(null);
    return true;
  }

  function applyTextFormat(blockId: string, format: TextFormat, start: number, end: number) {
    if (disabled || start === end) return;
    const current = blocksRef.current;
    caretRestoreRef.current = { id: blockId, start, end };
    onChange(current.map((block) => block.id === blockId && block.type === "text" ? formatTextBlock(block, start, end, format) : block));
  }

  function applyBlockAlignment(alignment: TextAlignment) {
    if (disabled) return;
    const next = blocksRef.current.map((block) => block.type === "text" ? { ...block, alignment } : block);
    blocksRef.current = next;
    onChange(next);
    onActivateTextAlignment?.(applyBlockAlignment, alignment);
  }

  function chooseFormula(event: ReactMouseEvent, id: string) {
    event.preventDefault();
    caretRestoreRef.current = null;
    setSelectedFormulaId(id);
  }

  function insertFormulaAt(textId: string, requestedOffset: number) {
    if (disabled) return;
    caretRestoreRef.current = null;
    const currentBlocks = blocksRef.current;
    const fallbackIndex = currentBlocks.findLastIndex((block) => block.type === "text");
    const textIndex = currentBlocks.findIndex((block) => block.id === textId && block.type === "text");
    const insertionIndex = textIndex >= 0 ? textIndex : fallbackIndex;
    const id = nextBlockId("formula", currentBlocks);
    const formula: InlineBlock = { id, type: "formula", latex: "", display: "inline" };
    if (insertionIndex < 0) {
      onChange([...currentBlocks, formula, { id: nextBlockId("text", [...currentBlocks, formula]), type: "text", text: "" }]);
    } else {
      const textBlock = currentBlocks[insertionIndex] as Extract<InlineBlock, { type: "text" }>;
      const offset = Math.max(0, Math.min(textBlock.id === textId ? requestedOffset : textBlock.text.length, textBlock.text.length));
      const [beforeSegments, afterSegments] = textBlock.segments?.length ? splitSegments(textBlock.segments, offset) : [undefined, undefined];
      const next = [...currentBlocks];
      next.splice(
        insertionIndex,
        1,
        { ...textBlock, text: textBlock.text.slice(0, offset), segments: beforeSegments },
        formula,
        { id: nextBlockId("text-after", [...currentBlocks, formula]), type: "text", text: textBlock.text.slice(offset), segments: afterSegments },
      );
      onChange(next);
    }
    setSelectedFormulaId(id);
  }

  function removeFormulaById(id: string) {
    const next = blocks.filter((block) => block.id !== id);
    onChange(next.length ? next : [{ id: "text-1", type: "text", text: "" }]);
    if (selectedFormulaId === id) setSelectedFormulaId(null);
  }

  function moveCaretAcrossBlocks(blockId: string, direction: -1 | 1) {
    const current = blocksRef.current;
    const currentIndex = current.findIndex((block) => block.id === blockId);
    for (let index = currentIndex + direction; index >= 0 && index < current.length; index += direction) {
      const candidate = current[index];
      if (candidate.type !== "text") continue;
      const element = editorRef.current?.querySelector<HTMLElement>(`.inline-text-part[data-block-id="${CSS.escape(candidate.id)}"]`);
      if (!element) return false;
      const offset = direction < 0
        ? candidate.text.trimEnd().length
        : candidate.text.length - candidate.text.trimStart().length;
      placeSelectionAtOffsets(element, offset);
      rememberCaret(element, candidate.id);
      setSelectedFormulaId(null);
      return true;
    }
    return false;
  }

  function handleTextKeyDown(event: ReactKeyboardEvent<HTMLElement>, block: TextBlock) {
    if (event.key === "ArrowLeft" || event.key === "ArrowRight") {
      const selection = selectionOffsets(event.currentTarget);
      const direction = event.key === "ArrowLeft" ? -1 : 1;
      const isBoundary = selectionHasOnlyWhitespaceToBoundary(event.currentTarget, direction);
      if (selection.start === selection.end && isBoundary && moveCaretAcrossBlocks(block.id, direction)) event.preventDefault();
      return;
    }
    if (event.key === "ArrowUp" || event.key === "ArrowDown") {
      const selection = selectionOffsets(event.currentTarget);
      const direction = event.key === "ArrowUp" ? -1 : 1;
      const shouldCrossBlock = !block.text.includes("\n") || selectionHasOnlyWhitespaceToBoundary(event.currentTarget, direction);
      if (selection.start === selection.end && shouldCrossBlock && moveCaretAcrossBlocks(block.id, direction)) event.preventDefault();
      return;
    }
    if (event.key !== "Backspace" && event.key !== "Delete") return;
    const offset = caretOffset(event.currentTarget);
    const index = blocks.findIndex((item) => item.id === block.id);
    const adjacent = event.key === "Backspace" && offset === 0
      ? blocks[index - 1]
      : event.key === "Delete" && offset === block.text.length
        ? blocks[index + 1]
        : undefined;
    if (adjacent?.type !== "formula" && adjacent?.type !== "script") return;
    event.preventDefault();
    caretRestoreRef.current = { id: block.id, start: offset, end: offset };
    removeFormulaById(adjacent.id);
    onActivateFormulaInsertion?.(() => insertFormulaAt(block.id, offset));
  }

  function updateFormula(latex: string) {
    if (!selectedFormula) return;
    replace({ id: selectedFormula.id, type: "formula", latex, display: selectedFormula.type === "formula" ? selectedFormula.display : "inline" });
  }

  function removeFormula() {
    if (!selectedFormula) return;
    const index = blocks.findIndex((block) => block.id === selectedFormula.id);
    const caret = blocks.slice(0, index).reduce((length, block) => length + (block.type === "text" ? block.text.length : 1), 0);
    const next = blocks.filter((block) => block.id !== selectedFormula.id);
    const before = next[index - 1];
    const after = next[index];
    if (before?.type === "text" && after?.type === "text") {
      const segments = before.segments?.length || after.segments?.length
        ? mergeSegments([...(before.segments || [{ text: before.text }]), ...(after.segments || [{ text: after.text }])])
        : undefined;
      next.splice(index - 1, 2, { ...before, text: before.text + after.text, segments });
    }
    const normalized = next.length ? next : [{ id: "text-1", type: "text", text: "" } satisfies TextBlock];
    blocksRef.current = normalized;
    scheduleCompositeCaret(caret);
    onChange(normalized);
    setSelectedFormulaId(null);
  }

  useEffect(() => {
    const syncSelection = () => {
      if (selectionSyncFrameRef.current !== null) cancelAnimationFrame(selectionSyncFrameRef.current);
      selectionSyncFrameRef.current = requestAnimationFrame(() => {
        selectionSyncFrameRef.current = null;
        if (pointerGestureRef.current || clickSyncTimerRef.current !== null) return;
        const editor = editorRef.current;
        const selection = window.getSelection();
        if (!editor || !selection?.anchorNode || !selection.focusNode
          || !editor.contains(selection.anchorNode) || !editor.contains(selection.focusNode)) return;
        const focusElement = selection.focusNode.nodeType === Node.ELEMENT_NODE
          ? selection.focusNode as Element
          : selection.focusNode.parentElement;
        if (focusElement?.closest("[data-inline-math-id]")) return;
        const current = blocksRef.current;
        const singleBlock = current.length === 1 && current[0].type === "text" ? current[0] : null;
        if (singleBlock) {
          const offsets = selectionOffsets(editor);
          const signature = `${singleBlock.id}:${offsets.start}:${offsets.end}`;
          if (selectionSignatureRef.current === signature) return;
          selectionSignatureRef.current = signature;
          rememberCaret(editor, singleBlock.id);
          return;
        }
        const offsets = compositeSelectionOffsets(editor);
        const signature = `composite:${offsets.start}:${offsets.end}`;
        if (selectionSignatureRef.current === signature) return;
        selectionSignatureRef.current = signature;
        rememberCompositeCaret(editor);
      });
    };
    document.addEventListener("selectionchange", syncSelection);
    return () => {
      document.removeEventListener("selectionchange", syncSelection);
      if (selectionSyncFrameRef.current !== null) cancelAnimationFrame(selectionSyncFrameRef.current);
      if (clickSyncTimerRef.current !== null) window.clearTimeout(clickSyncTimerRef.current);
      selectionSyncFrameRef.current = null;
      clickSyncTimerRef.current = null;
    };
  });

  return (
    <section className="inline-editor-wrap" onBlur={(event) => {
      if (!event.currentTarget.contains(event.relatedTarget as Node | null)) {
        selectionSignatureRef.current = "";
        onDeactivate?.();
      }
    }}>
      <div className="inline-editor-toolbar">
        <span>{label}</span>
      </div>
      <div
        key={contentKey}
        ref={editorRef}
        className={`inline-math-editor${disabled ? " disabled" : ""}${blocks.length === 1 && blocks[0].type === "text" ? " inline-text-part single-text-editor" : ""}`}
        aria-label={label}
        aria-multiline="true"
        role="textbox"
        contentEditable={!disabled}
        style={{ textAlign: blockAlignment }}
        data-block-id={blocks.length === 1 && blocks[0].type === "text" ? blocks[0].id : undefined}
        data-placeholder={!hasEditorContent ? "Digite o texto aqui…" : undefined}
        suppressContentEditableWarning
        onMouseDown={(event) => {
          if (event.button !== 0) return;
          if (clickSyncTimerRef.current !== null) {
            window.clearTimeout(clickSyncTimerRef.current);
            clickSyncTimerRef.current = null;
          }
          const now = event.timeStamp;
          const previousClick = clickSequenceRef.current;
          const repeated = previousClick && now - previousClick.at <= 500
            && Math.abs(event.clientX - previousClick.x) <= 5 && Math.abs(event.clientY - previousClick.y) <= 5;
          const clickCount = repeated ? previousClick.count + 1 : 1;
          clickSequenceRef.current = { x: event.clientX, y: event.clientY, at: now, count: clickCount };
          pointerGestureRef.current = { x: event.clientX, y: event.clientY, moved: false };
          const target = event.target instanceof HTMLElement ? event.target : null;
          if (clickCount === 1 && !target?.closest("[data-inline-math-id]")) {
            placeCaretFromPoint(event.currentTarget, event.clientX, event.clientY, false);
          } else if ((clickCount === 2 || clickCount === 3) && !target?.closest("[data-inline-math-id]")) {
            const editor = event.currentTarget;
            const mode = clickCount === 2 ? "word" : "line";
            window.setTimeout(() => selectTextFromPoint(editor, event.clientX, event.clientY, mode), 0);
          }
        }}
        onMouseMove={(event) => {
          const gesture = pointerGestureRef.current;
          if (!gesture || (event.buttons & 1) === 0) return;
          if (Math.abs(event.clientX - gesture.x) > 3 || Math.abs(event.clientY - gesture.y) > 3) gesture.moved = true;
        }}
        onMouseUp={(event) => {
          const gesture = pointerGestureRef.current;
          if (!gesture?.moved) return;
          const editor = event.currentTarget;
          const current = blocksRef.current;
          const singleBlock = current.length === 1 && current[0].type === "text" ? current[0] : null;
          window.setTimeout(() => {
            if (!editor.isConnected) return;
            if (singleBlock) rememberCaret(editor, singleBlock.id);
            else rememberCompositeCaret(editor);
          }, 0);
        }}
        onKeyDownCapture={(event) => {
          if (event.key === "Enter") {
            if (insertLineBreakAtSelection(event.currentTarget)) {
              event.preventDefault();
              event.stopPropagation();
            }
            return;
          }
          if (blocks.length === 1 && blocks[0].type === "text") return;
          if (event.key !== "Backspace" && event.key !== "Delete") return;
          const target = event.target instanceof HTMLElement ? event.target : null;
          const formula = target?.closest<HTMLElement>("[data-inline-math-id]");
          const handled = formula && event.currentTarget.contains(formula)
            ? deleteFormulaElement(formula.dataset.inlineMathId || "")
            : deleteCompositeSelection(event.currentTarget, event.key === "Backspace" ? "deleteContentBackward" : "deleteContentForward");
          if (handled) {
            event.preventDefault();
            event.stopPropagation();
          }
        }}
        onBeforeInput={(event) => {
          if (blocks.length > 1 || blocks[0]?.type !== "text") deleteCompositeContent(event);
        }}
        onInput={(event) => {
          const block = blocks.length === 1 && blocks[0].type === "text" ? blocks[0] : null;
          if (block) editText(event, block);
          else editCompositeText(event.currentTarget);
        }}
        onKeyDown={(event) => {
          const block = blocks.length === 1 && blocks[0].type === "text" ? blocks[0] : null;
          if (block) handleTextKeyDown(event, block);
        }}
        onClick={(event) => {
          if (disabled) return;
          const gesture = pointerGestureRef.current;
          pointerGestureRef.current = null;
          if (gesture?.moved) return;
          const target = event.target instanceof HTMLElement ? event.target : null;
          if (target?.closest("[data-inline-math-id]")) return;
          const editor = event.currentTarget;
          clickSyncTimerRef.current = window.setTimeout(() => {
            clickSyncTimerRef.current = null;
            const selection = window.getSelection();
            if (!editor.isConnected || !selection?.anchorNode || !selection.focusNode
              || !editor.contains(selection.anchorNode) || !editor.contains(selection.focusNode)) return;
            const current = blocksRef.current;
            const singleBlock = current.length === 1 && current[0].type === "text" ? current[0] : null;
            if (singleBlock) rememberCaret(editor, singleBlock.id);
            else rememberCompositeCaret(editor);
          }, 320);
        }}>
        {blocks.length === 1 && blocks[0].type === "text" ? renderTextBlock(blocks[0]) : blocks.map((block, blockIndex) => block.type === "text" ? (
          <span
            className="inline-text-part"
            key={block.id}
            data-block-id={block.id}
            data-caret-slot={block.text.length === 0 ? "true" : undefined}
            data-placeholder={!hasEditorContent && blockIndex === 0 ? "Digite o texto aqui…" : undefined}
          >{renderTextBlock(block)}</span>
        ) : (
          <span
            role="button"
            tabIndex={disabled ? -1 : 0}
            contentEditable={false}
            data-inline-math-id={block.id}
            className={`inline-formula-chip${selectedFormulaId === block.id ? " selected" : ""}`}
            aria-disabled={disabled}
            key={block.id}
            onClick={(event) => { if (!disabled) chooseFormula(event, block.id); }}
            onKeyDown={(event) => {
              if (event.key === "ArrowLeft" || event.key === "ArrowRight" || event.key === "ArrowUp" || event.key === "ArrowDown") {
                event.preventDefault();
                moveCaretAcrossBlocks(block.id, event.key === "ArrowLeft" || event.key === "ArrowUp" ? -1 : 1);
                return;
              }
              if (event.key === "Backspace" || event.key === "Delete") {
                event.preventDefault();
                deleteFormulaElement(block.id);
              }
            }}
            aria-label="Editar fórmula matemática"
          >
            <InlineMath latex={inlineLatex(block)} />
          </span>
        ))}
      </div>
      {selectedFormula && !disabled && (
        <div className="inline-formula-popover">
          <div><strong>Editar fórmula</strong><span>Use o teclado matemático para potência, índice, raiz ou fração.</span></div>
          <FormulaEditor value={selectedFormula.type === "formula" ? selectedFormula.latex : scriptLatex(selectedFormula)} onChange={updateFormula} />
          <div className="inline-formula-actions">
            <button type="button" className="remove-inline-formula" onClick={removeFormula}>Excluir fórmula</button>
            <button type="button" className="finish-inline-formula" onClick={() => setSelectedFormulaId(null)}>Concluir</button>
          </div>
        </div>
      )}
    </section>
  );
}
