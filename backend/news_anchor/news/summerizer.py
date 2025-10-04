# api/summarizer.py
from transformers import TFAutoModelForSeq2SeqLM, AutoTokenizer

MODEL_NAME = "t5-small"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = TFAutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)

def generate_summary(text, max_len=80, min_len=20):
    if not text:
        return ""

    input_text = "summarize: " + text
    inputs = tokenizer.encode(input_text, return_tensors="tf", max_length=512, truncation=True)

    outputs = model.generate(
        inputs,
        max_length=max_len,
        min_length=min_len,
        length_penalty=2.0,
        num_beams=4,
        early_stopping=True
    )

    return tokenizer.decode(outputs[0], skip_special_tokens=True)
