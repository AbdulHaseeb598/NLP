import re

# ---------- Step 1: Normalize Urdu text ----------
def normalize_text(text):
    # Remove multiple spaces
    text = re.sub(r'\s+', ' ', text)
    # Fix misplaced commas (English comma → Urdu comma)
    text = text.replace(",", "،")
    # Normalize Urdu quotes
    text = text.replace("''", "’’").replace("``", "‘‘")
    return text.strip()

# ---------- Step 2: Urdu Sentence Segmentation ----------
def urdu_sentence_segmenter(text):
    text = normalize_text(text)
    
    # Split sentences on Urdu punctuation: ۔ ? !
    sentences = re.split(r'([۔?!])', text)
    
    final_sentences = []
    for i in range(0, len(sentences)-1, 2):
        sentence = sentences[i].strip() + sentences[i+1]
        if sentence.strip():  
            final_sentences.append(sentence.strip())
    
    return final_sentences

# ---------- Step 3: Save Segmented Output ----------
if __name__ == "__main__":
    # Load Urdu corpus file
    with open("urdu-corpus.txt", "r", encoding="utf-8") as f:
        text = f.read()
    
    # Segment text
    segmented_sentences = urdu_sentence_segmenter(text)
    
    # Save results to new file
    with open("segmented_output.txt", "w", encoding="utf-8") as f:
        for s in segmented_sentences:
            f.write(s + "\n")
    
    print("✅ Segmentation completed! Check segmented_output.txt")
