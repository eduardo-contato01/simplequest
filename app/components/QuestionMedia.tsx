"use client";

/* eslint-disable @next/next/no-img-element -- dimensões naturais evitam ampliar arquivos pequenos artificialmente */

import { type CSSProperties, useEffect, useState } from "react";
import type { ImageDisplayScale } from "../question-model";
import { createPortal } from "react-dom";

type ImageDimensions = { width: number; height: number };

export function QuestionMedia({ urls, dimensions = [], displayScale = 50, hiddenByDefault = false, questionNumber, print = false }: {
  urls: string[];
  dimensions?: ImageDimensions[];
  displayScale?: ImageDisplayScale;
  hiddenByDefault?: boolean;
  questionNumber: number;
  print?: boolean;
}) {
  const [activeIndex, setActiveIndex] = useState<number | null>(null);
  const [measured, setMeasured] = useState<Record<number, ImageDimensions>>({});
  const [revealed, setRevealed] = useState(!hiddenByDefault);
  const activeUrl = activeIndex === null ? null : urls[activeIndex];
  const scale = ([25, 50, 75, 100] as number[]).includes(displayScale) ? displayScale : 50;

  useEffect(() => {
    if (activeIndex === null) return;
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    const closeOnEscape = (event: KeyboardEvent) => {
      if (event.key === "Escape") setActiveIndex(null);
    };
    document.addEventListener("keydown", closeOnEscape);
    return () => {
      document.body.style.overflow = previousOverflow;
      document.removeEventListener("keydown", closeOnEscape);
    };
  }, [activeIndex]);

  const imageAlt = (index: number) => `Ilustração da questão ${questionNumber}${urls.length > 1 ? `, imagem ${index + 1}` : ""}`;
  const imageDimensions = (index: number) => measured[index] || dimensions[index];
  const rememberNaturalSize = (index: number, image: HTMLImageElement) => {
    if (!image.naturalWidth || !image.naturalHeight) return;
    setMeasured((current) => {
      const previous = current[index];
      if (previous?.width === image.naturalWidth && previous.height === image.naturalHeight) return current;
      return { ...current, [index]: { width: image.naturalWidth, height: image.naturalHeight } };
    });
  };

  if (print) {
    if (hiddenByDefault) return null;
    return <div className="question-section print-images">{urls.map((url, index) => {
      return <img style={{ maxWidth: `${scale}%` }} key={`${url}-${index}`} src={url} alt={imageAlt(index)} onLoad={(event) => rememberNaturalSize(index, event.currentTarget)} />;
    })}</div>;
  }

  if (!revealed) {
    return <div className="question-section question-image-collapsed"><button type="button" onClick={(event) => { event.stopPropagation(); setRevealed(true); }}><span className="question-image-magnifier-icon" aria-hidden="true" />Ver imagem anexada{urls.length > 1 ? ` (${urls.length})` : ""}</button></div>;
  }

  const modal = activeUrl && activeIndex !== null ? (
    <div className="question-image-modal" role="dialog" aria-modal="true" aria-label={`Visualização ampliada da ${imageAlt(activeIndex).toLowerCase()}`} onMouseDown={(event) => {
      event.stopPropagation();
      if (event.target === event.currentTarget) setActiveIndex(null);
    }} onClick={(event) => event.stopPropagation()}>
      <button type="button" className="question-image-modal-close" onClick={() => setActiveIndex(null)} aria-label="Fechar imagem ampliada"><span aria-hidden="true" /></button>
      <div className="question-image-modal-content">{(() => {
        const size = imageDimensions(activeIndex);
        const modalStyle = size ? { "--question-image-zoom-width": `${size.width * 2}px` } as CSSProperties : undefined;
        return <img style={modalStyle} src={activeUrl} alt={imageAlt(activeIndex)} onLoad={(event) => rememberNaturalSize(activeIndex, event.currentTarget)} />;
      })()}</div>
      <p>Ampliação limitada para preservar a nitidez</p>
    </div>
  ) : null;

  return <>
    {hiddenByDefault && <div className="question-image-disclosure"><button type="button" onClick={(event) => { event.stopPropagation(); setRevealed(false); }}>Ocultar imagem</button></div>}
    <div className="question-section question-media-grid">{urls.map((url, index) => {
      const open = () => setActiveIndex(index);
      return <span className="question-image-trigger" style={{ maxWidth: `${scale}%` }} role="button" tabIndex={0} key={`${url}-${index}`} aria-label={`Ampliar ${imageAlt(index).toLowerCase()}`} onClick={(event) => {
        event.stopPropagation();
        open();
      }} onKeyDown={(event) => {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          event.stopPropagation();
          open();
        }
      }}>
        <img src={url} alt={imageAlt(index)} loading="lazy" onLoad={(event) => rememberNaturalSize(index, event.currentTarget)} />
        <span className="question-image-expand-hint" aria-hidden="true"><span className="question-image-magnifier-icon" /></span>
      </span>;
    })}</div>
    {typeof document !== "undefined" && modal ? createPortal(modal, document.body) : null}
  </>;
}
