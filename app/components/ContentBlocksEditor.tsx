import { contentBlocksPlainText, type ImageDisplayScale, type QuestionContentBlock, type TextAlignment } from "../question-model";
import { FormulaEditor } from "./FormulaEditor";
import { InlineMathEditor, type TextFormat } from "./InlineMathEditor";

type InlineBlock = Extract<QuestionContentBlock, { type: "text" | "formula" | "script" }>;

type Props = {
  blocks: QuestionContentBlock[];
  showFormula: boolean;
  showTable: boolean;
  showMedia: boolean;
  onChange: (blocks: QuestionContentBlock[]) => void;
  onActivateFormulaInsertion?: (insert: () => void) => void;
  onActivateTextFormatting?: (apply: (format: TextFormat) => void, activeFormats: TextFormat[]) => void;
  onActivateTextAlignment?: (apply: (alignment: TextAlignment) => void, activeAlignment: TextAlignment) => void;
  onDeactivateEditor?: () => void;
  disabled?: boolean;
  title?: string;
  compact?: boolean;
  imagePlaceholder?: string;
};

type EditorGroup =
  | { type: "inline-group"; id: string; blocks: InlineBlock[] }
  | Exclude<QuestionContentBlock, Extract<InlineBlock, { type: "text" | "script" }>>;

function tableFontSize(block: Extract<QuestionContentBlock, { type: "table" }>) {
  return Math.max(8, Math.min(18, block.fontSize || 11));
}

function tableHeaderRows(block: Extract<QuestionContentBlock, { type: "table" }>) {
  return Math.max(0, Math.min(2, block.headerRows ?? (block.hasHeader === false ? 0 : 1)));
}

const IMAGE_DISPLAY_SCALES: ImageDisplayScale[] = [25, 50, 75, 100];

function imageDisplayScale(block: Extract<QuestionContentBlock, { type: "image" }>): ImageDisplayScale {
  return IMAGE_DISPLAY_SCALES.includes(block.displayScale || 50) ? (block.displayScale || 50) as ImageDisplayScale : 50;
}

export function ContentBlocksEditor({ blocks, showFormula, showTable, showMedia, onChange, onActivateFormulaInsertion, onActivateTextFormatting, onActivateTextAlignment, onDeactivateEditor, disabled = false, title = "Conteúdo da questão", compact = false, imagePlaceholder = "Um endereço de imagem por linha" }: Props) {
  const groups: EditorGroup[] = [];
  let inline: InlineBlock[] = [];
  const flushInline = () => {
    if (!inline.length) return;
    groups.push({ type: "inline-group", id: inline[0].id, blocks: inline });
    inline = [];
  };

  for (const block of blocks) {
    if (block.type === "text" && block.section) {
      flushInline();
      inline.push(block);
      continue;
    }
    if (block.type === "text" || (block.type === "script" && showFormula) || (block.type === "formula" && showFormula && block.display !== "block")) {
      inline.push(block);
      continue;
    }
    flushInline();
    if (block.type === "formula" && showFormula) groups.push(block);
    if (block.type === "table" && showTable) groups.push(block);
    if ((block.type === "image" || block.type === "pending-media") && showMedia) groups.push(block);
  }
  flushInline();

  function replace(id: string, block: QuestionContentBlock) {
    onChange(blocks.map((item) => item.id === id ? block : item));
  }

  function replaceInline(current: InlineBlock[], next: InlineBlock[]) {
    const ids = new Set(current.map((block) => block.id));
    const first = blocks.findIndex((block) => ids.has(block.id));
    const last = blocks.findLastIndex((block) => ids.has(block.id));
    if (first < 0 || last < first) return;
    onChange([...blocks.slice(0, first), ...next, ...blocks.slice(last + 1)]);
  }

  const groupBlocks = (group: EditorGroup): QuestionContentBlock[] => group.type === "inline-group" ? group.blocks : [group];

  function moveGroup(index: number, direction: -1 | 1) {
    const target = index + direction;
    if (target < 0 || target >= groups.length) return;
    const next = [...groups];
    [next[index], next[target]] = [next[target], next[index]];
    onChange(next.flatMap(groupBlocks));
  }

  function removeGroup(index: number) {
    onChange(groups.filter((_, groupIndex) => groupIndex !== index).flatMap(groupBlocks));
  }

  return (
    <section className={`content-blocks-editor${compact ? " compact" : ""}`}>
      {!compact && <div className="content-blocks-heading"><span>{title}</span><small>Texto e matemática ficam juntos; tabelas e imagens permanecem em seções.</small></div>}
      {groups.map((group, groupIndex) => group.type === "inline-group" ? (
        <article className="content-block-card inline-content-block" key={group.id}>
          <header><strong>Texto{group.blocks.some((block) => block.type !== "text") ? " e fórmula" : ""}</strong><div><button type="button" disabled={disabled || groupIndex === 0} onClick={() => moveGroup(groupIndex, -1)} aria-label="Mover para cima">↑</button><button type="button" disabled={disabled || groupIndex === groups.length - 1} onClick={() => moveGroup(groupIndex, 1)} aria-label="Mover para baixo">↓</button><button type="button" className="remove-block-button" disabled={disabled} onClick={() => removeGroup(groupIndex)} aria-label="Excluir bloco" title="Excluir bloco">🗑</button></div></header>
          <InlineMathEditor
            blocks={group.blocks}
            disabled={disabled}
            label="Texto da questão"
            onActivateFormulaInsertion={onActivateFormulaInsertion}
            onActivateTextFormatting={onActivateTextFormatting}
            onActivateTextAlignment={onActivateTextAlignment}
            onDeactivate={onDeactivateEditor}
            onChange={(next) => replaceInline(group.blocks, next)}
          />
        </article>
      ) : (
        <article className={`content-block-card ${group.type}`} key={group.id}>
          <header>
            <strong>{group.type === "formula" ? "Fórmula matemática" : group.type === "table" ? "Tabela" : group.type === "image" ? "Imagem ou gráfico" : "Mídia pendente"}</strong>
            <div>
              {group.type === "table" && <><button type="button" className={`table-header-button${tableHeaderRows(group) > 0 ? " active" : ""}`} disabled={disabled} aria-label="Alterar quantidade de linhas de cabeçalho" onClick={() => { const headerRows = (tableHeaderRows(group) + 1) % 3; replace(group.id, { ...group, headerRows, hasHeader: headerRows > 0 }); }}>Cabeçalho: {tableHeaderRows(group) || "nenhum"}</button><button type="button" className="table-font-button" disabled={disabled || tableFontSize(group) >= 18} onClick={() => replace(group.id, { ...group, fontSize: tableFontSize(group) + 1 })} aria-label="Aumentar fonte da tabela" title="Aumentar fonte da tabela">A+</button><button type="button" className="table-font-button" disabled={disabled || tableFontSize(group) <= 8} onClick={() => replace(group.id, { ...group, fontSize: tableFontSize(group) - 1 })} aria-label="Diminuir fonte da tabela" title="Diminuir fonte da tabela">A−</button></>}
              {group.type === "image" && <><span className="image-size-label">Tamanho</span>{IMAGE_DISPLAY_SCALES.map((scale) => <button type="button" className={`image-scale-button${imageDisplayScale(group) === scale ? " active" : ""}`} aria-pressed={imageDisplayScale(group) === scale} disabled={disabled} onClick={() => replace(group.id, { ...group, displayScale: scale })} key={scale}>{scale}%</button>)}<button type="button" className={`image-visibility-button${!group.hiddenByDefault ? " active" : ""}`} aria-pressed={!group.hiddenByDefault} disabled={disabled} onClick={() => replace(group.id, { ...group, hiddenByDefault: false })}>Visível</button><button type="button" className={`image-visibility-button${group.hiddenByDefault ? " active" : ""}`} aria-pressed={Boolean(group.hiddenByDefault)} disabled={disabled} onClick={() => replace(group.id, { ...group, hiddenByDefault: true })}>Oculta</button></>}
              <button type="button" disabled={disabled || groupIndex === 0} onClick={() => moveGroup(groupIndex, -1)} aria-label="Mover para cima">↑</button><button type="button" disabled={disabled || groupIndex === groups.length - 1} onClick={() => moveGroup(groupIndex, 1)} aria-label="Mover para baixo">↓</button><button type="button" className="remove-block-button" disabled={disabled} onClick={() => removeGroup(groupIndex)} aria-label="Excluir bloco" title="Excluir bloco">🗑</button>
            </div>
          </header>
          {group.type === "formula" && <FormulaEditor readOnly={disabled} value={group.latex} onChange={(latex) => replace(group.id, { ...group, latex })} />}
          {group.type === "table" && <div className="table-rich-editor" style={{ fontSize: `${tableFontSize(group)}px` }}><InlineMathEditor
            blocks={group.content?.length ? group.content : [{ id: `${group.id}-text`, type: "text", text: group.data }]}
            disabled={disabled}
            label={'Use | para colunas e Enter para linhas; ^ mescla acima, > mescla à esquerda e ~ cria célula invisível; texto entre ` ou ´ permanece na mesma célula'}
            onActivateFormulaInsertion={onActivateFormulaInsertion}
            onActivateTextFormatting={onActivateTextFormatting}
            onActivateTextAlignment={onActivateTextAlignment}
            defaultAlignment="center"
            onDeactivate={onDeactivateEditor}
            onChange={(content) => replace(group.id, { ...group, content, data: contentBlocksPlainText(content) })}
          /></div>}
          {group.type === "image" && <textarea disabled={disabled} rows={compact ? 2 : 4} value={group.urls.join("\n")} onChange={(event) => replace(group.id, { ...group, urls: event.target.value.split(/\r?\n/).map((item) => item.trim()).filter(Boolean), dimensions: undefined })} placeholder={imagePlaceholder} />}
          {group.type === "pending-media" && <p>Arquivo {group.format.toUpperCase()} localizado no Word, mas ainda não convertido. Esta questão permanece na fila de revisão.</p>}
        </article>
      ))}
    </section>
  );
}
