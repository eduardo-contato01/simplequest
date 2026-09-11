const SEARCH_SYNONYM_GROUPS = [
  ["porcentagem", "percentagem"],
  ["mmc", "minimo multiplo comum"],
  ["mdc", "maximo divisor comum"],
] as const;

export function normalizeSearchText(value: string) {
  return value
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLocaleLowerCase("pt-BR")
    .replace(/[^a-z0-9]+/g, " ")
    .trim()
    .replace(/\s+/g, " ");
}

function canonicalizeSearchText(value: string) {
  let normalized = ` ${normalizeSearchText(value)} `;

  for (const [canonical, ...aliases] of SEARCH_SYNONYM_GROUPS) {
    for (const alias of aliases) {
      normalized = normalized.replaceAll(` ${alias} `, ` ${canonical} `);
    }
  }

  return normalized.trim();
}

function allowedDistance(token: string) {
  if (/^\d+$/.test(token) || token.length <= 3) return 0;
  if (token.length <= 7) return 1;
  return 2;
}

// Distância de Damerau-Levenshtein com interrupção antecipada. Além de letras
// ausentes ou extras, reconhece duas letras vizinhas digitadas na ordem errada.
function editDistanceWithin(left: string, right: string, limit: number) {
  if (left === right) return 0;
  if (!limit || Math.abs(left.length - right.length) > limit) return limit + 1;

  let previousPrevious: number[] | null = null;
  let previous = Array.from({ length: right.length + 1 }, (_, index) => index);

  for (let leftIndex = 1; leftIndex <= left.length; leftIndex += 1) {
    const current = [leftIndex];
    let rowMinimum = current[0];

    for (let rightIndex = 1; rightIndex <= right.length; rightIndex += 1) {
      const substitutionCost = left[leftIndex - 1] === right[rightIndex - 1] ? 0 : 1;
      let distance = Math.min(
        current[rightIndex - 1] + 1,
        previous[rightIndex] + 1,
        previous[rightIndex - 1] + substitutionCost,
      );

      if (
        previousPrevious
        && leftIndex > 1
        && rightIndex > 1
        && left[leftIndex - 1] === right[rightIndex - 2]
        && left[leftIndex - 2] === right[rightIndex - 1]
      ) {
        distance = Math.min(distance, previousPrevious[rightIndex - 2] + 1);
      }

      current[rightIndex] = distance;
      rowMinimum = Math.min(rowMinimum, distance);
    }

    if (rowMinimum > limit) return limit + 1;
    previousPrevious = previous;
    previous = current;
  }

  return previous[right.length];
}

function tokenDistance(queryToken: string, candidate: string) {
  if (candidate === queryToken) return 0;

  // Mantém a busca parcial já esperada ao começar a digitar uma palavra.
  if (queryToken.length >= 3 && candidate.startsWith(queryToken)) return 0;

  const limit = allowedDistance(queryToken);
  return editDistanceWithin(queryToken, candidate, limit);
}

/**
 * Retorna null quando não há correspondência. Quanto menor o valor, mais
 * relevante é o resultado: frase literal, palavras exatas e, por fim, erros
 * ortográficos tolerados.
 */
export function searchRelevance(query: string, searchableValue: string): number | null {
  const normalizedQuery = canonicalizeSearchText(query);
  if (!normalizedQuery) return 0;

  const normalizedSearchable = canonicalizeSearchText(searchableValue);
  if (normalizedSearchable.includes(normalizedQuery)) return 0;

  const queryTokens = normalizedQuery.split(" ").filter(Boolean);
  const searchableTokens = normalizedSearchable.split(" ").filter(Boolean);
  let fuzzyDistance = 0;

  for (const queryToken of queryTokens) {
    const limit = allowedDistance(queryToken);
    let bestDistance = limit + 1;

    for (const candidate of searchableTokens) {
      const distance = tokenDistance(queryToken, candidate);
      if (distance < bestDistance) bestDistance = distance;
      if (bestDistance === 0) break;
    }

    if (bestDistance > limit) return null;
    fuzzyDistance += bestDistance;
  }

  return fuzzyDistance === 0 ? 1 : 2 + fuzzyDistance;
}
