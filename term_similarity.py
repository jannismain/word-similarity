import itertools

import Levenshtein
import streamlit as st

from psql import similarity

st.set_page_config("Term Similarity", layout="wide")
initial_value = """
Microsoft Azure Developer Associate,
Azure Developer Associate (AZ-204),
Azure Developer Associate
""".strip().replace("\n", " ")

initial_synonyms = """
Azure,Microsoft Azure
""".strip()

st.title("Term Similarity")
terms = st.text_area(
    "Terms",
    help="comma-separated list of terms",
    value=initial_value,
)
terms = [w.strip() for w in terms.split(",")]
cols = st.columns(3)
with st.sidebar:
    metrics = (
        "levenshtein hamming jaro jaro_winkler ratio seqratio psql_similarity".split()
    )
    criteria = st.radio("Criteria", metrics, index=6)
    threshold = st.slider("Threshold", 0.0, 1.0, 0.8, 0.05)
    replace_synonyms = st.checkbox("Replace Synonyms")
    synonyms = [
        x.split(",")
        for x in st.text_area(
            "Synonyms", value=initial_synonyms, disabled=not replace_synonyms
        ).splitlines()
    ]

if criteria == "levenshtein":
    measure = Levenshtein.distance
elif criteria in {"psql_similarity"}:
    measure = similarity
else:
    measure = getattr(Levenshtein, criteria)

results = []
for w, w2 in itertools.combinations(terms, 2):
    w_orig, w2_orig = w, w2
    if replace_synonyms:
        for s in synonyms:
            w = w.replace(s[0], s[1])
            w2 = w2.replace(s[0], s[1])
    same = measure(w, w2) > threshold
    results += [
        dict(
            first=w_orig,
            second=w2_orig,
            levenshtein=Levenshtein.distance(w, w2),
            hamming=Levenshtein.hamming(w, w2),
            jaro=Levenshtein.jaro(w, w2),
            jaro_winkler=Levenshtein.jaro_winkler(w, w2),
            ratio=Levenshtein.ratio(w, w2),
            seqratio=Levenshtein.seqratio(w, w2),
            psql_similarity=similarity(w, w2),
            same="✅" if same else "",
        )
    ]


st.dataframe(results)
