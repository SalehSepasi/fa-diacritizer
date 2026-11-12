
import torch
from transformers import CanineTokenizer, CanineForTokenClassification

# Model ID on Hugging Face
MODEL_ID = "PedramR/canine-fa-diacritizer"

#Loading the Tokenizer from downloaded files
tokenizer = CanineTokenizer.from_pretrained(
    MODEL_ID,
    local_files_only=True
)

# Loading the model from downloaded files
model = CanineForTokenClassification.from_pretrained(
    MODEL_ID,
    local_files_only=True
).eval()

MARKS = {
    "FATHA": "َ",
    "DAMMA": "ُ",
    "KASRA": "ِ",
    "SOKUN": "ْ",
    "SHADDA": "ّ",
    "FATHATAN": "ً",
}


def label_to_marks(label):
    if label == "NONE":
        return ""

    return "".join(MARKS[part] for part in label.split("_"))

@torch.no_grad()
def diacritize(text: str) -> str:
    enc = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=2048
    )

    logits = model(**enc).logits

    preds = logits.argmax(-1)[0].tolist()

    char_preds = preds[1:1 + len(text)]

    id2label = model.config.id2label

    out = []

    for ch, pid in zip(text, char_preds):
        out.append(ch)
        out.append(label_to_marks(id2label[pid]))

    return "".join(out)
