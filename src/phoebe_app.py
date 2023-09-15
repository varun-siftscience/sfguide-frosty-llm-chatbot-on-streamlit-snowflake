import re
import matplotlib.pyplot as plt
import openai
import seaborn as sns
import streamlit as st
from phoebe_prompts import get_system_prompt

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

# Sidebar for plot type selection
plot_options = ["Bar plot", "Scatter plot", "Line plot", "No plot"]
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
            if selected_plot == "Bar plot":
                # x_axis = st.sidebar.selectbox("Select x-axis", data.columns)
                # st.sidebar.text_input('X axis:', x_axis)
                # y_axis = st.sidebar.selectbox("Select y-axis", data.columns)
                # st.sidebar.text_input('Y axis:', y_axis)

                x_axis, y_axis = data.columns[0], data.columns[1]
                st.write("Bar plot:")
                fig, ax = plt.subplots()
                sns.barplot(x=data[x_axis], y=data[y_axis], ax=ax)
                st.pyplot(fig)

            elif selected_plot == "Scatter plot":
                # x_axis = st.sidebar.selectbox("Select x-axis", data.columns)
                # st.sidebar.text_input('X axis:', x_axis)
                # y_axis = st.sidebar.selectbox("Select y-axis", data.columns)
                # st.sidebar.text_input('Y axis:', y_axis)

                x_axis, y_axis = data.columns[0], data.columns[1]
                st.write("Scatter plot:")
                fig, ax = plt.subplots()
                sns.scatterplot(x=data[x_axis], y=data[y_axis], ax=ax)
                st.pyplot(fig)

            elif selected_plot == "Line plot":
                # x_axis = st.sidebar.selectbox("Select x-axis", data.columns)
                # st.sidebar.text_input('X axis:', x_axis)
                # y_axis = st.sidebar.selectbox("Select y-axis", data.columns)
                # st.sidebar.text_input('Y axis:', y_axis)

                x_axis, y_axis = data.columns[0], data.columns[1]
                st.write("Line plot:")
                st.line_chart(data, x=x_axis, y=y_axis)

            elif selected_plot == "No plot":
                pass

        st.session_state.messages.append(message)
