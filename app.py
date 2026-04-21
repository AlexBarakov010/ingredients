import streamlit as st
import easyocr
import numpy as np
from PIL import Image
import re

# Initialize OCR reader
@st.cache_resource
def load_reader():
    return easyocr.Reader(['en'])

reader = load_reader()

st.title("🧪 Ingredient Scanner (E-number Detector)")
st.write("Upload an image of ingredients. The app will detect harmful additives.")

uploaded_file = st.file_uploader("Upload an image", type=["jpg", "png", "jpeg"])

# Unhealthy E-numbers
UNHEALTHY_E_NUMBERS = {
    "E620": "Monosodium glutamate (MSG)",
    "E621": "MSG variant",
    "E627": "Disodium guanylate",
    "E631": "Disodium inosinate",
    "E950": "Acesulfame K",
    "E951": "Aspartame",
    "E952": "Cyclamate",
    "E954": "Saccharin",
    "E210": "Benzoic Acid"
}

# Keyword-based unhealthy ingredients
UNHEALTHY_KEYWORDS = [
    "sucralose",
    "acesulfame potassium",
    "benzoic acid",
    "caffeine",
    "guarana"
]

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_container_width=True)

    # Convert to numpy array
    img_array = np.array(image)

    st.write("🔍 Extracting text...")

    results = reader.readtext(img_array, detail=0)
    extracted_text = " ".join(results)

    st.subheader("📄 Extracted Text")
    st.write(extracted_text)

    # Find E-numbers using regex
    found_e_numbers = re.findall(r'\b[Ee]\s?\d{3}\b', extracted_text)
    found_e_numbers = [e.replace(" ", "").upper() for e in found_e_numbers]

    # Detect keywords
    found_keywords = []
    lower_text = extracted_text.lower()

    for word in UNHEALTHY_KEYWORDS:
        if word in lower_text:
            found_keywords.append(word)

    st.subheader("⚠️ Detected Additives")

    found_unhealthy = []

    # Check E-numbers
    for e in set(found_e_numbers):
        if e in UNHEALTHY_E_NUMBERS:
            found_unhealthy.append((e, UNHEALTHY_E_NUMBERS[e]))

    if found_unhealthy or found_keywords:
        st.error("🚨 Unhealthy ingredients found!")

        # Show E-numbers
        for e, desc in found_unhealthy:
            st.write(f"{e} → {desc}")

        # Show keywords
        for word in set(found_keywords):
            st.write(f"{word} → flagged ingredient")

    elif found_e_numbers:
        st.success("✅ No harmful E-numbers detected.")
        st.write("Detected E-numbers:", ", ".join(set(found_e_numbers)))

    else:
        st.info("No concerning ingredients detected.")
