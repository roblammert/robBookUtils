import json
import re
import statistics
from collections import Counter
from typing import Any, Dict, List, Literal, Union


class RobPsychSignalAnalyzer:
    """Analyze free text for psychological, emotional, cognitive, and linguistic signals."""

    CATEGORY_ORDER = [
        "core_affect",
        "cognitive_patterns",
        "identity",
        "social",
        "behavioral_intent",
        "regulation",
        "temporal",
        "somatic",
        "existential",
        "linguistic_structure",
        "thought_speed",
        "meta_signals",
    ]

    __version__ = "1.0.0"
    def __init__(self, lexicon_path: str = "RobPsychSignalAnalyzer_Lexicon.json") -> None:
        self.lexicon_path = self._resolve_lexicon_path(lexicon_path)
        with open(self.lexicon_path, "r", encoding="utf-8") as infile:
            self.lexicon: Dict[str, Any] = json.load(infile)

    def analyze(self, text: str, categories: Union[List[str], Literal["all"]]) -> str:
        if not isinstance(text, str):
            raise TypeError("text must be a string")

        cleaned_text = text.strip()
        tokens = self._tokenize(cleaned_text)
        sentences = self._split_sentences(cleaned_text)

        selected = self._resolve_categories(categories)

        result: Dict[str, Any] = {
            "metadata": {
                "analyzer": "RobPsychSignalAnalyzer",
                "lexicon_path": self.lexicon_path,
                "text_char_count": len(cleaned_text),
                "word_count": len(tokens),
                "sentence_count": len(sentences),
                "selected_categories": selected,
            }
        }

        for category in selected:
            if category == "core_affect":
                result[category] = self._compute_core_affect(cleaned_text, tokens, sentences)
            elif category == "cognitive_patterns":
                result[category] = self._compute_cognitive_patterns(cleaned_text, tokens, sentences)
            elif category == "identity":
                result[category] = self._compute_identity(cleaned_text, tokens)
            elif category == "social":
                result[category] = self._compute_social(cleaned_text, tokens)
            elif category == "behavioral_intent":
                result[category] = self._compute_behavioral_intent(cleaned_text, tokens)
            elif category == "regulation":
                result[category] = self._compute_regulation(cleaned_text, tokens, sentences)
            elif category == "temporal":
                result[category] = self._compute_temporal(cleaned_text, tokens)
            elif category == "somatic":
                result[category] = self._compute_somatic(cleaned_text, tokens)
            elif category == "existential":
                result[category] = self._compute_existential(cleaned_text, tokens)
            elif category == "linguistic_structure":
                result[category] = self._compute_linguistic_structure(cleaned_text, tokens, sentences)
            elif category == "thought_speed":
                result[category] = self._compute_thought_speed(cleaned_text, tokens, sentences)
            elif category == "meta_signals":
                result[category] = self._compute_meta_signals(cleaned_text, tokens, sentences)

        result["summary"] = self._build_summary(result)
        return json.dumps(result, indent=2, sort_keys=False)

    def _resolve_lexicon_path(self, lexicon_path: str) -> str:
        if "/" in lexicon_path:
            return lexicon_path

        if "/" in __file__:
            folder = __file__.rsplit("/", 1)[0]
            return folder + "/" + lexicon_path

        return lexicon_path

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

    def _split_sentences(self, text: str) -> List[str]:
        raw = [segment.strip() for segment in re.split(r"(?<=[.!?])\s+", text) if segment.strip()]
        return raw if raw else ([text.strip()] if text.strip() else [])

    def _count_keywords(self, tokens: List[str], keywords: List[str]) -> int:
        if not tokens or not keywords:
            return 0
        keyword_set = set(word.lower() for word in keywords)
        return sum(1 for tok in tokens if tok in keyword_set)

    def _count_patterns(self, text: str, patterns: List[str]) -> int:
        if not text or not patterns:
            return 0
        total = 0
        for pattern in patterns:
            total += len(re.findall(pattern, text, flags=re.IGNORECASE))
        return total

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

    def _compute_identity(self, text: str, tokens: List[str]) -> Dict[str, Any]:
        lex = self.lexicon["identity"]
        denom = max(len(tokens), 1)

        return {
            "identity_uncertainty_score": self._ratio(self._count_patterns(text, lex["identity_uncertainty_patterns"]), denom),
            "self_fragmentation_score": self._ratio(self._count_patterns(text, lex["self_fragmentation_patterns"]), denom),
            "positive_self_talk_score": self._ratio(self._count_patterns(text, lex["positive_self_talk"]), denom),
            "negative_self_talk_score": self._ratio(self._count_patterns(text, lex["negative_self_talk"]), denom),
            "first_person_ratio": self._first_person_ratio(tokens),
        }

    def _compute_social(self, text: str, tokens: List[str]) -> Dict[str, Any]:
        lex = self.lexicon["social"]
        denom = max(len(tokens), 1)

        return {
            "social_withdrawal_score": self._ratio(self._count_patterns(text, lex["withdrawal_patterns"]), denom),
            "social_connection_score": self._ratio(self._count_patterns(text, lex["connection_patterns"]), denom),
            "perceived_rejection_score": self._ratio(self._count_patterns(text, lex["perceived_rejection_patterns"]), denom),
            "hyperfocus_on_others_opinions_score": self._ratio(self._count_patterns(text, lex["hyperfocus_patterns"]), denom),
            "attachment_language_score": self._ratio(self._count_patterns(text, lex["attachment_patterns"]), denom),
            "boundary_issue_score": self._ratio(self._count_patterns(text, lex["boundary_issue_patterns"]), denom),
            "trust_mistrust_score": self._ratio(self._count_patterns(text, lex["trust_mistrust_patterns"]), denom),
        }

    def _compute_behavioral_intent(self, text: str, tokens: List[str]) -> Dict[str, Any]:
        lex = self.lexicon["behavioral_intent"]
        denom = max(len(tokens), 1)

        return {
            "action_orientation_score": self._ratio(self._count_patterns(text, lex["action_orientation_patterns"]), denom),
            "behavioral_freeze_score": self._ratio(self._count_patterns(text, lex["behavioral_freeze_patterns"]), denom),
            "avoidance_behavior_score": self._ratio(self._count_patterns(text, lex["avoidance_behavior_patterns"]), denom),
            "coping_strategy_adaptive": self._ratio(self._count_patterns(text, lex["adaptive_coping_patterns"]), denom),
            "coping_strategy_maladaptive": self._ratio(self._count_patterns(text, lex["maladaptive_coping_patterns"]), denom),
            "coping_strategy_avoidant": self._ratio(self._count_patterns(text, lex["avoidant_coping_patterns"]), denom),
            "help_seeking_score": self._ratio(self._count_patterns(text, lex["help_seeking_patterns"]), denom),
        }

    def _compute_regulation(self, text: str, tokens: List[str], sentences: List[str]) -> Dict[str, Any]:
        lex = self.lexicon["regulation"]
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

        return {
            "agency_loss_score": self._ratio(self._count_patterns(text, lex["agency_loss_patterns"]), denom),
            "agency_reclamation_score": self._ratio(self._count_patterns(text, lex["agency_reclamation_patterns"]), denom),
            "escalation_language_score": self._ratio(self._count_patterns(text, lex["escalation_patterns"]), denom),
            "deescalation_language_score": self._ratio(self._count_patterns(text, lex["deescalation_patterns"]), denom),
            "emotional_suppression_score": self._ratio(self._count_patterns(text, lex["emotional_suppression_patterns"]), denom),
            "emotional_labeling_skill": self._ratio(emotion_label_count, denom),
            "emotional_differentiation_score": self._ratio(emotion_diff_count, max(emotion_label_count, 1)),
            "cognitive_load_indicator": load_factor,
            "linguistic_energy_score": self._ratio(energy_raw, max(len(sentences), 1)),
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

    def _compute_somatic(self, text: str, tokens: List[str]) -> Dict[str, Any]:
        lex = self.lexicon["somatic"]
        denom = max(len(tokens), 1)

        return {
            "stress_score": self._ratio(self._count_keywords(tokens, lex["stress_words"]), denom),
            "sleep_issue_score": self._ratio(self._count_patterns(text, lex["sleep_patterns"]), denom),
            "somatic_language_score": self._ratio(self._count_patterns(text, lex["somatic_patterns"]), denom),
            "energy_level_score": self._ratio(self._count_keywords(tokens, lex["energy_words"]), denom),
            "arousal_level_score": self._ratio(self._count_keywords(tokens, lex["arousal_words"]), denom),
            "pain_language_score": self._ratio(self._count_keywords(tokens, lex["pain_words"]), denom),
        }

    def _compute_existential(self, text: str, tokens: List[str]) -> Dict[str, Any]:
        lex = self.lexicon["existential"]
        denom = max(len(tokens), 1)

        return {
            "existential_anxiety_score": self._ratio(self._count_patterns(text, lex["existential_anxiety_patterns"]), denom),
            "meaning_making_score": self._ratio(self._count_patterns(text, lex["meaning_making_patterns"]), denom),
            "purpose_language_score": self._ratio(self._count_patterns(text, lex["purpose_patterns"]), denom),
            "value_conflict_score": self._ratio(self._count_patterns(text, lex["value_conflict_patterns"]), denom),
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
