"""
RobTextStats.py

A single-pass text analysis class for markdown and text files.
Collects basic, advanced, and LLM metrics efficiently.
"""
import re
import math
import statistics
import os
import glob
import datetime
from collections import Counter
import zlib
from typing import Dict, Any

DALE_CHALL_EASY_WORDS = set([
    # Source: https://www.readabilityformulas.com/articles/dale-chall-readability-word-list.php
    # The following is the full Dale-Chall list, formatted as quoted, comma-separated strings
    "A", "A.M.", "America", "American", "April", "August", "B", "C", "Christmas", "Creep", "D", "D.C.", "Dad", "December", "Easter", "Eskimo", "F", "February", "Friday", "G", "George Washington", "God", "Halloween", "I", "I'd", "I'll", "I'm", "I've", "Indian", "It", "It'll", "It's", "Its", "J", "January", "July", "June", "K", "L", 
    "Lincoln, Abraham", "London", "M", "Monday", "Mr.", "Mrs.", "N", "November", "O.K.", "October", "P", "P.M.", "Pa", "R", "S", "Saturday", "September", "Sir", "Sis", "So", "Sunday", "T", "TV", "Thanksgiving", "Thursday", "Tuesday", "U", "U.S.", "U.S.A.", "V", "Valentine", "W", "Washington", "Wednesday", "X", "Xmas", "Y", "Z", 
    "able", "aboard", "about", "above", "absent", "ac", "accept", "accident", "account", "ace", "ache", "acid", "acorn", "across", "action", "add", "addition", "address", "adjust", "adjustment", "admire", "admission", "adore", "adult", "adventure", "advice", "afraid", "after", "afternoon", "afterward", "afterwards", "again", 
    "against", "age", "ago", "agree", "ah", "ahead", "aid", "aim", "air", "airline", "airplane", "airport", "airy", "alarm", "album", "alike", "alive", "all", "alley", "alligator", "allright", "almost", "alone", "along", "alongside", "aloud", "alphabet", "already", "also", "always", "am", "amaze", "amazement", "among", "amount", 
    "an", "and", "angel", "anger", "angry", "animal", "ankle", "announce", "announcement", "another", "answer", "ant", "any", "anybody", "anyhow", "anyone", "anything", "anyway", "anywhere", "apart", "apartment", "ape", "apiece", "appear", "applause", "apple", "apron", "are", "area", "aren't", "arise", "arithmetic", "arm", "army", 
    "around", "arrange", "arrest", "arrive", "arrow", "arrowhead", "art", "artist", "as", "ash", "aside", "ask", "asleep", "astronaut", "at", "ate", "atlas", "attack", "attend", "attention", "aunt", "author", "auto", "automobile", "autumn", "avenue", "awake", "awaken", "award", "away", "awful", "awhile", "ax", "baa", "baby", 
    "baby-sitter", "back", "backache", "background", "backtrack", "backward", "backwards", "bacon", "bad", "badge", "bag", "baggage", "bait", "bake", "bakery", "balance", "ball", "balloon", "ballpoint", "banana", "band", "bandage", "bang", "banjo", "bank", "bar", "barbecue", "barber", "bare", "barefoot", "bark", "barn", "barrel", 
    "base", "baseball", "basement", "basket", "basketball", "bat", "bath", "bathe", "bathroom", "battle", "be", "beach", "bead", "beak", "beam", "bean", "bear", "beard", "beast", "beat", "beautiful", "beauty", "beaver", "became", "because", "become", "bed", "bedroom", "bedspread", "bee", "beef", "beefsteak", "been", "beer", "beet", 
    "before", "beg", "began", "beggar", "begin", "begun", "behave", "behind", "belief", "believe", "bell", "belly", "belong", "belonging", "belongings", "below", "belt", "bench", "bend", "beneath", "bent", "berry", "beside", "besides", "best", "bet", "better", "between", "beyond", "bib", "bible", "bicycle", "big", "bigness", "bill", 
    "billfold", "billion", "bingo", "bird", "birth", "birthday", "biscuit", "bit", "bite", "bitter", "black", "blackboard", "blackness", "blacksmith", "blame", "blank", "blanket", "blast", "blastoff", "blaze", "bleed", "bless", "blew", "blind", "blindfold", "blink", "blinker", "block", "blond", "blonde", "blood", "bloodhound", 
    "bloodstream", "bloom", "blossom", "blot", "blouse", "blow", "blue", "blueberry", "blush", "board", "boat", "bobwhite", "body", "bodyguard", "boil", "bold", "bolt", "bomb", "bone", "bonnet", "boo", "book", "boom", "boot", "born", "borrow", "boss", "both", "bother", "bottle", "bottom", "bought", "boulder", "bounce", "bow", 
    "bow-wow", "bowl", "box", "boxcar", "boy", "brace", "bracelet", "brain", "brake", "bran", "branch", "brand", "brand-new", "brass", "brave", "bravery", "bread", "break", "breakfast", "breast", "breath", "breathe", "breeze", "brick", "bridge", "bright", "brighten", "bring", "broad", "broadcast", "broke", "broken", 
    "broken-hearted", "brook", "broom", "brother", "brought", "brown", "brownie", "brush", "bubble", "bucket", "buckle", "bud", "budge", "buffalo", "bug", "buggy", "build", "building", "bulb", "bull", "bullet", "bulletin", "bumblebee", "bump", "bumpy", "bun", "bunch", "bundle", "bunk", "bunny", "burglar", "burn", "burnt", 
    "burro", "burst", "bury", "bus", "bush", "bushel", "business", "busy", "but", "butcher", "butter", "butterfly", "butterscotch", "button", "buy", "buzz", "by", "bye", "cab", "cabbage", "cabin", "cage", "cake", "calendar", "calf", "call", "came", "camel", "camera", "camp", "can", "can't", "canal", "canary", "candle", "candy", 
    "cane", "cannon", "cannot", "canoe", "canyon", "cap", "cape", "capital", "capsule", "captain", "capture", "car", "card", "cardboard", "care", "careful", "carefully", "careless", "carload", "carpenter", "carpet", "carriage", "carrot", "carry", "cart", "cartoon", "carve", "case", "cash", "cashier", "castle", "cat", "catch", 
    "caterpillar", "catsup", "cattle", "caught", "cause", "cave", "ceiling", "celebrate", "celebration", "cell", "cellar", "cent", "center", "cereal", "certain", "chain", "chair", "chalk", "chalkboard", "champion", "chance", "change", "channel", "chapter", "charge", "charm", "chart", "chase", "chatter", "cheap", "cheat", "check", 
    "checkers", "checkup", "cheek", "cheer", "cheerful", "cheerfully", "cheese", "cheeseburger", "cherry", "chest", "chestnut", "chew", "chick", "chicken", "chief", "child", "childhood", "children", "chili", "chill", "chilly", "chimney", "chimpanzee", "chin", "china", "chip", "chipmunk", "chirp", "chocolate", "choice", "choke", 
    "choose", "chop", "chop-suey", "chorus", "chose", "chosen", "church", "churn", "cigarette", "circle", "circus", "citizen", "city", "clap", "class", "classroom", "claw", "clay", "clean", "cleanser", "clear", "clerk", "clever", "click", "climate", "climb", "clip", "clock", "close", "closet", "cloth", "cloud", "cloudy", "clown", 
    "club", "clubhouse", "coach", "coal", "coast", "coat", "cob", "cobweb", "cocktail", "cocoa", "coconut", "coffee", "coin", "cold", "collar", "collect", "collection", "collector", "college", "color", "colorful", "colt", "column", "comb", "come", "comfort", "comfortable", "comic", "comma", "command", "commercial", "company", 
    "complete", "computer", "concrete", "conductor", "cone", "connect", "contest", "continue", "control", "cook", "cookie", "cooky", "cool", "copy", "cord", "cork", "corn", "corner", "cornmeal", "correct", "cost", "cosy", "cottage", "cotton", "couch", "cough", "could", "couldn't", "count", "counter", "country", "course", "court", 
    "cousin", "cover", "cow", "coward", "cowboy", "cozy", "crab", "crack", "cracker", "cradle", "cranberry", "crank", "crash", "crawl", "crayon", "crazy", "cream", "creature", "creek", "crib", "cricket", "crime", "cripple", "crisp", "croak", "crook", "crop", "cross", "crosswalk", "crossways", "crow", "crowd", "crown", "cruel", "crumb", 
    "crumble", "crush", "crust", "crutch", "cry", "cub", "cup", "cupboard", "cupful", "cure", "curl", "curly", "curtain", "curve", "cushion", "customer", "cute", "daddy", "dady-long-legs", "daily", "dairy", "daisy", "dam", "damage", "damp", "dance", "dandy", "danger", "dangerous", "dare", "dark", "darkness", "darling", "dart", "dash", 
    "date", "daughter", "dawn", "day", "daylight", "daytime", "dead", "deaf", "deal", "dear", "death", "decide", "deck", "deep", "deer", "defend", "delighted", "deliver", "delivery", "den", "dentist", "depend", "deposit", "describe", "desert", "design", "desire", "desk", "destroy", "detective", "detergent", "devil", "dew", "dial", 
    "diamond", "dice", "dictionary", "did", "didn't", "die", "diet", "difference", "differences", "difficult", "difficulty", "dig", "dim", "dime", "dimple", "dine", "ding-dong", "dinner", "dinosaur", "dip", "direct", "direction", "dirt", "dirty", "disagree", "disappear", "discover", "disease", "disgrace", "disgraceful", "dish", 
    "dismiss", "distance", "ditch", "dive", "divide", "do", "dock", "doctor", "dodge", "does", "doesn't", "dog", "doll", "dollar", "dolly", "don't", "done", "donkey", "door", "doorstep", "dope", "dot", "double", "dove", "down", "downstairs", "downtown", "downward", "downwards", "dozen", "drag", "dragon", "drain", "drank", "draw", 
    "dream", "dress", "drew", "drill", "drink", "drip", "drive", "driveway", "drop", "drove", "drown", "drowsy", "drug", "drugstore", "drum", "drunk", "dry", "duck", "duckling", "due", "dug", "dull", "dumb", "dump", "during", "dust", "dusty", "dying", "each", "eager", "eagle", "ear", "earache", "eardrum", "early", "earn", "earnings", 
    "earth", "earthquake", "east", "eastern", "easy", "eat", "eaten", "edge", "education", "egg", "eight", "eighteen", "eighth", "eighty", "either", "el", "elastic", "elbow", "election", "electric", "electricity", "elephant", "elevator", "eleven", "elm", "else", "empty", "encyclopedia", "end", "endless", "enemy", "engine", "engineer", 
    "english", "enjoy", "enjoyment", "enough", "enter", "envelope", "equal", "equator", "erase", "errand", "error", "escape", "evaporate", "even", "evening", "ever", "everlasting", "every", "everybody", "everyday", "everyone", "everything", "everywhere", "evil", "exactly", "example", "excellent", "except", "exchange", "excited", 
    "exciting", "excuse", "exercise", "exit", "expect", "experiment", "explain", "explode", "explore", "explosive", "express", "expressway", "extinguisher", "extra", "eye", "eyeball", "eyebrow", "eyeglass", "eyelash", "eyelid", "eyesight", "fable", "face", "fact", "factory", "fade", "fail", "failure", "faint", "fair", "fairy", 
    "fairyland", "faith", "fake", "fall", "false", "family", "fan", "fancy", "far", "far-off", "faraway", "fare", "farm", "farmer", "farther", "fashion", "fast", "fasten", "fat", "father", "fault", "favor", "favorite", "fear", "feast", "feather", "fed", "feed", "feel", "feet", "fell", "fellow", "felt", "female", "fence", "fern", 
    "festival", "fever", "few", "fib", "fiddle", "field", "fifteen", "fifth", "fifty", "fig", "fight", "figure", "file", "fill", "film", "final", "finally", "find", "fine", "finger", "fingernail", "fingerprint", "fingertip", "finish", "fire", "firefly", "fireplace", "fireproof", "fireworks", "first", "fish", "fist", "fit", "five", 
    "fix", "fizz", "flag", "flame", "flap", "flare", "flash", "flashlight", "flat", "flavor", "flea", "flesh", "flew", "flies", "flight", "flip", "float", "flock", "flood", "floor", "flour", "flow", "flu", "flunk", "flute", "fly", "foam", "fog", "foggy", "fold", "folks", "follow", "fond", "food", "fool", "foolish", "foot", "football", 
    "footpath", "footprint", "footsteps", "for", "force", "forehead", "forest", "forever", "forget", "forgetful", "forgot", "forgotten", "fork", "form", "fort", "fortune", "forty", "forward", "fought", "found", "fountain", "four", "fourteen", "fourth", "fox", "frame", "freckles", "free", "freedom", "freeze", "freight", "fresh", "friend", 
    "friendship", "frighten", "frog", "from", "front", "frost", "frown", "froze", "fruit", "fry", "fudge", "fuel", "full", "fun", "funny", "fur", "furniture", "further", "gallon", "gallop", "gamble", "game", "gang", "gangster", "garage", "garbage", "garden", "gargle", "gas", "gasoline", "gate", "gather", "gauge", "gave", "gay", "geese", 
    "general", "gentle", "gentleman", "gentlemen", "geography", "get", "ghost", "giant", "gift", "giggle", "gill", "giraffe", "girl", "give", "glad", "gladness", "glance", "glare", "glass", "glassware", "glide", "globe", "glory", "glove", "glow", "glue", "goal", "goat", "gobble", "godmother", "gold", "golden", "goldfish", "golf", "gone", 
    "good", "good-by", "goodbye", "goodies", "goodness", "goose", "got", "gotten", "government", "gown", "grab", "grace", "grade", "grain", "grand", "grandchild", "granddaughter", "grandfather", "grandma", "grandmother", "grandpa", "grandson", "grandstand", "grape", "grapefruit", "grass", "grasshopper", "grave", "gravel", "graveyard", 
    "gravy", "gray", "graze", "grease", "greasy", "great", "greedy", "green", "greens", "greet", "grew", "grey", "greyhound", "grill", "grin", "grind", "grip", "grizzly", "groan", "grocery", "groom", "ground", "group", "grow", "growl", "grown-up", "growth", "guard", "guess", "guest", "guide", "guitar", "gum", "gun", "guy", "gym", "h", 
    "habit", "had", "hadn't", "hail", "hair", "hairy", "half", "hall", "hallway", "ham", "hamburger", "hammer", "hamster", "hand", "handful", "handkerchief", "handle", "handmade", "handsome", "handwriting", "hang", "happen", "happiness", "happy", "harbor", "hard", "hardware", "harm", "harmful", "harmless", "harness", "harp", "harvest", 
    "has", "hasn't", "hat", "hatch", "hatchet", "hate", "haul", "have", "haven't", "hawk", "hay", "he", "he'll", "head", "headache", "headline", "headquarters", "heal", "health", "heap", "hear", "heard", "heart", "heat", "heaven", "heavy", "heel", "height", "held", "helicopter", "hell", "hello", "helmet", "help", "helpful", "hen", "her", 
    "herd", "here", "hero", "herself", "hi-fi", "hid", "hidden", "hide", "hide-and-seek", "hideout", "high", "highway", "hike", "hill", "hilly", "him", "himself", "hint", "hip", "hippo", "hire", "his", "history", "hit", "hitch", "hive", "ho", "hobble", "hobby", "hockey", "hoe", "hold", "holdup", "hole", "holiday", "hollow", "holster", 
    "holy", "home", "homerun", "homesick", "homework", "honest", "honey", "honeybee", "honk", "honor", "hood", "hoof", "hook", "hoot", "hop", "hope", "hopscotch", "horn", "horse", "hose", "hospital", "hot", "hotdog", "hotel", "hound", "hour", "house", "housekeeper", "housewife", "how", "howl", "hug", "huge", "hum", "human", "hump", 
    "hundred", "hung", "hunger", "hungry", "hunk", "hunt", "hurricane", "hurry", "hurt", "husband", "hush", "hut", "hymn", "ice", "iceberg", "icy", "idea", "if", "igloo", "imagine", "important", "impossible", "improve", "in", "inch", "indeed", "indoors", "industry", "ink", "inn", "insect", "inside", "inspection", "instead", "intend", 
    "interest", "into", "introduce", "invent", "inventor", "invite", "iron", "is", "island", "isn't", "ivory", "ivy", "jack", "jack-o-lantern", "jacket", "jackpot", "jacks", "jail", "jam", "janitor", "jar", "jaw", "jawbone", "jay", "jaywalker", "jazz", "jeans", "jeep", "jelly", "jerk", "jet", "jewel", "jewelry", "jig", "join", "joke", 
    "jolly", "jot", "journey", "joy", "joyful", "judge", "jug", "juice", "juicy", "jump", "jungle", "junk", "just", "kangaroo", "keep", "kept", "ketchup", "kettle", "key", "kick", "kid", "kidnap", "kill", "kind", "kindergarten", "kindness", "king", "kiss", "kit", "kitchen", "kite", "kitten", "kitty", "knee", "kneel", "knew", "knife", 
    "knight", "knit", "knives", "knob", "knock", "know", "known", "lace", "lad", "ladder", "lady", "laid", "lake", "lamb", "lame", "lamp", "land", "lane", "language", "lantern", "lap", "large", "last", "late", "laugh", "laundry", "law", "lawn", "lawyer", "lay", "lazy", "lead", "leaf", "leak", "lean", "leap", "learn", "leather", "leave", 
    "leaves", "led", "left", "leg", "lemon", "lemonade", "lend", "length", "lens", "leopard", "less", "lesson", "let", "letter", "lettuce", "level", "liar", "liberty", "librarian", "library", "lick", "lid", "lie", "life", "lifeboat", "lifeguard", "lift", "light", "lighthouse", "lightness", "lightning", "like", "lily", "limb", "lime", 
    "line", "linen", "lion", "lip", "lipstick", "liquor", "list", "listen", "litterbug", "little", "live", "liver", "lizard", "load", "loaf", "loan", "loaves", "lobster", "lock", "log", "lollipop", "lone", "lonesome", "long", "look", "loop", "loose", "lord", "lose", "loss", "lost", "lot", "lotion", "loud", "loudspeaker", "love", "low", 
    "lower", "luck", "lucky", "luggage", "lullaby", "lumber", "lump", "lunch", "lung", "luxury", "lying", "ma", "macaroni", "machine", "mad", "made", "magazine", "magic", "magnet", "maid", "mail", "mailman", "major", "majorette", "make", "make-believe", "male", "mama", "man", "manager", "mane", "mange", "manners", "many", "map", "maple", 
    "marble", "march", "mark", "market", "marriage", "marry", "marvelous", "mash", "mask", "master", "match", "mate", "matter", "mattress", "may", "maybe", "mayor", "me", "meadow", "meal", "mean", "meaning", "measure", "meat", "medicine", "meet", "melon", "melt", "member", "memorize", "memory", "men", "mend", "mention", "menu", "meow", 
    "merchant", "mermaid", "merry", "merry-go-round", "mess", "message", "messenger", "met", "metal", "meter", "mice", "microphone", "middle", "midget", "midnight", "midsummer", "might", "mighty", "mile", "milk", "milkshake", "mill", "million", "millionaire", "mind", "mine", "miner", "minister", "mink", "minnow", "mint", "minute", 
    "miracle", "mirror", "misery", "mislay", "misplace", "misprint", "miss", "missile", "misspell", "mist", "mistake", "mister", "misty", "mitt", "mitten", "mix", "mixture", "mob", "model", "modern", "moist", "moisture", "mom", "moment", "money", "monkey", "monster", "month", "moo", "moon", "moonlight", "moose", "mop", "more", "morning", 
    "most", "motel", "moth", "mother", "motion", "motor", "motorcycle", "mountain", "mouse", "mouth", "movable", "move", "moveable", "movie", "much", "mud", "muffin", "mule", "multiplication", "multiply", "mumps", "murder", "museum", "mush", "mushroom", "music", "musical", "musician", "must", "mustard", "mustn't", "my", "myself", "mystery", 
    "nail", "name", "nap", "napkin", "narrow", "nasty", "nation", "nature", "naughty", "navy", "near", "nearby", "neat", "neatness", "necessary", "neck", "necklace", "necktie", "need", "needle", "needn't", "negro", "neighbor", "neighborhood", "neither", "nerve", "nest", "net", "never", "new", "newborn", "newcomer", "news", "newscast", 
    "newspaper", "next", "nibble", "nice", "nickel", "nickname", "night", "nightfall", "nightmare", "nighttime", "nine", "nineteen", "ninety", "ninth", "nipple", "nobody", "nod", "noise", "none", "noodle", "noon", "normal", "north", "northern", "nose", "not", "note", "nothing", "notice", "now", "nowhere", "number", "nurse", "nursery", 
    "nut", "o'clock", "oak", "oar", "oatmeal", "oats", "obey", "ocean", "octopus", "odd", "of", "off", "offer", "office", "often", "oh", "oil", "okay", "old", "on", "once", "one", "one-fourth", "one-way", "oneself", "onion", "only", "onward", "onwards", "open", "operator", "opossum", "or", "orange", "orbit", "orchard", "order", "ordinary", 
    "organ", "orphan", "ostrich", "other", "ouch", "ought", "ounce", "our", "ourselves", "out", "outdoors", "outer", "outlaw", "outline", "outside", "oven", "over", "overalls", "overboard", "overcoat", "overdo", "overdone", "overeat", "overflow", "overhead", "overnight", "overseas", "overtime", "overweight", "owe", "owl", "own", "pack", 
    "package", "pad", "page", "paid", "pail", "pain", "painful", "paint", "pair", "pajamas", "pal", "palace", "pale", "pan", "pancake", "panda", "pants", "papa", "paper", "parade", "pardon", "parent", "park", "parrot", "part", "partner", "partnership", "party", "pass", "passenger", "password", "past", "paste", "pasture", "pat", "patch", 
    "path", "pave", "paw", "pay", "payment", "pea", "peace", "peaceful", "peach", "peacock", "peak", "peanut", "pear", "pearl", "pecan", "peck", "peek", "peel", "peep", "peg", "pen", "pencil", "penguin", "penny", "people", "pep", "pepper", "peppermint", "peppy", "perfume", "perhaps", "period", "permit", "person", "personal", "pest", "pet", 
    "phone", "phonograph", "photo", "photograph", "piano", "pick", "pickle", "picnic", "picture", "pie", "piece", "pig", "pigeon", "pile", "pilgrim", "pill", "pillow", "pilot", "pimple", "pin", "pine", "pineapple", "ping-pong", "pink", "pint", "pioneer", "pipe", "pistol", "pit", "pitch", "pitcher", "pitiful", "pity", "pizza", "place", 
    "plain", "plan", "plane", "planet", "plant", "plantation", "plaster", "plate", "play", "playful", "playground", "playhouse", "playmate", "plaything", "pleasant", "please", "pleasure", "plenty", "plow", "plug", "plum", "plumber", "plus", "pocket", "pocketbook", "poem", "point", "poison", "poke", "pole", "police", "policeman", "polite", 
    "pond", "pony", "poodle", "pool", "poor", "pop", "popcorn", "poppy", "porch", "pork", "pose", "possible", "post", "postage", "postman", "postmark", "postpone", "pot", "potato", "potatoes", "pottery", "pound", "pour", "powder", "power", "powerful", "prairie", "praise", "pray", "prayer", "prepare", "present", "preserver", "president", 
    "press", "pretend", "pretty", "prevent", "price", "primary", "prince", "princess", "print", "prison", "private", "prize", "problem", "program", "promise", "promote", "proof", "property", "protect", "proud", "prove", "prune", "public", "puddle", "puff", "pull", "pump", "pumpkin", "punch", "punish", "pup", "pupil", "puppet", "puppy", 
    "pure", "purple", "purse", "push", "puss", "pussy", "put", "puzzle", "quack", "quarrel", "quart", "quarter", "quarterback", "queen", "queer", "question", "quick", "quickly", "quiet", "quilt", "quit", "quite", "rabbit", "raccoon", "race", "rack", "radio", "radish", "rag", "rail", "railroad", "rain", "rainbow", "raindrop", "rainy", 
    "raise", "raisin", "rake", "ram", "ran", "ranch", "rang", "range", "rascal", "rat", "rate", "rather", "rattle", "rattlesnake", "raw", "ray", "rayon", "razor", "reach", "read", "ready", "real", "really", "rear", "reason", "rebuild", "receive", "recess", "record", "red", "redbird", "redbreast", "reflect", "refresh", "refreshment", 
    "refrigerator", "refuse", "register", "reindeer", "rejoice", "rejoin", "related", "religion", "remain", "remember", "remind", "remove", "rent", "repair", "repay", "repeat", "report", "respect", "rest", "restaurant", "restroom", "retire", "return", "review", "reward", "rhyme", "rib", "ribbon", "rice", "rich", "rid", "riddle", "ride", 
    "right", "rim", "ring", "rip", "ripe", "rise", "river", "road", "roar", "roast", "rob", "robber", "robbery", "robe", "robin", "rock", "rocket", "rocky", "rode", "roll", "roller", "romance", "roof", "room", "rooster", "root", "rope", "rose", "rot", "rotten", "rough", "round", "route", "row", "rowboat", "royal", "rub", "rubber", "rug", 
    "rule", "run", "rung", "rush", "rust", "rusty", "sack", "sad", "saddle", "sadness", "safe", "safety", "said", "sail", "sailboat", "sailor", "saint", "salad", "sale", "salt", "same", "sample", "sand", "sandwich", "sandy", "sang", "sank", "sap", "sat", "satisfactory", "sauce", "saucer", "sausage", "save", "savings", "saw", "sawdust", 
    "say", "scab", "scale", "scalp", "scamper", "scare", "scarecrow", "scarf", "scary", "scatter", "school", "schoolboy", "schoolgirl", "science", "scissors", "scoop", "scooter", "score", "scout", "scrap", "scratch", "scream", "screen", "screw", "scrub", "sea", "seal", "seam", "search", "seashore", "season", "seat", "second", "secret", 
    "see", "seed", "seem", "seen", "seesaw", "selection", "self", "selfish", "sell", "selves", "send", "sense", "sensible", "sent", "sentence", "separate", "servant", "serve", "service", "set", "settle", "seven", "seventeen", "seventh", "seventy", "several", "sew", "shade", "shadow", "shady", "shake", "shall", "shame", "shampoo", "shape", 
    "share", "sharp", "shave", "she", "she'd", "she'll", "sheep", "sheet", "shelf", "shell", "shelves", "shepherd", "shine", "shiny", "ship", "shipment", "shirt", "shock", "shoe", "shoemaker", "shook", "shoot", "shop", "shore", "short", "shortness", "shot", "should", "shoulder", "shouldn't", "shout", "shove", "shovel", "show", "shower", 
    "shown", "shut", "shutter", "shy", "sick", "sickness", "side", "sidewalk", "sigh", "sight", "sign", "silence", "silent", "silk", "sill", "silly", "silver", "simple", "sin", "since", "sing", "single", "sink", "sip", "sister", "sit", "six", "sixteen", "sixth", "sixty", "size", "skate", "ski", "skin", "skip", "skirt", "skunk", "sky", 
    "skyscraper", "slam", "slap", "slave", "sled", "sleep", "sleepy", "sleeve", "sleigh", "slept", "slice", "slid", "slide", "slim", "slip", "slipper", "slippery", "slosh", "slow", "slowly", "sly", "small", "smart", "smash", "smell", "smile", "smog", "smoke", "smoky", "smooth", "snack", "snail", "snake", "snap", "sneeze", "sniff", 
    "snow", "snowball", "snowflake", "snowy", "snug", "soak", "soap", "social", "sock", "soda", "sofa", "soft", "softball", "soil", "sold", "soldier", "solid", "solve", "some", "somebody", "someone", "something", "sometime", "somewhere", "son", "song", "soon", "sore", "sorrow", "sorry", "sort", "soul", "sound", "soup", "sour", "south", 
    "southern", "space", "spaceship", "spade", "spaghetti", "spank", "spark", "sparrow", "speak", "spear", "special", "speck", "speech", "speed", "speedometer", "spell", "spend", "spice", "spider", "spill", "spin", "spirit", "spit", "splash", "split", "spoil", "spoke", "sponge", "spook", "spooky", "spool", "spoon", "sport", "spot", 
    "sprain", "spray", "spread", "spring", "sprinkle", "spy", "square", "squash", "squeak", "squeaky", "squeal", "squeeze", "squirrel", "stab", "stable", "stack", "stage", "stair", "stale", "stalk", "stamp", "stand", "star", "starch", "stare", "start", "starve", "state", "states", "station", "statue", "stay", "steak", "steal", "steam", 
    "steel", "steep", "steeple", "steer", "step", "stepfather", "stepmother", "stereo", "stew", "stick", "sticky", "stiff", "still", "sting", "stink", "stir", "stitch", "stock", "stocking", "stole", "stolen", "stomach", "stone", "stood", "stool", "stoop", "stop", "stoplight", "store", "storeroom", "stork", "storm", "stormy", "story", 
    "storyteller", "stove", "straight", "straighten", "strange", "strap", "straw", "strawberry", "stream", "street", "strength", "stretch", "strike", "string", "strip", "stripe", "strong", "stuck", "student", "studio", "study", "stuff", "stumble", "stung", "stunt", "style", "subject", "submarine", "subtract", "subtraction", "such", 
    "suck", "sudden", "suddenly", "suffer", "sugar", "suit", "sum", "summer", "sun", "sunbeam", "sunburn", "sundown", "sunflower", "sung", "sunk", "sunken", "sunlight", "sunrise", "sunset", "sunshine", "supper", "suppose", "sure", "surface", "surfboard", "surgeon", "surprise", "surround", "surroundings", "suspect", "swallow", "swam", 
    "swamp", "swan", "swear", "sweat", "sweater", "sweep", "sweepstakes", "sweet", "sweeten", "sweetheart", "sweetness", "swell", "swept", "swift", "swim", "swing", "switch", "sword", "syllable", "table", "tablespoon", "tablet", "tack", "taffy", "tail", "tailor", "take", "taken", "tale", "talk", "tall", "tame", "tan", "tangle", "tank", 
    "tap", "tape", "tar", "taste", "tattle", "tattletale", "tattoo", "taught", "tax", "taxpayer", "tea", "teach", "teacher", "team", "teapot", "tear", "tease", "teaspoon", "teeth", "telegram", "telephone", "telescope", "television", "tell", "temper", "temperature", "ten", "tend", "tender", "tennis", "tent", "tenth", "term", "terrible", 
    "test", "than", "thank", "thankful", "that", "that's", "the", "theater", "their", "them", "then", "there", "there's", "thermometer", "these", "they", "they'd", "they'll", "they're", "they've", "thick", "thief", "thin", "thing", "think", "third", "thirst", "thirsty", "thirteen", "thirty", "this", "thorn", "those", "thought", "thoughtful", 
    "thoughtless", "thousand", "thread", "three", "threw", "throat", "throne", "through", "throw", "thrown", "thumb", "thunder", "tick", "tick-tock", "ticket", "tickle", "tiddlywinks", "tie", "tiger", "tight", "till", "timber", "time", "tin", "tinkle", "tiny", "tiptoe", "tire", "tissue", "title", "to", "toad", "toast", "tobacco", "today", 
    "toe", "together", "toilet", "told", "tomato", "tomorrow", "ton", "tone", "tongue", "tonight", "too", "took", "tool", "tooth", "toothbrush", "toothpaste", "top", "tore", "torn", "tornado", "torpedo", "tortoise", "toss", "total", "touch", "toward", "towel", "town", "toy", "trace", "track", "tractor", "trade", "traffic", "trail", "train", 
    "tramp", "trap", "trash", "travel", "tray", "treasure", "tree", "trespass", "trick", "tricycle", "trim", "trip", "trombone", "troop", "trophy", "trouble", "truck", "true", "truly", "trumpet", "trunk", "trust", "truth", "truthful", "try", "tub", "tube", "tug", "tulip", "tumble", "tune", "tunnel", "turkey", "turn", "turnip", "turtle", 
    "twelve", "twenty", "twice", "twig", "twin", "twist", "two", "type", "typewriter", "ugly", "umbrella", "umpire", "uncle", "under", "underline", "undershirt", "understand", "underwear", "undress", "uneducated", "unemployed", "unfair", "unfasten", "unfinished", "unfold", "unfurnished", "unhappy", "uniform", "united", "unkind", "unknown", 
    "unnecessary", "unsafe", "untie", "until", "untrue", "unwilling", "unwise", "unwrap", "up", "upon", "upper", "upset", "upside-down", "upstairs", "uptown", "upward", "us", "use", "useful", "usher", "vacant", "vacation", "valley", "valuable", "value", "vanish", "varnish", "vase", "vegetable", "velvet", "verse", "very", "vessel", "vest", 
    "vice-president", "view", "village", "vine", "violet", "violin", "visit", "visitor", "vitamin", "voice", "volleyball", "vote", "waffle", "wag", "wagon", "waist", "wait", "waiter", "wake", "waken", "walk", "wall", "wallet", "walnut", "wander", "want", "war", "warm", "warmth", "warn", "wart", "was", "wash", "washer", "washroom", "wasn't", 
    "wasp", "waste", "watch", "watchdog", "water", "waterfall", "watermelon", "waterproof", "wave", "wax", "way", "we", "we'll", "we're", "weak", "weaken", "weakness", "wealth", "weapon", "wear", "weather", "weave", "web", "wedding", "wee", "weed", "week", "weekdays", "weekend", "weep", "weigh", "weight", "welcome", "well", "went", "were", 
    "weren't", "west", "western", "wet", "whale", "what", "wheat", "wheel", "wheelbarrow", "when", "where", "where's", "which", "while", "whip", "whirl", "whirlpool", "whirlwind", "whisker", "whisper", "whistle", "white", "whiteness", "who", "who's", "whole", "whom", "whooping", "whose", "why", "wicked", "wide", "wide-awake", "wife", "wigwam", 
    "wild", "wildcat", "wildlife", "will", "willing", "willow", "win", "wind", "window", "windowpane", "windy", "wine", "wing", "wink", "winter", "wipe", "wire", "wise", "wish", "witch", "with", "without", "woke", "wolf", "wolves", "woman", "women", "won", "won't", "wonder", "wonderful", "wood", "woodchuck", "wooden", "woodpecker", "woods", 
    "woof", "wool", "woolen", "word", "wore", "work", "workman", "world", "worm", "worn", "worry", "worse", "worst", "worth", "would", "wouldn't", "wound", "wrap", "wreck", "wren", "wrist", "write", "written", "wrong", "wrote", "x-mas", "x-ray", "yard", "yarn", "yawn", "year", "yell", "yellow", "yellowish", "yes", "yesterday", "yet", "yolk", 
    "yonder", "you", "you'd", "you'll", "young", "youngster", "your", "yourself", "youth", "zebra", "zero", "zone", "zoo"
])
STOPWORDS = set([
    "a", "an", "and", "are", "as", "at", "be", "but", "by", "for", "from", "has", "have", "he", "her",
        "hers", "him", "his", "in", "is", "it", "its", "of", "on", "or", "that", "the", "to", "was", "were",
        "will", "with", "i", "you", "we", "they", "this", "those", "these", "my", "our", "your", "their", "me",
        "us", "mine", "ours", "yours", "theirs", "myself", "yourself", "ourselves", "themselves", "yourselves",
        "am", "do", "does", "did", "doing", "done", "can", "could", "may", "might", "should", "would", "shall",
        "if", "then", "than", "so", "because", "while", "when", "where", "which", "who", "whom", "whose", "what",
        "why", "how", "not", "no", "nor", "only", "also", "very", "just", "too", "into", "onto", "upon", "about",
        "across", "after", "before", "between", "through", "during", "under", "over", "again", "further", "once",
        "there", "here", "such", "same", "own", "per", "via", "off", "out", "up", "down", "inside", "outside",
        "within", "without", "toward", "towards", "along", "among", "amongst", "beside", "besides", "beyond", "near",
        "around", "against", "except", "plus", "minus", "yet", "however", "therefore", "thus", "hence", "otherwise",
        "although", "though", "unless", "until", "since", "whether", "either", "neither", "both", "many", "much",
        "more", "most", "some", "any", "few", "several", "various", "another", "other", "others", "someone",
        "something", "somewhere", "anyone", "anything", "anywhere", "everyone", "everything", "everywhere", "nobody",
        "nothing", "nowhere", "one", "ones", "two", "three", "first", "second", "third", "former", "latter",
        "im", "ive", "id", "ill", "youre", "youve", "youll", "theyre", "theyve", "theyll", "dont", "didnt",
        "doesnt", "cant", "couldnt", "shouldnt", "wouldnt", "isnt", "arent", "wasnt", "werent", "havent", "hasnt",
        "hadnt", "wont", "neednt", "mustnt", "lets", "thats", "whats", "heres", "theres", "okay", "ok"
])
# Sentiment lexicon
POSITIVE_WORDS = {
    "good", "great", "excellent", "happy", "love", "wonderful", "best", "positive", "success", "fortunate", "correct", "superior",
    "amazing", "awesome", "fantastic", "outstanding", "brilliant", "delight", "delighted", "delightful", "enjoy", "enjoyed", "enjoyable",
    "pleasure", "pleased", "pleasing", "pleasurable", "satisfied", "satisfying", "satisfaction", "cheerful", "cheery", "joy", "joyful", "joyous",
    "bliss", "blissful", "optimistic", "hopeful", "encourage", "encouraging", "encouraged", "strong", "strength", "improve", "improved", "improving",
    "progress", "progressed", "progressing", "win", "winner", "winning", "achieve", "achieved", "achievement", "achieving", "advance", "advanced",
    "advancing", "benefit", "beneficial", "benefited", "benefiting", "reward", "rewarding", "reliable", "reliably", "secure", "secured", "securely",
    "support", "supported", "supportive", "supporting", "trust", "trusted", "trustworthy", "valued", "value", "valuing", "admire", "admired",
    "admiring", "admiration", "respect", "respected", "respectful", "respecting", "grateful", "gratitude", "thankful", "thanks", "thank",
    "peace", "peaceful", "calm", "calming", "calmed", "relax", "relaxed", "relaxing", "relaxation", "inspire", "inspired", "inspiring",
    "inspiration", "creative", "creativity", "creative", "creatively", "innovate", "innovative", "innovation", "innovator"
}
NEGATIVE_WORDS = {
    "bad", "terrible", "poor", "sad", "hate", "awful", "worst", "negative", "failure", "unfortunate", "wrong", "inferior",
    "horrible", "horrid", "disgust", "disgusted", "disgusting", "disappoint", "disappointed", "disappointing", "disappointment", "angry", "anger",
    "upset", "upsetting", "upsetted", "depress", "depressed", "depressing", "depression", "miserable", "misery", "pain", "painful", "hurt", "hurting",
    "worse", "weak", "weaken", "weakened", "weakening", "fail", "failed", "failing", "fails", "problem", "problems", "problematic", "loss", "lost",
    "losing", "lose", "loser", "risk", "risky", "danger", "dangerous", "dangerously", "unsafe", "unsecure", "unreliable", "untrustworthy",
    "unhappy", "unhappily", "unlucky", "unluckily", "unloved", "unwanted", "unwelcome", "unpleasant", "unpleasantly", "unfortunate", "unfortunately",
    "stress", "stressed", "stressful", "stressfully", "worry", "worried", "worrying", "worrisome", "fear", "fearful", "afraid", "scared", "scary",
    "anxious", "anxiety", "regret", "regretted", "regretting", "regretful", "regretfully", "resent", "resentful", "resentment", "criticize", "criticized",
    "criticizing", "criticism", "blame", "blamed", "blaming", "blames", "complain", "complained", "complaining", "complaint", "complaints", "failures"
}
# Emotion lexicon
EMOTION_LEXICON = {
    "joy": {
        "happy", "happiness", "joy", "joyful", "joyous", "cheerful", "cheery", "delighted", "delight", "delightful", "excited", "exciting", "excitable", "content", "contented", "contentment", "grateful", "gratitude", "relieved", "relief", "hopeful", "hope", "optimistic", "optimism", "calm", "calming", "calmed", "peaceful", "peace", "proud", "pride", "thankful", "thanks", "satisfied", "satisfying", "satisfaction", "encouraged", "encouraging", "inspired", "inspiring", "energized", "energised", "uplifted", "uplifting", "glad", "confident", "confidence", "secure", "security", "loved", "love", "loving", "connected", "connection", "playful", "playfulness", "amused", "amusement", "enthusiastic", "enthusiasm", "motivated", "motivation", "stable", "stability", "pleasant", "pleasantness", "bright", "brightness", "thrilled", "thrilling", "ecstatic", "ecstasy", "blessed", "blessing", "comforted", "comfort", "light", "lighter", "settled", "grounded", "supported", "support", "safe", "safety", "rewarded", "reward", "fulfilled", "fulfillment", "renewed", "renewal", "fresh", "freshness", "alive", "aliveness", "curious", "curiosity", "creative", "creativity", "productive", "productivity", "elated", "elation", "gleeful", "glee", "radiant", "radiance", "vivacious", "vivacity", "merry", "merriment", "exuberant", "exuberance", "bubbly", "bubbling", "jubilant", "jubilation", "exhilarated", "exhilaration", "zestful", "zest", "buoyant", "buoyancy"
    },
    "sadness": {
        "sad", "sadness", "down", "downcast", "downhearted", "lonely", "loneliness", "tired", "tiredness", "hurt", "hurting", "empty", "emptiness", "hopeless", "hopelessness", "depressed", "depression", "blue", "blues", "gloomy", "gloom", "heartbroken", "heartbreak", "discouraged", "discouragement", "disappointed", "disappointment", "drained", "draining", "unmotivated", "unmotivating", "ashamed", "shame", "guilty", "guilt", "regretful", "regret", "miserable", "misery", "grief", "grieving", "lost", "loss", "isolated", "isolation", "withdrawn", "withdrawal", "numb", "numbness", "fragile", "fragility", "burned", "burnt", "defeated", "defeat", "helpless", "helplessness", "low", "lowness", "heavy", "heaviness", "melancholy", "sorrow", "sorrowful", "tearful", "teary", "weary", "weariness", "worn", "wornout", "unseen", "invisible", "rejected", "rejection", "abandoned", "abandonment", "forsaken", "forsakenness", "despair", "despairing", "resigned", "resignation", "flattened", "blunted", "demoralized", "demoralization", "dismayed", "dismay", "apathetic", "apathy", "doleful", "woeful", "mournful", "lament", "lamenting", "crestfallen", "disheartened", "disheartenment", "downspirited"
    },
    "anger": {
        "angry", "anger", "frustrated", "frustration", "annoyed", "annoyance", "furious", "fury", "irritated", "irritation", "resentful", "resentment", "mad", "enraged", "enrage", "outraged", "outrage", "bitter", "bitterness", "hostile", "hostility", "impatient", "impatience", "agitated", "agitation", "offended", "offense", "disgusted", "disgust", "fedup", "betrayed", "betrayal", "defensive", "defensiveness", "tense", "tension", "volatile", "volatility", "heated", "irate", "fuming", "fume", "upset", "upsetting", "triggered", "provoked", "provocation", "contempt", "spiteful", "spite", "raging", "rage", "snappy", "aggravated", "aggravation", "inflamed", "inflame", "workedup", "seething", "embittered", "soured", "cross", "indignant", "indignation", "combative", "argumentative", "argument", "harsh", "harshness", "steam", "boiling", "shorttempered", "shorttemperedness", "explosive", "explosiveness", "abrasive", "abrasiveness", "wrath", "wrathful", "incensed", "incense", "irascible", "irascibility", "stormy", "storminess", "fiery", "fire", "tempestuous", "tempest", "belligerent", "belligerence"
    },
    "fear": {
        "afraid", "fear", "fearful", "fearfulness", "anxious", "anxiety", "worried", "worry", "worrisome", "nervous", "nervousness", "scared", "scary", "uncertain", "uncertainty", "panicked", "panic", "dread", "dreadful", "terrified", "terror", "stressed", "stress", "overwhelmed", "overwhelming", "uneasy", "uneasiness", "apprehensive", "apprehension", "restless", "restlessness", "onedge", "onedge", "vulnerable", "vulnerability", "insecure", "insecurity", "hesitant", "hesitation", "cautious", "caution", "concerned", "concern", "alarmed", "alarm", "shaky", "shakiness", "paranoid", "paranoia", "threatened", "threat", "unsafe", "distrustful", "distrust", "tense", "tension", "jittery", "jitteriness", "hypervigilant", "hypervigilance", "edgy", "frightened", "fright", "unsettled", "startled", "startle", "intimidated", "intimidation", "spooked", "wary", "wariness", "guarded", "timid", "timidity", "avoidant", "avoidance", "foreboding", "forebode", "suspicious", "suspicion", "timorous", "timorousness", "phobic", "phobia", "alarmed", "alarmist"
    },
    "disgust": {
        "disgust", "disgusted", "disgusting", "gross", "grossedout", "revolting", "revolt", "repulsed", "repulsive", "repulse", "nauseated", "nauseous", "nausea", "sickened", "sickening", "filthy", "filth", "dirty", "dirtiness", "toxic", "toxicity", "abhorrent", "abhorrence", "appalled", "appalling", "distaste", "distasteful", "detest", "detested", "detestable", "loathing", "loathe", "loathsome", "offensive", "offense", "foul", "foulness", "vile", "vileness", "contaminated", "contamination", "contaminant", "unclean", "uncleanness", "revolted", "revoltingly"
    },
    "surprise": {
        "surprised", "surprise", "surprising", "shocked", "shock", "astonished", "astonish", "astonishing", "amazed", "amaze", "amazing", "startled", "startle", "stunned", "stun", "unexpected", "unexpectedly", "suddenly", "sudden", "wow", "unreal", "unreality", "blindsided", "caughtoffguard", "abrupt", "abruptly", "unforeseen", "outofnowhere", "remarkable", "eyeopening", "eyeopener", "disbelief", "incredulous", "incredulity", "baffled", "baffling", "flabbergasted", "flabbergast", "dumbfounded", "dumbfound", "gobsmacked", "staggered", "staggering", "jawdrop", "jawdropping", "bewildered", "bewildering", "perplexed", "perplexing", "confounded", "confounding"
    },
}

class RobTextStats:
    __version__ = "1.0.0"
    def __init__(self, text: str):
        self.text = text
        self.words = re.findall(r'\b\w+\b', text)
        self.sentences = [s for s in re.split(r'[.!?]+', text) if s.strip()]
        self.word_count = len(self.words)
        self.sentence_count = max(len(self.sentences), 1)
        self.char_count = sum(len(w) for w in self.words)
        self.syllable_count = sum(self.count_syllables(w) for w in self.words)
        self.polysyllables = sum(1 for w in self.words if self.count_syllables(w) >= 3)
        self.long_words = [w for w in self.words if len(w) >= 7]
        self.difficult_words = [w for w in self.words if w.lower() not in DALE_CHALL_EASY_WORDS]
        self.percent_difficult = (len(self.difficult_words) / self.word_count) * 100 if self.word_count > 0 else 0
        self.word_freq = Counter(self.words)
        self.unique_words = set(self.words)
        self.stopword_count = sum(1 for w in self.words if w.lower() in STOPWORDS)
        self.paragraph_count = text.count('\n\n') + 1 if text.strip() else 0
        self.dialogue_count = sum(1 for s in self.sentences if s and s[0] in {'"', "'", '“', '‘'})
        self.passive_count = len(re.findall(r'\b(?:was|were|is|are|been|be)\b\s+\w+ed\b', text, re.IGNORECASE))
        self.question_count = text.count('?')
        self.exclam_count = text.count('!')

    @staticmethod
    def count_syllables(word: str) -> int:
        word = word.lower()
        syllable_count = 0
        vowels = "aeiouy"
        if word and word[0] in vowels:
            syllable_count += 1
        for index in range(1, len(word)):
            if word[index] in vowels and word[index - 1] not in vowels:
                syllable_count += 1
        if word.endswith("e") and not word.endswith("le"):
            syllable_count -= 1
        if syllable_count == 0:
            syllable_count = 1
        return syllable_count

    def basic_metrics(self) -> Dict[str, Any]:
        word_count = self.word_count
        sentence_count = self.sentence_count
        syllable_count = self.syllable_count
        polysyllables = self.polysyllables
        char_count = self.char_count
        percent_difficult = self.percent_difficult
        dale_chall_score = 0.1579 * percent_difficult + 0.0496 * (word_count / sentence_count) + (3.6365 if percent_difficult > 5 else 0)
        avg_word_length = (char_count / word_count) if word_count > 0 else 0
        long_word_ratio = (len(self.long_words) / word_count) if word_count > 0 else 0
        thought_fragmentation = (sentence_count / word_count) * 100 if word_count > 0 else 0
        flesch_reading_ease = 206.835 - 1.015 * (word_count / sentence_count) - 84.6 * (syllable_count / word_count)
        flesch_grade_level = 0.39 * (word_count / sentence_count) + 11.8 * (syllable_count / word_count) - 15.59
        smog = 1.0430 * (polysyllables * (30 / sentence_count)) ** 0.5 + 3.1291 if sentence_count >= 1 else 0
        ari = 4.71 * (char_count / word_count) + 0.5 * (word_count / sentence_count) - 21.43 if word_count > 0 else 0
        gunning_fog = 0.4 * ((word_count / sentence_count) + 100 * (polysyllables / word_count)) if word_count > 0 else 0
        reading_time_min = word_count / 200
        return {
            "word_count": word_count,
            "sentence_count": sentence_count,
            "syllable_count": syllable_count,
            "polysyllable_count": polysyllables,
            "flesch_reading_ease": round(flesch_reading_ease, 2),
            "flesch_grade_level": round(flesch_grade_level, 2),
            "smog_index": round(smog, 2),
            "ari": round(ari, 2),
            "gunning_fog": round(gunning_fog, 2),
            "dale_chall": round(dale_chall_score, 2),
            "avg_word_length": round(avg_word_length, 2),
            "long_word_ratio": round(long_word_ratio, 3),
            "thought_fragmentation": round(thought_fragmentation, 2),
            "approx_reading_time_min": round(reading_time_min, 2)
        }

    def advanced_metrics(self) -> Dict[str, Any]:
        word_count = self.word_count
        sentence_count = self.sentence_count
        lexical_diversity = len(self.unique_words) / word_count if word_count > 0 else 0
        avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
        median_word_length = statistics.median(map(len, self.words)) if self.words else 0
        median_sentence_length = statistics.median([len(re.findall(r'\b\w+\b', s)) for s in self.sentences]) if self.sentences else 0
        ttr = len(self.unique_words) / word_count if word_count > 0 else 0
        hapax_legomena = sum(1 for w in self.word_freq if self.word_freq[w] == 1)
        hapax_legomena_ratio = hapax_legomena / word_count if word_count > 0 else 0
        longest_word = max(self.words, key=len) if self.words else ''
        longest_sentence = max(self.sentences, key=lambda s: len(re.findall(r'\b\w+\b', s))) if self.sentences else ''
        passive_ratio = self.passive_count / sentence_count if sentence_count > 0 else 0
        question_exclam_ratio = (self.question_count + self.exclam_count) / sentence_count if sentence_count > 0 else 0
        paragraph_count = self.paragraph_count
        dialogue_ratio = self.dialogue_count / sentence_count if sentence_count > 0 else 0
        reading_time_150 = word_count / 150 if word_count > 0 else 0
        reading_time_250 = word_count / 250 if word_count > 0 else 0
        syllables_per_word = self.syllable_count / word_count if word_count > 0 else 0
        def is_number(s):
            try:
                float(s)
                return True
            except Exception:
                return False
        difficult_word_list = sorted(set(w for w in self.difficult_words if not is_number(w)))
        return {
            "lexical_diversity": round(lexical_diversity, 3),
            "avg_sentence_length": round(avg_sentence_length, 2),
            "median_word_length": median_word_length,
            "median_sentence_length": median_sentence_length,
            "type_token_ratio": round(ttr, 3),
            "hapax_legomena_ratio": round(hapax_legomena_ratio, 3),
            "longest_word": longest_word,
            "longest_sentence": longest_sentence.strip(),
            "passive_voice_ratio": round(passive_ratio, 3),
            "question_exclamation_ratio": round(question_exclam_ratio, 3),
            "paragraph_count": paragraph_count,
            "dialogue_ratio": round(dialogue_ratio, 3),
            "reading_time_150wpm": round(reading_time_150, 2),
            "reading_time_250wpm": round(reading_time_250, 2),
            "syllables_per_word": round(syllables_per_word, 3),
            "difficult_word_list": difficult_word_list
        }

    def llm_metrics(self) -> Dict[str, Any]:
        token_count = int(self.word_count * 1.33)
        context_suggestion = next((c for c in [2048, 4096, 8192, 32768, 100000] if token_count <= c), 100000)
        total = sum(self.word_freq.values())
        entropy = -sum((freq/total) * math.log2(freq/total) for freq in self.word_freq.values() if freq > 0) if total > 0 else 0
        token_word_ratio = token_count / self.word_count if self.word_count > 0 else 0
        stopword_ratio = self.stopword_count / self.word_count if self.word_count > 0 else 0
        try:
            compressed = len(zlib.compress(self.text.encode('utf-8')))
            compression_ratio = compressed / len(self.text.encode('utf-8')) if len(self.text) > 0 else 0
        except Exception:
            compression_ratio = 0
        unique_token_ratio = len(self.unique_words) / token_count if token_count > 0 else 0
        return {
            "token_count": token_count,
            "context_suggestion": context_suggestion,
            "perplexity_entropy": round(entropy, 3),
            "token_word_ratio": round(token_word_ratio, 3),
            "stopword_ratio": round(stopword_ratio, 3),
            "compression_ratio": round(compression_ratio, 3),
            "unique_token_ratio": round(unique_token_ratio, 3)
        }

    def text_analytics(self) -> Dict[str, Any]:
        # Frequency Distribution
        words_3plus = [w.lower() for w in self.words if len(w) > 3]
        freq_dist = Counter(words_3plus)
        top_10 = freq_dist.most_common(10)
        def ngrams(words, n):
            return [" ".join(words[i:i+n]) for i in range(len(words)-n+1)] if len(words) >= n else []
        lower_words = [w.lower() for w in self.words]
        bigrams = Counter(ngrams(lower_words, 2)).most_common(10)
        trigrams = Counter(ngrams(lower_words, 3)).most_common(10)
        quadgrams = Counter(ngrams(lower_words, 4)).most_common(10)
        quintgrams = Counter(ngrams(lower_words, 5)).most_common(10)
        # Semantic and Content (simple heuristics)
        # Sentiment: simple polarity by counting positive/negative words (placeholder)
        pos_count = sum(1 for w in self.words if w.lower() in POSITIVE_WORDS)
        neg_count = sum(1 for w in self.words if w.lower() in NEGATIVE_WORDS)
        intensity_score = (pos_count - neg_count) / max(self.word_count, 1)
        if intensity_score > 0.05:
            score_text_label = "positive"
        elif intensity_score < -0.05:
            score_text_label = "negative"
        else:
            score_text_label = "neutral"
        # Emotion analysis
        emotion_counts = {}
        for emotion, words in EMOTION_LEXICON.items():
            emotion_counts[emotion] = sum(1 for w in self.words if w.lower() in words)

        # Find dominant emotion (with at least one hit), else None
        dominant_emotion = None
        if emotion_counts:
            # Only consider emotions with at least one hit
            filtered = {k: v for k, v in emotion_counts.items() if v > 0}
            if filtered:
                dominant_emotion = max(filtered, key=lambda k: filtered[k])

        return {
            "frequency_distribution": {
                "top_10_most_common_words_3plus": top_10,
                "word_count": self.word_count,
                "avg_word_length": round(self.char_count / self.word_count, 2) if self.word_count else 0,
                "phrase_frequency": {
                    "bigrams": [{"phrase": k, "count": v} for k, v in bigrams],
                    "trigrams": [{"phrase": k, "count": v} for k, v in trigrams],
                    "quadgrams": [{"phrase": k, "count": v} for k, v in quadgrams],
                    "quintgrams": [{"phrase": k, "count": v} for k, v in quintgrams],
                }
            },
            "semantic_and_content": {
                "sentiment": {
                    "intensity_score": round(intensity_score, 3),
                    "score_text_label": score_text_label
                },
                "emotion": {
                    "dominant_emotion": dominant_emotion,
                    "emotion_counts": emotion_counts
                }
            }
        }

    def analyze(self, advanced: bool = False, llm: bool = False, text_analytics: bool = True) -> Dict[str, Any]:
        result = {"basic": self.basic_metrics()}
        if advanced:
            result["advanced"] = self.advanced_metrics()
        if llm:
            result["llm"] = self.llm_metrics()
        if text_analytics:
            result["text_analytics"] = self.text_analytics()
        return result

# CLI/main logic

def collect_files(targets):
    files = []
    for target in targets:
        if os.path.isdir(target):
            for root, _, filenames in os.walk(target):
                for fname in filenames:
                    if fname.lower().endswith(('.md', '.markdown', '.txt')):
                        files.append(os.path.join(root, fname))
        else:
            files.extend(glob.glob(target))
    return list(sorted(set(files)))

if __name__ == "__main__":
    import argparse
    import sys
    import json
    parser = argparse.ArgumentParser(
        description=f"RobTextStats CLI v{RobTextStats.__version__}: Analyze text files for readability and LLM metrics.")
    parser.add_argument('targets', nargs='*', help='Files, folders, or glob patterns to analyze')
    parser.add_argument('-o', '--output', help='Output JSON file (if omitted, prints to console)')
    parser.add_argument('--advanced', action='store_true', help='Include advanced metrics')
    parser.add_argument('--llm', action='store_true', help='Include LLM metrics')
    parser.add_argument('--text_analytics', action='store_true', help='Include text analytics section (frequency, n-grams, sentiment, emotion)')
    parser.add_argument('--help-metric', metavar='METRIC', help='Show detailed help for a specific metric (e.g., flesch_reading_ease)')
    parser.add_argument('--list-metrics', action='store_true', help='List all available stat metrics collected by this utility')
    parser.add_argument('--overall', action='store_true', help='Output only overall totals/averages across all files, not per-file stats')
    parser.add_argument('--version', action='store_true', help='Show version and exit')
    args = parser.parse_args()

    if args.version:
        print(f"RobTextStats version {RobTextStats.__version__}")
        sys.exit(0)

    if args.help_metric:
        metric_help = {
            "word_count": "Total number of words in the text.",
            "sentence_count": "Total number of sentences.",
            "syllable_count": "Total number of syllables.",
            "polysyllable_count": "Words with 3 or more syllables.",
            "flesch_reading_ease": "Flesch Reading Ease score: higher is easier to read.",
            "flesch_grade_level": "Flesch-Kincaid Grade Level: US school grade required to understand.",
            "smog_index": "SMOG Index: estimates years of education needed.",
            "ari": "Automated Readability Index: grade level estimate.",
            "gunning_fog": "Gunning Fog Index: grade level estimate.",
            "dale_chall": "Dale-Chall score: readability based on familiar words.",
            "avg_word_length": "Average word length in characters.",
            "long_word_ratio": "Ratio of words with 7+ characters.",
            "thought_fragmentation": "Sentence-to-word ratio, higher means more fragmented thoughts.",
            "approx_reading_time_min": "Estimated reading time in minutes (200 wpm).",
            "lexical_diversity": "Unique words divided by total words.",
            "avg_sentence_length": "Average number of words per sentence.",
            "median_word_length": "Median word length.",
            "median_sentence_length": "Median sentence length in words.",
            "type_token_ratio": "Unique words divided by total words.",
            "hapax_legomena_ratio": "Ratio of words that appear only once.",
            "longest_word": "Longest word in the text.",
            "longest_sentence": "Longest sentence in the text.",
            "passive_voice_ratio": "Ratio of sentences using passive voice.",
            "question_exclamation_ratio": "Ratio of questions and exclamations to total sentences.",
            "paragraph_count": "Number of paragraphs (split by blank lines).",
            "dialogue_ratio": "Ratio of sentences that are dialogue.",
            "reading_time_150wpm": "Estimated reading time at 150 words per minute.",
            "reading_time_250wpm": "Estimated reading time at 250 words per minute.",
            "syllables_per_word": "Average syllables per word.",
            "difficult_word_list": "List of words not in Dale-Chall easy word list.",
            "token_count": "Estimated token count for LLMs (word count x 1.33).",
            "context_suggestion": "Suggested LLM context window size.",
            "perplexity_entropy": "Shannon entropy of word distribution (lower = more predictable).",
            "token_word_ratio": "Ratio of tokens to words.",
            "stopword_ratio": "Ratio of stopwords to total words.",
            "compression_ratio": "Ratio of compressed to original text size.",
            "unique_token_ratio": "Unique words divided by token count."
        }
        if args.help_metric in metric_help:
            print(f"{args.help_metric}: {metric_help[args.help_metric]}")
        else:
            print(f"No help found for metric '{args.help_metric}'.")
        sys.exit(0)
    if args.list_metrics:
        all_metrics = [
            "word_count", "sentence_count", "syllable_count", "polysyllable_count", "flesch_reading_ease", "flesch_grade_level", "smog_index", "ari", "gunning_fog", "dale_chall", "avg_word_length", "long_word_ratio", "thought_fragmentation", "approx_reading_time_min",
            "lexical_diversity", "avg_sentence_length", "median_word_length", "median_sentence_length", "type_token_ratio", "hapax_legomena_ratio", "longest_word", "longest_sentence", "passive_voice_ratio", "question_exclamation_ratio", "paragraph_count", "dialogue_ratio", "reading_time_150wpm", "reading_time_250wpm", "syllables_per_word", "difficult_word_list",
            "token_count", "context_suggestion", "perplexity_entropy", "token_word_ratio", "stopword_ratio", "compression_ratio", "unique_token_ratio"
        ]
        print("Available metrics:")
        for m in all_metrics:
            print(f"- {m}")
        sys.exit(0)
    files = collect_files(args.targets)
    if not files:
        print("No files found matching targets.")
        sys.exit(1)
    results = []
    for filepath in files:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()
        except Exception as e:
            results.append({"file_info": {"file_name": os.path.basename(filepath), "file_path": filepath}, "error": str(e)})
            continue
        stat = os.stat(filepath)
        created = datetime.datetime.fromtimestamp(stat.st_ctime).isoformat()
        modified = datetime.datetime.fromtimestamp(stat.st_mtime).isoformat()
        ext = os.path.splitext(filepath)[1].lower()
        if ext in ['.md', '.markdown']:
            file_type = 'Markdown'
        elif ext in ['.txt']:
            file_type = 'Text'
        else:
            file_type = 'Other'
        stats = RobTextStats(text)
        analysis = stats.analyze(advanced=args.advanced, llm=args.llm, text_analytics=args.text_analytics)
        file_info = {
            "file_name": os.path.basename(filepath),
            "file_path": filepath,
            "created": created,
            "modified": modified,
            "file_type": file_type
        }
        result = {"file_info": file_info}
        result.update(analysis)
        results.append(result)

    if args.overall:
        valid = [r for r in results if 'error' not in r]
        if not valid:
            overall = {"error": "No valid files to aggregate."}
        else:
            from collections import Counter
            type_counter = Counter(r['file_info']['file_type'] for r in valid)
            basic_keys = list(valid[0]['basic'].keys())
            adv_keys = list(valid[0]['advanced'].keys()) if args.advanced and 'advanced' in valid[0] else []
            def sum_or_avg(key, is_avg=True, adv=False):
                vals = [r['advanced' if adv else 'basic'][key] for r in valid if key in r['advanced' if adv else 'basic']]
                if not vals:
                    return 0
                sum_basic = {"word_count", "sentence_count", "syllable_count", "polysyllable_count", "paragraph_count", "approx_reading_time_min"}
                sum_advanced = {"paragraph_count", "reading_time_150wpm", "reading_time_250wpm"}
                if (not adv and key in sum_basic) or (adv and key in sum_advanced):
                    return round(sum(vals), 3)
                if all(isinstance(v, int) for v in vals):
                    return sum(vals)
                return round(sum(vals) / len(vals), 3)
            def is_number(s):
                try:
                    float(s)
                    return True
                except Exception:
                    return False
            def concat_lists(key, adv=False):
                all_items = []
                for r in valid:
                    v = r['advanced' if adv else 'basic'].get(key)
                    if isinstance(v, list):
                        all_items.extend(v)
                return sorted(set(x for x in all_items if not is_number(x)))
            file_info = {
                "file_name": args.targets if len(args.targets) > 1 else (args.targets[0] if args.targets else ""),
                "created": datetime.datetime.now().isoformat(),
                "file_type": [{k: v for k, v in type_counter.items()}],
            }
            overall = {"file_info": file_info}
            overall["basic"] = {}
            for k in basic_keys:
                if k == "longest_word":
                    overall["basic"][k] = max((r['basic'][k] for r in valid if r['basic'][k]), key=len, default="")
                elif k == "longest_sentence":
                    overall["basic"][k] = max((r['basic'][k] for r in valid if r['basic'][k]), key=lambda s: len(s.split()), default="")
                elif k == "difficult_word_list":
                    overall["basic"][k] = concat_lists(k)
                elif k in {"word_count", "sentence_count", "syllable_count", "polysyllable_count", "paragraph_count", "approx_reading_time_min"}:
                    overall["basic"][k] = sum_or_avg(k, is_avg=False)
                else:
                    overall["basic"][k] = sum_or_avg(k, is_avg=True)
            if args.advanced and adv_keys:
                overall["advanced"] = {}
                for k in adv_keys:
                    if k == "longest_word":
                        overall["advanced"][k] = max((r['advanced'][k] for r in valid if r['advanced'][k]), key=len, default="")
                    elif k == "longest_sentence":
                        overall["advanced"][k] = max((r['advanced'][k] for r in valid if r['advanced'][k]), key=lambda s: len(s.split()), default="")
                    elif k == "difficult_word_list":
                        overall["advanced"][k] = concat_lists(k, adv=True)
                    elif k in {"paragraph_count", "reading_time_150wpm", "reading_time_250wpm"}:
                        overall["advanced"][k] = sum_or_avg(k, is_avg=False, adv=True)
                    else:
                        overall["advanced"][k] = sum_or_avg(k, is_avg=True, adv=True)
            if args.llm:
                llm_keys = [k for k in valid[0].get('llm', {}).keys()] if valid and 'llm' in valid[0] else []
                if llm_keys:
                    overall['llm'] = {}
                    for k in llm_keys:
                        vals = [r['llm'][k] for r in valid if 'llm' in r and k in r['llm'] and r['llm'][k] is not None]
                        if not vals:
                            overall['llm'][k] = None
                        elif k == 'token_count':
                            overall['llm'][k] = sum(vals)
                        elif k == 'context_suggestion':
                            overall['llm'][k] = max(vals)
                        else:
                            overall['llm'][k] = round(sum(vals) / len(vals), 3)
            # Aggregate text_analytics if requested
            if args.text_analytics:
                # For frequency_distribution, aggregate top words and n-grams
                from collections import Counter
                all_words_3plus = []
                all_bigrams = []
                all_trigrams = []
                all_quadgrams = []
                all_quintgrams = []
                for r in valid:
                    ta = r.get('text_analytics', {})
                    fd = ta.get('frequency_distribution', {})
                    all_words_3plus.extend([w for w, _ in fd.get('top_10_most_common_words_3plus', [])])
                    all_bigrams.extend([item['phrase'] for item in fd.get('phrase_frequency', {}).get('bigrams', [])])
                    all_trigrams.extend([item['phrase'] for item in fd.get('phrase_frequency', {}).get('trigrams', [])])
                    all_quadgrams.extend([item['phrase'] for item in fd.get('phrase_frequency', {}).get('quadgrams', [])])
                    all_quintgrams.extend([item['phrase'] for item in fd.get('phrase_frequency', {}).get('quintgrams', [])])
                freq_dist = Counter(all_words_3plus)
                bigrams = Counter(all_bigrams)
                trigrams = Counter(all_trigrams)
                quadgrams = Counter(all_quadgrams)
                quintgrams = Counter(all_quintgrams)
                # Semantic and content: merge sentiment
                sentiments = [r.get('text_analytics', {}).get('semantic_and_content', {}).get('sentiment', {}) for r in valid]
                avg_intensity = round(sum(s.get('intensity_score', 0) for s in sentiments) / len(sentiments), 3) if sentiments else 0
                from collections import Counter as C2
                label_counts = C2(s.get('score_text_label', 'neutral') for s in sentiments)
                score_text_label = label_counts.most_common(1)[0][0] if label_counts else 'neutral'
                # Aggregate emotion
                emotion_dicts = [r.get('text_analytics', {}).get('semantic_and_content', {}).get('emotion', {}) for r in valid]
                # Sum emotion_counts for each emotion
                total_emotion_counts = {}
                for emo in emotion_dicts:
                    for k, v in emo.get('emotion_counts', {}).items():
                        total_emotion_counts[k] = total_emotion_counts.get(k, 0) + v
                # Find dominant emotion overall
                dominant_emotion = None
                filtered = {k: v for k, v in total_emotion_counts.items() if v > 0}
                if filtered:
                    dominant_emotion = max(filtered, key=lambda k: filtered[k])
                overall['text_analytics'] = {
                    'frequency_distribution': {
                        'top_10_most_common_words_3plus': freq_dist.most_common(10),
                        'word_count': sum(r['basic']['word_count'] for r in valid),
                        'avg_word_length': round(sum(r['basic']['avg_word_length'] for r in valid) / len(valid), 2) if valid else 0,
                        'phrase_frequency': {
                            'bigrams': [{'phrase': k, 'count': v} for k, v in bigrams.most_common(10)],
                            'trigrams': [{'phrase': k, 'count': v} for k, v in trigrams.most_common(10)],
                            'quadgrams': [{'phrase': k, 'count': v} for k, v in quadgrams.most_common(10)],
                            'quintgrams': [{'phrase': k, 'count': v} for k, v in quintgrams.most_common(10)],
                        }
                    },
                    'semantic_and_content': {
                        'sentiment': {
                            'intensity_score': avg_intensity,
                            'score_text_label': score_text_label
                        },
                        'emotion': {
                            'dominant_emotion': dominant_emotion,
                            'emotion_counts': total_emotion_counts
                        }
                    }
                }
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as out:
                    json.dump(overall, out, indent=2)
                print(f"Overall statistics written to {args.output}")
            else:
                print(json.dumps(overall, indent=2))
    else:
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as out:
                json.dump(results, out, indent=2)
            print(f"Statistics written to {args.output}")
        else:
            print(json.dumps(results, indent=2))
