"""Synthetic-only checks. No real PDFs, human GT, or Auditor execution."""
import copy
from pathlib import Path
import tempfile
import unittest
import v5_ground_truth_batch02 as v

def fixture():
    documents = [{"documentId": f"synthetic-prior-{i}", "selectedQuestions": []} for i in range(3)]
    index_docs, questions = [], []
    for i in range(3):
        document_id, fingerprint = f"synthetic-next-{i}", f"{i + 1:064x}"
        selected = []
        for number in range(1, 4):
            frozen = {"questionId": f"{document_id}:q{number}", "questionNumber": number,
                      "pageStart": number, "pageEnd": number, "printedQuestionNumber": number}
            selected.append(frozen)
            questions.append({"documentId": document_id, "contentFingerprint": fingerprint,
                              "questionId": frozen["questionId"], "canonicalQuestionNumber": number,
                              "printedQuestionNumber": number, "pageStart": number, "pageEnd": number,
                              "pages": [number], "responseMode": "single_choice", "optionCount": 3,
                              "optionLabels": ["α", "β", "γ"], "subitems": [], "responseControls": [],
                              "layout": "grid", "markerStyle": "parenthesized", "contentKind": "mixed",
                              "notes": "Synthetic only: ação ⋅ ½; tentative context, not real human evidence",
                              "annotationOrigin": "synthetic_reviewer_declaration",
                              "independentHumanAdjudicationClaimed": True,
                              "externalIndependenceCertification": False, "aiClassificationAssistanceDeclared": False})
        documents.append({"documentId": document_id, "contentFingerprint": fingerprint,
                          "effectivePhysicalPageCount": 3, "selectedQuestions": selected})
        index_docs.append({"documentId": document_id, "contentFingerprint": fingerprint, "questions": copy.deepcopy(selected)})
    gt = {"protocolVersion": "holdout-v5", "annotationVersion": 1, "documentsCount": 3, "questionsCount": 9,
          "documents": [{"documentId": d["documentId"]} for d in documents[3:]],
          "documentFingerprints": {d["documentId"]: d["contentFingerprint"] for d in documents[3:]},
          "questions": questions, "externalIndependenceCertified": False,
          "auditorExecuted": False, "metricsSeen": False, "ocrExecuted": False, "merge": False}
    return gt, {"questions": copy.deepcopy(questions)}, {"documents": documents}, {"documents": index_docs}

class Validation(unittest.TestCase):
    def test_01_lossless_binding(self):
        data = fixture()
        original = copy.deepcopy(data)
        result = v.validate_questions(*data)
        self.assertEqual(result["batch02Questions"], 9)
        self.assertEqual(result["humanDecisionDifferences"], 0)
        self.assertEqual(data, original)

    def test_02_human_change(self):
        data = fixture()
        data[0]["questions"][0]["notes"] += " altered"
        with self.assertRaisesRegex(ValueError, "human decision difference"):
            v.validate_questions(*data)

    def test_03_order_duplicate(self):
        for duplicate in (False, True):
            data = fixture()
            if duplicate:
                data[0]["questions"][1] = copy.deepcopy(data[0]["questions"][0])
            else:
                data[0]["questions"].reverse()
            with self.assertRaises(ValueError):
                v.validate_questions(*data)

    def test_04_document_fingerprint(self):
        for key, wrong in (("documentId", "wrong"), ("contentFingerprint", "0" * 64)):
            data = fixture()
            for q in (data[0]["questions"][0], data[1]["questions"][0]):
                q[key] = wrong
            with self.assertRaises(ValueError):
                v.validate_questions(*data)

    def test_05_pages_selection(self):
        data = fixture()
        for q in (data[0]["questions"][0], data[1]["questions"][0]):
            q["pageEnd"] = 4
        with self.assertRaises(ValueError):
            v.validate_questions(*data)
        data = fixture()
        data[2]["documents"][3]["selectedQuestions"][0]["unapproved"] = True
        with self.assertRaisesRegex(ValueError, "selected object"):
            v.validate_questions(*data)

    def test_06_printed_distinct_legacy(self):
        data = fixture()
        data[2]["documents"][3]["selectedQuestions"][0]["printedQuestionNumber"] = 11
        data[3]["documents"][0]["questions"][0]["printedQuestionNumber"] = 11
        for q in (data[0]["questions"][0], data[1]["questions"][0]):
            q["printedQuestionNumber"] = 11
        v.validate_questions(*data)
        for q in (data[0]["questions"][0], data[1]["questions"][0]):
            q["printedQuestionNumber"] = 1
        with self.assertRaisesRegex(ValueError, "frozen printed number"):
            v.validate_questions(*data)

    def test_07_count_types_enums(self):
        for field, invalid in (("optionCount", True), ("optionCount", []), ("optionLabels", 0),
                               ("markerStyle", "typo"), ("responseMode", "unregistered")):
            data = fixture()
            for q in (data[0]["questions"][0], data[1]["questions"][0]):
                q[field] = invalid
            with self.assertRaises(ValueError):
                v.validate_questions(*data)

    def test_08_unknown_not_forced_zero(self):
        data = fixture()
        for q in (data[0]["questions"][0], data[1]["questions"][0]):
            q["responseMode"] = "unknown"
            q["optionCount"] = None
            q["optionLabels"] = None
            q["notes"] = "Synthetic insufficient evidence; not real adjudication"
        self.assertEqual(v.validate_questions(*data)["unknownClassificationQuestions"], 1)

    def test_09_structured_controls_and_unicode(self):
        data = fixture()
        for q in (data[0]["questions"][0], data[1]["questions"][0]):
            q["responseControls"] = [{"label": "□", "role": "synthetic control", "pages": [1], "notes": "α ⋅ ½"}]
        v.validate_questions(*data)
        for q in (data[0]["questions"][0], data[1]["questions"][0]):
            q["responseControls"][0]["pages"] = [2]
        with self.assertRaisesRegex(ValueError, "structured element pages"):
            v.validate_questions(*data)

    def test_10_no_certification_execution(self):
        for field in ("externalIndependenceCertified", "auditorExecuted", "metricsSeen", "ocrExecuted", "merge"):
            data = fixture()
            data[0][field] = True
            with self.assertRaises(ValueError):
                v.validate_questions(*data)

    def test_11_strict_evidence(self):
        with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
            v.strict_json(b'{"notes":"first","notes":"second"}')
        raw = "ação α".encode("utf-8")
        record = {"path": "synthetic.json", "rawUtf8": raw.decode(), "sizeBytes": len(raw), "sha256": v.sha(raw)}
        self.assertEqual(v.unpack(record), raw)
        record["sizeBytes"] += 1
        with self.assertRaises(ValueError):
            v.unpack(record)

    def test_12_atomic_deterministic_no_overwrite(self):
        raw = v.encoded({"notes": "ação α ⋅ ½", "unknown": None})
        self.assertFalse(raw.startswith(b"\xef\xbb\xbf"))
        self.assertEqual(raw, v.encoded({"notes": "ação α ⋅ ½", "unknown": None}))
        with tempfile.TemporaryDirectory(prefix="simplequest-batch02-synthetic-") as directory:
            target = Path(directory) / "data.json"
            v.atomic_new(target, raw)
            stamp = target.stat().st_mtime_ns
            v.atomic_new(target, raw)
            self.assertEqual(stamp, target.stat().st_mtime_ns)
            with self.assertRaises(ValueError):
                v.atomic_new(target, b"changed")
            self.assertEqual(target.read_bytes(), raw)

if __name__ == "__main__":
    unittest.main(verbosity=2)
