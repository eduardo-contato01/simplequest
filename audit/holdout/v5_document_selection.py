"""V5 Phase A metadata-only selector/verifier. No PDF, OCR or Auditor imports.

Selection consumes only the frozen neutral universe and prior-exposure registry.
Run from the repository root: python -X utf8 audit/holdout/v5_document_selection.py
"""
from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

CANDIDATE = '3b306d6a544cc63928ec8adf07640b224651742e'
TARGET = 48
SEED_MATERIAL = 'simplequest-holdout-v5|' + CANDIDATE
SEED = hashlib.sha256(SEED_MATERIAL.encode('utf-8')).hexdigest()
SERIES_NULL = 'not_applicable_or_unspecified'
ROOT = Path(__file__).resolve().parents[2]
HOLDOUT = ROOT / 'audit/holdout'
FLAGS = {
    'selectionFrozenBeforeQuestionInspection': True,
    'questionInspectionPerformed': False,
    'questionSelectionStarted': False,
    'groundTruthStarted': False,
    'auditorExecuted': False,
    'metricsSeen': False,
}
NEUTRAL_FIELDS = {
    'documentId', 'contentFingerprint', 'canonicalPath', 'relativePath', 'family',
    'year', 'series', 'sourceType', 'pageCount', 'sizeBytes', 'fileAvailable',
    'metadataSource', 'eligible', 'exclusionReason', 'exclusionReasons',
}

def digest(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def era(year: int) -> str:
    if 2004 <= year <= 2009: return '2004-2009'
    if 2010 <= year <= 2014: return '2010-2014'
    if 2015 <= year <= 2019: return '2015-2019'
    if 2020 <= year <= 2025: return '2020-2025'
    return f'{year // 5 * 5}-{year // 5 * 5 + 4}'

def series(row: dict) -> str:
    return row['series'] if row['series'] is not None else SERIES_NULL

def cell(row: dict) -> tuple:
    return (row['sourceType'], row['family'], era(row['year']), series(row))

def cell_text(key: tuple) -> str:
    return json.dumps(list(key), ensure_ascii=False, separators=(',', ':'))

def source_quotas(rows: list[dict], target: int = TARGET) -> dict[str, int]:
    capacities = Counter(row['sourceType'] for row in rows)
    assert len(rows) >= target and 0 < len(capacities) <= target
    quota = {source: 1 for source in sorted(capacities)}
    remaining = target - len(quota)
    # Hamilton allocation of the remaining slots, after reserving one per source.
    exact = {s: Fraction(remaining * n, len(rows)) for s, n in capacities.items()}
    for s, value in exact.items(): quota[s] += value.numerator // value.denominator
    left = target - sum(quota.values())
    order = sorted(capacities, key=lambda s: (
        -(exact[s] - exact[s].numerator // exact[s].denominator),
        digest(SEED + '|source|' + s), s))
    for s in order[:left]: quota[s] += 1
    assert sum(quota.values()) == target
    assert all(quota[s] <= capacities[s] for s in quota), 'source quota exceeds capacity'
    return dict(sorted(quota.items()))

def select(rows: list[dict], target: int = TARGET) -> tuple[list[dict], dict]:
    eligible = [r for r in rows if r['eligible']]
    assert len({r['contentFingerprint'] for r in eligible}) == len(eligible)
    assert len({r['documentId'] for r in eligible}) == len(eligible)
    quotas = source_quotas(eligible, target)
    cells = defaultdict(list)
    for r in eligible: cells[cell(r)].append(r)
    for key in cells:
        cells[key].sort(key=lambda r: (digest(SEED + '|' + r['contentFingerprint']),
                                      r['contentFingerprint'], r['canonicalPath']))
    era_capacity = Counter(era(r['year']) for r in eligible)
    series_capacity = Counter(series(r) for r in eligible)
    chosen = []
    source_count, family_count, year_count = Counter(), Counter(), Counter()
    era_count, series_count, cell_count = Counter(), Counter(), Counter()
    for _ in range(target):
        remaining_sources = [s for s in quotas if source_count[s] < quotas[s]]
        source = min(remaining_sources, key=lambda s: (
            Fraction(source_count[s], quotas[s]), digest(SEED + '|source|' + s), s))
        available = [key for key, values in cells.items()
                     if key[0] == source and cell_count[key] < len(values)
                     and family_count[key[1]] < 3]
        assert available, 'selection_constraints_unsatisfied; no relaxation or retry'
        def score(key):
            r = cells[key][cell_count[key]]
            return (0 if series_count[key[3]] == 0 else 1,
                    family_count[key[1]], year_count[r['year']],
                    Fraction(era_count[key[2]], era_capacity[key[2]]),
                    Fraction(series_count[key[3]], series_capacity[key[3]]),
                    Fraction(cell_count[key], len(cells[key])),
                    digest(SEED + '|stratum|' + cell_text(key)), cell_text(key))
        key = min(available, key=score)
        r = cells[key][cell_count[key]]
        chosen.append(r)
        source_count[source] += 1
        family_count[r['family']] += 1
        year_count[r['year']] += 1
        era_count[key[2]] += 1
        series_count[key[3]] += 1
        cell_count[key] += 1
    assert len(chosen) == target
    assert dict(source_count) == quotas
    assert len(family_count) >= 16 and max(family_count.values()) <= 3
    assert len(year_count) >= 12
    assert set(era_count) == set(era_capacity), 'eligible era not represented'
    assert set(series_count) == set(series_capacity), 'eligible series not represented'
    return chosen, {
        'sourceQuotas': quotas,
        'selectedBySource': dict(sorted(source_count.items())),
        'selectedByFamily': dict(sorted(family_count.items())),
        'selectedByYear': {str(y): n for y, n in sorted(year_count.items())},
        'selectedByEra': dict(sorted(era_count.items())),
        'selectedBySeries': dict(sorted(series_count.items())),
        'selectedStrata': [{'stratum': list(key), 'eligible': len(cells[key]), 'selected': n}
                           for key, n in sorted(cell_count.items()) if n],
        'distinctFamilies': len(family_count), 'distinctYears': len(year_count),
        'maxDocumentsPerFamily': max(family_count.values()),
    }

def verify() -> dict:
    read = lambda name: json.loads((HOLDOUT/name).read_text(encoding='utf-8'))
    universe = read('v5-eligible-document-universe.json')
    registry = read('v5-prior-document-exclusions.json')
    manifest = read('manifest-v5-documents-frozen.json')
    provenance = read('manifest-v5-documents-frozen.provenance.json')
    rows = universe['documents']
    for r in rows:
        assert not set(r) - NEUTRAL_FIELDS, 'non-neutral universe field'
        if r['contentFingerprint']:
            assert r['documentId'] == 'v5-doc-' + r['contentFingerprint'][:16]
        assert r['eligible'] == ('exclusionReason' not in r)
    selected, summary = select(rows)
    assert manifest['documents'] == selected
    assert manifest['selectionSummary'] == summary
    assert manifest['candidateSourceCommit'] == CANDIDATE
    assert manifest['questionSelectionStatus'] == 'not_started'
    assert manifest['seedSha256'] == SEED
    for k, v in FLAGS.items(): assert manifest[k] is v and provenance[k] is v
    holdouts = {r['contentFingerprint'] for r in registry['priorHoldoutFingerprints']}
    calibration = {r['contentFingerprint'] for r in registry['priorCalibrationFingerprints']}
    fingerprints = {r['contentFingerprint'] for r in selected}
    assert len(fingerprints) == TARGET
    assert not fingerprints & holdouts, 'priorHoldoutFingerprintOverlap'
    assert not fingerprints & calibration, 'priorPatchCalibrationDocumentOverlap'
    for r in rows:
        if r['contentFingerprint'] in holdouts | calibration: assert not r['eligible']
    for name, value in provenance['artifactFileSha256'].items():
        assert file_sha(HOLDOUT/name) == value, f'hash drift: {name}'
    assert provenance['candidateSourceCommitSha256'] == digest(CANDIDATE)
    assert provenance['priorHoldoutFingerprintOverlap'] == 0
    assert provenance['priorPatchCalibrationDocumentOverlap'] == 0
    # Determinism under an independently reversed neutral input order.
    reversed_selected, reversed_summary = select(list(reversed(rows)))
    assert reversed_selected == selected and reversed_summary == summary
    return {'status': 'PASS', 'selectedDocuments': len(selected),
            'priorHoldoutFingerprintOverlap': 0, 'priorPatchCalibrationDocumentOverlap': 0,
            'determinismWithReversedInput': True, 'selectionSummary': summary, **FLAGS}

if __name__ == '__main__':
    assert not sys.argv[1:], 'Read-only verifier takes no arguments'
    print(json.dumps(verify(), ensure_ascii=False, indent=2))
