import assert from "node:assert/strict";
import { access, readFile, readdir } from "node:fs/promises";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";
import katex from "katex";

const root = fileURLToPath(new URL("../", import.meta.url));

test("implements ordered question blocks and mathematical editing", async () => {
  const mathFormula = await readFile(path.join(root, "app/components/MathFormula.tsx"), "utf8");
  const [page, review, blocks, media, inlineEditor, contentEditor, model, search, layout, css, migration, extractor] = await Promise.all([
    readFile(path.join(root, "app/page.tsx"), "utf8"),
    readFile(path.join(root, "app/revisao/page.tsx"), "utf8"),
    readFile(path.join(root, "app/components/QuestionBlocks.tsx"), "utf8"),
    readFile(path.join(root, "app/components/QuestionMedia.tsx"), "utf8"),
    readFile(path.join(root, "app/components/InlineMathEditor.tsx"), "utf8"),
    readFile(path.join(root, "app/components/ContentBlocksEditor.tsx"), "utf8"),
    readFile(path.join(root, "app/question-model.ts"), "utf8"),
    readFile(path.join(root, "app/search-utils.ts"), "utf8"),
    readFile(path.join(root, "app/layout.tsx"), "utf8"),
    readFile(path.join(root, "app/globals.css"), "utf8"),
    readFile(path.join(root, "drizzle/0002_ordered_content_blocks.sql"), "utf8"),
    readFile(path.join(root, "scripts/extract_question_media.py"), "utf8"),
  ]);

  assert.match(model, /stem\?: string/);
  assert.match(model, /alternatives\?: string\[\]/);
  assert.match(model, /formula\?: string/);
  assert.match(model, /contentBlocks\?: QuestionContentBlock\[\]/);
  assert.match(model, /type: "script"/);
  assert.match(model, /QuestionTextSegment/);
  assert.match(model, /TextAlignment = "left" \| "center" \| "right" \| "justify"/);
  assert.match(model, /alignment\?: TextAlignment/);
  assert.match(model, /headerRows\?: number/);
  assert.match(model, /export type ImageDisplayScale = 25 \| 50 \| 75 \| 100/);
  assert.match(model, /displayScale\?: ImageDisplayScale/);
  assert.match(model, /hiddenByDefault\?: boolean/);
  assert.match(model, /segments\?: QuestionTextSegment\[\]/);
  assert.match(model, /function defaultAlternativeText/);
  assert.match(model, /function normalizeImportedFormulaAlternatives/);
  assert.match(model, /function normalizeQuestionContent/);
  assert.match(model, /function repairCmb2004Question3/);
  assert.match(model, /II- 10% de 25 é maior que 5% de 50/);
  assert.match(model, /III- /);
  assert.match(model, /IV- 650/);
  assert.match(model, /V- 2584 em algarismos romanos/);
  assert.match(model, /function mergeAdjacentTextBlocks/);
  assert.match(model, /previous\.text \+ block\.text/);
  assert.match(model, /continuesSentence/);
  assert.match(model, /display: continuesSentence \? "inline" : "block"/);
  assert.match(model, /blocks\.slice\(-optionCount\)/);
  assert.match(model, /\.map\(normalizeQuestionContent\)/);
  assert.match(page, /className="question-blocks"/);
  assert.match(page, /<QuestionBlocks question=\{question\}/);
  assert.match(page, /defaultAlternativeText\(choiceMode, option\)/);
  assert.match(page, /simplequest:questions-view:v1/);
  assert.match(page, /searchRelevance/);
  assert.match(page, /localStorage\.setItem\(QUESTIONS_VIEW_KEY/);
  assert.match(page, /restoredScrollRef/);
  assert.doesNotMatch(page, /Formato<select/);
  assert.match(page, /const stateClass = response \? \(option === officialAnswer \? "correct"/);
  assert.match(blocks, /<InlineMath/);
  assert.match(mathFormula, /`\\\\displaystyle \$\{latex\}`/);
  assert.match(blocks, /<MathFormula/);
  assert.match(blocks, /<sup>\{part\.value\}<\/sup>/);
  assert.match(blocks, /<sub>\{part\.value\}<\/sub>/);
  assert.match(blocks, /segment\.bold/);
  assert.match(blocks, /segment\.italic/);
  assert.match(blocks, /segment\.underline/);
  assert.match(blocks, /inlineCandidates\.length > 1/);
  assert.match(blocks, /compact \|\| block\.display === "inline"/);
  assert.match(blocks, /className="question-table"/);
  assert.match(blocks, /block\.headerRows \?\? \(block\.hasHeader === false \? 0 : 1\)/);
  assert.match(blocks, /<thead>/);
  assert.match(blocks, /scope=\{cell\.colSpan > 1 \? "colgroup" : "col"\}/);
  assert.match(blocks, /function parseTableContent/);
  assert.match(blocks, /function isVerticalMergeMarker/);
  assert.match(blocks, /function isHorizontalMergeMarker/);
  assert.match(blocks, /function isGhostCellMarker/);
  assert.match(blocks, /blocks\[0\]\.text\.trim\(\) === "\^"/);
  assert.match(blocks, /blocks\[0\]\.text\.trim\(\) === ">"/);
  assert.match(blocks, /blocks\[0\]\.text\.trim\(\) === "~"/);
  assert.match(blocks, /rowSpan=\{cell\.rowSpan\}/);
  assert.match(blocks, /colSpan=\{cell\.colSpan\}/);
  assert.match(blocks, /const className = cell\.ghost \? \[/);
  assert.match(blocks, /rowIndex \+ cell\.rowSpan >= rowCount/);
  assert.match(blocks, /cellIndex \+ cell\.colSpan >= columnCount/);
  assert.match(blocks, /legacyHeaderSpansBody/);
  assert.match(blocks, /let quoted = false/);
  assert.match(blocks, /character === "`"/);
  assert.match(blocks, /character === "´"/);
  assert.match(blocks, /!quoted && character === "\|"/);
  assert.match(blocks, /!quoted && character === "\\n"/);
  assert.match(blocks, /function TableCellContent/);
  assert.match(blocks, /style=\{\{ textAlign: block\.alignment \|\| "left" \}\}/);
  assert.match(blocks, /style=\{\{ textAlign: alignment \}\}/);
  assert.match(blocks, /block\.fontSize \|\| 11/);
  assert.match(blocks, /<QuestionMedia/);
  assert.match(media, /loading="lazy"/);
  assert.match(media, /createPortal\(modal, document\.body\)/);
  assert.match(media, /event\.key === "Escape"/);
  assert.match(media, /event\.stopPropagation\(\)/);
  assert.doesNotMatch(media, /width: 1600, height: 900/);
  assert.match(media, /size\.width \* 2/);
  assert.match(media, /question-image-magnifier-icon/);
  assert.match(media, /question-image-modal-close[^>]*>[\s\S]*<span aria-hidden="true"/);
  assert.match(media, /displayScale = 50/);
  assert.match(media, /hiddenByDefault = false/);
  assert.match(media, /if \(hiddenByDefault\) return null/);
  assert.match(media, /Ver imagem anexada/);
  assert.match(media, /setRevealed\(true\)/);
  assert.match(media, /style=\{\{ maxWidth: `\$\{scale\}%` \}\}/);
  assert.match(review, /<ContentBlocksEditor/);
  assert.match(review, /simplequest:review-view:v1/);
  assert.match(review, /searchRelevance/);
  assert.match(search, /function editDistanceWithin/);
  assert.match(search, /SEARCH_SYNONYM_GROUPS/);
  assert.match(review, /"unauthenticated"/);
  assert.match(review, /<option value="unauthenticated">Não autenticadas<\/option>/);
  assert.match(review, /!question\.isLocked \|\| !question\.authenticatedAt/);
  assert.match(review, /localStorage\.setItem\(REVIEW_VIEW_KEY/);
  assert.match(review, /preferredQuestionId/);
  assert.match(review, /queueListRef/);
  assert.match(review, /ANSWER_OPTIONS\[editing\.answerType \|\| "ABCDE"\]\.map/);
  assert.match(review, /normalizeQuestionContent\(question\)/);
  assert.match(review, /<ContentBlocksEditor compact/);
  assert.match(contentEditor, /<InlineMathEditor/);
  assert.match(review, /function addContentBlock/);
  assert.match(review, /addContentBlock\("text"\)/);
  assert.match(review, /addContentBlock\("image"\)/);
  assert.match(review, /addContentBlock\("table"\)/);
  assert.match(contentEditor, /table-header-button/);
  assert.match(contentEditor, /function tableHeaderRows/);
  assert.match(contentEditor, /Cabeçalho: \{tableHeaderRows\(group\) \|\| "nenhum"\}/);
  assert.match(contentEditor, /\^ mescla acima, > mescla à esquerda e ~ cria célula invisível/);
  assert.match(contentEditor, /contentBlocksPlainText\(content\)/);
  assert.match(contentEditor, /tableFontSize/);
  assert.match(contentEditor, /Aumentar fonte da tabela/);
  assert.match(contentEditor, /Diminuir fonte da tabela/);
  assert.match(contentEditor, /IMAGE_DISPLAY_SCALES/);
  assert.match(contentEditor, /imageDisplayScale\(group\) === scale/);
  assert.match(contentEditor, /hiddenByDefault: false/);
  assert.match(contentEditor, /hiddenByDefault: true/);
  assert.match(contentEditor, /!group\.hiddenByDefault \? " active"/);
  assert.match(review, /className="global-formula-button"/);
  assert.match(review, /function insertFormulaFromToolbar/);
  assert.match(review, /disabled=\{isEditingLocked\}/);
  assert.match(review, /const flags = contentFlags\(blocks, editing\.alternativeBlocks \|\| \[\]\)/);
  assert.match(review, /function contentFlags/);
  assert.doesNotMatch(review, /disabled=\{isEditingLocked \|\| !editing\.hasMath \|\| !hasFormulaCursor\}/);
  assert.match(review, /Inserir fórmula\{hasFormulaCursor \? " no cursor" : ""\}/);
  assert.doesNotMatch(review, /type="checkbox" checked=\{editing\.has/);
  assert.doesNotMatch(inlineEditor, /Inserir fórmula no cursor/);
  assert.match(inlineEditor, /contentEditable={!disabled}/);
  assert.match(inlineEditor, /single-text-editor/);
  assert.match(inlineEditor, /blocks\.length === 1 && blocks\[0\]\.type === "text"/);
  assert.doesNotMatch(inlineEditor, /onFocus=\{/);
  assert.match(inlineEditor, /const hasEditorContent = blocks\.some/);
  assert.match(inlineEditor, /function compositeBlocksFromElement/);
  assert.match(inlineEditor, /function editorContentKey/);
  assert.match(inlineEditor, /key=\{contentKey\}/);
  assert.match(inlineEditor, /function compositeSelectionOffsets/);
  assert.match(inlineEditor, /function deleteCompositeRange/);
  assert.match(inlineEditor, /function deleteCompositeContent/);
  assert.match(inlineEditor, /function deleteCompositeSelection/);
  assert.match(inlineEditor, /typeof inputType !== "string"/);
  assert.match(inlineEditor, /function deleteFormulaElement/);
  assert.match(inlineEditor, /function scheduleCompositeCaret/);
  assert.match(inlineEditor, /scheduleCompositeCaret\(caret\)/);
  assert.match(inlineEditor, /data-caret-slot=\{block\.text\.length === 0/);
  assert.match(inlineEditor, /onBeforeInput=/);
  assert.match(inlineEditor, /onKeyDownCapture=/);
  assert.match(inlineEditor, /event\.preventDefault\(\)/);
  assert.match(inlineEditor, /contentEditable=\{!disabled\}/);
  assert.match(inlineEditor, /data-inline-math-id=\{block\.id\}/);
  assert.match(inlineEditor, /!hasEditorContent && blockIndex === 0/);
  assert.match(inlineEditor, /<FormulaEditor/);
  assert.match(inlineEditor, /event\.key !== "Backspace"/);
  assert.match(inlineEditor, /event\.key !== "Delete"/);
  assert.match(inlineEditor, /placeSelectionAtOffsets/);
  assert.match(inlineEditor, /function placeCaretFromPoint/);
  assert.match(inlineEditor, /function captureNativeSelection/);
  assert.match(inlineEditor, /function restoreNativeSelection/);
  assert.match(inlineEditor, /selection\.setBaseAndExtent/);
  assert.match(inlineEditor, /nativeSelectionRestoreRef/);
  assert.match(inlineEditor, /document\.addEventListener\("selectionchange", syncSelection\)/);
  assert.match(inlineEditor, /document\.removeEventListener\("selectionchange", syncSelection\)/);
  assert.match(inlineEditor, /selectionSignatureRef/);
  assert.match(inlineEditor, /pointerGestureRef/);
  assert.match(inlineEditor, /gesture\.moved/);
  assert.match(inlineEditor, /function placeCaretFromPoint\(editor: HTMLElement, clientX: number, clientY: number, remember = true\)/);
  assert.match(inlineEditor, /clickSequenceRef/);
  assert.match(inlineEditor, /function selectTextFromPoint/);
  assert.match(inlineEditor, /mode: "word" \| "line"/);
  assert.match(inlineEditor, /now - previousClick\.at <= 500/);
  assert.match(inlineEditor, /clickCount === 2 \|\| clickCount === 3/);
  assert.match(inlineEditor, /placeCaretFromPoint\(event\.currentTarget, event\.clientX, event\.clientY, false\)/);
  assert.match(inlineEditor, /clickSyncTimerRef/);
  assert.match(inlineEditor, /clickSyncTimerRef\.current = window\.setTimeout/);
  assert.match(inlineEditor, /}, 320\)/);
  assert.match(inlineEditor, /selectionWithinTextPart/);
  assert.match(inlineEditor, /caretPositionFromPoint/);
  assert.match(inlineEditor, /caretRangeFromPoint/);
  assert.match(inlineEditor, /function moveCaretAcrossBlocks/);
  assert.match(inlineEditor, /function selectionHasOnlyWhitespaceToBoundary/);
  assert.match(inlineEditor, /candidate\.text\.trimEnd\(\)\.length/);
  assert.match(inlineEditor, /event\.key === "ArrowLeft" \|\| event\.key === "ArrowRight"/);
  assert.match(inlineEditor, /event\.key === "ArrowUp" \|\| event\.key === "ArrowDown"/);
  assert.match(inlineEditor, /caretRestoreRef/);
  assert.match(inlineEditor, /\[blocks, selectedFormulaId\]/);
  assert.match(inlineEditor, /editorRef\.current\.dataset\.blockId === request\.id/);
  assert.doesNotMatch(inlineEditor, /document\.execCommand/);
  assert.match(inlineEditor, /formatTextBlock/);
  assert.match(inlineEditor, /segmentsFromElement/);
  assert.match(review, /text-format-buttons/);
  assert.match(review, /applyTextFormatting\("bold"\)/);
  assert.match(review, /applyTextFormatting\("italic"\)/);
  assert.match(review, /applyTextFormatting\("underline"\)/);
  assert.match(review, /activeTextFormats\.includes\("bold"\)/);
  assert.match(review, /activeTextAlignment === alignment/);
  assert.match(review, /applyTextAlignment\(alignment\)/);
  assert.match(review, /align-\$\{alignment\}/);
  assert.match(inlineEditor, /function textFormatsAt/);
  assert.match(inlineEditor, /function applyBlockAlignment/);
  assert.match(inlineEditor, /style=\{\{ textAlign: blockAlignment \}\}/);
  assert.match(inlineEditor, /function replaceTextBlockRange/);
  assert.match(inlineEditor, /function insertLineBreakAtSelection/);
  assert.match(inlineEditor, /event\.key === "Enter"/);
  assert.match(inlineEditor, /caret = Math\.min\(offsets\.start, offsets\.end\) \+ 1/);
  assert.match(page, /blocks=\{question\.alternativeBlocks\[optionIndex\]\} compact/);
  assert.match(page, /className=\{`alternative-option/);
  assert.match(page, /role="radiogroup"/);
  assert.match(review, /addAlternativeBlock\(index, "image"\)/);
  assert.match(review, /addAlternativeBlock\(index, "table"\)/);
  assert.match(review, /imagePlaceholder=\{alternativeImagePlaceholder/);
  assert.doesNotMatch(review, /alternativeBlocks\?\.\[index\]\?\.filter/);
  assert.match(review, /function undoEditing/);
  assert.match(review, /function redoEditing/);
  assert.match(review, /className="history-buttons"/);
  assert.ok(review.indexOf('className="element-add-buttons"') < review.indexOf('className="global-formula-button"'));
  assert.ok(review.indexOf('className="global-formula-button"') < review.indexOf('className="text-format-buttons"'));
  assert.ok(review.indexOf('className="text-format-buttons"') < review.indexOf('className="history-buttons"'));
  assert.match(review, /disabled=\{isEditingLocked \|\| !undoStack\.length\}/);
  assert.match(review, /disabled=\{isEditingLocked \|\| !redoStack\.length\}/);
  assert.match(contentEditor, /className="remove-block-button"/);
  assert.match(contentEditor, /aria-label="Excluir bloco"/);
  assert.match(contentEditor, /<FormulaEditor/);
  assert.match(contentEditor, /function moveGroup/);
  assert.match(contentEditor, /id: inline\[0\]\.id/);
  assert.doesNotMatch(contentEditor, /inline\.map\(\(block\) => block\.id\)\.join/);
  assert.match(extractor, /def media_slug/);
  assert.match(extractor, /media_filenames/);
  assert.match(extractor, /block\["display"\] = "inline" if has_text else "block"/);
  assert.match(layout, /katex\/dist\/katex\.min\.css/);
  assert.match(css, /\.question-blocks\s*\{[^}]*gap:\s*10px/);
  assert.match(css, /\.alternative-option\.correct/);
  assert.match(css, /\.alternative-option\.incorrect/);
  assert.match(css, /\.question-image-trigger img\s*\{[^}]*width:\s*auto[^}]*max-width:\s*100%/);
  assert.match(css, /\.question-image-modal\s*\{/);
  assert.match(css, /--question-image-zoom-width/);
  assert.match(css, /\.question-image-modal-close > span::before/);
  assert.match(css, /\.question-table \.ghost-cell\s*\{[^}]*background:\s*transparent/);
  assert.match(css, /\.ghost-cell\.ghost-top\s*\{[^}]*border-top-color:\s*transparent/);
  assert.match(css, /\.ghost-cell\.ghost-bottom\s*\{[^}]*border-bottom-color:\s*transparent/);
  assert.match(css, /\.question-image-collapsed/);
  assert.match(css, /\.image-scale-button\.active/);
  assert.match(css, /\.image-visibility-button\.active/);
  assert.match(css, /\.inline-text-part\[data-caret-slot="true"\]/);
  assert.match(css, /\.alignment-icon/);
  assert.ok(migration.includes("ADD `content_blocks`"));
});

test("keeps the extracted media catalog internally consistent", async () => {
  const catalog = JSON.parse(await readFile(path.join(root, "public/data/questions.json"), "utf8"));
  const mediaDirectory = path.join(root, "public/question-media");
  const mediaFiles = await readdir(mediaDirectory);
  const allBlocks = catalog.flatMap((question) => [...(question.contentBlocks || []), ...(question.alternativeBlocks || []).flat()]);
  const formulaBlocks = allBlocks.filter((block) => block.type === "formula" && block.latex.trim());
  const references = allBlocks.filter((block) => block.type === "image").flatMap((block) => block.urls);
  const pendingBlocks = allBlocks.filter((block) => block.type === "pending-media");
  const pendingQuestions = catalog.filter((question) => [...(question.contentBlocks || []), ...(question.alternativeBlocks || []).flat()].some((block) => block.type === "pending-media"));
  const scriptBlocks = allBlocks.filter((block) => block.type === "script");
  const scriptQuestions = catalog.filter((question) => [...(question.contentBlocks || []), ...(question.alternativeBlocks || []).flat()].some((block) => block.type === "script"));

  assert.equal(catalog.length, 1217);
  assert.equal(pendingBlocks.length, 10);
  assert.equal(pendingQuestions.length, 6);
  assert.equal(scriptBlocks.length, 88);
  assert.equal(scriptQuestions.length, 21);
  assert.equal(scriptBlocks.filter((block) => !block.base).length, 0);
  assert.ok(references.length >= 429);
  assert.ok([...new Set(references)].every((reference) => mediaFiles.includes(path.basename(reference))));
  assert.ok(references.every((reference) => reference.endsWith(".webp")));

  for (const reference of references) {
    assert.match(reference, /^\/question-media\/[a-z0-9]+-\d{4}-\d+(?:_(?:\d+|[a-e](?:_\d+)?))?\.webp$/);
    await access(path.join(root, "public", reference.slice(1)));
  }

  for (const block of allBlocks.filter((item) => item.type === "image")) {
    assert.equal(block.dimensions?.length, block.urls.length, `Dimensões ausentes no bloco ${block.id}`);
    assert.ok(block.dimensions.every(({ width, height }) => width > 0 && height > 0), `Dimensão inválida no bloco ${block.id}`);
  }

  for (const question of catalog) {
    const base = `${question.school.toLowerCase().replace(/[^a-z0-9]+/g, "-")}-${question.year}-${question.number}`;
    const mainUrls = [...new Set((question.contentBlocks || []).filter((block) => block.type === "image").flatMap((block) => block.urls))];
    const expectedMain = mainUrls.map((_, index) => `/question-media/${base}${mainUrls.length === 1 ? "" : `_${index + 1}`}.webp`);
    assert.deepEqual(mainUrls, expectedMain, `Nomes de mídia inesperados no enunciado de ${question.id}`);
    for (const [alternativeIndex, blocks] of (question.alternativeBlocks || []).entries()) {
      const urls = [...new Set(blocks.filter((block) => block.type === "image").flatMap((block) => block.urls))];
      const letter = String.fromCharCode(97 + alternativeIndex);
      const expected = urls.map((_, index) => `/question-media/${base}_${letter}${urls.length === 1 ? "" : `_${index + 1}`}.webp`);
      assert.deepEqual(urls, expected, `Nomes de mídia inesperados na alternativa ${letter.toUpperCase()} de ${question.id}`);
    }
  }

  for (const block of formulaBlocks) {
    assert.doesNotThrow(() => katex.renderToString(block.latex, { displayMode: true, throwOnError: true, strict: "ignore" }), `Fórmula inválida no bloco ${block.id}`);
  }

  const cmb2003 = catalog.find((question) => question.id === "cmb-2003-1-2");
  assert.deepEqual(cmb2003.contentBlocks.map((block) => block.type), ["text", "formula", "text"]);
  assert.equal(cmb2003.contentBlocks[2].text, "É igual a:");

  const cmb2003Question3 = catalog.find((question) => question.id === "cmb-2003-3-4");
  assert.equal(cmb2003Question3.alternatives[4], "Em três dias temos menos do que \\(2\\times10^5\\) segundos.");
  assert.deepEqual(cmb2003Question3.alternativeBlocks[4].map((block) => block.type), ["text", "formula", "text"]);
  assert.deepEqual(cmb2003Question3.alternativeBlocks[4][1], { id: "a5-2", type: "formula", latex: "2\\times10^5", display: "inline" });
});

test("implements administrative authentication and locking", async () => {
  const [page, review, model, api, schema, migration, css] = await Promise.all([
    readFile(path.join(root, "app/page.tsx"), "utf8"),
    readFile(path.join(root, "app/revisao/page.tsx"), "utf8"),
    readFile(path.join(root, "app/question-model.ts"), "utf8"),
    readFile(path.join(root, "app/api/questions/revisions/route.ts"), "utf8"),
    readFile(path.join(root, "db/schema.ts"), "utf8"),
    readFile(path.join(root, "drizzle/0003_question_authentication.sql"), "utf8"),
    readFile(path.join(root, "app/globals.css"), "utf8"),
  ]);

  for (const field of ["authenticatedAt", "authenticatedBy", "isLocked", "lockedAt", "lockedBy", "lastUnlockReason", "auditTrail"]) {
    assert.ok(model.includes(field), `Campo ausente no modelo: ${field}`);
    assert.ok(schema.includes(field), `Campo ausente no esquema: ${field}`);
  }
  assert.match(review, /Autenticar e travar/);
  assert.match(review, /Motivo do desbloqueio/);
  assert.match(review, /Histórico de confiança/);
  assert.match(page, /Autenticada · Admin/);
  assert.match(api, /status: 423/);
  assert.match(api, /changedProtectedContent/);
  assert.match(api, /pelo menos 5 caracteres/);
  assert.match(migration, /authenticated_at/);
  assert.match(migration, /audit_trail/);
  assert.match(css, /\.quality\.authenticated/);
  assert.match(css, /\.authentication-banner/);
});
