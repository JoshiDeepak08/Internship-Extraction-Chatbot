from flask import Flask, render_template, request
import sqlite3
import os
import pandas as pd
from langchain_community.utilities import SQLDatabase
from langchain_groq import ChatGroq
from langchain.chains import create_sql_query_chain
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from deep_translator import GoogleTranslator

app = Flask(__name__)

# Set API Keys
os.environ["OPENAI_API_KEY"] = ""
os.environ["GROQ_API_KEY"] = ""

# LangChain setup
db = SQLDatabase.from_uri("sqlite:///internship.db")
llm = ChatGroq(model="llama3-8b-8192")
write_query = create_sql_query_chain(llm, db)
execute_query = QuerySQLDataBaseTool(db=db)

# Prompt template
answer_prompt = PromptTemplate.from_template(
    """You are given a SQL query and the result from the database.
Convert the result into a short and natural-sounding list format that answers the original question.
For each internship, include its name and clickable link (in Markdown style: [name](url)).

Question: {question}
SQL Result: {result}
Answer:"""
)

# To store conversations
previous_conversations = []

@app.route('/', methods=['GET', 'POST'])
def index():
    global previous_conversations
    response = ""
    table_html = ""

    if request.method == 'POST':
        user_question = request.form['question']
        user_message = {"type": "user", "text": user_question}
        previous_conversations.append(user_message)

        try:
            # Translate to English
            translated_question = GoogleTranslator(source='auto', target='en').translate(user_question)

            # Generate SQL query
            generated_query = write_query.invoke({"question": translated_question})

            # Extract SQL part
            sql_query = generated_query.split("SQLQuery: ")[-1].strip()

            # Execute query
            query_result = execute_query.invoke({"query": sql_query})

            # Table formatting for internships with stipend less than ₹1000
            if isinstance(query_result, list) and query_result:
                # Prepare the data for the table
                internships_data = [
                    {
                        "title": internship[0],
                        "link": internship[1],
                        "stipend": internship[2]
                    }
                    for internship in query_result
                ]

                # Create the table in HTML format
                table_html = '''
                <table class="table table-striped table-bordered">
                    <thead>
                        <tr>
                            <th>Internship Title</th>
                            <th>Link</th>
                            <th>Stipend</th>
                        </tr>
                    </thead>
                    <tbody>
                '''

                for internship in internships_data:
                    table_html += f'''
                    <tr>
                        <td><a href="{internship['link']}" target="_blank">{internship['title']}</a></td>
                        <td>{internship['stipend']}</td>
                    </tr>
                    '''

                table_html += '</tbody></table>'

            # Format and send to LLM
            formatted_prompt = answer_prompt.format(
                question=translated_question,
                result=query_result
            )
            llm_response = llm.invoke(formatted_prompt)
            english_response = StrOutputParser().invoke(llm_response.content)

            # Translate back to original language
            translated_response = GoogleTranslator(source='en', target='auto').translate(english_response)

            response = translated_response
            bot_message = {"type": "bot", "text": response}
            previous_conversations.append(bot_message)

        except Exception as e:
            response = f"Error occurred: {e}"
            bot_message = {"type": "bot", "text": response}
            previous_conversations.append(bot_message)

    return render_template('index.html', previous_conversations=previous_conversations, table=table_html)

if __name__ == '__main__':
    app.run(debug=True)






