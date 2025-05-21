import streamlit as st
import time
import numpy as np
import pandas as pd

@st.cache_data
def load_data(nrows):
    ''' Load Data once when the App is loaded '''
    time.sleep(2)
    print(f"Loading {nrows} rows")

# ''' Load Data Text with an animation change '''
data = load_data(1000)


_LOREM_IPSUM = """
Lorem ipsum dolor sit amet, **consectetur adipiscing** elit, sed do eiusmod tempor
incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis
nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
"""


def stream_data():
    for word in _LOREM_IPSUM.split(" "):
        yield word + " "
        time.sleep(0.02)

    yield pd.DataFrame(
        np.random.randn(5, 10),
        columns=["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"],
    )

    for word in _LOREM_IPSUM.split(" "):
        yield word + " "
        time.sleep(0.02)


# ''' Display Data '''
st.title("Hello Streamlit!")
# st.write("My first Streamlit app")

prompt = st.chat_input("Say something")
if prompt:
    st.write(f"User: {prompt}")
    st.write_stream(stream_data)