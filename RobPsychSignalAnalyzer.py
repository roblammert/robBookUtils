import json
import os
import re
import statistics
from datetime import datetime, timezone
from hashlib import sha256
from collections import Counter
from typing import Any, Dict, List, Literal, Pattern, Set, Tuple, Union


class RobPsychSignalAnalyzer:
    """Analyze free text for psychological, emotional, cognitive, and linguistic signals."""

    CATEGORY_ORDER = [
        "core_affect",
        "emotional_granularity",
        "discourse_process",
        "cognitive_patterns",
        "cognitive_control",
        "cognitive_style",
        "identity",
        "social",
        "interpersonal_stance",
        "relational_depth",
        "behavioral_intent",
        "behavioral_execution",
        "motivation_reward",
        "regulation",
        "stress_recovery",
        "physiological_dynamics",
        "temporal",
        "sleep_circadian",
        "somatic",
        "existential",
        "self_coherence",
        "risk_safety",
        "risk_protection_advanced",
        "resilience_strengths",
        "longitudinal_dynamics",
        "calibration_monitoring",
        "linguistic_structure",
        "thought_speed",
        "meta_signals",
        "analysis_quality",
    ]

    __version__ = "2.0.0"

    def __init__(self, lexicon_path: str = "RobPsychSignalAnalyzer_Lexicon.json") -> None:
        self.lexicon_path = self._resolve_lexicon_path(lexicon_path)
        with open(self.lexicon_path, "r", encoding="utf-8") as infile:
            self.lexicon: Dict[str, Any] = json.load(infile)
        self.text_processing: Dict[str, Any] = self.lexicon["text_processing"]
        self.runtime_lexicon: Dict[str, Any] = self.lexicon["runtime_lexicon"]
        self.negation_words: Set[str] = set(self.text_processing["negation_words"])
        self._pattern_cache: Dict[str, Pattern[str]] = {}

    def analyze(
        self,
        text: str,
        categories: Union[List[str], Literal["all"]],
        history_entries: Union[None, List[str]] = None,
        normalize_scores: bool = True,
    ) -> str:
        if not isinstance(text, str):
            raise TypeError("text must be a string")

        cleaned_text = text.strip()
        analysis_text = self._normalize_text(cleaned_text)
        tokens = self._tokenize(analysis_text)
        sentences = self._split_sentences(analysis_text)

        selected = self._resolve_categories(categories)

        result: Dict[str, Any] = {
            "metadata": {
                "analyzer": "RobPsychSignalAnalyzer",
                "lexicon_path": self.lexicon_path,
                "text_char_count": len(cleaned_text),
                "word_count": len(tokens),
                "sentence_count": len(sentences),
                "normalization_applied": True,
                "timeline_entry_count": len(history_entries) if isinstance(history_entries, list) else 1,
                "selected_categories": selected,
            }
        }

        for category in selected:
            if category == "core_affect":
                result[category] = self._compute_core_affect(analysis_text, tokens, sentences)
            elif category == "emotional_granularity":
                result[category] = self._compute_emotional_granularity(analysis_text, tokens, sentences)
            elif category == "discourse_process":
                result[category] = self._compute_discourse_process(analysis_text, tokens, sentences)
            elif category == "cognitive_patterns":
                result[category] = self._compute_cognitive_patterns(analysis_text, tokens, sentences)
            elif category == "cognitive_control":
                result[category] = self._compute_cognitive_control(analysis_text, tokens, sentences)
            elif category == "cognitive_style":
                result[category] = self._compute_cognitive_style(analysis_text, tokens, sentences)
            elif category == "identity":
                result[category] = self._compute_identity(analysis_text, tokens)
            elif category == "social":
                result[category] = self._compute_social(analysis_text, tokens)
            elif category == "interpersonal_stance":
                result[category] = self._compute_interpersonal_stance(analysis_text, tokens)
            elif category == "relational_depth":
                result[category] = self._compute_relational_depth(analysis_text, tokens)
            elif category == "behavioral_intent":
                result[category] = self._compute_behavioral_intent(analysis_text, tokens)
            elif category == "behavioral_execution":
                result[category] = self._compute_behavioral_execution(analysis_text, tokens)
            elif category == "motivation_reward":
                result[category] = self._compute_motivation_reward(analysis_text, tokens)
            elif category == "regulation":
                result[category] = self._compute_regulation(analysis_text, tokens, sentences)
            elif category == "stress_recovery":
                result[category] = self._compute_stress_recovery(analysis_text, tokens, sentences)
            elif category == "physiological_dynamics":
                result[category] = self._compute_physiological_dynamics(analysis_text, tokens)
            elif category == "temporal":
                result[category] = self._compute_temporal(analysis_text, tokens)
            elif category == "sleep_circadian":
                result[category] = self._compute_sleep_circadian(analysis_text, tokens)
            elif category == "somatic":
                result[category] = self._compute_somatic(analysis_text, tokens)
            elif category == "existential":
                result[category] = self._compute_existential(analysis_text, tokens)
            elif category == "self_coherence":
                result[category] = self._compute_self_coherence(analysis_text, tokens, sentences)
            elif category == "risk_safety":
                result[category] = self._compute_risk_safety(analysis_text, tokens, sentences)
            elif category == "risk_protection_advanced":
                result[category] = self._compute_risk_protection_advanced(analysis_text, tokens)
            elif category == "resilience_strengths":
                result[category] = self._compute_resilience_strengths(analysis_text, tokens)
            elif category == "longitudinal_dynamics":
                result[category] = self._compute_longitudinal_dynamics(analysis_text, history_entries)
            elif category == "calibration_monitoring":
                result[category] = self._compute_calibration_monitoring(result)
            elif category == "linguistic_structure":
                result[category] = self._compute_linguistic_structure(analysis_text, tokens, sentences)
            elif category == "thought_speed":
                result[category] = self._compute_thought_speed(analysis_text, tokens, sentences)
            elif category == "meta_signals":
                result[category] = self._compute_meta_signals(analysis_text, tokens, sentences)
            elif category == "analysis_quality":
                result[category] = self._compute_analysis_quality(result, analysis_text, tokens, sentences)

        result["analyzer_score_report"] = self._build_analyzer_score_report(
            result=result,
            selected_categories=selected,
            cleaned_text=cleaned_text,
            word_count=len(tokens),
            normalize_scores=normalize_scores,
        )
        result["summary"] = self._build_summary(result)
        return json.dumps(result, indent=2, sort_keys=False)

    def _resolve_lexicon_path(self, lexicon_path: str) -> str:
        if os.path.isabs(lexicon_path):
            return os.path.abspath(lexicon_path)

        folder = os.path.dirname(os.path.abspath(__file__))
        return os.path.abspath(os.path.join(folder, lexicon_path))

    def _runtime_group(self, name: str) -> Dict[str, Any]:
        return self.runtime_lexicon[name]

    def _resolve_categories(self, categories: Union[List[str], Literal["all"]]) -> List[str]:
        if categories == "all":
            return list(self.CATEGORY_ORDER)

        if not isinstance(categories, list) or not all(isinstance(item, str) for item in categories):
            raise TypeError("categories must be a list[str] or the string 'all'")

        invalid = [cat for cat in categories if cat not in self.CATEGORY_ORDER]
        if invalid:
            raise ValueError(
                "Unknown categories: "
                + ", ".join(invalid)
                + ". Allowed: "
                + ", ".join(self.CATEGORY_ORDER)
            )

        deduped: List[str] = []
        seen = set()
        for cat in categories:
            if cat not in seen:
                deduped.append(cat)
                seen.add(cat)
        return deduped

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r"\b[a-zA-Z']+\b", text.lower())

    def _normalize_text(self, text: str) -> str:
        if not text:
            return ""
        normalized = text.lower()
        for contraction, expanded in self.text_processing["contraction_map"].items():
            normalized = re.sub(rf"\b{re.escape(contraction)}\b", expanded, normalized)
        normalized = re.sub(r"\s+", " ", normalized).strip()
        return normalized

    def _split_sentences(self, text: str) -> List[str]:
        raw = [segment.strip() for segment in re.split(r"(?<=[.!?])\s+", text) if segment.strip()]
        return raw if raw else ([text.strip()] if text.strip() else [])

    def _stem_token(self, token: str) -> str:
        if len(token) <= 4:
            return token
        for suffix in ("ing", "ed", "ly", "ness", "ment", "tion", "s"):
            if token.endswith(suffix) and len(token) - len(suffix) >= 3:
                return token[: -len(suffix)]
        return token

    def _count_keywords(self, tokens: List[str], keywords: List[str], negation_window: int = 3) -> int:
        if not tokens or not keywords:
            return 0

        keyword_tokens: Set[str] = set()
        keyword_stems: Set[str] = set()
        for word in keywords:
            pieces = self._tokenize(self._normalize_text(word))
            for piece in pieces:
                keyword_tokens.add(piece)
                keyword_stems.add(self._stem_token(piece))

        total = 0
        for idx, tok in enumerate(tokens):
            tok_stem = self._stem_token(tok)
            if tok in keyword_tokens or tok_stem in keyword_stems:
                left = max(0, idx - negation_window)
                scope = tokens[left:idx]
                if any(item in self.negation_words for item in scope):
                    continue
                total += 1
        return total

    def _compile_pattern(self, pattern: str) -> Pattern[str]:
        if pattern not in self._pattern_cache:
            self._pattern_cache[pattern] = re.compile(pattern, flags=re.IGNORECASE)
        return self._pattern_cache[pattern]

    def _count_patterns(self, text: str, patterns: List[str]) -> int:
        if not text or not patterns:
            return 0
        total = 0
        for pattern in patterns:
            compiled = self._compile_pattern(pattern)
            total += len(compiled.findall(text))
        return total

    def _hybrid_score(
        self,
        pattern_hits: int,
        keyword_hits: int,
        denominator: int,
        pattern_weight: float = 2.0,
        keyword_weight: float = 1.0,
    ) -> float:
        if denominator <= 0:
            return 0.0
        raw = (pattern_hits * pattern_weight) + (keyword_hits * keyword_weight)
        return round(raw / denominator, 4)

    def _confidence(self, pattern_hits: int, keyword_hits: int, denominator: int) -> float:
        if denominator <= 0:
            return 0.0
        weighted_hits = (pattern_hits * 1.5) + keyword_hits
        return self._bounded_score(weighted_hits, scale=max(3.0, denominator * 0.04))

    def _ratio(self, numerator: int, denominator: int) -> float:
        return round(numerator / denominator, 4) if denominator > 0 else 0.0

    def _bounded_score(self, raw_value: float, scale: float = 1.0) -> float:
        if scale <= 0:
            return 0.0
        value = raw_value / scale
        if value < 0:
            return 0.0
        if value > 1:
            return 1.0
        return round(value, 4)

    def _clamped(self, value: float, low: float = 0.0, high: float = 1.0) -> float:
        return round(max(low, min(high, value)), 4)

    def _average(self, values: List[float]) -> float:
        return round(sum(values) / len(values), 4) if values else 0.0

    def _first_person_ratio(self, tokens: List[str]) -> float:
        first_person = {"i", "me", "my", "mine", "myself", "we", "us", "our", "ours", "ourselves"}
        social_pronouns = first_person | {
            "you",
            "your",
            "yours",
            "yourself",
            "yourselves",
            "they",
            "them",
            "their",
            "theirs",
            "themselves",
            "he",
            "she",
            "him",
            "her",
            "his",
            "hers",
        }
        first_count = sum(1 for tok in tokens if tok in first_person)
        pronoun_total = sum(1 for tok in tokens if tok in social_pronouns)
        return self._ratio(first_count, pronoun_total)

    def _average_signal_confidence(self, result: Dict[str, Any]) -> float:
        values: List[float] = []
        for category in self.CATEGORY_ORDER:
            if category not in result or not isinstance(result[category], dict):
                continue
            for key, value in result[category].items():
                if "confidence" in key and isinstance(value, (int, float)):
                    values.append(float(value))
        return self._average(values)

    def _distinct_group_hits(self, text: str, groups: Dict[str, List[str]]) -> int:
        hits = 0
        for keywords in groups.values():
            if self._count_keywords(self._tokenize(text), keywords) > 0:
                hits += 1
        return hits

    def _compute_core_affect(self, text: str, tokens: List[str], sentences: List[str]) -> Dict[str, Any]:
        lex = self.lexicon["core_affect"]
        pos_words = lex["positive_words"]
        neg_words = lex["negative_words"]

        pos_count = self._count_keywords(tokens, pos_words)
        neg_count = self._count_keywords(tokens, neg_words)
        sentiment_total = max(pos_count + neg_count, 1)

        sentence_scores: List[float] = []
        for sentence in sentences:
            sentence_tokens = self._tokenize(sentence)
            sp = self._count_keywords(sentence_tokens, pos_words)
            sn = self._count_keywords(sentence_tokens, neg_words)
            denom = max(sp + sn, 1)
            sentence_scores.append(round((sp - sn) / denom, 4))

        if len(sentence_scores) > 1:
            variability = statistics.pstdev(sentence_scores)
        else:
            variability = 0.0

        third = max(len(sentence_scores) // 3, 1)
        first_avg = self._average(sentence_scores[:third])
        last_avg = self._average(sentence_scores[-third:])
        drift_delta = round(last_avg - first_avg, 4)
        if drift_delta > 0.1:
            drift_direction = "improving"
        elif drift_delta < -0.1:
            drift_direction = "declining"
        else:
            drift_direction = "stable"

        emotion_counts: Dict[str, int] = {}
        emotion_total = 0
        for emotion_name, words in lex["emotion_categories"].items():
            count = self._count_keywords(tokens, words)
            emotion_counts[emotion_name] = count
            emotion_total += count

        intensifier_count = self._count_keywords(tokens, lex["intensifiers"])
        mixed_marker_count = self._count_patterns(text, lex["mixed_emotion_patterns"])

        return {
            "sentiment_overall": round((pos_count - neg_count) / sentiment_total, 4),
            "sentiment_per_sentence": sentence_scores,
            "emotional_stability": round(max(0.0, 1.0 - min(1.0, variability)), 4),
            "drift_direction": drift_direction,
            "emotion_counts": emotion_counts,
            "emotional_word_density": self._ratio(emotion_total, max(len(tokens), 1)),
            "emotional_variability": self._ratio(sum(1 for v in emotion_counts.values() if v > 0), max(len(emotion_counts), 1)),
            "emotional_intensity": self._bounded_score(intensifier_count + mixed_marker_count, scale=max(emotion_total, 1)),
            "mixed_emotion_markers": mixed_marker_count,
        }

    def _compute_cognitive_patterns(self, text: str, tokens: List[str], sentences: List[str]) -> Dict[str, Any]:
        lex = self.lexicon["cognitive_patterns"]

        self_negative_hits = self._count_patterns(text, lex["self_negative_patterns"])

        distortions: Dict[str, float] = {}
        distortion_raw_total = 0
        for subtype, patterns in lex["cognitive_distortions"].items():
            hits = self._count_patterns(text, patterns)
            distortion_raw_total += hits
            distortions[subtype] = self._ratio(hits, max(len(sentences), 1))

        ambivalence_hits = self._count_patterns(text, lex["ambivalence_patterns"])
        uncertainty_hits = self._count_patterns(text, lex["uncertainty_patterns"])
        metacognition_hits = self._count_patterns(text, lex["metacognition_patterns"])

        repeated_pairs = 0
        if len(tokens) > 1:
            pairs = Counter(zip(tokens, tokens[1:]))
            repeated_pairs = sum(count - 1 for count in pairs.values() if count > 1)

        rigidity_raw = (
            self._count_patterns(text, lex["cognitive_distortions"]["black_white"])
            + self._count_patterns(text, lex["cognitive_distortions"]["should_statements"])
        )
        flexibility_raw = metacognition_hits + ambivalence_hits

        return {
            "self_negative_score": self._ratio(self_negative_hits, max(len(sentences), 1)),
            "cognitive_distortions": distortions,
            "rumination_score": self._ratio(self_negative_hits + repeated_pairs, max(len(tokens), 1)),
            "cognitive_rigidity_score": self._ratio(rigidity_raw, max(len(sentences), 1)),
            "cognitive_flexibility_score": self._ratio(flexibility_raw, max(len(sentences), 1)),
            "ambivalence_score": self._ratio(ambivalence_hits, max(len(sentences), 1)),
            "uncertainty_score": self._ratio(uncertainty_hits, max(len(sentences), 1)),
            "metacognition_markers": metacognition_hits,
        }

    def _compute_emotional_granularity(self, text: str, tokens: List[str], sentences: List[str]) -> Dict[str, Any]:
        core = self.lexicon["core_affect"]
        ext = self._runtime_group("emotional_granularity")
        pos_words = core["positive_words"]
        neg_words = core["negative_words"]

        high_arousal = ext["high_arousal_words"]
        low_arousal = ext["low_arousal_words"]

        sentence_states: List[Tuple[float, float, int]] = []
        dominant_emotions: List[str] = []
        blended = 0

        for sentence in sentences:
            stoks = self._tokenize(sentence)
            pos = self._count_keywords(stoks, pos_words)
            neg = self._count_keywords(stoks, neg_words)
            hi = self._count_keywords(stoks, high_arousal)
            lo = self._count_keywords(stoks, low_arousal)

            valence = (pos - neg) / max(pos + neg, 1)
            arousal = (hi - lo) / max(hi + lo, 1)

            emotion_hits = []
            for label, words in core["emotion_categories"].items():
                hit = self._count_keywords(stoks, words)
                if hit > 0:
                    emotion_hits.append((label, hit))

            if len(emotion_hits) > 1 or (pos > 0 and neg > 0):
                blended += 1

            if emotion_hits:
                dominant_emotions.append(sorted(emotion_hits, key=lambda item: item[1], reverse=True)[0][0])

            sentence_states.append((valence, arousal, len(emotion_hits)))

        transitions = 0
        for idx in range(1, len(dominant_emotions)):
            if dominant_emotions[idx] != dominant_emotions[idx - 1]:
                transitions += 1

        anxious_excited = self._count_keywords(tokens, ext["mixed_state_pairs"]["anxious_set"]) * self._count_keywords(tokens, ext["mixed_state_pairs"]["excited_set"])
        sad_angry = self._count_keywords(tokens, ext["mixed_state_pairs"]["sad_set"]) * self._count_keywords(tokens, ext["mixed_state_pairs"]["angry_set"])
        hopeful_fearful = self._count_keywords(tokens, ext["mixed_state_pairs"]["hopeful_set"]) * self._count_keywords(tokens, ext["mixed_state_pairs"]["fearful_set"])

        avg_valence = self._average([item[0] for item in sentence_states])
        avg_arousal = self._average([item[1] for item in sentence_states])
        denom_sent = max(len(sentences), 1)

        return {
            "blended_emotion_score": self._ratio(blended, denom_sent),
            "emotion_transition_rate": self._ratio(transitions, max(len(dominant_emotions) - 1, 1)),
            "emotional_state_entropy": self._ratio(sum(1 for _, _, count in sentence_states if count > 1), denom_sent),
            "valence_arousal_coordinates": {
                "valence": avg_valence,
                "arousal": avg_arousal,
            },
            "mixed_state_markers": {
                "anxious_excited": anxious_excited,
                "sad_angry": sad_angry,
                "hopeful_fearful": hopeful_fearful,
            },
            "emotional_granularity_confidence": self._confidence(blended + transitions, len(dominant_emotions), max(len(tokens), 1)),
        }

    def _compute_cognitive_control(self, text: str, tokens: List[str], sentences: List[str]) -> Dict[str, Any]:
        thought = self.lexicon["thought_speed"]
        ext = self._runtime_group("cognitive_control")
        narrowing_keywords = ext["narrowing_keywords"]
        threat_keywords = ext["threat_keywords"]
        unfinished_markers = ext["unfinished_markers"]
        planning_keywords = ext["planning_keywords"]
        overload_keywords = ext["overload_keywords"]

        narrowing_hits = self._count_keywords(tokens, narrowing_keywords) + self._count_keywords(tokens, threat_keywords)
        shifts = self._count_patterns(text, thought["topic_shift_markers"]) + self._count_patterns(text, [re.escape(marker) for marker in unfinished_markers])
        planning_hits = self._count_keywords(tokens, planning_keywords)
        overload_hits = self._count_keywords(tokens, overload_keywords)

        exec_raw = (overload_hits + shifts) - planning_hits
        exec_score = self._clamped(exec_raw / max(len(sentences), 1))

        return {
            "attentional_narrowing_score": self._ratio(narrowing_hits, max(len(tokens), 1)),
            "distractibility_score": self._ratio(shifts, max(len(sentences), 1)),
            "executive_strain_score": exec_score,
            "cognitive_control_confidence": self._confidence(shifts, narrowing_hits + planning_hits + overload_hits, max(len(tokens), 1)),
        }

    def _compute_discourse_process(self, text: str, tokens: List[str], sentences: List[str]) -> Dict[str, Any]:
        denom = max(len(tokens), 1)
        ext = self._runtime_group("discourse_process")
        victim_markers = ext["victim_markers"]
        agent_markers = ext["agent_markers"]
        learner_markers = ext["learner_markers"]
        causal_markers = ext["causal_markers"]
        mentalization_markers = ext["mentalization_markers"]
        certainty_markers = ext["certainty_markers"]
        counterfactual_markers = ext["counterfactual_markers"]

        victim_hits = self._count_keywords(tokens, victim_markers)
        agent_hits = self._count_keywords(tokens, agent_markers)
        learner_hits = self._count_keywords(tokens, learner_markers)
        role_total = victim_hits + agent_hits + learner_hits

        role_balance = {
            "victim": self._ratio(victim_hits, max(role_total, 1)),
            "agent": self._ratio(agent_hits, max(role_total, 1)),
            "learner": self._ratio(learner_hits, max(role_total, 1)),
        }

        causal_hits = self._count_keywords(tokens, causal_markers)
        causal_depth = self._ratio(causal_hits, max(len(sentences), 1))

        mentalization_hits = self._count_keywords(tokens, mentalization_markers)
        certainty_hits = self._count_keywords(tokens, certainty_markers)
        mentalization_score = self._clamped((mentalization_hits + 1) / max(mentalization_hits + certainty_hits + 1, 1))

        counterfactual_hits = self._count_keywords(tokens, counterfactual_markers)

        return {
            "narrative_role_balance": role_balance,
            "causal_coherence_depth": causal_depth,
            "mentalization_score": mentalization_score,
            "counterfactual_load": self._ratio(counterfactual_hits, denom),
            "discourse_confidence": self._confidence(causal_hits + counterfactual_hits, mentalization_hits + role_total, denom),
        }

    def _compute_cognitive_style(self, text: str, tokens: List[str], sentences: List[str]) -> Dict[str, Any]:
        denom = max(len(tokens), 1)
        ext = self._runtime_group("cognitive_style")
        rigid_markers = ext["rigid_markers"]
        uncertainty_markers = ext["uncertainty_markers"]
        evidence_markers = ext["evidence_markers"]
        claim_markers = ext["claim_markers"]
        problem_markers = ext["problem_markers"]
        option_markers = ext["option_markers"]
        choice_markers = ext["choice_markers"]
        reflection_markers = ext["reflection_markers"]

        rigid_hits = self._count_keywords(tokens, rigid_markers)
        uncertain_hits = self._count_keywords(tokens, uncertainty_markers)
        certainty_rigidity = self._clamped((rigid_hits - uncertain_hits + 3) / 6.0)

        evidence_hits = self._count_keywords(tokens, evidence_markers)
        claim_hits = self._count_keywords(tokens, claim_markers)
        evidence_reasoning = self._clamped((evidence_hits + 1) / max(claim_hits + 1, 1))

        completeness_parts = 0
        if self._count_keywords(tokens, problem_markers) > 0:
            completeness_parts += 1
        if self._count_keywords(tokens, option_markers) > 0:
            completeness_parts += 1
        if self._count_keywords(tokens, choice_markers) > 0:
            completeness_parts += 1
        if self._count_keywords(tokens, reflection_markers) > 0:
            completeness_parts += 1

        return {
            "certainty_rigidity_score": certainty_rigidity,
            "evidence_based_reasoning_score": evidence_reasoning,
            "problem_solving_completeness": self._ratio(completeness_parts, 4),
            "cognitive_style_confidence": self._confidence(rigid_hits, evidence_hits + claim_hits + completeness_parts, denom),
        }

    def _compute_identity(self, text: str, tokens: List[str]) -> Dict[str, Any]:
        lex = self.lexicon["identity"]
        ext = self._runtime_group("identity")
        denom = max(len(tokens), 1)

        uncertainty_p = self._count_patterns(text, lex["identity_uncertainty_patterns"])
        fragmentation_p = self._count_patterns(text, lex["self_fragmentation_patterns"])
        positive_p = self._count_patterns(text, lex["positive_self_talk"])
        negative_p = self._count_patterns(text, lex["negative_self_talk"])

        uncertainty_k = self._count_keywords(tokens, ext["uncertainty_keywords"])
        fragmentation_k = self._count_keywords(tokens, ext["fragmentation_keywords"])
        positive_k = self._count_keywords(tokens, ext["positive_keywords"])
        negative_k = self._count_keywords(tokens, ext["negative_keywords"])

        return {
            "identity_uncertainty_score": self._hybrid_score(uncertainty_p, uncertainty_k, denom),
            "self_fragmentation_score": self._hybrid_score(fragmentation_p, fragmentation_k, denom),
            "positive_self_talk_score": self._hybrid_score(positive_p, positive_k, denom),
            "negative_self_talk_score": self._hybrid_score(negative_p, negative_k, denom),
            "first_person_ratio": self._first_person_ratio(tokens),
            "identity_confidence": self._confidence(
                uncertainty_p + fragmentation_p + positive_p + negative_p,
                uncertainty_k + fragmentation_k + positive_k + negative_k,
                denom,
            ),
        }

    def _compute_social(self, text: str, tokens: List[str]) -> Dict[str, Any]:
        lex = self.lexicon["social"]
        ext = self._runtime_group("social")
        denom = max(len(tokens), 1)

        withdrawal_p = self._count_patterns(text, lex["withdrawal_patterns"])
        connection_p = self._count_patterns(text, lex["connection_patterns"])
        rejection_p = self._count_patterns(text, lex["perceived_rejection_patterns"])
        hyperfocus_p = self._count_patterns(text, lex["hyperfocus_patterns"])
        attachment_p = self._count_patterns(text, lex["attachment_patterns"])
        boundary_p = self._count_patterns(text, lex["boundary_issue_patterns"])
        trust_p = self._count_patterns(text, lex["trust_mistrust_patterns"])

        withdrawal_k = self._count_keywords(tokens, ext["withdrawal_keywords"])
        connection_k = self._count_keywords(tokens, ext["connection_keywords"])
        rejection_k = self._count_keywords(tokens, ext["rejection_keywords"])
        hyperfocus_k = self._count_keywords(tokens, ext["hyperfocus_keywords"])
        attachment_k = self._count_keywords(tokens, ext["attachment_keywords"])
        boundary_k = self._count_keywords(tokens, ext["boundary_keywords"])
        trust_k = self._count_keywords(tokens, ext["trust_keywords"])

        return {
            "social_withdrawal_score": self._hybrid_score(withdrawal_p, withdrawal_k, denom),
            "social_connection_score": self._hybrid_score(connection_p, connection_k, denom),
            "perceived_rejection_score": self._hybrid_score(rejection_p, rejection_k, denom),
            "hyperfocus_on_others_opinions_score": self._hybrid_score(hyperfocus_p, hyperfocus_k, denom),
            "attachment_language_score": self._hybrid_score(attachment_p, attachment_k, denom),
            "boundary_issue_score": self._hybrid_score(boundary_p, boundary_k, denom),
            "trust_mistrust_score": self._hybrid_score(trust_p, trust_k, denom),
            "social_confidence": self._confidence(
                withdrawal_p + connection_p + rejection_p + hyperfocus_p + attachment_p + boundary_p + trust_p,
                withdrawal_k + connection_k + rejection_k + hyperfocus_k + attachment_k + boundary_k + trust_k,
                denom,
            ),
        }

    def _compute_behavioral_intent(self, text: str, tokens: List[str]) -> Dict[str, Any]:
        lex = self.lexicon["behavioral_intent"]
        ext = self._runtime_group("behavioral_intent")
        denom = max(len(tokens), 1)

        action_p = self._count_patterns(text, lex["action_orientation_patterns"])
        freeze_p = self._count_patterns(text, lex["behavioral_freeze_patterns"])
        avoidance_p = self._count_patterns(text, lex["avoidance_behavior_patterns"])
        adaptive_p = self._count_patterns(text, lex["adaptive_coping_patterns"])
        maladaptive_p = self._count_patterns(text, lex["maladaptive_coping_patterns"])
        avoidant_p = self._count_patterns(text, lex["avoidant_coping_patterns"])
        help_p = self._count_patterns(text, lex["help_seeking_patterns"])

        action_k = self._count_keywords(tokens, ext["action_keywords"])
        freeze_k = self._count_keywords(tokens, ext["freeze_keywords"])
        avoidance_k = self._count_keywords(tokens, ext["avoidance_keywords"])
        adaptive_k = self._count_keywords(tokens, ext["adaptive_keywords"])
        maladaptive_k = self._count_keywords(tokens, ext["maladaptive_keywords"])
        avoidant_k = self._count_keywords(tokens, ext["avoidant_keywords"])
        help_k = self._count_keywords(tokens, ext["help_keywords"])

        return {
            "action_orientation_score": self._hybrid_score(action_p, action_k, denom),
            "behavioral_freeze_score": self._hybrid_score(freeze_p, freeze_k, denom),
            "avoidance_behavior_score": self._hybrid_score(avoidance_p, avoidance_k, denom),
            "coping_strategy_adaptive": self._hybrid_score(adaptive_p, adaptive_k, denom),
            "coping_strategy_maladaptive": self._hybrid_score(maladaptive_p, maladaptive_k, denom),
            "coping_strategy_avoidant": self._hybrid_score(avoidant_p, avoidant_k, denom),
            "help_seeking_score": self._hybrid_score(help_p, help_k, denom),
            "behavioral_confidence": self._confidence(
                action_p + freeze_p + avoidance_p + adaptive_p + maladaptive_p + avoidant_p + help_p,
                action_k + freeze_k + avoidance_k + adaptive_k + maladaptive_k + avoidant_k + help_k,
                denom,
            ),
        }

    def _compute_interpersonal_stance(self, text: str, tokens: List[str]) -> Dict[str, Any]:
        denom = max(len(tokens), 1)
        ext = self._runtime_group("interpersonal_stance")
        assertive = ext["assertive_keywords"]
        passive = ext["passive_keywords"]
        give_words = ext["give_keywords"]
        receive_words = ext["receive_keywords"]

        styles = ext["styles"]

        assertive_hits = self._count_keywords(tokens, assertive)
        passive_hits = self._count_keywords(tokens, passive)
        assertive_vs_passive = self._clamped((assertive_hits - passive_hits + 3) / 6.0)

        style_scores: Dict[str, float] = {}
        style_total = 0
        for style, words in styles.items():
            hit = self._count_keywords(tokens, words)
            style_total += hit
            style_scores[style] = self._ratio(hit, denom)

        i_ratio = self._ratio(sum(1 for tok in tokens if tok in {"i", "me", "my", "mine"}), denom)
        you_we_ratio = self._ratio(sum(1 for tok in tokens if tok in {"you", "your", "we", "our", "us"}), denom)
        exchange = self._count_keywords(tokens, give_words) + self._count_keywords(tokens, receive_words)
        reciprocity = self._clamped(1.0 - abs(i_ratio - you_we_ratio) + (exchange / max(denom, 1)))

        return {
            "assertiveness_vs_passivity_score": assertive_vs_passive,
            "conflict_style_markers": style_scores,
            "reciprocity_score": reciprocity,
            "interpersonal_confidence": self._confidence(style_total, assertive_hits + passive_hits + exchange, denom),
        }

    def _compute_relational_depth(self, text: str, tokens: List[str]) -> Dict[str, Any]:
        denom = max(len(tokens), 1)
        ext = self._runtime_group("relational_depth")
        domains = ext["domains"]
        attachment_reactivity = ext["attachment_reactivity_keywords"]
        boundary_enactment = ext["boundary_enactment_keywords"]

        profile: Dict[str, float] = {}
        domain_hits = 0
        for name, words in domains.items():
            hit = self._count_keywords(tokens, words)
            if hit > 0:
                domain_hits += 1
            profile[name] = self._ratio(hit, denom)

        attach_hits = self._count_keywords(tokens, attachment_reactivity)
        boundary_hits = self._count_keywords(tokens, boundary_enactment)

        return {
            "relationship_specific_profile": profile,
            "attachment_reactivity_index": self._ratio(attach_hits, denom),
            "boundary_enactment_score": self._ratio(boundary_hits, denom),
            "relational_depth_confidence": self._confidence(domain_hits, attach_hits + boundary_hits, denom),
        }

    def _compute_motivation_reward(self, text: str, tokens: List[str]) -> Dict[str, Any]:
        denom = max(len(tokens), 1)
        ext = self._runtime_group("motivation_reward")
        anticipation = ext["anticipation_keywords"]
        enjoyment = ext["enjoyment_keywords"]
        blunted = ext["blunted_keywords"]
        goal_flow = ext["goal_flow"]
        effort_words = ext["effort_words"]
        reward_words = ext["reward_words"]

        anticipation_hits = self._count_keywords(tokens, anticipation)
        enjoyment_hits = self._count_keywords(tokens, enjoyment)
        blunted_hits = self._count_keywords(tokens, blunted)

        anhedonia_raw = blunted_hits + max(0, 2 - (anticipation_hits + enjoyment_hits))

        goal_stage_hits = {stage: self._count_keywords(tokens, words) for stage, words in goal_flow.items()}
        momentum = self._ratio(sum(1 for count in goal_stage_hits.values() if count > 0), max(len(goal_stage_hits), 1))

        effort_hits = self._count_keywords(tokens, effort_words)
        reward_hits = self._count_keywords(tokens, reward_words)
        mismatch = self._clamped((effort_hits - reward_hits + 2) / 5.0)

        return {
            "anhedonia_proxy_score": self._ratio(anhedonia_raw, denom),
            "goal_pursuit_momentum": momentum,
            "effort_reward_mismatch_score": mismatch,
            "motivation_confidence": self._confidence(blunted_hits, anticipation_hits + enjoyment_hits + effort_hits + reward_hits, denom),
        }

    def _compute_behavioral_execution(self, text: str, tokens: List[str]) -> Dict[str, Any]:
        denom = max(len(tokens), 1)
        ext = self._runtime_group("behavioral_execution")
        intention_words = ext["intention_words"]
        action_words = ext["action_words"]

        adaptive_habit_words = ext["adaptive_habit_words"]
        passive_avoidance = ext["passive_avoidance"]
        active_escape = ext["active_escape"]
        cognitive_avoidance = ext["cognitive_avoidance"]

        intention_hits = self._count_keywords(tokens, intention_words)
        action_hits = self._count_keywords(tokens, action_words)
        intention_action_gap = self._clamped((intention_hits - action_hits + 3) / 6.0)

        token_counts = Counter(tokens)
        habit_hits = sum(count for token, count in token_counts.items() if token in set(adaptive_habit_words) and count > 1)

        subtype_profile = {
            "passive_delay": self._ratio(self._count_keywords(tokens, passive_avoidance), denom),
            "active_escape": self._ratio(self._count_keywords(tokens, active_escape), denom),
            "cognitive_avoidance": self._ratio(self._count_keywords(tokens, cognitive_avoidance), denom),
        }

        return {
            "intention_action_gap_score": intention_action_gap,
            "habit_consistency_score": self._ratio(habit_hits, denom),
            "avoidance_subtype_profile": subtype_profile,
            "behavioral_execution_confidence": self._confidence(intention_hits, action_hits + habit_hits, denom),
        }

    def _compute_regulation(self, text: str, tokens: List[str], sentences: List[str]) -> Dict[str, Any]:
        lex = self.lexicon["regulation"]
        ext = self._runtime_group("regulation")
        denom = max(len(tokens), 1)

        load_factor = 0.0
        if sentences:
            lengths = [len(self._tokenize(sentence)) for sentence in sentences]
            mean_len = self._average([float(length) for length in lengths])
            variance = statistics.pvariance(lengths) if len(lengths) > 1 else 0.0
            load_factor = self._bounded_score(mean_len + variance / 25.0, scale=40.0)

        emotion_label_count = self._count_keywords(tokens, lex["emotion_labeling_words"])
        emotion_diff_count = self._count_keywords(tokens, lex["emotion_differentiation_words"])

        thought_lex = self.lexicon["thought_speed"]
        racing_count = self._count_patterns(text, thought_lex["racing_markers"])
        slowed_count = self._count_patterns(text, thought_lex["slowed_markers"])
        energy_raw = max(racing_count - slowed_count, 0) + text.count("!")

        agency_loss_p = self._count_patterns(text, lex["agency_loss_patterns"])
        agency_gain_p = self._count_patterns(text, lex["agency_reclamation_patterns"])
        escalation_p = self._count_patterns(text, lex["escalation_patterns"])
        deescalation_p = self._count_patterns(text, lex["deescalation_patterns"])
        suppression_p = self._count_patterns(text, lex["emotional_suppression_patterns"])

        agency_loss_k = self._count_keywords(tokens, ext["agency_loss_keywords"])
        agency_gain_k = self._count_keywords(tokens, ext["agency_gain_keywords"])
        escalation_k = self._count_keywords(tokens, ext["escalation_keywords"])
        deescalation_k = self._count_keywords(tokens, ext["deescalation_keywords"])
        suppression_k = self._count_keywords(tokens, ext["suppression_keywords"])

        return {
            "agency_loss_score": self._hybrid_score(agency_loss_p, agency_loss_k, denom),
            "agency_reclamation_score": self._hybrid_score(agency_gain_p, agency_gain_k, denom),
            "escalation_language_score": self._hybrid_score(escalation_p, escalation_k, denom),
            "deescalation_language_score": self._hybrid_score(deescalation_p, deescalation_k, denom),
            "emotional_suppression_score": self._hybrid_score(suppression_p, suppression_k, denom),
            "emotional_labeling_skill": self._ratio(emotion_label_count, denom),
            "emotional_differentiation_score": self._bounded_score(float(emotion_diff_count), scale=float(max(emotion_label_count, 1))),
            "cognitive_load_indicator": load_factor,
            "linguistic_energy_score": self._ratio(energy_raw, max(len(sentences), 1)),
            "regulation_confidence": self._confidence(
                agency_loss_p + agency_gain_p + escalation_p + deescalation_p + suppression_p,
                agency_loss_k + agency_gain_k + escalation_k + deescalation_k + suppression_k + emotion_label_count,
                denom,
            ),
        }

    def _compute_stress_recovery(self, text: str, tokens: List[str], sentences: List[str]) -> Dict[str, Any]:
        denom = max(len(tokens), 1)
        ext = self._runtime_group("stress_recovery")
        distress_words = ext["distress_words"]
        urgency_words = ext["urgency_words"]
        recovery_words = ext["recovery_words"]
        adaptive_words = ext["adaptive_words"]

        distress_hits = self._count_keywords(tokens, distress_words)
        urgency_hits = self._count_keywords(tokens, urgency_words) + text.count("!")
        recovery_hits = self._count_keywords(tokens, recovery_words)
        adaptive_hits = self._count_keywords(tokens, adaptive_words)

        acute_index = self._ratio(distress_hits + urgency_hits, max(len(sentences), 1))
        recovery_score = self._ratio(recovery_hits + adaptive_hits, denom)

        distress_idx = -1
        recovery_idx = -1
        for idx, sentence in enumerate(sentences):
            stoks = self._tokenize(sentence)
            if distress_idx < 0 and self._count_keywords(stoks, distress_words) > 0:
                distress_idx = idx
            if self._count_keywords(stoks, recovery_words) > 0:
                recovery_idx = idx
                if distress_idx >= 0:
                    break

        latency = 1.0
        if distress_idx >= 0 and recovery_idx >= distress_idx:
            latency = self._ratio(recovery_idx - distress_idx, max(len(sentences) - 1, 1))

        return {
            "acute_stress_spike_index": acute_index,
            "recovery_behavior_score": recovery_score,
            "recovery_latency_proxy": latency,
            "stress_recovery_confidence": self._confidence(distress_hits, recovery_hits + adaptive_hits + urgency_hits, denom),
        }

    def _compute_physiological_dynamics(self, text: str, tokens: List[str]) -> Dict[str, Any]:
        denom = max(len(tokens), 1)
        ext = self._runtime_group("physiological_dynamics")
        arousal_words = ext["arousal_words"]
        regulation_words = ext["regulation_words"]
        somatic_cluster = ext["somatic_cluster"]

        arousal_hits = self._count_keywords(tokens, arousal_words)
        regulation_hits = self._count_keywords(tokens, regulation_words)
        autonomic_load = self._clamped((arousal_hits - regulation_hits + 3) / 6.0)

        cluster_counts: Dict[str, int] = {}
        active_clusters = 0
        for cluster, words in somatic_cluster.items():
            hit = self._count_keywords(tokens, words)
            cluster_counts[cluster] = hit
            if hit > 0:
                active_clusters += 1

        recovery_norm = self._clamped((regulation_hits + 1) / max(arousal_hits + 1, 1))

        return {
            "autonomic_load_proxy": autonomic_load,
            "somatic_clustering_index": self._ratio(active_clusters, max(len(somatic_cluster), 1)),
            "recovery_physiology_proxy": recovery_norm,
            "physiological_confidence": self._confidence(arousal_hits, regulation_hits + active_clusters, denom),
            "somatic_cluster_counts": cluster_counts,
        }

    def _compute_temporal(self, text: str, tokens: List[str]) -> Dict[str, Any]:
        lex = self.lexicon["temporal"]
        past_hits = self._count_patterns(text, lex["past_markers"])
        present_hits = self._count_patterns(text, lex["present_markers"])
        future_hits = self._count_patterns(text, lex["future_markers"])
        total = max(past_hits + present_hits + future_hits, 1)

        return {
            "past_focus_score": self._ratio(past_hits, max(len(tokens), 1)),
            "present_focus_score": self._ratio(present_hits, max(len(tokens), 1)),
            "future_focus_score": self._ratio(future_hits, max(len(tokens), 1)),
            "temporal_orientation_ratios": {
                "past": self._ratio(past_hits, total),
                "present": self._ratio(present_hits, total),
                "future": self._ratio(future_hits, total),
            },
        }

    def _compute_sleep_circadian(self, text: str, tokens: List[str]) -> Dict[str, Any]:
        denom = max(len(tokens), 1)
        ext = self._runtime_group("sleep_circadian")
        irregular_markers = ext["irregular_markers"]
        onset_markers = ext["onset_markers"]
        maintenance_markers = ext["maintenance_markers"]
        early_waking_markers = ext["early_waking_markers"]
        restoration_markers = ext["restoration_markers"]
        fatigue_markers = ext["fatigue_markers"]

        irregular_hits = self._count_keywords(tokens, irregular_markers)
        onset_hits = self._count_keywords(tokens, onset_markers)
        maintenance_hits = self._count_keywords(tokens, maintenance_markers)
        early_hits = self._count_keywords(tokens, early_waking_markers)
        restoration_hits = self._count_keywords(tokens, restoration_markers)
        fatigue_hits = self._count_keywords(tokens, fatigue_markers)

        return {
            "sleep_timing_irregularity_score": self._ratio(irregular_hits, denom),
            "sleep_quality_subcomponents": {
                "sleep_onset_difficulty": self._ratio(onset_hits, denom),
                "sleep_maintenance_difficulty": self._ratio(maintenance_hits, denom),
                "early_waking": self._ratio(early_hits, denom),
                "restoration_quality": self._clamped(1.0 - self._ratio(restoration_hits, max(onset_hits + maintenance_hits + early_hits + 1, 1))),
            },
            "fatigue_carryover_score": self._ratio(fatigue_hits, denom),
            "sleep_circadian_confidence": self._confidence(onset_hits + maintenance_hits + early_hits, irregular_hits + fatigue_hits + restoration_hits, denom),
        }

    def _compute_somatic(self, text: str, tokens: List[str]) -> Dict[str, Any]:
        lex = self.lexicon["somatic"]
        ext = self._runtime_group("somatic")
        denom = max(len(tokens), 1)

        stress_k = self._count_keywords(tokens, lex["stress_words"])
        sleep_p = self._count_patterns(text, lex["sleep_patterns"])
        somatic_p = self._count_patterns(text, lex["somatic_patterns"])
        energy_k = self._count_keywords(tokens, lex["energy_words"])
        arousal_k = self._count_keywords(tokens, lex["arousal_words"])
        pain_k = self._count_keywords(tokens, lex["pain_words"])

        sleep_k = self._count_keywords(tokens, ext["sleep_keywords"])
        somatic_k = self._count_keywords(tokens, ext["somatic_keywords"])

        return {
            "stress_score": self._hybrid_score(0, stress_k, denom),
            "sleep_issue_score": self._hybrid_score(sleep_p, sleep_k, denom),
            "somatic_language_score": self._hybrid_score(somatic_p, somatic_k, denom),
            "energy_level_score": self._hybrid_score(0, energy_k, denom),
            "arousal_level_score": self._hybrid_score(0, arousal_k, denom),
            "pain_language_score": self._hybrid_score(0, pain_k, denom),
            "somatic_confidence": self._confidence(sleep_p + somatic_p, stress_k + sleep_k + somatic_k + energy_k + arousal_k + pain_k, denom),
        }

    def _compute_existential(self, text: str, tokens: List[str]) -> Dict[str, Any]:
        lex = self.lexicon["existential"]
        ext = self._runtime_group("existential")
        denom = max(len(tokens), 1)

        anxiety_p = self._count_patterns(text, lex["existential_anxiety_patterns"])
        meaning_p = self._count_patterns(text, lex["meaning_making_patterns"])
        purpose_p = self._count_patterns(text, lex["purpose_patterns"])
        values_p = self._count_patterns(text, lex["value_conflict_patterns"])

        anxiety_k = self._count_keywords(tokens, ext["anxiety_keywords"])
        meaning_k = self._count_keywords(tokens, ext["meaning_keywords"])
        purpose_k = self._count_keywords(tokens, ext["purpose_keywords"])
        values_k = self._count_keywords(tokens, ext["values_keywords"])

        return {
            "existential_anxiety_score": self._hybrid_score(anxiety_p, anxiety_k, denom),
            "meaning_making_score": self._hybrid_score(meaning_p, meaning_k, denom),
            "purpose_language_score": self._hybrid_score(purpose_p, purpose_k, denom),
            "value_conflict_score": self._hybrid_score(values_p, values_k, denom),
            "existential_confidence": self._confidence(anxiety_p + meaning_p + purpose_p + values_p, anxiety_k + meaning_k + purpose_k + values_k, denom),
        }

    def _compute_self_coherence(self, text: str, tokens: List[str], sentences: List[str]) -> Dict[str, Any]:
        denom = max(len(tokens), 1)
        temporal = self._compute_temporal(text, tokens)
        identity = self._compute_identity(text, tokens)
        ext = self._runtime_group("self_coherence")

        causal_markers = ext["causal_markers"]
        continuity_markers = ext["continuity_markers"]
        value_words = ext["value_words"]
        action_words = ext["action_words"]

        causal_hits = self._count_keywords(tokens, causal_markers)
        continuity_hits = self._count_keywords(tokens, continuity_markers)
        sentence_lengths = [len(self._tokenize(sentence)) for sentence in sentences] if sentences else [0]
        variance = statistics.pvariance(sentence_lengths) if len(sentence_lengths) > 1 else 0.0

        coherence = self._clamped((causal_hits + continuity_hits) / max(len(sentences), 1) * 0.4 + (1.0 - min(1.0, variance / 100.0)) * 0.6)

        identity_uncertainty = float(identity["identity_uncertainty_score"])
        identity_fragmentation = float(identity["self_fragmentation_score"])
        identity_consistency = self._clamped(1.0 - (identity_uncertainty + identity_fragmentation))

        value_hits = self._count_keywords(tokens, value_words)
        action_hits = self._count_keywords(tokens, action_words)
        congruence = self._clamped(min(value_hits, action_hits) / max(value_hits + action_hits, 1) * 2.0)

        return {
            "narrative_coherence_index": coherence,
            "identity_consistency_score": identity_consistency,
            "value_behavior_congruence_score": congruence,
            "self_coherence_confidence": self._confidence(causal_hits, continuity_hits + value_hits + action_hits, denom),
            "temporal_balance_reference": temporal["temporal_orientation_ratios"],
        }

    def _compute_risk_safety(self, text: str, tokens: List[str], sentences: List[str]) -> Dict[str, Any]:
        denom = max(len(tokens), 1)
        ext = self._runtime_group("risk_safety")
        hopeless_words = ext["hopeless_words"]
        escalation_words = ext["escalation_words"]
        protective_words = ext["protective_words"]

        hopeless_hits = self._count_keywords(tokens, hopeless_words)
        escalation_hits = self._count_keywords(tokens, escalation_words)
        protective_hits = self._count_keywords(tokens, protective_words)

        thirds = max(len(sentences) // 3, 1)
        start = " ".join(sentences[:thirds])
        end = " ".join(sentences[-thirds:])
        start_escalation = self._count_keywords(self._tokenize(start), escalation_words)
        end_escalation = self._count_keywords(self._tokenize(end), escalation_words)
        trajectory = self._clamped((end_escalation - start_escalation + 2) / 4.0)

        hopeless_sentence_count = 0
        for sentence in sentences:
            if self._count_keywords(self._tokenize(sentence), hopeless_words) > 0:
                hopeless_sentence_count += 1

        return {
            "crisis_escalation_trajectory": trajectory,
            "hopelessness_persistence_score": self._ratio(hopeless_sentence_count, max(len(sentences), 1)),
            "protective_factors_score": self._ratio(protective_hits, denom),
            "risk_balance_score": self._clamped((hopeless_hits + escalation_hits) / max(protective_hits + 1, 1)),
            "risk_safety_confidence": self._confidence(hopeless_hits + escalation_hits, protective_hits, denom),
        }

    def _compute_risk_protection_advanced(self, text: str, tokens: List[str]) -> Dict[str, Any]:
        denom = max(len(tokens), 1)
        ext = self._runtime_group("risk_protection_advanced")
        risk_terms = ext["risk_terms"]
        protective_terms = ext["protective_terms"]
        commitment_terms = ext["commitment_terms"]

        component_scores: Dict[str, float] = {}
        composite_raw = 0.0
        for name, words in risk_terms.items():
            score = self._ratio(self._count_keywords(tokens, words), denom)
            component_scores[name] = score
            composite_raw += score

        risk_lattice = self._clamped(composite_raw / max(len(risk_terms), 1) * 3.0)
        protective_hits = self._count_keywords(tokens, protective_terms)
        buffering = self._clamped((protective_hits + 1) / max((composite_raw * denom) + 1, 1))
        commitment_hits = self._count_keywords(tokens, commitment_terms)

        return {
            "multi_factor_risk_lattice": risk_lattice,
            "risk_component_scores": component_scores,
            "protective_buffering_index": buffering,
            "ambivalence_to_safety_marker": self._clamped(commitment_hits / max(int(composite_raw * denom) + 1, 1)),
            "risk_protection_confidence": self._confidence(int(composite_raw * denom), protective_hits + commitment_hits, denom),
        }

    def _compute_longitudinal_dynamics(self, text: str, history_entries: Union[None, List[str]]) -> Dict[str, Any]:
        series = history_entries if isinstance(history_entries, list) and history_entries else [text]
        ext = self._runtime_group("longitudinal_dynamics")

        normalized_entries = [self._normalize_text(item) for item in series if isinstance(item, str) and item.strip()]
        if not normalized_entries:
            normalized_entries = [text]

        stress_words = ext["stress_words"]
        mood_words = {
            "positive": self.lexicon["core_affect"]["positive_words"],
            "negative": self.lexicon["core_affect"]["negative_words"],
        }
        protective_words = ext["protective_words"]

        stress_series: List[float] = []
        mood_series: List[float] = []
        protective_series: List[float] = []

        for entry in normalized_entries:
            toks = self._tokenize(entry)
            denom = max(len(toks), 1)
            stress_series.append(self._ratio(self._count_keywords(toks, stress_words), denom))
            pos = self._count_keywords(toks, mood_words["positive"])
            neg = self._count_keywords(toks, mood_words["negative"])
            mood_series.append(round((pos - neg) / max(pos + neg, 1), 4))
            protective_series.append(self._ratio(self._count_keywords(toks, protective_words), denom))

        n = len(normalized_entries)
        slope = 0.0
        if n > 1:
            slope = round((stress_series[-1] - stress_series[0]) / max(n - 1, 1), 4)

        volatility = round(statistics.pstdev(stress_series), 4) if len(stress_series) > 1 else 0.0
        sustained_windows = sum(1 for val in stress_series if val >= self._average(stress_series) + 0.01)

        threshold = self._average(stress_series) + (statistics.pstdev(stress_series) if len(stress_series) > 1 else 0.0)
        episodes = 0
        in_episode = False
        for value in stress_series:
            if value > threshold and not in_episode:
                episodes += 1
                in_episode = True
            elif value <= threshold:
                in_episode = False

        early_warning = self._clamped((max(slope, 0.0) * 8.0) + (volatility * 3.0))
        protective_trend = round((protective_series[-1] - protective_series[0]) if len(protective_series) > 1 else protective_series[0], 4)

        return {
            "entry_count": n,
            "trajectory_stability": {
                "stress_slope": slope,
                "stress_volatility": volatility,
                "sustained_elevation_windows": sustained_windows,
            },
            "episode_segmentation_count": episodes,
            "early_warning_index": early_warning,
            "protective_trend_index": protective_trend,
            "timeline_preview": {
                "stress": stress_series,
                "mood": mood_series,
                "protective": protective_series,
            },
            "longitudinal_confidence": self._clamped(min(1.0, n / 5.0)),
        }

    def _compute_calibration_monitoring(self, result: Dict[str, Any]) -> Dict[str, Any]:
        confidence_values: List[float] = []
        low_coverage_categories = 0
        numeric_metric_total = 0
        numeric_metric_nonzero = 0

        for category in self.CATEGORY_ORDER:
            if category not in result or not isinstance(result[category], dict):
                continue

            category_numeric = [float(v) for v in result[category].values() if isinstance(v, (int, float))]
            numeric_metric_total += len(category_numeric)
            numeric_metric_nonzero += sum(1 for v in category_numeric if v > 0)

            if category_numeric:
                coverage = sum(1 for v in category_numeric if v > 0) / max(len(category_numeric), 1)
                if coverage < 0.25:
                    low_coverage_categories += 1

            for key, value in result[category].items():
                if "confidence" in key and isinstance(value, (int, float)):
                    confidence_values.append(float(value))

        avg_conf = self._average(confidence_values)
        conf_std = round(statistics.pstdev(confidence_values), 4) if len(confidence_values) > 1 else 0.0
        n = max(len(confidence_values), 1)
        margin = round(1.96 * (conf_std / (n ** 0.5)), 4)

        ci_low = self._clamped(avg_conf - margin)
        ci_high = self._clamped(avg_conf + margin)

        drift_risk = self._clamped((low_coverage_categories / max(len(self.CATEGORY_ORDER), 1)) + conf_std)
        global_coverage = self._ratio(numeric_metric_nonzero, max(numeric_metric_total, 1))

        return {
            "calibration_quality": avg_conf,
            "confidence_interval_95": {
                "low": ci_low,
                "high": ci_high,
            },
            "global_construct_coverage": global_coverage,
            "drift_monitor_score": drift_risk,
            "low_coverage_category_count": low_coverage_categories,
            "calibration_confidence": self._clamped(1.0 - conf_std),
        }

    def _build_analyzer_score_report(
        self,
        result: Dict[str, Any],
        selected_categories: List[str],
        cleaned_text: str,
        word_count: int,
        normalize_scores: bool,
    ) -> Dict[str, Any]:
        checksum = sha256(cleaned_text.encode("utf-8")).hexdigest()
        analyzed_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        categories_report: Dict[str, Any] = {}
        overall_sum = 0.0
        overall_numeric_count = 0
        tested_category_count = 0

        for category in selected_categories:
            data = result.get(category)
            if not isinstance(data, dict):
                continue

            numeric_items = [(key, float(value)) for key, value in data.items() if isinstance(value, (int, float))]
            numeric_count = len(numeric_items)
            if numeric_count == 0:
                continue

            tested_category_count += 1
            metric_values = [self._normalize_report_value(value) if normalize_scores else value for _, value in numeric_items]
            score_sum = round(sum(metric_values), 4)
            score_avg = round(score_sum / numeric_count, 4)
            non_zero_count = sum(1 for value in metric_values if value > 0)
            top_metric_name, top_metric_value = max(numeric_items, key=lambda item: item[1])

            categories_report[category] = {
                "numeric_metric_count": numeric_count,
                "non_zero_metric_count": non_zero_count,
                "category_score_sum": score_sum,
                "category_score_average": score_avg,
                "coverage_ratio": self._ratio(non_zero_count, numeric_count),
                "top_metric": {
                    "name": top_metric_name,
                    "value": round(self._normalize_report_value(top_metric_value) if normalize_scores else top_metric_value, 4),
                },
            }

            overall_sum += score_sum
            overall_numeric_count += numeric_count

        overall_average = round(overall_sum / overall_numeric_count, 4) if overall_numeric_count > 0 else 0.0

        return {
            "header": {
                "analyzer_version": self.__version__,
                "word_count": word_count,
                "analysis_datetime_utc": analyzed_at,
                "text_checksum_sha256": checksum,
                "score_normalization_used": normalize_scores,
                "score_normalization_strategy": "bounded_piecewise_v1" if normalize_scores else "none",
            },
            "totals": {
                "tested_category_count": tested_category_count,
                "total_numeric_metric_count": overall_numeric_count,
                "overall_score_sum": round(overall_sum, 4),
                "overall_score_average": overall_average,
            },
            "categories": categories_report,
        }

    def _normalize_report_value(self, value: float) -> float:
        if 0.0 <= value <= 1.0:
            return round(value, 4)
        if -1.0 <= value < 0.0:
            return round((value + 1.0) / 2.0, 4)
        return round(abs(value) / (1.0 + abs(value)), 4)

    def _compute_resilience_strengths(self, text: str, tokens: List[str]) -> Dict[str, Any]:
        denom = max(len(tokens), 1)
        ext = self._runtime_group("resilience_strengths")
        coping_groups = ext["coping_groups"]
        efficacy_words = ext["efficacy_words"]
        anti_efficacy_words = ext["anti_efficacy_words"]
        reconstruction_words = ext["reconstruction_words"]

        distinct_groups = self._distinct_group_hits(text, coping_groups)
        efficacy_hits = self._count_keywords(tokens, efficacy_words)
        anti_hits = self._count_keywords(tokens, anti_efficacy_words)
        meaning_hits = self._count_keywords(tokens, reconstruction_words)

        self_efficacy = self._clamped((efficacy_hits - anti_hits + 3) / 6.0)

        return {
            "coping_flexibility_index": self._ratio(distinct_groups, max(len(coping_groups), 1)),
            "self_efficacy_trend_score": self_efficacy,
            "meaning_reconstruction_strength": self._ratio(meaning_hits, denom),
            "resilience_confidence": self._confidence(distinct_groups, efficacy_hits + meaning_hits, denom),
        }

    def _compute_linguistic_structure(self, text: str, tokens: List[str], sentences: List[str]) -> Dict[str, Any]:
        lex = self.lexicon["linguistic_structure"]
        denom = max(len(tokens), 1)

        sentence_lengths = [len(self._tokenize(sentence)) for sentence in sentences] if sentences else [0]
        variance = statistics.pvariance(sentence_lengths) if len(sentence_lengths) > 1 else 0.0
        long_sentences = sum(1 for length in sentence_lengths if length >= 30)

        exclusion = set(word.lower() for word in lex["lexical_variety_exclusions"])
        content_tokens = [tok for tok in tokens if tok not in exclusion]
        lexical_variety = self._ratio(len(set(content_tokens)), max(len(content_tokens), 1))

        return {
            "disorganization_score": self._ratio(self._count_patterns(text, lex["disorganization_markers"]), denom),
            "overcontrolled_language_score": self._ratio(self._count_patterns(text, lex["overcontrolled_markers"]), denom),
            "run_on_sentence_score": self._ratio(
                long_sentences + self._count_patterns(text, lex["run_on_markers"]),
                max(len(sentences), 1),
            ),
            "sentence_length_variance": round(variance, 4),
            "lexical_variety_score": lexical_variety,
        }

    def _compute_thought_speed(self, text: str, tokens: List[str], sentences: List[str]) -> Dict[str, Any]:
        lex = self.lexicon["thought_speed"]
        denom = max(len(tokens), 1)

        repeated_tokens = 0
        token_counts = Counter(tokens)
        for count in token_counts.values():
            if count > 2:
                repeated_tokens += count - 2

        return {
            "racing_thoughts_score": self._ratio(self._count_patterns(text, lex["racing_markers"]), denom),
            "slowed_thoughts_score": self._ratio(self._count_patterns(text, lex["slowed_markers"]), denom),
            "repetition_score": self._ratio(repeated_tokens + self._count_patterns(text, lex["repetition_markers"]), denom),
            "topic_shift_score": self._ratio(self._count_patterns(text, lex["topic_shift_markers"]), max(len(sentences), 1)),
        }

    def _compute_meta_signals(self, text: str, tokens: List[str], sentences: List[str]) -> Dict[str, Any]:
        affect = self._compute_core_affect(text, tokens, sentences)
        cognition = self._compute_cognitive_patterns(text, tokens, sentences)
        behavior = self._compute_behavioral_intent(text, tokens)

        positive = self._count_keywords(tokens, self.lexicon["core_affect"]["positive_words"])
        negative = self._count_keywords(tokens, self.lexicon["core_affect"]["negative_words"])
        emotional_balance = self._ratio(min(positive, negative), max(positive + negative, 1))

        distortion_values = list(cognition["cognitive_distortions"].values())
        distortion_avg = self._average([float(v) for v in distortion_values])
        negative_density = self._ratio(negative, max(len(tokens), 1))
        cognitive_emotional_alignment = round(max(0.0, 1.0 - abs(negative_density - distortion_avg)), 4)

        action = behavior["action_orientation_score"]
        freeze = behavior["behavioral_freeze_score"]
        hope_count = self._count_keywords(tokens, self.lexicon["core_affect"]["emotion_categories"]["hope"])
        fear_count = self._count_keywords(tokens, self.lexicon["core_affect"]["emotion_categories"]["fear"])
        behavior_emotion_alignment = round(max(0.0, 1.0 - abs((action + self._ratio(hope_count, max(len(tokens), 1))) - (freeze + self._ratio(fear_count, max(len(tokens), 1))))), 4)

        first_person = self._first_person_ratio(tokens)
        other_ratio = self._ratio(
            sum(1 for tok in tokens if tok in {"you", "your", "yours", "they", "them", "their", "he", "she", "him", "her"}),
            max(len(tokens), 1),
        )
        self_other_balance = round(max(0.0, 1.0 - abs(first_person - other_ratio)), 4)

        needs_profile: Dict[str, float] = {}
        needs_lex = self.lexicon["meta_signals"]["psychological_needs_keywords"]
        for need, keywords in needs_lex.items():
            needs_profile[need] = self._ratio(self._count_keywords(tokens, keywords), max(len(tokens), 1))

        return {
            "emotional_congruence_score": round((1.0 - min(affect["emotional_variability"], 1.0)) * 0.6 + emotional_balance * 0.4, 4),
            "cognitive_emotional_alignment_score": cognitive_emotional_alignment,
            "behavior_emotion_alignment_score": behavior_emotion_alignment,
            "self_other_balance_score": self_other_balance,
            "psychological_needs_profile": needs_profile,
        }

    def _compute_analysis_quality(
        self,
        result: Dict[str, Any],
        text: str,
        tokens: List[str],
        sentences: List[str],
    ) -> Dict[str, Any]:
        denom = max(len(tokens), 1)
        ext = self._runtime_group("analysis_quality")
        signal_tokens = ext["signal_tokens"]
        evidence_hits = self._count_keywords(tokens, signal_tokens)

        confidence = self._average_signal_confidence(result)
        uncertainty = self._clamped(1.0 - confidence)

        contradiction_pairs = [tuple(pair) for pair in ext["contradiction_pairs"]]
        contradiction_hits = 0
        token_set = set(tokens)
        for left, right in contradiction_pairs:
            if left in token_set and right in token_set:
                contradiction_hits += 1

        per_category_coverage: Dict[str, float] = {}
        for category in self.CATEGORY_ORDER:
            if category not in result or not isinstance(result[category], dict):
                continue
            numeric_count = sum(1 for value in result[category].values() if isinstance(value, (int, float)))
            if numeric_count <= 0:
                continue
            non_zero_count = sum(1 for value in result[category].values() if isinstance(value, (int, float)) and float(value) > 0)
            per_category_coverage[category] = self._ratio(non_zero_count, numeric_count)

        return {
            "evidence_coverage_ratio": self._ratio(evidence_hits, denom),
            "signal_confidence_overall": confidence,
            "uncertainty_band": uncertainty,
            "contradiction_index": self._ratio(contradiction_hits, max(len(contradiction_pairs), 1)),
            "category_coverage": per_category_coverage,
            "analysis_quality_confidence": self._confidence(contradiction_hits, evidence_hits + len(per_category_coverage), denom),
            "sentence_count_reference": len(sentences),
            "text_length_reference": len(text),
        }

    def _build_summary(self, result: Dict[str, Any]) -> str:
        numeric_signals: List[tuple[str, float]] = []

        for category in self.CATEGORY_ORDER:
            if category not in result:
                continue
            for metric, value in result[category].items():
                if isinstance(value, (int, float)):
                    numeric_signals.append((f"{category}.{metric}", float(value)))
                elif isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        if isinstance(sub_value, (int, float)):
                            numeric_signals.append((f"{category}.{metric}.{sub_key}", float(sub_value)))

        if not numeric_signals:
            return "No numeric signals were generated from the provided input."

        top = sorted(numeric_signals, key=lambda item: item[1], reverse=True)[:5]
        highlights = ", ".join(f"{name}={value:.3f}" for name, value in top)
        return "Top observed signals: " + highlights + "."


def main() -> None:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(base_dir, "sample.txt")
    output_path = os.path.join(base_dir, "sample.txt.json")

    with open(input_path, "r", encoding="utf-8") as infile:
        text = infile.read()

    analyzer = RobPsychSignalAnalyzer()
    output_json = analyzer.analyze(text, "all")

    with open(output_path, "w", encoding="utf-8") as outfile:
        outfile.write(output_json)
        outfile.write("\n")

    print(f"Wrote analysis JSON to: {output_path}")


if __name__ == "__main__":
    main()
