import re

# ---------- Step 1: Normalize Urdu text ----------
def normalize_text(text):
    text = re.sub(r'\s+', ' ', text)  # remove multiple spaces
    text = text.replace(",", "،")     # fix commas
    text = text.replace("''", "’’").replace("``", "‘‘")  # quotes
    return text.strip()

# ---------- Step 2: Insert full stops before discourse markers ----------
def insert_fullstop_before_markers(text):
    # Only strong markers, not "اور"
    markers = ["دوسری جانب", "اس موقعے پر", "چنانچہ", "لیکن", "مگر", "اب", "آج", "ساتھ ہی"]
    for m in markers:
        text = re.sub(
            rf'(?<![۔؟!،])\s+({m})',
            r'۔ \1',
            text
        )
    return text

# ---------- Step 3: Urdu Sentence Segmentation ----------
def urdu_sentence_segmenter(text):
    text = normalize_text(text)
    text = insert_fullstop_before_markers(text)

    sentences = re.split(r'([۔?!])(?=\s|$)', text)


    final_sentences = []
    for i in range(0, len(sentences) - 1, 2):
        s = sentences[i].strip() + sentences[i + 1]
        if s.strip():
            final_sentences.append(s.strip())

    # ---------- Step 4: Post-processing (merge fragments) ----------
    cleaned = []
    for i, s in enumerate(final_sentences):
        # Remove "،۔"
        s = s.replace("،۔", "۔")

        # If starts with weak connectors, merge with previous
        if cleaned and (s.startswith(("اور", "تو", "اسی", "بلکہ")) or len(s.split()) <= 3):
            cleaned[-1] = cleaned[-1].rstrip("۔") + " " + s
        else:
            cleaned.append(s)

    return cleaned

# ---------- Step 5: Save Segmented Output ----------
if __name__ == "__main__":
    with open("urdu-corpus.txt", "r", encoding="utf-8") as f:
        text = f.read()

    segmented_sentences = urdu_sentence_segmenter(text)

    with open("segmented_output.txt", "w", encoding="utf-8") as f:
        for s in segmented_sentences:
            f.write(s + "\n")

    print("✅ Improved segmentation completed! Check segmented_output.txt")
