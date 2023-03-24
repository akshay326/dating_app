import os
import openai
from typing import *
import logging
import random
import streamlit as st
from streamlit_chat import message as ChatMessage

from langchain.chat_models import ChatOpenAI
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)

# define logger
logger = logging.getLogger(__name__)

openai.api_key = os.getenv("OPENAIIKEY")
ChatGPTAgent = ChatOpenAI(
    model_name='gpt-3.5-turbo',
    openai_api_key=os.getenv("OPENAIIKEY"),
    temperature=0, 
    max_tokens=100
)

DATING_PARTNER_PROMPT = open("prompts/dating_scenario_1.txt").read()

# set page config
st.set_page_config(
    page_title="Dating Coach",
    page_icon=":heart:",
)


def construct_chatgpt_input(messages: List[Dict[str, str]]):
    result = []

    for message in messages:
        if message['type'] == 'system':
            result.append(SystemMessage(content=message['text']))
        elif message['type'] == 'user':
            result.append(HumanMessage(content=message['text']))
        elif message['type'] == 'bot':
            result.append(AIMessage(content=message['text']))

    return result
    

def init():
    logger.info('USERNAME: ' + st.session_state.username)
    st.session_state.messages = [
        {
            'text': DATING_PARTNER_PROMPT,
            'type': 'system'
        }
    ]

    # generate the 1st message
    messages = st.session_state.messages
    response = ChatGPTAgent(construct_chatgpt_input(messages))
    logger.info('FIRST CHATGPT RESPONSE: ' + response.content)

    # add to messages in session
    messages.append({
        'text': response.content,
        'type': 'bot'
    })
    st.session_state.messages = messages


def submit():
    # get user input 
    st.session_state.user_input = user_input = st.session_state.widget

    # clear widget input
    st.session_state.widget = ''

    # check for moderation
    response = openai.Moderation.create(user_input)
    logger.info(response)
    output = response["results"][0]

    # open modal if flagged
    if output['flagged']:
        st.warning('You have violated the terms of service. Please avoid using profanity or other offensive language.', icon="⚠️")
        return 

    # add user_input to messages
    messages = st.session_state.messages
    messages.append({
        'text': user_input,
        'type': 'user'
    })

    response = ChatGPTAgent(construct_chatgpt_input(messages))
    logger.info('CHATGPT RESPONSE: ' + response.content)
    
    # add to messages in session
    messages.append({
        'text': response.content,
        'type': 'bot'
    })
    st.session_state.messages = messages
    # logger.info(messages)


def display_messages(messages: List[Dict[str, str]]):
    for message in messages:
        if message['type'] == 'user':
            ChatMessage(message['text'], is_user=True, key=random.randint(0, 10**9)) 
        elif message['type'] == 'bot':
            ChatMessage(message['text'], avatar_style='adventurer', key=random.randint(0, 10**9)) 


def main():
    st.markdown("# Date Game")
    st.markdown("You are at an italian diner sipping some red wine.")
    st.markdown("**Anna**, your date, is sitting across from you.")
    st.markdown("Can you make her laugh?")

    st.sidebar.button('Reset Game', on_click=init)

    display_messages(st.session_state.messages)

    st.text_input("Talk to Anna:", key='widget', on_change=submit)


if __name__ == "__main__":
    if 'username' not in st.session_state:
        st.markdown("""# Date Game""")
        username = st.text_input('Whats your name')
        st.session_state.username = username
    else:
        if 'messages' not in st.session_state:
            init()
        main()
