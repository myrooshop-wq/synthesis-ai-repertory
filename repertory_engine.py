import sqlite3
import re
from typing import List, Dict, Any, Optional

ACUTE_REMEDIES = {
    "acon", "bell", "bry", "ars", "nux-v", "rhus-t", "gels", "chin", "verat", 
    "cham", "coloc", "apis", "ip", "bapt", "arn", "canth", "camph", "ant-t", 
    "cupr", "merc", "hep", "phos", "dros", "eup-per", "all-c", "puls", "pod"
}

class RepertoryServer:
    def __init__(self, db_path: str = "synthesis.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._ensure_indexes()

    def _ensure_indexes(self):
        """Create helpful search indexes if missing."""
        c = self.conn.cursor()
        for stmt in [
            "CREATE INDEX IF NOT EXISTS idx_syntree_path ON syntree(path);",
            "CREATE INDEX IF NOT EXISTS idx_syntree_search_path ON syntree(search_path);",
            "CREATE INDEX IF NOT EXISTS idx_symp_rem_sid ON symptom_remedies(symptom_id);",
            "CREATE INDEX IF NOT EXISTS idx_rem_auth_sid ON remedy_authors(symptom_id);"
        ]:
            try:
                c.execute(stmt)
            except Exception:
                pass
        self.conn.commit()

    def autocomplete_rubrics(self, query: str, limit: int = 20, require_remedies: bool = False) -> List[Dict[str, Any]]:
        """
        Smart Clinical Rubric Discovery:
        1. Token-based path search across syntree (any word in any position, e.g. 'migraine', 'cough morning', 'head right').
        2. Automatic Cross-Reference Aliasing: When a search term lands on a zero-remedy clinical pointer rubric
           (e.g. 'HEAD - MIGRAINE' which points to 'HEAD - PAIN'), automatically resolves the primary rubric
           or presents it with its cross-referenced target rubric and target remedy count.
        3. Ranks by remedy count (well-proved polycrests & established remedies first).
        """
        clean_q = query.strip()
        raw_tokens = [t.strip().upper() for t in clean_q.split() if t.strip()]
        if not raw_tokens:
            return []

        c = self.conn.cursor()
        
        where_clauses = []
        params = []
        for t in raw_tokens:
            clause = "(s.search_path LIKE ? OR s.path LIKE ?)"
            params.extend([f"%{t}%", f"%{t}%"])
            where_clauses.append(clause)

        min_rems = 3 if require_remedies else 0

        # Query matches
        sql = f"""
        SELECT 
            s.id, 
            s.path, 
            s.level, 
            s.chapter_id, 
            COUNT(sr.remedy_abbreviation) as remedy_count,
            cr.symptom_id as xref_target_id,
            cr.text as xref_target_path
        FROM syntree s
        LEFT JOIN symptom_remedies sr ON s.id = sr.symptom_id
        LEFT JOIN cross_references cr ON s.id = cr.id
        WHERE {' AND '.join(where_clauses)}
        GROUP BY s.id
        HAVING remedy_count >= ? OR cr.symptom_id IS NOT NULL
        ORDER BY 
           CASE WHEN s.level <= 3 THEN 0 ELSE 1 END ASC,
           remedy_count DESC,
           LENGTH(s.path) ASC
        LIMIT {limit * 2}
        """
        c.execute(sql, params + [min_rems])
        rows = c.fetchall()

        # If zero-remedy rubric has a cross reference (like HEAD - MIGRAINE -> HEAD - PAIN),
        # also fetch the target rubric's remedy count so the doctor gets actionable results!
        results = []
        seen_ids = set()

        for r in rows:
            sid = r['id']
            if sid in seen_ids:
                continue
            seen_ids.add(sid)

            rem_count = r['remedy_count']
            xref_target_id = r['xref_target_id']
            xref_target_path = r['xref_target_path']

            # If this rubric has 0 remedies but points to a master rubric (e.g. HEAD - MIGRAINE -> HEAD - PAIN)
            if rem_count == 0 and xref_target_id:
                c.execute("SELECT COUNT(remedy_abbreviation) FROM symptom_remedies WHERE symptom_id = ?", (xref_target_id,))
                target_cnt = c.fetchone()[0]
                results.append({
                    "id": xref_target_id,
                    "path": f"{r['path']} ➔ (See: {xref_target_path})",
                    "original_path": r['path'],
                    "level": r['level'],
                    "remedy_count": target_cnt,
                    "is_xref_alias": True
                })
            else:
                results.append({
                    "id": sid,
                    "path": r['path'],
                    "level": r['level'],
                    "remedy_count": rem_count,
                    "is_xref_alias": False
                })

        # Re-sort to put high-remedy relevant rubrics first
        results.sort(key=lambda x: (
            0 if x['level'] <= 3 else 1,
            -x['remedy_count'],
            len(x['path'])
        ))

        return results[:limit]

    def semantic_rubric_search(self, query: str, limit: int = 15) -> List[Dict[str, Any]]:
        """
        Hybrid Semantic Search for Synthesis Repertory:
        Combines synonym concept expansion, FTS5 BM25 ranking, and Kentian hierarchy weighting.
        Allows doctors to type conversational or clinical queries like:
          - 'severe migraine right side'
          - 'loose motion with stomach pain'
          - 'fear of darkness and ghosts'
          - 'burning acidity after eating'
        and get the closest matched Kentian rubrics ranked by clinical relevance.
        """
        q_lower = query.lower().strip()
        if not q_lower:
            return []

        STOPWORDS = {"and", "or", "the", "a", "an", "in", "on", "at", "to", "for", "of", "with", "from", "by", "is", "after", "before", "during"}
        
        SYNONYMS = {
            "headache": ["HEAD", "PAIN"],
            "migraine": ["HEAD", "PAIN", "HEMICRANIA"],
            "hemicrania": ["HEAD", "PAIN"],
            "vomiting": ["STOMACH", "VOMITING"],
            "vomit": ["STOMACH", "VOMITING"],
            "nausea": ["STOMACH", "NAUSEA"],
            "diarrhea": ["RECTUM", "DIARRHEA"],
            "loose": ["RECTUM", "DIARRHEA"],
            "motion": ["RECTUM", "DIARRHEA"],
            "fever": ["FEVER"],
            "chill": ["CHILL"],
            "cold": ["NOSE", "CORYZA"],
            "coryza": ["NOSE", "CORYZA"],
            "cough": ["COUGH"],
            "anorexia": ["STOMACH", "APPETITE", "WANTING"],
            "appetite": ["STOMACH", "APPETITE"],
            "hunger": ["STOMACH", "APPETITE"],
            "weakness": ["GENERALS", "WEAKNESS"],
            "fatigue": ["GENERALS", "WEAKNESS"],
            "debility": ["GENERALS", "DEBILITY"],
            "tired": ["GENERALS", "WEAKNESS", "TIRED"],
            "thirst": ["STOMACH", "THIRST"],
            "thirsty": ["STOMACH", "THIRST"],
            "sleeplessness": ["SLEEP", "SLEEPLESSNESS"],
            "insomnia": ["SLEEP", "SLEEPLESSNESS"],
            "sleepless": ["SLEEP", "SLEEPLESSNESS"],
            "sleep": ["SLEEP"],
            "restlessness": ["MIND", "RESTLESSNESS"],
            "restless": ["MIND", "RESTLESSNESS"],
            "anxiety": ["MIND", "ANXIETY"],
            "anxious": ["MIND", "ANXIETY"],
            "fear": ["MIND", "FEAR"],
            "afraid": ["MIND", "FEAR"],
            "dark": ["DARK"],
            "darkness": ["DARK"],
            "death": ["DEATH"],
            "anger": ["MIND", "ANGER"],
            "angry": ["MIND", "ANGER"],
            "irritability": ["MIND", "IRRITABILITY"],
            "irritable": ["MIND", "IRRITABILITY"],
            "vertigo": ["VERTIGO"],
            "dizziness": ["VERTIGO"],
            "dizzy": ["VERTIGO"],
            "burning": ["BURNING"],
            "cramp": ["CRAMPING", "PAIN"],
            "cramps": ["CRAMPING", "PAIN"],
            "cramping": ["CRAMPING", "PAIN"],
            "acidity": ["STOMACH", "ERUCTATIONS", "ACIDITY"],
            "acid": ["STOMACH", "ERUCTATIONS", "ACIDITY"],
            "gas": ["ABDOMEN", "DISTENSION", "FLATULENCE"],
            "flatulence": ["ABDOMEN", "FLATULENCE"],
            "bloating": ["ABDOMEN", "DISTENSION"],
            "constipation": ["RECTUM", "CONSTIPATION"],
            "piles": ["RECTUM", "HEMORRHOIDS"],
            "hemorrhoids": ["RECTUM", "HEMORRHOIDS"],
            "itching": ["SKIN", "ITCHING"],
            "itch": ["SKIN", "ITCHING"],
            "eruptions": ["SKIN", "ERUPTIONS"],
            "sweat": ["PERSPIRATION"],
            "perspiration": ["PERSPIRATION"],
            "backache": ["BACK", "PAIN"],
            "joint": ["EXTREMITIES", "PAIN", "JOINTS"],
            "throat": ["THROAT", "PAIN"],
            "chest": ["CHEST"]
        }

        # Extract tokens and expand synonyms
        raw_words = [w for w in re.split(r'[^a-zA-Z0-9]+', q_lower) if w and w not in STOPWORDS]
        if not raw_words:
            return []

        concept_words = set(raw_words)
        for w in raw_words:
            if w in SYNONYMS:
                concept_words.update(SYNONYMS[w])
        for phrase, syns in SYNONYMS.items():
            if phrase in q_lower:
                concept_words.update(syns)

        PHRASE_EXPANSIONS = {
            "loose motion": ["RECTUM - DIARRHEA", "STOOL - THIN", "STOOL - WATERY"],
            "loose motions": ["RECTUM - DIARRHEA", "STOOL - THIN", "STOOL - WATERY"],
            "watery stool": ["RECTUM - DIARRHEA", "STOOL - WATERY"],
            "stomach ache": ["ABDOMEN - PAIN", "STOMACH - PAIN"],
            "belly ache": ["ABDOMEN - PAIN"],
            "runny nose": ["NOSE - CORYZA", "NOSE - DISCHARGE"],
            "body ache": ["GENERALS - PAIN", "EXTREMITIES - PAIN"],
            "limb pain": ["EXTREMITIES - PAIN"],
            "loss of appetite": ["STOMACH - APPETITE - wanting"],
            "no appetite": ["STOMACH - APPETITE - wanting"],
            "burning stomach": ["STOMACH - PAIN - burning"],
            "burning in stomach": ["STOMACH - PAIN - burning"],
            "dry mouth": ["MOUTH - DRYNESS"],
            "restless night": ["MIND - RESTLESSNESS - night", "SLEEP - RESTLESS - night"],
            "restlessness at night": ["MIND - RESTLESSNESS - night"],
            "night sweat": ["PERSPIRATION - NIGHT"],
            "sweating at night": ["PERSPIRATION - NIGHT"],
            "high fever": ["FEVER - INTENSE heat", "FEVER - CONTINUED fever"],
            "chill with fever": ["FEVER - CHILL; with", "CHILL - FEVER; with"],
            "migraine": ["HEAD - PAIN", "HEAD - PAIN - Sides - one side"],
            "headache": ["HEAD - PAIN"],
            "vomiting": ["STOMACH - VOMITING"],
            "nausea": ["STOMACH - NAUSEA"],
            "acidity": ["STOMACH - ERUCTATIONS; TYPE OF - sour", "STOMACH - ACIDITY"],
            "gas in stomach": ["ABDOMEN - DISTENSION", "ABDOMEN - FLATULENCE"],
            "bloating": ["ABDOMEN - DISTENSION"]
        }

        # Check direct phrase expansions first (immediate top hits)
        c = self.conn.cursor()
        results = []
        seen_ids = set()

        for phrase, target_paths in PHRASE_EXPANSIONS.items():
            if phrase in q_lower:
                for tpath in target_paths:
                    c.execute("""
                    SELECT s.id, s.path, s.level, COUNT(sr.remedy_abbreviation) as remedy_count
                    FROM syntree s
                    LEFT JOIN symptom_remedies sr ON s.id = sr.symptom_id
                    WHERE s.path = ?
                    GROUP BY s.id
                    """, (tpath,))
                    row = c.fetchone()
                    if row and row['id'] not in seen_ids:
                        seen_ids.add(row['id'])
                        results.append({
                            "id": row['id'],
                            "path": row['path'],
                            "level": row['level'],
                            "remedy_count": row['remedy_count'],
                            "match_type": "Semantic Match"
                        })

        def add_rows(rows, match_type):
            for r in rows:
                sid = r['symptom_id'] if 'symptom_id' in r.keys() else r['id']
                if sid in seen_ids:
                    continue
                seen_ids.add(sid)
                results.append({
                    "id": sid,
                    "path": r['path'],
                    "level": r['level'],
                    "remedy_count": r['remedy_count'],
                    "match_type": match_type
                })

        # Build clean FTS queries: try high-precision combinations
        search_terms = [t.upper() for t in concept_words if len(t) >= 2]

        # Step A: Exact ALL-concept AND match
        if len(search_terms) >= 2:
            import itertools
            # Test 2-3 word combinations
            for k in range(min(len(search_terms), 3), 1, -1):
                for combo in itertools.combinations(search_terms, k):
                    and_q = " AND ".join([f'"{term}"*' for term in combo])
                    sql = """
                    SELECT f.symptom_id, f.path, s.level, COUNT(sr.remedy_abbreviation) as remedy_count
                    FROM syntree_fts( ? ) f
                    JOIN syntree s ON f.symptom_id = s.id
                    LEFT JOIN symptom_remedies sr ON s.id = sr.symptom_id
                    GROUP BY f.symptom_id
                    HAVING remedy_count >= 1
                    ORDER BY (s.level <= 3) DESC, remedy_count DESC
                    LIMIT 8
                    """
                    try:
                        c.execute(sql, (and_q,))
                        add_rows(c.fetchall(), "Semantic Match")
                    except Exception:
                        pass
                    if len(results) >= limit:
                        break
                if len(results) >= limit:
                    break

        # Step B: If still need more, use standard token autocomplete as high-quality fallback
        if len(results) < limit:
            fallback_items = self.autocomplete_rubrics(query, limit=limit)
            for item in fallback_items:
                if item['id'] not in seen_ids:
                    seen_ids.add(item['id'])
                    item['match_type'] = "Lexical"
                    results.append(item)

        # Sort results: Level <= 3 first, then remedy_count DESC
        results.sort(key=lambda x: (
            0 if x.get('match_type') == "Semantic Match" else 1,
            0 if x['level'] <= 3 else 1,
            -x['remedy_count'],
            len(x['path'])
        ))

        return results[:limit]

    def get_rubric_hierarchy_and_crossrefs(self, symptom_id: int) -> Dict[str, Any]:
        """Fetch full path, children rubrics, and cross-references for inspection."""
        c = self.conn.cursor()
        c.execute("SELECT * FROM syntree WHERE id = ?", (symptom_id,))
        curr = c.fetchone()
        if not curr:
            return {}

        # Fetch child sub-rubrics
        c.execute("SELECT id, item, path FROM syntree WHERE id_father = ? ORDER BY order_index LIMIT 25", (symptom_id,))
        children = [dict(row) for row in c.fetchall()]

        # Fetch cross-references
        c.execute("SELECT text, kind FROM cross_references WHERE symptom_id = ?", (symptom_id,))
        xrefs = [dict(row) for row in c.fetchall()]

        return {
            "current": dict(curr),
            "children": children,
            "cross_references": xrefs
        }

    def get_cell_citation(self, symptom_id: int, remedy_abbr: str) -> Dict[str, Any]:
        """Fetch exact authors/masters who proved/confirmed this symptom."""
        c = self.conn.cursor()
        
        # 1. Degree and remedy name
        c.execute("""
        SELECT sr.degree, r.description as remedy_full
        FROM symptom_remedies sr
        LEFT JOIN remedies r ON sr.remedy_abbreviation = r.remedy_abbreviation
        WHERE sr.symptom_id = ? AND sr.remedy_abbreviation = ?
        """, (symptom_id, remedy_abbr))
        base_info = c.fetchone()
        
        # 2. Authors
        c.execute("""
        SELECT ra.author_abbreviation, a.description as author_desc
        FROM remedy_authors ra
        LEFT JOIN authors a ON ra.author_abbreviation = a.author_abbreviation
        WHERE ra.symptom_id = ? AND ra.remedy_abbreviation = ?
        """, (symptom_id, remedy_abbr))
        author_rows = c.fetchall()

        return {
            "symptom_id": symptom_id,
            "remedy": remedy_abbr,
            "remedy_full": base_info['remedy_full'] if base_info else remedy_abbr,
            "degree": base_info['degree'] if base_info else 0,
            "authors": [dict(a) for a in author_rows]
        }

    def repertorise_matrix(
        self, 
        symptom_weights: Dict[int, int], 
        eliminating_symptom_ids: List[int] = None,
        min_degree: int = 1,
        top_n: int = 12,
        is_acute_mode: bool = False
    ) -> Dict[str, Any]:
        """
        Calculates Synthesis Repertorisation Matrix:
        symptom_weights: {symptom_id: weight (1, 2, or 3)}
        eliminating_symptom_ids: Must-have symptoms (filters remedies)
        is_acute_mode: boosts acute crisis remedies (Ars, Nux-v, Verat, Bell, etc.)
        """
        if not symptom_weights:
            return {"rubrics": [], "remedies": [], "matrix": []}

        eliminating_ids = set(eliminating_symptom_ids or [])
        symptom_ids = list(symptom_weights.keys())
        id_list = ",".join(map(str, symptom_ids))
        c = self.conn.cursor()

        # 1. Get rubric paths
        c.execute(f"SELECT id, path FROM syntree WHERE id IN ({id_list})")
        rubric_map = {r['id']: r['path'] for r in c.fetchall()}

        # 2. Get remedy scores with weight multiplication
        c.execute(f"""
        SELECT 
            sr.symptom_id,
            sr.remedy_abbreviation,
            sr.degree,
            r.description as remedy_full
        FROM symptom_remedies sr
        LEFT JOIN remedies r ON sr.remedy_abbreviation = r.remedy_abbreviation
        WHERE sr.symptom_id IN ({id_list}) AND sr.degree >= ?
        """, (min_degree,))
        
        all_records = c.fetchall()
        
        remedy_totals = {}
        degree_lookup = {}
        remedy_names = {}

        for rec in all_records:
            sid = rec['symptom_id']
            rem = rec['remedy_abbreviation']
            deg = rec['degree']
            weight = symptom_weights.get(sid, 1)

            degree_lookup[(sid, rem)] = deg
            remedy_names[rem] = rec['remedy_full'] or rem

            if rem not in remedy_totals:
                remedy_totals[rem] = {
                    "abbr": rem,
                    "name": rec['remedy_full'] or rem,
                    "covered_symptoms": set(),
                    "total_score": 0
                }
            remedy_totals[rem]["covered_symptoms"].add(sid)
            remedy_totals[rem]["total_score"] += (deg * weight)

        # 3. Apply elimination filter and scoring
        eligible_remedies = []
        for rem, data in remedy_totals.items():
            if eliminating_ids and not eliminating_ids.issubset(data["covered_symptoms"]):
                continue
            
            cov_count = len(data["covered_symptoms"])
            tot_score = data["total_score"]
            
            # Clinical Rank: Breadth (cov * 10) + Depth (score * 2)
            clinical_rank = (cov_count * 10) + (tot_score * 2)

            # In acute mode, give acute crisis polycrests a clinical prominence boost
            if is_acute_mode and rem in ACUTE_REMEDIES:
                clinical_rank += 12

            eligible_remedies.append({
                "remedy_abbreviation": rem,
                "remedy_full": data["name"],
                "rubrics_covered": cov_count,
                "total_score": tot_score,
                "clinical_rank": clinical_rank,
                "is_acute": rem in ACUTE_REMEDIES
            })

        # Sort: Clinical rank DESC
        eligible_remedies.sort(key=lambda x: (x["clinical_rank"], x["rubrics_covered"], x["total_score"]), reverse=True)
        top_remedies = eligible_remedies[:top_n]

        # 4. Construct table rows
        matrix_rows = []
        for sid in symptom_ids:
            row = {
                "symptom_id": sid,
                "rubric": rubric_map.get(sid, f"Rubric #{sid}"),
                "weight": symptom_weights.get(sid, 1),
                "is_eliminating": sid in eliminating_ids,
                "scores": {}
            }
            for tr in top_remedies:
                abbr = tr["remedy_abbreviation"]
                row["scores"][abbr] = degree_lookup.get((sid, abbr), 0)
            matrix_rows.append(row)

        return {
            "total_rubrics": len(symptom_ids),
            "remedies": top_remedies,
            "matrix": matrix_rows
        }

if __name__ == "__main__":
    rep = RepertoryServer("synthesis.db")
    print("Test Autocomplete ('mi con int'):")
    print(rep.autocomplete_rubrics("mi con int", limit=3))
