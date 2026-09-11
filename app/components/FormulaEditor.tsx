"use client";

import { useEffect, useRef } from "react";

type MathFieldNode = HTMLElement & { value: string; virtualKeyboardMode: string; readOnly: boolean };

export function FormulaEditor({ value, onChange, readOnly = false }: { value: string; onChange: (value: string) => void; readOnly?: boolean }) {
  const hostRef = useRef<HTMLDivElement>(null);
  const fieldRef = useRef<MathFieldNode | null>(null);
  const onChangeRef = useRef(onChange);
  const initialValueRef = useRef(value);
  const initialReadOnlyRef = useRef(readOnly);

  useEffect(() => {
    onChangeRef.current = onChange;
  }, [onChange]);

  useEffect(() => {
    let active = true;
    let field: MathFieldNode | null = null;
    const handleInput = () => field && onChangeRef.current(field.value);
    import("mathlive").then(() => {
      if (!active || !hostRef.current) return;
      field = document.createElement("math-field") as MathFieldNode;
      field.className = "mathlive-field";
      field.virtualKeyboardMode = "manual";
      field.readOnly = initialReadOnlyRef.current;
      field.value = initialValueRef.current;
      field.setAttribute("aria-label", "Editor visual de fórmula matemática");
      field.addEventListener("input", handleInput);
      hostRef.current.replaceChildren(field);
      fieldRef.current = field;
    });
    return () => {
      active = false;
      field?.removeEventListener("input", handleInput);
    };
  }, []);

  useEffect(() => {
    if (fieldRef.current && fieldRef.current.value !== value) fieldRef.current.value = value;
  }, [value]);

  useEffect(() => {
    if (fieldRef.current) fieldRef.current.readOnly = readOnly;
  }, [readOnly]);

  return <div ref={hostRef} className="formula-editor-host"><span>Carregando editor matemático…</span></div>;
}
