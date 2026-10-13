"""Synthetic-only tests. No real corpus, GT labels, PDFs or Auditor imported."""
import copy
import json
from pathlib import Path
import tempfile
import unittest

import v5_prepare_gt_review_packages as p


def fixture(root):
    docs, canon = [], []
    for i in range(48):
        content = f"synthetic binary source {i}; not a real PDF".encode()
        source = root / "synthetic-sources" / f"{i}.pdf"
        p.atomic_new(source, content)
        did, fp = f"synthetic-{i}", p.digest(content)
        qs = [{"questionId": f"{did}:q{n}", "questionNumber": n, "pageStart": 2,
               "pageEnd": 3 if n == 2 else 2, "printedQuestionNumber": n,
               "section": "synthetic", "neutralExtra": {"unicode": "ação"}}
              for n in range(1, (44 if i < 47 else 68) + 1)]
        c = {"documentId": did, "contentFingerprint": fp, "globalOrder": 48 - i,
             "effectivePhysicalPageCount": 15 if i < 47 else 36, "neutralNotes": ["synthetic note"],
             "questions": qs}
        canon.append(c)
        docs.append({"documentId": did, "contentFingerprint": fp, "canonicalPath": str(source),
                     "sizeBytes": len(content), "sourceFrozenPageCount": c["effectivePhysicalPageCount"],
                     "effectivePhysicalPageCount": c["effectivePhysicalPageCount"],
                     "canonicalDocumentMetadata": {k: copy.deepcopy(v) for k, v in c.items() if k != "questions"},
                     "selectedQuestions": copy.deepcopy(qs[:3])})
    ordered = [[d["documentId"], [q["questionId"] for q in d["selectedQuestions"]]] for d in docs]
    ids_hash = p.digest(json.dumps(ordered, ensure_ascii=False, separators=(",", ":")).encode())
    manifest = {"protocolVersion": "holdout-v5", "documentsCount": 48,
                "selectedQuestionsCount": 144, "documents": docs}
    provenance = {"orderedSelectedIds": ordered, "orderedSelectedIdsSha256": ids_hash,
                  "officialInvocationCount": 1, "officialRetries": 0}
    index = {"protocolVersion": "holdout-v5", "totalPhysicalPages": 741,
             "canonicalQuestions": 2136, "documents": list(reversed(canon))}
    return manifest, provenance, index, ids_hash


class PackagesTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="simplequest-v5-gt-synthetic-")
        self.root = Path(self.tmp.name)
        self.m, self.prov, self.index, self.ids = fixture(self.root)
        self.docs = self.m["documents"]

    def tearDown(self):
        self.tmp.cleanup()

    def test_exact_bindings_and_nonmatching_index_order(self):
        before = copy.deepcopy(self.m)
        self.assertEqual(p.validate_inputs(self.m, self.prov, self.index, self.ids), self.docs)
        self.assertEqual(before, self.m)

    def test_order_and_duplicate_rejected(self):
        self.docs.reverse()
        with self.assertRaisesRegex(ValueError, "ordered IDs"):
            p.validate_inputs(self.m, self.prov, self.index, self.ids)
        self.docs.reverse()
        self.docs[1]["contentFingerprint"] = self.docs[0]["contentFingerprint"]
        with self.assertRaises(ValueError):
            p.validate_inputs(self.m, self.prov, self.index, self.ids)

    def test_changed_object_and_invalid_range_rejected(self):
        self.docs[0]["selectedQuestions"][0]["neutralExtra"]["unicode"] = "different"
        with self.assertRaisesRegex(ValueError, "exact selected"):
            p.validate_inputs(self.m, self.prov, self.index, self.ids)
        q = self.docs[0]["selectedQuestions"][0]
        q["neutralExtra"]["unicode"] = "ação"
        q["pageEnd"] = 99
        next(d for d in self.index["documents"] if d["documentId"] == self.docs[0]["documentId"])["questions"][0]["pageEnd"] = 99
        with self.assertRaisesRegex(ValueError, "pages"):
            p.validate_inputs(self.m, self.prov, self.index, self.ids)

    def test_blank_fields_and_neutral_context(self):
        data = p.payloads(self.root, 1, self.docs[:3])
        template = json.loads(data["ANNOTATION_TEMPLATE.json"])
        self.assertFalse(template["humanAdjudicated"])
        self.assertEqual(len(template["questions"]), 9)
        for q in template["questions"]:
            self.assertTrue(all(q[f] is None for f in p.FIELDS))
        context = json.loads(data["review-context.json"])
        self.assertNotIn("responseMode", str(context))
        self.assertEqual(context["documents"][0]["selectedQuestions"][1]["pages"], [2, 3])
        self.assertEqual(p.payloads(self.root, 1, self.docs[:3]), data)

    def test_all16_disjoint_and_resume_without_rewrites(self):
        batches = [p.prepare_batch(self.root, b, self.docs[(b-1)*3:b*3]) for b in range(1, 17)]
        self.assertEqual(len({d for b in batches for d in b["documentIds"]}), 48)
        self.assertEqual(len({q for b in batches for q in b["questionIds"]}), 144)
        before = {f: f.stat().st_mtime_ns for f in (self.root / p.OUT).rglob("*") if f.is_file()}
        for b in range(1, 17):
            self.assertEqual(p.prepare_batch(self.root, b, self.docs[(b-1)*3:b*3]), batches[b-1])
        self.assertTrue(all(f.stat().st_mtime_ns == t for f, t in before.items()))

    def test_partial_resume_and_atomic_pending_recovery(self):
        doc = self.docs[0]
        base = p.batch_dir(self.root, 1)
        target = base / p.pdf_name(1, doc)
        provenance = {"documentId": doc["documentId"], **p.copy_pdf(self.root, doc, target)}
        p.atomic_progress(self.root / p.PROGRESS / "batch-01-files.json",
                          {"batch": "01", "files": [p.entry(self.root, target)], "pdfSources": [provenance]})
        mtime = target.stat().st_mtime_ns
        p.atomic_new(base / "review-context.json.pending", b"incomplete generated temporary file")
        p.prepare_batch(self.root, 1, self.docs[:3])
        self.assertEqual(target.stat().st_mtime_ns, mtime)
        p.verify_batch(self.root, 1, self.docs[:3])

    def test_bad_source_does_not_hide_drift_with_fallback(self):
        source = Path(self.docs[0]["canonicalPath"])
        fallback = self.root / p.OUT / "v5-tier-b-review/copies" / f"{self.docs[0]['documentId']}.pdf"
        p.atomic_new(fallback, source.read_bytes())
        # Modify only this synthetic fixture; no user source is ever touched.
        source.write_bytes(b"synthetic drift")
        with self.assertRaisesRegex(ValueError, "original fingerprint"):
            p.source_for(self.root, self.docs[0])

    def test_missing_source_verified_fallback_and_missing_stop(self):
        doc = self.docs[0]
        source = Path(doc["canonicalPath"])
        fallback = self.root / p.OUT / "v5-tier-b-review/copies" / f"{doc['documentId']}.pdf"
        p.atomic_new(fallback, source.read_bytes())
        doc["canonicalPath"] = str(self.root / "absent-original.pdf")
        found, prov = p.source_for(self.root, doc)
        self.assertEqual(found, fallback)
        self.assertEqual(prov["mode"], "preexisting_hash_verified_copy")
        self.docs[1]["canonicalPath"] = str(self.root / "absent-mandatory.pdf")
        with self.assertRaisesRegex(ValueError, "mandatory PDF unavailable"):
            p.source_for(self.root, self.docs[1])

    def test_completed_tampering_stops_not_overwrites(self):
        p.prepare_batch(self.root, 1, self.docs[:3])
        target = p.batch_dir(self.root, 1) / "ANNOTATION_TEMPLATE.json"
        target.write_bytes(b"synthetic tampering")
        with self.assertRaises(ValueError):
            p.prepare_batch(self.root, 1, self.docs[:3])
        self.assertEqual(target.read_bytes(), b"synthetic tampering")

    def test_utf8_no_bom_and_existing_mismatch_stop(self):
        data = p.encoded({"text": "ação"})
        self.assertNotIn(b"\xef\xbb\xbf", data)
        self.assertTrue(data.endswith(b"\n"))
        target = self.root / "atomic.json"
        p.atomic_new(target, data)
        with self.assertRaises(ValueError):
            p.atomic_new(target, b"different")
        self.assertEqual(target.read_bytes(), data)


if __name__ == "__main__":
    unittest.main(verbosity=2)
