import re

import openai
import streamlit as st

from phoebe_prompts import get_system_prompt
from plots import plot, NO_PLOT, BAR_TYPE, SCATTER_TYPE, LINE_TYPE, PIE_TYPE


st.title("Phoebe")

# Initialize the chat messages history
openai.api_key = st.secrets.OPENAI_API_KEY
if "messages" not in st.session_state:
    # system prompt includes table information, rules, and prompts the LLM to produce
    # a welcome message to the user.
    st.session_state.messages = [{"role": "system", "content": get_system_prompt()}]

# Prompt for user input and save
if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})

# display the existing chat messages
for message in st.session_state.messages:
    if message["role"] == "system":
        continue
    with st.chat_message(message["role"]):
        st.write(message["content"])
        if "results" in message:
            st.dataframe(message["results"])
        # if "plots" in message:
        #     for plot in message["plots"]:
        #         plot_type = plot["type"]
        #         plot(message["results"], plot_type)

# Sidebar for plot type selection
st.sidebar.image("./assets/Sift_Logo_Color_RGB.jpg", use_column_width=True)
plot_options = [NO_PLOT, BAR_TYPE, SCATTER_TYPE, LINE_TYPE, PIE_TYPE]
selected_plot = st.sidebar.selectbox("Choose a plot type", plot_options)
st.sidebar.text_input('Plot type:', selected_plot)

# If last message is not from assistant, we need to generate a new response
if st.session_state.messages[-1]["role"] != "assistant":
    # plot_options = ["Bar plot", "Scatter plot", "Histogram", "Box plot", "No plot"]
    # selected_plot = st.sidebar.selectbox("Choose a plot type", plot_options)
    # st.sidebar.text_input('Choose plot', selected_plot)
    with st.chat_message("assistant"):
        response = ""
        resp_container = st.empty()
        for delta in openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
            stream=True,
        ):
            response += delta.choices[0].delta.get("content", "")
            resp_container.markdown(response)

        message = {"role": "assistant", "content": response}
        # Parse the response for a SQL query and execute if available
        sql_match = re.search(r"```sql\n(.*)\n```", response, re.DOTALL)
        data = None
        if sql_match:
            sql = sql_match.group(1)
            conn = st.experimental_connection("snowpark")
            data = conn.query(sql)
            message["results"] = data
            st.dataframe(message["results"])

            # try plotting
            if selected_plot != NO_PLOT:
                plot_obj = plot(data, selected_plot)
                if "plots" not in message:
                    message["plots"] = [plot_obj]
                else:
                    message["plots"].append(plot_obj)

        st.session_state.messages.append(message)
