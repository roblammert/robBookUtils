import json
import math
import re
import statistics


class JournalMetricsAnalyzer:
    __version__ = "1.0.0"
    def __init__(self, lexicon_path: str = "RobTextAnalyzer_Lexicon.json") -> None:
        with open(lexicon_path, "r", encoding="utf-8") as f:
            self.lexicon = json.load(f)
        self._set_cache = {}

    def analyze(self, text: str, categories: list[str] | None = None) -> str:
        normalized_text = text or ""
        features = self._extract_features(normalized_text)

        category_functions = {
            "structural_metrics": self._compute_structural_metrics,
            "readability_complexity": self._compute_readability_complexity,
            "emotional_lexicon_metrics": self._compute_emotional_lexicon_metrics,
            "cognitive_distortions": self._compute_cognitive_distortions,
            "agency_control": self._compute_agency_control,
            "self_focus_vs_other_focus": self._compute_self_focus_vs_other_focus,
            "temporal_orientation": self._compute_temporal_orientation,
            "narrative_coherence_flow": self._compute_narrative_coherence_flow,
            "behavioral_signals": self._compute_behavioral_signals,
            "meta_psychological_metrics": self._compute_meta_psychological_metrics,
            "linguistic_style": self._compute_linguistic_style,
            "social_relational_signals": self._compute_social_relational_signals,
            "motivation_goal_orientation": self._compute_motivation_goal_orientation,
            "advanced_derived_metrics": self._compute_advanced_derived_metrics,
        }

        if categories is None:
            selected = list(category_functions.keys())
        else:
            selected = []
            unknown = []
            for c in categories:
                key = self._normalize_category_name(c)
                if key in category_functions:
                    selected.append(key)
                else:
                    unknown.append(c)
            if unknown:
                raise ValueError(f"Unknown categories: {unknown}")

        result = {"categories": {}}
        for key in selected:
            result["categories"][key] = category_functions[key](features)

        return json.dumps(result, ensure_ascii=True, sort_keys=True)

    def _normalize_category_name(self, name: str) -> str:
        cleaned = re.sub(r"[^a-z0-9]+", "_", (name or "").strip().lower()).strip("_")
        alias_map = {
            "structural": "structural_metrics",
            "structural_metrics": "structural_metrics",
            "readability": "readability_complexity",
            "readability_complexity": "readability_complexity",
            "emotional_lexicon": "emotional_lexicon_metrics",
            "emotional_lexicon_metrics": "emotional_lexicon_metrics",
            "cognitive": "cognitive_distortions",
            "cognitive_distortions": "cognitive_distortions",
            "agency": "agency_control",
            "agency_control": "agency_control",
            "self_focus": "self_focus_vs_other_focus",
            "self_focus_vs_other_focus": "self_focus_vs_other_focus",
            "temporal": "temporal_orientation",
            "temporal_orientation": "temporal_orientation",
            "narrative": "narrative_coherence_flow",
            "narrative_coherence_flow": "narrative_coherence_flow",
            "behavioral": "behavioral_signals",
            "behavioral_signals": "behavioral_signals",
            "meta_psychological": "meta_psychological_metrics",
            "meta_psychological_metrics": "meta_psychological_metrics",
            "linguistic": "linguistic_style",
            "linguistic_style": "linguistic_style",
            "social": "social_relational_signals",
            "social_relational_signals": "social_relational_signals",
            "motivation": "motivation_goal_orientation",
            "motivation_goal_orientation": "motivation_goal_orientation",
            "advanced": "advanced_derived_metrics",
            "advanced_derived_metrics": "advanced_derived_metrics",
            "all": "all",
        }
        return alias_map.get(cleaned, cleaned)

    def _extract_features(self, text: str) -> dict:
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s.strip()]
        if not sentences and text.strip():
            sentences = [text.strip()]
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n+", text.strip()) if p.strip()]
        words = re.findall(r"[A-Za-z]+(?:'[A-Za-z]+)?", text.lower())
        sentence_words = [re.findall(r"[A-Za-z]+(?:'[A-Za-z]+)?", s.lower()) for s in sentences]
        sentence_lengths = [len(sw) for sw in sentence_words]
        syllables_per_word = [self._count_syllables(w) for w in words]
        hard_words = [w for w, syl in zip(words, syllables_per_word) if syl >= 3]

        return {
            "text": text,
            "text_lower": text.lower(),
            "sentences": sentences,
            "paragraphs": paragraphs,
            "words": words,
            "sentence_words": sentence_words,
            "sentence_lengths": sentence_lengths,
            "word_count": len(words),
            "sentence_count": len(sentences),
            "paragraph_count": max(len(paragraphs), 1 if text.strip() else 0),
            "syllables_per_word": syllables_per_word,
            "hard_words": hard_words,
            "hard_word_count": len(hard_words),
            "total_syllables": sum(syllables_per_word),
        }

    def _count_syllables(self, word: str) -> int:
        w = re.sub(r"[^a-z]", "", word.lower())
        if not w:
            return 1
        vowels = "aeiouy"
        count = 0
        prev_vowel = False
        for ch in w:
            is_vowel = ch in vowels
            if is_vowel and not prev_vowel:
                count += 1
            prev_vowel = is_vowel
        if w.endswith("e") and count > 1:
            count -= 1
        if w.endswith("le") and len(w) > 2 and w[-3] not in vowels:
            count += 1
        return max(count, 1)

    def _safe_div(self, num: float, den: float) -> float:
        return float(num) / float(den) if den else 0.0

    def _get_set(self, key_path: str) -> set:
        if key_path in self._set_cache:
            return self._set_cache[key_path]
        node = self.lexicon
        for k in key_path.split("."):
            node = node.get(k, {})
        val = set(node) if isinstance(node, list) else set()
        self._set_cache[key_path] = val
        return val

    def _count_terms(self, words: list[str], key_path: str) -> int:
        lex = self._get_set(key_path)
        return sum(1 for w in words if w in lex)

    def _count_phrase_list(self, text_lower: str, phrases: list[str]) -> int:
        total = 0
        for p in phrases:
            pattern = r"\b" + re.sub(r"\s+", r"\\s+", re.escape(p.lower())) + r"\b"
            total += len(re.findall(pattern, text_lower))
        return total

    def _avg(self, values: list[float]) -> float:
        return float(sum(values) / len(values)) if values else 0.0

    def _std(self, values: list[float]) -> float:
        return float(statistics.pstdev(values)) if len(values) > 1 else 0.0

    def _sentence_emotion_scores(self, features: dict) -> list[float]:
        pos = self._get_set("positive_emotions")
        neg = self._get_set("negative_emotions")
        scores = []
        for sw in features["sentence_words"]:
            if not sw:
                scores.append(0.0)
                continue
            p = sum(1 for w in sw if w in pos)
            n = sum(1 for w in sw if w in neg)
            scores.append(self._safe_div(p - n, len(sw)))
        return scores

    def _count_cat(self, features: dict, key_path: str) -> int:
        return self._count_terms(features["words"], key_path)

    def _count_suffix_words(self, words: list[str], suffixes: list[str]) -> int:
        return sum(1 for w in words if any(w.endswith(sfx) for sfx in suffixes))

    def _compute_structural_metrics(self, features: dict) -> dict:
        wc = features["word_count"]
        sc = features["sentence_count"]
        sentence_lengths = features["sentence_lengths"]
        text = features["text"]

        stop_count = self._count_cat(features, "stopwords")
        punct_count = len(re.findall(r"[^\w\s]", text))
        exclam_count = text.count("!")
        ques_count = text.count("?")
        ellipsis_count = len(re.findall(r"\.\.\.", text))
        parenthetical_count = len(re.findall(r"\([^)]*\)|\[[^\]]*\]", text))
        adverb_count = sum(1 for w in features["words"] if re.search(r"ly$", w))
        nominal_count = self._count_suffix_words(features["words"], self.lexicon.get("nominalization_suffixes", []))

        return {
            "word_count": wc,
            "sentence_count": sc,
            "paragraph_count": features["paragraph_count"],
            "avg_sentence_length": self._safe_div(wc, sc),
            "sentence_length_variance": float(statistics.pvariance(sentence_lengths)) if len(sentence_lengths) > 1 else 0.0,
            "longest_sentence_length": max(sentence_lengths) if sentence_lengths else 0,
            "shortest_sentence_length": min(sentence_lengths) if sentence_lengths else 0,
            "lexical_diversity": self._safe_div(len(set(features["words"])), wc),
            "stopword_ratio": self._safe_div(stop_count, wc),
            "punctuation_density": self._safe_div(punct_count, wc),
            "exclamation_density": self._safe_div(exclam_count, wc),
            "question_density": self._safe_div(ques_count, wc),
            "ellipsis_count": ellipsis_count,
            "parenthetical_count": parenthetical_count,
            "adverb_density": self._safe_div(adverb_count, wc),
            "nominalization_density": self._safe_div(nominal_count, wc),
        }

    def _compute_readability_complexity(self, features: dict) -> dict:
        wc = features["word_count"]
        sc = features["sentence_count"]
        total_syllables = features["total_syllables"]
        hard_word_count = features["hard_word_count"]

        polysyllables = sum(1 for s in features["syllables_per_word"] if s >= 3)
        clause_markers = self.lexicon.get("clause_markers", [])
        clause_count = self._count_phrase_list(features["text_lower"], clause_markers)

        asl = self._safe_div(wc, sc)
        asw = self._safe_div(total_syllables, wc)
        hard_ratio = self._safe_div(hard_word_count, wc)

        flesch = 206.835 - (1.015 * asl) - (84.6 * asw)
        fk_grade = (0.39 * asl) + (11.8 * asw) - 15.59
        gunning = 0.4 * (asl + (100.0 * hard_ratio))
        smog = 1.043 * math.sqrt(self._safe_div(polysyllables * 30.0, sc)) + 3.1291 if sc else 0.0

        return {
            "flesch_reading_ease": float(flesch),
            "flesch_kincaid_grade": float(fk_grade),
            "gunning_fog_index": float(gunning),
            "smog_index": float(smog),
            "avg_syllables_per_word": float(asw),
            "hard_word_ratio": float(hard_ratio),
            "clause_density": self._safe_div(clause_count, sc),
        }

    def _compute_emotional_lexicon_metrics(self, features: dict) -> dict:
        wc = features["word_count"]
        pos_count = self._count_cat(features, "positive_emotions")
        neg_count = self._count_cat(features, "negative_emotions")
        emo_total = pos_count + neg_count
        scores = self._sentence_emotion_scores(features)

        diffs = [scores[i] - scores[i - 1] for i in range(1, len(scores))]
        acceleration = self._avg([abs(diffs[i] - diffs[i - 1]) for i in range(1, len(diffs))]) if len(diffs) > 1 else 0.0

        turning_points = 0
        for i in range(1, len(scores)):
            prev = scores[i - 1]
            cur = scores[i]
            if prev == 0.0 or cur == 0.0:
                continue
            if (prev > 0 and cur < 0) or (prev < 0 and cur > 0):
                turning_points += 1

        high_activation = self._count_cat(features, "activation_words.high")
        low_activation = self._count_cat(features, "activation_words.low")
        catastrophizing_hits = self._count_cat(features, "catastrophizing_terms")

        return {
            "positive_emotion_count": pos_count,
            "negative_emotion_count": neg_count,
            "emotion_ratio": self._safe_div(pos_count, neg_count if neg_count else 1),
            "emotional_density": self._safe_div(emo_total, wc),
            "emotional_volatility": self._std(scores),
            "emotional_acceleration": float(acceleration),
            "emotional_turning_points": turning_points,
            "activation_level": self._safe_div(high_activation - low_activation, wc),
            "catastrophizing_hits": catastrophizing_hits,
        }

    def _compute_cognitive_distortions(self, features: dict) -> dict:
        txt = features["text_lower"]
        cd = self.lexicon.get("cognitive_distortions", {})

        all_or_nothing = self._count_phrase_list(txt, cd.get("all_or_nothing", []))
        should_statements = self._count_phrase_list(txt, cd.get("should_statements", []))
        mind_reading = self._count_phrase_list(txt, cd.get("mind_reading", []))
        catastrophizing = self._count_phrase_list(txt, self.lexicon.get("catastrophizing_terms", []))
        overgeneralization = self._count_phrase_list(txt, cd.get("overgeneralization", []))
        labeling = self._count_phrase_list(txt, cd.get("labeling", []))
        fortune_telling = self._count_phrase_list(txt, cd.get("fortune_telling", []))
        personalization = self._count_phrase_list(txt, cd.get("personalization", []))
        discounting = self._count_phrase_list(txt, cd.get("discounting_positives", []))

        return {
            "all_or_nothing_hits": all_or_nothing,
            "should_statements": should_statements,
            "mind_reading_hits": mind_reading,
            "catastrophizing_phrases": catastrophizing,
            "overgeneralization_hits": overgeneralization,
            "labeling_hits": labeling,
            "fortune_telling_hits": fortune_telling,
            "personalization_hits": personalization,
            "discounting_positives_hits": discounting,
        }

    def _compute_agency_control(self, features: dict) -> dict:
        internal = self._count_cat(features, "agency.internal")
        external = self._count_cat(features, "agency.external")
        powerless = self._count_cat(features, "powerlessness")
        self_efficacy = self._count_cat(features, "self_efficacy")

        return {
            "internal_agency_hits": internal,
            "external_agency_hits": external,
            "agency_ratio": self._safe_div(internal, external if external else 1),
            "powerlessness_hits": powerless,
            "self_efficacy_hits": self_efficacy,
        }

    def _compute_self_focus_vs_other_focus(self, features: dict) -> dict:
        wc = features["word_count"]
        fp = self._count_cat(features, "pronouns.first_person")
        sp = self._count_cat(features, "pronouns.second_person")
        tp = self._count_cat(features, "pronouns.third_person")
        pron_total = fp + sp + tp

        self_crit = self._count_cat(features, "self_criticism")
        self_affirm = self._count_cat(features, "self_affirmation")

        return {
            "first_person_ratio": self._safe_div(fp, pron_total),
            "second_person_ratio": self._safe_div(sp, pron_total),
            "third_person_ratio": self._safe_div(tp, pron_total),
            "self_reference_density": self._safe_div(fp, wc),
            "self_criticism_hits": self_crit,
            "self_affirmation_hits": self_affirm,
        }

    def _compute_temporal_orientation(self, features: dict) -> dict:
        past = self._count_cat(features, "temporal.past")
        present = self._count_cat(features, "temporal.present")
        future = self._count_cat(features, "temporal.future")
        total = past + present + future

        regret = self._count_cat(features, "regret_terms")
        anticipation = self._count_cat(features, "anticipation_terms")

        return {
            "past_orientation_ratio": self._safe_div(past, total),
            "present_orientation_ratio": self._safe_div(present, total),
            "future_orientation_ratio": self._safe_div(future, total),
            "regret_hits": regret,
            "anticipation_hits": anticipation,
        }

    def _compute_narrative_coherence_flow(self, features: dict) -> dict:
        sentences = features["sentence_words"]
        sw_set = self._get_set("stopwords")
        transition_count = self._count_cat(features, "transition_words")

        overlaps = []
        for i in range(1, len(sentences)):
            a = {w for w in sentences[i - 1] if w not in sw_set}
            b = {w for w in sentences[i] if w not in sw_set}
            union = len(a | b)
            inter = len(a & b)
            overlaps.append(self._safe_div(inter, union))
        topic_continuity = self._avg(overlaps)
        abrupt_shift = 1.0 - topic_continuity

        wc = features["word_count"]
        unique_words = len(set(features["words"]))
        repetition_score = 1.0 - self._safe_div(unique_words, wc)

        sentence_texts = [re.sub(r"\s+", " ", s.strip().lower()) for s in features["sentences"] if s.strip()]
        unique_sentences = len(set(sentence_texts))
        redundancy = 1.0 - self._safe_div(unique_sentences, len(sentence_texts))

        transition_density = self._safe_div(transition_count, max(len(sentences), 1))
        coherence = max(0.0, min(1.0, (0.5 * topic_continuity) + (0.3 * (1.0 - redundancy)) + (0.2 * min(transition_density, 1.0))))

        emo_scores = self._sentence_emotion_scores(features)
        if emo_scores:
            n = len(emo_scores)
            a = emo_scores[: max(1, n // 3)]
            b = emo_scores[max(1, n // 3): max(2, (2 * n) // 3)]
            c = emo_scores[max(2, (2 * n) // 3):]
            narrative_arc = [self._avg(a), self._avg(b), self._avg(c)]
        else:
            narrative_arc = [0.0, 0.0, 0.0]

        return {
            "transition_word_count": transition_count,
            "topic_continuity_score": float(topic_continuity),
            "abrupt_topic_shift_score": float(abrupt_shift),
            "repetition_score": float(repetition_score),
            "redundancy_score": float(redundancy),
            "coherence_score": float(coherence),
            "narrative_arc": narrative_arc,
        }

    def _compute_behavioral_signals(self, features: dict) -> dict:
        return {
            "sleep_references": self._count_cat(features, "behavioral.sleep"),
            "eating_references": self._count_cat(features, "behavioral.eating"),
            "social_references": self._count_cat(features, "behavioral.social"),
            "work_stress_references": self._count_cat(features, "behavioral.work_stress"),
            "physical_symptom_references": self._count_cat(features, "behavioral.physical_symptoms"),
            "routine_references": self._count_cat(features, "behavioral.routines"),
            "avoidance_references": self._count_cat(features, "behavioral.avoidance"),
            "coping_references": self._count_cat(features, "behavioral.coping"),
            "goal_references": self._count_cat(features, "behavioral.goals"),
        }

    def _compute_meta_psychological_metrics(self, features: dict) -> dict:
        wc = features["word_count"]
        emo = self._compute_emotional_lexicon_metrics(features)
        pos = emo["positive_emotion_count"]
        neg = emo["negative_emotion_count"]
        scores = self._sentence_emotion_scores(features)

        inertia = 0.0
        if len(scores) > 1:
            x = scores[:-1]
            y = scores[1:]
            mx = self._avg(x)
            my = self._avg(y)
            cov = sum((a - mx) * (b - my) for a, b in zip(x, y))
            vx = sum((a - mx) ** 2 for a in x)
            vy = sum((b - my) ** 2 for b in y)
            inertia = self._safe_div(cov, math.sqrt(vx * vy)) if vx and vy else 0.0

        emotional_balance = self._safe_div(pos, pos + neg)
        polarity_ratio = self._safe_div(pos, neg if neg else 1)
        volatility_index = float(emo["emotional_volatility"])
        stability = self._safe_div(1.0, 1.0 + volatility_index)

        rumination = self._count_cat(features, "rumination_terms")
        rumination += self._count_phrase_list(features["text_lower"], self.lexicon.get("cognitive_distortions", {}).get("overgeneralization", []))

        avg_sentence = self._safe_div(features["word_count"], features["sentence_count"])
        clause_density = self._compute_readability_complexity(features)["clause_density"]
        hard_ratio = self._compute_readability_complexity(features)["hard_word_ratio"]
        cognitive_load = (avg_sentence * 0.5) + (clause_density * 10.0) + (hard_ratio * 10.0)

        insight = self._count_cat(features, "insight_terms")
        self_awareness = self._count_cat(features, "self_awareness_terms")
        metacognition = self._count_cat(features, "metacognition_terms")

        return {
            "emotional_inertia": float(inertia),
            "emotional_balance": float(emotional_balance),
            "polarity_ratio": float(polarity_ratio),
            "volatility_index": float(volatility_index),
            "stability_score": float(stability),
            "rumination_indicators": rumination,
            "cognitive_load_index": float(cognitive_load),
            "insight_density": self._safe_div(insight, wc),
            "self_awareness_markers": self_awareness,
            "metacognition_markers": metacognition,
        }

    def _compute_linguistic_style(self, features: dict) -> dict:
        wc = features["word_count"]
        formal = self._count_cat(features, "formal_words")
        slang = self._count_cat(features, "slang")
        profanity = self._count_cat(features, "profanity")
        hedging = self._count_cat(features, "hedging")
        certainty = self._count_cat(features, "certainty_markers")
        intensifiers = self._count_cat(features, "intensifiers")
        commitment = self._count_cat(features, "commitment_terms")

        formality = self._safe_div(formal - slang - profanity, wc)
        hedging_density = self._safe_div(hedging, wc)
        certainty_density = self._safe_div(certainty, wc)
        commitment_density = self._safe_div(commitment, wc)
        assertiveness = certainty_density + commitment_density - hedging_density

        return {
            "formality_score": float(formality),
            "slang_density": self._safe_div(slang, wc),
            "profanity_density": self._safe_div(profanity, wc),
            "hedging_density": float(hedging_density),
            "certainty_markers": certainty,
            "intensifier_density": self._safe_div(intensifiers, wc),
            "assertiveness_score": float(assertiveness),
        }

    def _compute_social_relational_signals(self, features: dict) -> dict:
        wc = features["word_count"]
        names = self._count_cat(features, "names")
        kinship = self._count_cat(features, "kinship_terms")
        person_mentions = names + kinship

        support = self._count_cat(features, "support_seeking")
        isolation = self._count_cat(features, "isolation_terms")
        conflict = self._count_cat(features, "conflict_terms")
        gratitude = self._count_cat(features, "gratitude")

        relationship_valence = self._safe_div((support + gratitude) - (conflict + isolation), wc)

        return {
            "person_mentions": person_mentions,
            "relationship_valence_score": float(relationship_valence),
            "support_seeking_hits": support,
            "isolation_indicators": isolation,
            "conflict_indicators": conflict,
            "gratitude_density": self._safe_div(gratitude, wc),
        }

    def _compute_motivation_goal_orientation(self, features: dict) -> dict:
        goal_statements = self._count_cat(features, "goal_statements")
        progress = self._count_cat(features, "progress_terms")
        stuck = self._count_cat(features, "stuck_terms")
        planning = self._count_cat(features, "planning_terms")
        avoidance = self._count_cat(features, "avoidance_language")
        commitment = self._count_cat(features, "commitment_terms")

        return {
            "goal_statements": goal_statements,
            "progress_statements": progress,
            "stuckness_indicators": stuck,
            "planning_language_hits": planning,
            "avoidance_language_hits": avoidance,
            "commitment_language_hits": commitment,
        }

    def _compute_advanced_derived_metrics(self, features: dict) -> dict:
        emo = self._compute_emotional_lexicon_metrics(features)
        cog = self._compute_cognitive_distortions(features)
        nar = self._compute_narrative_coherence_flow(features)
        mot = self._compute_motivation_goal_orientation(features)
        meta = self._compute_meta_psychological_metrics(features)
        self_focus = self._compute_self_focus_vs_other_focus(features)
        temporal = self._compute_temporal_orientation(features)
        behavioral = self._compute_behavioral_signals(features)

        emotional_coherence = max(0.0, 1.0 - emo["emotional_volatility"]) * nar["coherence_score"]

        sent_scores = self._sentence_emotion_scores(features)
        sentence_cd = []
        cd_terms = []
        for bucket in self.lexicon.get("cognitive_distortions", {}).values():
            cd_terms.extend(bucket)
        cd_terms.extend(self.lexicon.get("catastrophizing_terms", []))
        for s in features["sentences"]:
            sentence_cd.append(self._count_phrase_list(s.lower(), cd_terms))
        cognitive_emotional_alignment = self._pearson(sent_scores, sentence_cd)

        linguistic_stability = self._safe_div(1.0, 1.0 + self._compute_structural_metrics(features)["sentence_length_variance"])

        future = temporal["future_orientation_ratio"]
        progress_density = self._safe_div(mot["progress_statements"], features["word_count"])
        stuck_density = self._safe_div(mot["stuckness_indicators"], features["word_count"])
        commitment_density = self._safe_div(mot["commitment_language_hits"], features["word_count"])
        psychological_momentum = future + progress_density + commitment_density - stuck_density

        insight = meta["insight_density"] * features["word_count"]
        rumination = meta["rumination_indicators"]
        insight_to_rumination = self._safe_div(insight, rumination + 1)

        self_compassion = self._safe_div(self_focus["self_affirmation_hits"], self_focus["self_criticism_hits"] + 1)

        stress_terms = (
            behavioral["work_stress_references"]
            + behavioral["physical_symptom_references"]
            + emo["negative_emotion_count"]
            + cog["catastrophizing_phrases"]
        )
        stress_load = self._safe_div(stress_terms, features["word_count"])

        return {
            "emotional_coherence": float(emotional_coherence),
            "cognitive_emotional_alignment": float(cognitive_emotional_alignment),
            "linguistic_stability": float(linguistic_stability),
            "psychological_momentum": float(psychological_momentum),
            "insight_to_rumination_ratio": float(insight_to_rumination),
            "self_compassion_index": float(self_compassion),
            "stress_load_index": float(stress_load),
        }

    def _pearson(self, x: list[float], y: list[float]) -> float:
        if len(x) != len(y) or len(x) < 2:
            return 0.0
        mx = self._avg(x)
        my = self._avg(y)
        num = sum((a - mx) * (b - my) for a, b in zip(x, y))
        den_x = math.sqrt(sum((a - mx) ** 2 for a in x))
        den_y = math.sqrt(sum((b - my) ** 2 for b in y))
        den = den_x * den_y
        return self._safe_div(num, den) if den else 0.0


RobTextAnalyzer = JournalMetricsAnalyzer
