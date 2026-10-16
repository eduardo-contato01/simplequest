"""Synthetic-only checks for the isolated Batch03 tool; no real GT/PDF/Auditor."""
import copy
from pathlib import Path
import tempfile
import unittest
import v5_ground_truth_batch03 as v


def fixture():
    docs = [{"documentId": f"synthetic-prior-{i}", "selectedQuestions": []} for i in range(6)]
    index_docs, questions = [], []
    for i in range(3):
        did, fingerprint = f"synthetic-batch03-{i}", f"{i + 1:064x}"
        selected = []
        for number in range(1, 4):
            frozen = {"questionId": f"{did}:q{number}", "questionNumber": number,
                      "pageStart": number, "pageEnd": number, "printedQuestionNumber": number}
            selected.append(frozen)
            questions.append({"documentId": did, "contentFingerprint": fingerprint, "questionId": frozen["questionId"],
                              "canonicalQuestionNumber": number, "printedQuestionNumber": number,
                              "pageStart": number, "pageEnd": number, "pages": [number],
                              "responseMode": "single_choice", "optionCount": 3, "optionLabels": ["α", "β", "γ"],
                              "subitems": [], "responseControls": [], "layout": "grid", "markerStyle": "parenthesized",
                              "contentKind": "mixed", "notes": "Synthetic only: ação ⋅ ½; shared context, not a real human decision",
                              "annotationOrigin": "synthetic_reviewer_declaration", "independentHumanAdjudicationClaimed": True,
                              "externalIndependenceCertification": False, "aiClassificationAssistanceDeclared": False})
        docs.append({"documentId": did, "contentFingerprint": fingerprint, "effectivePhysicalPageCount": 3, "selectedQuestions": selected})
        index_docs.append({"documentId": did, "contentFingerprint": fingerprint, "questions": copy.deepcopy(selected)})
    return questions, copy.deepcopy(questions), {"documents": docs}, {"documents": index_docs}


class Validation(unittest.TestCase):
    def test_01_lossless(self):
        data = fixture()
        before = copy.deepcopy(data)
        self.assertEqual(v.validate_questions(*data)["humanDecisionDifferences"], 0)
        self.assertEqual(data, before)

    def test_02_human_fields_immutable(self):
        for field, value in (("notes", "changed"), ("optionLabels", ["A", "B", "C"]), ("markerStyle", "textual")):
            data = fixture()
            data[0][0][field] = value
            with self.assertRaisesRegex(ValueError, "human decision difference"):
                v.validate_questions(*data)

    def test_03_order_duplicates(self):
        for duplicate in (False, True):
            data = fixture()
            if duplicate:
                data[0][1] = copy.deepcopy(data[0][0])
            else:
                data[0].reverse()
            with self.assertRaises(ValueError):
                v.validate_questions(*data)

    def test_04_fingerprint_document(self):
        for key, value in (("documentId", "wrong"), ("contentFingerprint", "0" * 64)):
            data = fixture()
            for q in (data[0][0], data[1][0]):
                q[key] = value
            with self.assertRaises(ValueError):
                v.validate_questions(*data)

    def test_05_boundaries_and_selected_object(self):
        data = fixture()
        for q in (data[0][0], data[1][0]):
            q["pageEnd"] = 4
        with self.assertRaises(ValueError):
            v.validate_questions(*data)
        data = fixture()
        data[2]["documents"][6]["selectedQuestions"][0]["unapproved"] = True
        with self.assertRaisesRegex(ValueError, "selected object"):
            v.validate_questions(*data)

    def test_06_printed_number(self):
        data = fixture()
        data[2]["documents"][6]["selectedQuestions"][0]["printedQuestionNumber"] = 11
        data[3]["documents"][0]["questions"][0]["printedQuestionNumber"] = 11
        for q in (data[0][0], data[1][0]):
            q["printedQuestionNumber"] = 11
        v.validate_questions(*data)
        data[0][0]["printedQuestionNumber"] = data[1][0]["printedQuestionNumber"] = 1
        with self.assertRaisesRegex(ValueError, "frozen printed number"):
            v.validate_questions(*data)

    def test_07_types_enums(self):
        for key, value in (("optionCount", True), ("optionCount", []), ("optionLabels", 0), ("markerStyle", "typo")):
            data = fixture()
            for q in (data[0][0], data[1][0]):
                q[key] = value
            with self.assertRaises(ValueError):
                v.validate_questions(*data)

    def test_08_unknown_and_legacy_numeric_not_normalized(self):
        data = fixture()
        for q in (data[0][0], data[1][0]):
            q.update(responseMode="unknown", optionCount=None, optionLabels=None, notes="Synthetic insufficient evidence")
        self.assertEqual(v.validate_questions(*data)["unknownClassificationQuestions"], 1)
        data[0][0]["responseMode"] = data[1][0]["responseMode"] = "numeric"
        v.validate_questions(*data)
        self.assertEqual(data[0][0]["responseMode"], "numeric")

    def test_09_controls_unicode(self):
        data = fixture()
        for q in (data[0][0], data[1][0]):
            q["responseControls"] = [{"label": "□", "role": "synthetic control", "pages": [1], "notes": "α ⋅ ½"}]
        v.validate_questions(*data)
        data[0][0]["responseControls"][0]["pages"] = data[1][0]["responseControls"][0]["pages"] = [2]
        with self.assertRaisesRegex(ValueError, "structured pages"):
            v.validate_questions(*data)

    def test_10_no_external_certification(self):
        for key, value in (("externalIndependenceCertification", True), ("aiClassificationAssistanceDeclared", True), ("independentHumanAdjudicationClaimed", False)):
            data = fixture()
            for q in (data[0][0], data[1][0]):
                q[key] = value
            with self.assertRaises(ValueError):
                v.validate_questions(*data)

    def test_11_duplicate_json_and_evidence_tampering(self):
        with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
            v.strict_json(b'{"notes":"one","notes":"two"}')
        raw = "ação α".encode("utf-8")
        item = {"path": "synthetic.json", "rawUtf8": raw.decode(), "sizeBytes": len(raw), "sha256": v.sha(raw)}
        self.assertEqual(v.unpack(item), raw)
        item["rawUtf8"] += "!"
        with self.assertRaises(ValueError):
            v.unpack(item)

    def test_12_atomic_deterministic_no_overwrite(self):
        raw = v.encoded({"notes": "ação α ⋅ ½", "unknown": None})
        self.assertFalse(raw.startswith(b"\xef\xbb\xbf"))
        self.assertNotIn(b"\r\n", raw)
        self.assertEqual(raw, v.encoded({"notes": "ação α ⋅ ½", "unknown": None}))
        with tempfile.TemporaryDirectory(prefix="simplequest-batch03-synthetic-") as directory:
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
