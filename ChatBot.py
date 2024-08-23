from difflib import get_close_matches
from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import nltk
nltk.download('punkt')
nltk.download('stopwords')
from nltk.stem import PorterStemmer
from spellchecker import SpellChecker
from typing import List ,Optional





app = Flask(__name__)
CORS(app)

def load_data(path: str) -> dict:
    with open(path, 'r') as file:
        return json.load(file)


stemmer = PorterStemmer()
spell = SpellChecker()


# Save data on the json file
def save_data(file_path:str,data:dict):
    with open(file_path,'w') as file:
        json.dump(data,file,indent=2)
        

# Find best matches
#def find_best_matches(question: str, questions: list[str]) -> str | None:
    #best_match = None
    #max_ratio = 0
    #for q in questions:
        # Calculate fuzzy match ratio
        #ratio = fuzz.partial_ratio(question, q)
        # Check if the ratio is higher than a threshold and if the question is a valid English word
        #if ratio > max_ratio and q.lower() in spell:
            #max_ratio = ratio
            #best_match = q
    #return best_match

def find_best_matches(question: str, questions: List[str]) -> Optional[str]:
    matches = get_close_matches(question, questions, n=1, cutoff=0.6)
    return matches[0] if matches else None

# Correct spell checker
def correct_spelling_in_string(input_string):
   
    words = input_string.split()
    corrected_words = []
    
    
    for word in words:
        
        if word.lower() not in spell:
            
            corrected_word = spell.correction(word)
            corrected_words.append(corrected_word)
        else:
            corrected_words.append(word)  
    
    
    corrected_string = ' '.join(corrected_words)
    return corrected_string



# Get answer for question
def get_answer_for_question(question: str, data: dict) -> Optional[str]:
    for q in data['questions']:
        if q["question"] == question:
            return q["answer"]

def delete_question(file_path: str, question: str):
    with open(file_path, 'r') as file:
        data = json.load(file)
    index_to_delete = None
    for i, entry in enumerate(data['questions']):
        if entry['question'] == question:
            index_to_delete = i
            break
    
    if index_to_delete is not None:
        del data['questions'][index_to_delete]
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=2)
        
        print(f"Successfully deleted question '{question}' from the JSON file.")
    else:
        print(f"Question '{question}' not found in the JSON data.")

# delete all questions
def delete_All(file_path: str):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        return {'error': 'File not found'}
    except json.JSONDecodeError:
        return {'error': 'Invalid JSON format'}
    data['questions'] = []
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=2)

    return {'message': 'All questions deleted successfully'}

# Define a route to handle incoming requests
@app.route('/chatbot', methods=['POST'])
def chatbot():
    try:
        data = request.json
        user_question = data['question'].lower()
        user_question_corrected = correct_spelling_in_string(user_question)
        qa_data = load_data(r'qa_data.json')
        unmatched_questions = load_data(r'unmatched_questions.json')
        best_match = find_best_matches(user_question_corrected, [q["question"] for q in qa_data["questions"]])
        if best_match:
            answer = get_answer_for_question(best_match, qa_data)
        else:
            unmatched_questions['questions'].append({'question': user_question_corrected})
            save_data(r'unmatched_questions.json', unmatched_questions)
            answer = "Sorry, I don't understand that question."
    except Exception as e:
        print("An error occurred:", e)
        answer = "An error occurred while processing the request.Please ty again"
    
    return jsonify({'response': answer})



@app.route('/unmatched', methods=['GET'])
def getUnmatchedquestions():
    data = load_data(r'unmatched_questions.json')
    return jsonify(data['questions'])


# Teach chatBot
@app.route('/teach', methods=['POST'])
def TeachChatbot():
    data = request.json
    qa_data = load_data(r'qa_data.json')
    qa_data['questions'].append({'question':data['question'].lower(),'answer':data['answer'].lower()})
    save_data(r'qa_data.json',qa_data )
    delete_question(r'unmatched_questions.json', data['question'])
    return jsonify("Question added successfully")

# Add question & answer
@app.route('/add', methods=['POST'])
def add():
    data = request.json
    qa_data = load_data(r'qa_data.json')
    qa_data['questions'].append({'question':data['question'].lower(),'answer':data['answer'].lower()})
    save_data(r'qa_data.json',qa_data )
    return jsonify("Question & Answer added successfully")

@app.route('/deletebyKey', methods=['POST'])
def deleteByKey():
    try:
        data = request.json
        delete_question(r'unmatched_questions.json',data['question'])
        if data['question'] not in data:
           return {'error': f'Key "{data["question"]}" not found in JSON'}
        return jsonify("Question deleted successfully")
    except Exception as e:
        return jsonify({'error': str(e)})
    
@app.route('/deleteAll', methods=['POST'])
def deleteAll():
    try:
        data = request.json
        delete_All(r'unmatched_questions.json')
        return jsonify("All unmatched questions are deleted successfully")
    except Exception as e:
        return jsonify({'error': str(e)})
    

app.run(host='0.0.0.0', port=5000)

