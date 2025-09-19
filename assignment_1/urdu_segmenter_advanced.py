import re

# ---------- Step 1: Normalize Urdu text ----------
def normalize_text(text):
    text = re.sub(r'\s+', ' ', text)  # remove multiple spaces
    text = text.replace(",", "،")     # replace English comma with Urdu comma
    text = text.replace("''", "’’").replace("``", "‘‘")  # fix quotes

    # Remove spaces before Urdu punctuation
    text = re.sub(r'\s+،', '،', text)
    text = re.sub(r'\s+۔', '۔', text)
    return text.strip()


# ---------- Step 2: Insert full stops before discourse markers ----------
def insert_fullstop_before_markers(text):
    markers = [
        "لیکن", "مگر", "اب", "آج", "ساتھ ہی", "دوسری جانب",
        "چنانچہ", "آخرکار", "اس موقعے پر", "لہٰذا"
    ]
    for m in markers:
        text = re.sub(
            rf'(?<![۔؟!])\s+({m})',
            r'۔ \1',
            text
        )
    return text


# ---------- Step 3: Urdu Sentence Segmentation ----------
def urdu_sentence_segmenter(text):
    text = normalize_text(text)
    text = insert_fullstop_before_markers(text)

    # Protect quotes (‘‘ … ’’ or " … ")
    protected_quotes = re.findall(r'(‘‘.*?’’|".*?")', text)
    replacements = {}
    for i, q in enumerate(protected_quotes):
        key = f"__QUOTE_{i}__"
        replacements[key] = q
        text = text.replace(q, key)

    # Split sentences at ۔ ? !
    sentences = re.split(r'([۔?!])', text)

    # Recombine tokens into full sentences
    final_sentences = []
    buffer = ""
    for token in sentences:
        if not token.strip():
            continue
        buffer += token.strip()
        if token in ["۔", "?", "!"]:
            if buffer.strip():
                final_sentences.append(buffer.strip())
            buffer = ""
    if buffer.strip():
        final_sentences.append(buffer.strip())

    # Restore protected quotes
    restored = []
    for s in final_sentences:
        for key, q in replacements.items():
            s = s.replace(key, q)
        restored.append(s)

    # ---------- Step 4: Post-processing ----------
    cleaned = []
    for s in restored:
        s = s.replace("،۔", "۔")  # remove duplicate punctuation

        # Weak connectors: merge with previous sentence if too short
        if cleaned and (s.startswith(("اور", "تو", "اسی", "بلکہ")) or len(s.split()) <= 3):
            cleaned[-1] = cleaned[-1].rstrip("۔") + " " + s
        else:
            cleaned.append(s)

    # Step 5: Handle run-ons (split at کہ, جسے, چونکہ, اگرچہ only after ہے)
    refined = []
    for s in cleaned:
        parts = re.split(r'(?<=ہے)\s+(?=(کہ|جسے|چونکہ|اگرچہ))', s)
        if len(parts) > 1:
            chunk = []
            for p in parts:
                if not p.strip():
                    continue
                if re.match(r'^(کہ|جسے|چونکہ|اگرچہ)', p) and chunk:
                    chunk[-1] = chunk[-1].rstrip("۔") + "۔"
                chunk.append(p.strip())
            refined.extend(chunk)
        else:
            refined.append(s)

    # Step 6: Numbers/Dates → split only if followed by ۔?! or discourse marker
    strict_split = []
    for s in refined:
        parts = re.split(r'(?<=\d)(?=\s*(۔|؟|!| لیکن| مگر| اب| آج))', s)
        if len(parts) > 1:
            strict_split.extend([p.strip() for p in parts if p.strip()])
        else:
            strict_split.append(s)
    refined = strict_split

    # Step 7: Drop meaningless fragments (< 3 words)
    final_output = [s for s in refined if len(s.split()) > 2]

    return final_output


# ---------- Step 8: Save + Print Segmented Output ----------
if __name__ == "__main__":
    with open("urdu-corpus.txt", "r", encoding="utf-8") as f:
        text = f.read()

    segmented_sentences = urdu_sentence_segmenter(text)

    # Save to file
    with open("segmented_output.txt", "w", encoding="utf-8") as f:
        for s in segmented_sentences:
            f.write(s + "\n")

    print("\n👉 Full result saved in segmented_output.txt")
