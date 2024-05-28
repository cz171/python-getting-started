import singlestoredb as s2
import json
from openai import OpenAI
import os
from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS
import logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
# CORS(app, resources={r"/*": {"origins": "*"}})  # This allows all domains for all routes


conn = s2.connect('admin:niCAWET9oSGrjZjJ2X8x345dQFeQhT1t@svc-d79973dc-78a0-42df-8a25-5ab0cd3c2bc9-dml.aws-virginia-6.svc.singlestore.com:3306/llm_dataset')
os.environ['OPENAI_API_KEY']= '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'

client = OpenAI()

def get_embedding(text, model="text-embedding-ada-002"):
   text = text.replace("\n", " ")
   return client.embeddings.create(input = [text], model=model).data[0].embedding

def get_answer(question: str):
    with conn.cursor() as cur:
        query_emb = get_embedding(question)
        query = "SELECT text, dot_product(vector, JSON_ARRAY_PACK(%s)) as score FROM section718 where score > 0.5 order by score desc limit 5"
        cur.execute(query, (json.dumps(query_emb)))
        results = cur.fetchall()
        # print(f"result: {results}")
        sorted(results, key=lambda x: x[1], reverse=True)
        texts = ['"""{}"""'.format(result[0]) for result in results]  # Extracting text and surrounding it with triple quotes
        # sort reference with score
        
        # reference = ['\n{}\n'.format(result[0]) for result in results]
        texts_joined = '\n'.join(texts)  # Joining all texts with a newline character for separation
        # print(f"texts_joined: {texts_joined}")
        completion = client.chat.completions.create(
            model="ft:gpt-3.5-turbo-1106:personal::8hAW249u",
            # model="gpt-3.5-turbo-1106",
            messages=[
                {"role": "system", "content": "Use the provided articles delimited by newline to answer questions. If the answer cannot be found in the articles, write I could not find an answer."},
                {"role": "user", "content": f"{texts_joined}\nQuestion:{question}"},
            ]
        )
        reference = "\n".join([ref[0] for ref in results[:3]])
        print(f"reference: {reference}")
        answer = f"{completion.choices[0].message.content}\nReference:\n{reference}" # Not yet completing reference part 
        return answer
        
# @app.route('/call-chatbot', methods=['POST'])
# def handle_request():
#     try: 
#         # Extract data from request
#         data = request.json
        
#         # Call your codelab code with the data
#         response_data = your_codelab_function(data)
        
#         # Return the response in JSON format
#         return jsonify(response_data)
#     except Exception as e:
#         logging.error(f"An error occurred: {e}")
#         return jsonify({"error": "An error occurred"}), 500 
@app.route('/', methods=['GET'])
def handle_request():
    try: 
        # Extract data from request
        data = request.json
        
        # Call your codelab code with the data
        response_data = "hello world 111"
        
        # Return the response in JSON format
        return jsonify(response_data)
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return jsonify({"error": "An error occurred"}), 500 

def your_codelab_function(data):
    # Here you will process the data
    # and return the response
    # For example:

    question = data["question"]
    answer = get_answer(question)

    # print("helloworld")
    return {"response": answer}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)