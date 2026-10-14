"""Synthetic-only validator tests; no PDFs, original GT or Auditor accessed."""
import copy
from pathlib import Path
import tempfile
import unittest

import v5_ground_truth_batch01 as v


def fixture():
    docs, index_docs, questions = [], [], []
    for di in range(3):
        did, fp = f"synthetic-doc-{di}", f"{di + 1:064x}"
        selected = []
        for qi in range(3):
            n = qi + 1
            frozen = {"questionId": f"{did}:q{n}", "questionNumber": n, "pageStart": n, "pageEnd": n}
            selected.append(frozen)
            independent = bool(di or qi)
            questions.append({"documentId": did, "contentFingerprint": fp, "questionId": frozen["questionId"],
                              "canonicalQuestionNumber": n, "pageStart": n, "pageEnd": n, "pages": [n],
                              "responseMode": "single_choice", "optionCount": 3,
                              "optionLabels": ["α", "β", "γ"], "subitems": [], "responseControls": [],
                              "layout": "vertical", "markerStyle": "textual", "contentKind": "mixed",
                              "notes": "Synthetic fixture: ação ⋅ α ½; not real human evidence",
                              "annotationOrigin": "human_reviewer_declared_without_ai" if independent else "ai_assisted_human_verified",
                              "independentHumanAdjudicationClaimed": independent})
        docs.append({"documentId": did, "contentFingerprint": fp, "effectivePhysicalPageCount": 3, "selectedQuestions": selected})
        index_docs.append({"documentId": did, "contentFingerprint": fp, "questions": copy.deepcopy(selected)})
    approved = {"questions": copy.deepcopy(questions)}
    gt = {"protocolVersion": "holdout-v5", "annotationVersion": 1, "documentsCount": 3, "questionsCount": 9,
          "documents": [{"documentId": d["documentId"]} for d in docs], "questions": questions,
          "documentFingerprints": {d["documentId"]: d["contentFingerprint"] for d in docs},
          "wholeBatchStrictlyIndependent": False, "auditorExecuted": False, "metricsSeen": False}
    return gt, approved, {"documents": docs}, {"documents": index_docs}


class ValidationTest(unittest.TestCase):
    def test_complete_synthetic_binding_lossless(self):
        f = fixture()
        before = copy.deepcopy(f)
        gates = v.validate_questions(*f)
        self.assertEqual(gates["humanDecisionDifferences"], 0)
        self.assertEqual(gates["strictlyIndependentHumanQuestions"], 8)
        self.assertEqual(f, before)

    def test_changed_human_value_rejected(self):
        f = fixture()
        f[0]["questions"][1]["notes"] += " changed"
        with self.assertRaisesRegex(ValueError, "human decision difference"):
            v.validate_questions(*f)

    def test_duplicate_or_reordered_question_rejected(self):
        f = fixture()
        f[0]["questions"][2] = copy.deepcopy(f[0]["questions"][1])
        with self.assertRaises(ValueError):
            v.validate_questions(*f)
        f = fixture()
        f[0]["questions"].reverse()
        with self.assertRaises(ValueError):
            v.validate_questions(*f)

    def test_cross_document_and_fingerprint_rejected(self):
        for field, bad in (("documentId", "wrong-document"), ("contentFingerprint", "0" * 64)):
            f = fixture()
            f[0]["questions"][1][field] = bad
            f[1]["questions"][1][field] = bad
            with self.assertRaises(ValueError):
                v.validate_questions(*f)

    def test_page_and_selected_object_changes_rejected(self):
        f = fixture()
        for q in (f[0]["questions"][2], f[1]["questions"][2]):
            q["pageEnd"] = 4
            q["pages"] = [3, 4]
        with self.assertRaises(ValueError):
            v.validate_questions(*f)
        f = fixture()
        f[2]["documents"][0]["selectedQuestions"][0]["neutralExtra"] = "changed"
        with self.assertRaisesRegex(ValueError, "selected object"):
            v.validate_questions(*f)

    def test_invalid_count_bool_enum_and_labels_rejected(self):
        for field, bad in (("optionCount", True), ("optionCount", []), ("optionLabels", 0),
                           ("markerStyle", "circled_filles"), ("responseMode", "made_up")):
            f = fixture()
            for q in (f[0]["questions"][1], f[1]["questions"][1]):
                q[field] = bad
            with self.assertRaises(ValueError):
                v.validate_questions(*f)

    def test_structured_symbols_and_nulls_preserved(self):
        f = fixture()
        for q in (f[0]["questions"][1], f[1]["questions"][1]):
            q["optionCount"] = None
            q["optionLabels"] = None
            q["notes"] = "Synthetic explicitly uncertain count, not a real adjudication"
            q["subitems"] = [{"label": "⋅", "role": "internal synthetic content",
                             "pages": [2], "notes": "fração ½"} for _ in range(3)]
        v.validate_questions(*f)
        self.assertEqual(len(f[0]["questions"][1]["subitems"]), 3)
        self.assertIsNone(f[0]["questions"][1]["optionCount"])

    def test_false_independence_claim_and_execution_flags_rejected(self):
        for field in ("wholeBatchStrictlyIndependent", "auditorExecuted", "metricsSeen"):
            f = fixture()
            f[0][field] = True
            with self.assertRaises(ValueError):
                v.validate_questions(*f)

    def test_no_duplicate_json_or_tampered_embedded_evidence(self):
        with self.assertRaises(ValueError):
            v.strict_json(b'{"notes":"first","notes":"second"}')
        record = {"path": "synthetic.json", "rawUtf8": "ação", "sizeBytes": 0, "sha256": "0" * 64}
        with self.assertRaises(ValueError):
            v.unpack(record)

    def test_atomic_idempotence_deterministic_utf8(self):
        data = v.encoded({"symbols": ["⋅", "⋅", "⋅"], "null": None, "notes": "ação"})
        self.assertEqual(data, v.encoded({"symbols": ["⋅", "⋅", "⋅"], "null": None, "notes": "ação"}))
        self.assertFalse(data.startswith(b"\xef\xbb\xbf"))
        with tempfile.TemporaryDirectory(prefix="simplequest-v5-gt-synthetic-") as directory:
            p = Path(directory) / "data.json"
            v.atomic_new(p, data)
            mtime = p.stat().st_mtime_ns
            v.atomic_new(p, data)
            self.assertEqual(mtime, p.stat().st_mtime_ns)
            with self.assertRaises(ValueError):
                v.atomic_new(p, b"different")
            self.assertEqual(p.read_bytes(), data)


if __name__ == "__main__":
    unittest.main(verbosity=2)
