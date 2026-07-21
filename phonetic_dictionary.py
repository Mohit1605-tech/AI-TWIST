# -*- coding: utf-8 -*-
"""
Phonetic Dictionary and Acoustic Similarity Module.
Maps common tongue-twister vocabularies to their corresponding IPA (International Phonetic Alphabet)
phonetic transcriptions. Provides phonetic similarity analysis using sound classification maps
(e.g., sibilants, plosives, nasals, liquids) and calculates acoustic edit distance.
"""

from typing import Dict, List, Set, Tuple, Optional

# Static phonetic dictionary containing standard tongue-twister vocabularies mapped to IPA
IPA_DICTIONARY: Dict[str, str] = {
    # Peter Piper Vocabulary
    "peter": "ˈpiːtər",
    "piper": "ˈpaɪpər",
    "picked": "pɪkt",
    "peck": "pek",
    "pickled": "ˈpɪkəld",
    "peppers": "ˈpepərz",
    "a": "ə",
    "of": "ʌv",
    "where": "wɛər",
    "is": "ɪz",
    
    # She Sells Seashells Vocabulary
    "she": "ʃiː",
    "sells": "selz",
    "seashells": "ˈsiːˌʃelz",
    "by": "baɪ",
    "the": "ðə",
    "seashore": "ˈsiːˌʃɔːr",
    "shells": "ʃelz",
    "are": "ɑːr",
    "surely": "ˈʃʊəli",
    "sure": "ʃʊər",
    "on": "ɒn",
    
    # Woodchuck Vocabulary
    "how": "haʊ",
    "much": "mʌtʃ",
    "wood": "wʊd",
    "would": "wʊd",
    "woodchuck": "ˈwʊdˌtʃʌk",
    "chuck": "tʃʌk",
    "if": "ɪf",
    "could": "kʊd",
    "so": "soʊ",
    "as": "æz",
    "he": "hiː",
    
    # Swans and Snakes Vocabulary
    "six": "sɪks",
    "sleek": "sliːk",
    "swans": "swɒnz",
    "swam": "swæm",
    "swiftly": "ˈswɪftli",
    "southwards": "ˈsaʊθwədz",
    "silly": "ˈsɪli",
    "snakes": "sneɪks",
    "singing": "ˈsɪŋɪŋ",
    "songs": "sɒŋz",
    "slow": "sloʊ",
    "silent": "ˈsaɪlənt",
    "slapping": "ˈslæpɪŋ",
    "slimy": "ˈslaɪmi",
    "slippery": "ˈslɪpəri",
    
    # Frogs and Fellowship Vocabulary
    "fidgety": "ˈfɪdʒɪti",
    "frogs": "frɒgz",
    "fishing": "ˈfɪʃɪŋ",
    "flying": "ˈflaɪɪŋ",
    "flies": "flaɪz",
    "funny": "ˈfʌni",
    "fellowship": "ˈfeloʊʃɪp",
    "finding": "ˈfaɪndɪŋ",
    "forty": "ˈfɔːrti",
    "feathers": "ˈfeðərz",
    "friend": "frend",
    "friendly": "ˈfrendli",
    "frightened": "ˈfraɪtənd",
    "frantic": "ˈfræntɪk",
    "flight": "flaɪt",
    "forest": "ˈfɒrɪst",
    
    # Cats and Cooking Vocabulary
    "crazy": "ˈkreɪzi",
    "cats": "kæts",
    "cooking": "ˈkʊkɪŋ",
    "carrots": "ˈkærəts",
    "cookie": "ˈkʊki",
    "kitchen": "ˈkɪtʃɪn",
    "cupboard": "ˈkʌbərd",
    "cupcake": "ˈkʌpkeɪk",
    "crying": "ˈkraɪɪŋ",
    "creamy": "ˈkriːmi",
    "cold": "koʊld",
    "crisp": "krɪsp",
    
    # Tacos and Town Vocabulary
    "tasty": "ˈteɪsti",
    "tacos": "ˈtɑːkoʊz",
    "tumbling": "ˈtʌmblɪŋ",
    "town": "taʊn",
    "two": "tuː",
    "tiny": "ˈtaɪni",
    "tigers": "ˈtaɪɡərz",
    "trying": "ˈtraɪɪŋ",
    "to": "tuː",
    "taste": "teɪst",
    "tea": "tiː",
    "teeth": "tiːθ",
    "tongue": "tʌŋ",
    "twister": "ˈtwɪstər",
    "talking": "ˈtɔːkɪŋ",
    
    # Strawberry and Syrup Vocabulary
    "sweet": "swiːt",
    "strawberry": "ˈstrɔːbəri",
    "syrup": "ˈsɪrəp",
    "sliding": "ˈslaɪdɪŋ",
    "slowly": "ˈsloʊli",
    "sugar": "ˈʃʊɡər",
    "sticky": "ˈstɪki",
    "spoon": "spuːn",
    "spinning": "ˈspɪnɪŋ",
    "spread": "spred",
    
    # Garlic and Grapes Vocabulary
    "greasy": "ˈɡriːsi",
    "garlic": "ˈɡɑːrlɪk",
    "grapes": "ɡreɪps",
    "glowing": "ˈɡloʊɪŋ",
    "green": "ɡriːn",
    "giant": "ˈdʒaɪənt",
    "good": "ɡʊd",
    "great": "ɡreɪt",
    "grand": "ɡrænd",
    "garden": "ˈɡɑːrdən",
    "growing": "ˈɡroʊɪŋ",
    
    # Robotic Rovers Vocabulary
    "robotic": "roʊˈbɒtɪk",
    "rovers": "ˈroʊvərz",
    "running": "ˈrʌnɪŋ",
    "rusty": "ˈrʌsti",
    "rings": "rɪŋz",
    "red": "red",
    "rapid": "ˈræpɪd",
    "racing": "ˈreɪsɪŋ",
    "roads": "roʊdz",
    "rough": "rʌf",
    "rivers": "ˈrɪvərz",
    
    # Cosmic Comets Vocabulary
    "alien": "ˈeɪliən",
    "astronauts": "ˈæstrənɔːts",
    "altering": "ˈɔːltərɪŋ",
    "active": "ˈæktɪv",
    "atmosphere": "ˈætməsfiər",
    "cosmic": "ˈkɒzmɪk",
    "comets": "ˈkɒmɪts",
    "crashing": "ˈkræʃɪŋ",
    "craters": "ˈkreɪtərz",
    "capsule": "ˈkæpsuːl",
    "celestial": "sɪˈlestʃəl",
    "constellation": "ˌkɒnstəˈleɪʃən",
    
    # Winter Winds Vocabulary
    "windy": "ˈwɪndi",
    "winter": "ˈwɪntər",
    "winds": "wɪndz",
    "whispering": "ˈwɪspərɪŋ",
    "whimsical": "ˈwɪmzɪkəl",
    "words": "wɜːdz",
    "warm": "wɔːrm",
    "wet": "wet",
    "wild": "waɪld",
    "waves": "weɪvz",
    "water": "ˈwɔːtər",
    
    # Queen and Quarters Vocabulary
    "quick": "kwɪk",
    "queen": "kwiːn",
    "questioning": "ˈkwestʃənɪŋ",
    "quiet": "ˈkwaɪət",
    "quarters": "ˈkwɔːrtərz",
    "quite": "kwaɪt",
    "quacking": "ˈkwækɪŋ",
    "quail": "kweɪl",
    "quivering": "ˈkwɪvərɪŋ",
    
    # French Fallbacks Vocabulary
    "un": "œ̃",
    "chasseur": "ʃasœʁ",
    "sachant": "saʃɑ̃",
    "chasser": "ʃase",
    "doit": "dwa",
    "savoir": "savwaʁ",
    "sans": "sɑ̃",
    "son": "sɔ̃",
    "chien": "ʃjɛ̃",
    
    # German Fallbacks Vocabulary
    "fischers": "ˈfɪʃɐs",
    "fritz": "frɪts",
    "fischt": "fɪʃt",
    "frische": "ˈfrɪʃə",
    "fische": "ˈfɪʃə",
    
    # Spanish Fallbacks Vocabulary
    "tres": "tres",
    "tristes": "ˈtɾistes",
    "tigres": "ˈtɾiɣɾes",
    "tragaban": "tɾaˈɣaβan",
    "trigo": "ˈtɾiɣo",
    "en": "en",
    "un": "un",
    "trigal": "tɾiˈɣal",
    "trastos": "ˈtɾastos",
    
    # Alphabet and Common Utterances
    "i": "aɪ",
    "you": "juː",
    "they": "ðeɪ",
    "we": "wiː",
    "this": "ðɪs",
    "that": "ðæt",
    "these": "ðiːz",
    "those": "ðoʊz",
    "here": "hɪər",
    "there": "ðɛər",
    "can": "kæn",
    "will": "wɪl",
    "shall": "ʃæl",
    "should": "ʃʊd",
    "may": "meɪ",
    "might": "maɪt",
    "must": "mʌst",
    "do": "duː",
    "does": "dʌz",
    "did": "dɪd",
    "done": "dʌn",
    "make": "meɪk",
    "made": "meɪd",
    "go": "ɡoʊ",
    "went": "went",
    "gone": "ɡɒn",
    "see": "siː",
    "saw": "sɔː",
    "seen": "siːn",
    "hear": "hɪər",
    "heard": "hɜːd",
    "say": "seɪ",
    "said": "sed",
    "speak": "spiːk",
    "spoke": "spoʊk",
    "spoken": "ˈspoʊkən",
    "read": "riːd",
    "write": "raɪt",
    "wrote": "roʊt",
    "written": "ˈrɪtən",
    "learn": "lɜːn",
    "practice": "ˈpræktɪs",
    "voice": "vɔɪs",
    "sound": "saʊnd",
    "breath": "breθ",
    "breathe": "briːð",
    "lip": "lɪp",
    "jaw": "dʒɔː",
    "throat": "θroʊt",
    "nose": "noʊz",
    "ear": "ɪər",
    "eye": "aɪ",
    "head": "hed",
    "face": "feɪs"
}

# Phonetic Feature maps grouping IPA symbols into articulatory categories
PHONETIC_GROUPS: Dict[str, Set[str]] = {
    "sibilants": {"s", "z", "ʃ", "ʒ", "tʃ", "dʒ"},
    "plosives": {"p", "b", "t", "d", "k", "ɡ"},
    "nasals": {"m", "n", "ŋ"},
    "liquids": {"l", "r", "ɹ", "j", "w", "ɾ", "ʁ", "ɣ", "β"},
    "fricatives": {"f", "v", "θ", "ð", "s", "z", "ʃ", "ʒ", "h"}
}

class PhoneticDictionary:
    """
    Main controller for phonetic transcriptions, classifications,
    and articulatory similarity diagnostics.
    """

    @classmethod
    def get_ipa(cls, word: str) -> str:
        """
        Translates a plain word into its corresponding IPA representation.
        If not present in the static dictionary, returns a simplified phonetic spelling guess.
        """
        w_clean = word.lower().strip(".,?!;:\"'()[]")
        if w_clean in IPA_DICTIONARY:
            return IPA_DICTIONARY[w_clean]
        
        # Heuristic guess for unknown words
        guess = w_clean
        guess = guess.replace("sh", "ʃ").replace("ch", "tʃ").replace("th", "θ")
        guess = guess.replace("ee", "iː").replace("oo", "uː").replace("ck", "k")
        guess = guess.replace("ph", "f").replace("c", "k").replace("q", "kw")
        return guess

    @classmethod
    def get_phonetic_features(cls, ipa_str: str) -> Dict[str, int]:
        """
        Analyzes an IPA transcription to tally active articulatory features.
        Helps diagnose which vocal muscles are being loaded heavily.
        """
        counts = {group: 0 for group in PHONETIC_GROUPS}
        for char in ipa_str:
            for group, symbols in PHONETIC_GROUPS.items():
                if char in symbols:
                    counts[group] += 1
        return counts

    @classmethod
    def calculate_phonetic_distance(cls, word1: str, word2: str) -> float:
        """
        Calculates edit distance on the IPA string levels instead of letters.
        This provides a highly precise acoustic similarity score.
        Returns a normalized score between 0.0 (identical) and 1.0 (completely dissimilar).
        """
        ipa1 = cls.get_ipa(word1)
        ipa2 = cls.get_ipa(word2)

        if not ipa1 or not ipa2:
            return 1.0 if ipa1 != ipa2 else 0.0

        len1, len2 = len(ipa1), len(ipa2)
        dp = [[0] * (len2 + 1) for _ in range(len1 + 1)]

        for i in range(len1 + 1):
            dp[i][0] = i
        for j in range(len2 + 1):
            dp[0][j] = j

        for i in range(1, len1 + 1):
            for j in range(1, len2 + 1):
                char1 = ipa1[i - 1]
                char2 = ipa2[j - 1]

                # If chars are identical, cost is 0
                if char1 == char2:
                    cost = 0
                else:
                    # If chars belong to the same phonetic group, substitution cost is lower (e.g. s vs sh is 0.5)
                    same_group = False
                    for symbols in PHONETIC_GROUPS.values():
                        if char1 in symbols and char2 in symbols:
                            same_group = True
                            break
                    cost = 0.5 if same_group else 1.0

                dp[i][j] = min(
                    dp[i - 1][j] + 1,      # Deletion
                    dp[i][j - 1] + 1,      # Insertion
                    dp[i - 1][j - 1] + cost # Substitution
                )

        max_len = max(len1, len2)
        return dp[len1][len2] / max_len if max_len > 0 else 0.0

    @classmethod
    def analyze_phonetic_collisions(cls, text: str) -> List[Tuple[str, int]]:
        """
        Identifies sibilant, plosive, or liquid sound collisions inside a tongue twister.
        Returns a sorted list of active phonetic loads (e.g. [('sibilants', 12), ('plosives', 8)]).
        """
        words = text.split()
        totals = {group: 0 for group in PHONETIC_GROUPS}
        
        for w in words:
            ipa = cls.get_ipa(w)
            features = cls.get_phonetic_features(ipa)
            for group, val in features.items():
                totals[group] += val

        return sorted(totals.items(), key=lambda x: x[1], reverse=True)
