"""Synthetic-only tests; never loads frozen inputs or chooses real V5 IDs."""
import copy
import hashlib
import json
import sys
import unittest
sys.dont_write_bytecode = True
from v5_select_questions import candidate_hash, choose, encode, validate_pool, windows


def synthetic(n=10):
    return {"documentId": "synthetic-é", "contentFingerprint": "synthetic-fingerprint", "canonicalPath": "synthetic-not-a-PDF",
            "effectivePhysicalPageCount": 3, "status": "adjudicated",
            "questions": [{"questionId": f"fake:q{i+1}", "questionNumber": i+10, "pageStart": 1, "pageEnd": 2,
                           "neutralNotes": ["língua", "e\u0301"], "section": "synthetic"} for i in range(n)]}


class SyntheticSelectionTest(unittest.TestCase):
    def test_partition_exhaustive(self):
        for n in range(3, 301):
            parts = windows(n)
            self.assertTrue(all(a < b for a,b in parts))
            self.assertEqual([i for a,b in parts for i in range(a,b)], list(range(n)))
        self.assertEqual(windows(4), [(0,1),(1,2),(2,4)])
        self.assertEqual(windows(5), [(0,1),(1,3),(3,5)])

    def test_invalid_small_pool(self):
        for n in (0, 1, 2, -1, True):
            with self.assertRaises(ValueError):
                windows(n)

    def test_exact_hash_bytes(self):
        literal = b"v5-question-selection|synthetic-seed|fake-doc|2|fake:q9"
        self.assertEqual(candidate_hash("synthetic-seed", "fake-doc", 2, "fake:q9"), hashlib.sha256(literal).hexdigest())
        self.assertNotEqual(candidate_hash("synthetic-seed", "fake-doc", 2, "fake:q9"), hashlib.sha256(literal+b"\n").hexdigest())

    def test_unicode_is_literal(self):
        s = "v5-question-selection|s|escola-é|0|fake:漢字"
        self.assertEqual(candidate_hash("s", "escola-é", 0, "fake:漢字"), hashlib.sha256(s.encode("utf-8")).hexdigest())
        self.assertNotEqual(candidate_hash("s", "é", 0, "q"), candidate_hash("s", "e\u0301", 0, "q"))

    def test_hash_priority_and_tie(self):
        d = synthetic(9)
        d["questions"][0]["questionId"] = "z"
        d["questions"][1]["questionId"] = "a"
        equal = choose(d, "synthetic", lambda *args: "0"*64)
        self.assertEqual(equal[0]["questionId"], "a")
        hashes = choose(d, "synthetic", lambda s,d,t,q: "0"*64 if q == "z" else "f"*64)
        self.assertEqual(hashes[0]["questionId"], "z")

    def test_objects_order_and_deepcopy(self):
        d = synthetic(11)
        before = copy.deepcopy(d)
        selected = choose(d, "synthetic")
        self.assertEqual([p["tertileIndex"] for p in selected], [0,1,2])
        for p in selected:
            self.assertEqual(p["question"], d["questions"][p["canonicalArrayIndex"]])
        selected[0]["question"]["neutralNotes"].append("changed")
        self.assertEqual(d, before)

    def test_reproducible_bytes_and_compact_ids(self):
        d = synthetic(26)
        self.assertEqual(encode(choose(d,"s")), encode(choose(copy.deepcopy(d),"s")))
        ids = [["doc-é", ["fake:a","fake:b","fake:c"]]]
        self.assertEqual(encode(ids, True), '[["doc-é",["fake:a","fake:b","fake:c"]]]'.encode("utf-8"))
        self.assertFalse(encode(ids, True).endswith(b"\n"))
        self.assertEqual(json.loads(encode(ids,True)),ids)

    def test_strict_document_binding_and_ranges(self):
        d = synthetic(6)
        m = {"documents": [{"documentId": d["documentId"], "contentFingerprint": d["contentFingerprint"], "canonicalPath": d["canonicalPath"]}]}
        index = {"documents": [d]}
        validate_pool(m,index,1,6)
        for field,value in [("contentFingerprint","wrong"),("documentId","wrong")]:
            bad=copy.deepcopy(m);bad["documents"][0][field]=value
            with self.assertRaises(ValueError):validate_pool(bad,index,1,6)
        bad=copy.deepcopy(index);bad["documents"][0]["questions"][0]["pageEnd"]=4
        with self.assertRaises(ValueError):validate_pool(m,bad,1,6)
        bad=copy.deepcopy(index);bad["documents"][0]["questions"][1]["questionId"]=d["questions"][0]["questionId"]
        with self.assertRaises(ValueError):validate_pool(m,bad,1,6)


if __name__ == "__main__":
    unittest.main(verbosity=2)
