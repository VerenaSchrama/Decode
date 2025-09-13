# python rag_pipeline.py
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.schema.messages import HumanMessage, AIMessage
import os
from dotenv import load_dotenv
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

load_dotenv()

# Define paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VECTORSTORE_PATH = os.path.join(BASE_DIR, "data", "vectorstore")
STRATEGY_VECTORSTORE_PATH = os.path.join(VECTORSTORE_PATH, "strategies_chroma")
MAIN_VECTORSTORE_PATH = os.path.join(VECTORSTORE_PATH, "chroma")

# Initialize LLM and Embeddings
llm = ChatOpenAI(model="gpt-4", temperature=0, api_key=os.getenv("OPENAI_API_KEY"))
embeddings = OpenAIEmbeddings(api_key=os.getenv("OPENAI_API_KEY"))

# Load vector stores
strategy_vectorstore = None
strategy_retriever = None
main_vectorstore = None
main_retriever = None

try:
    strategy_vectorstore = Chroma(
        persist_directory=STRATEGY_VECTORSTORE_PATH,
        embedding_function=embeddings,
        collection_name="strategies"
    )
    strategy_retriever = strategy_vectorstore.as_retriever(search_kwargs={"k": 3})

    main_vectorstore = Chroma(
        persist_directory=MAIN_VECTORSTORE_PATH,
        embedding_function=embeddings
    )
    main_retriever = main_vectorstore.as_retriever()

except Exception as e:
    # Don't exit, let the app continue with None retrievers
    pass


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def ensure_list(val):
    if isinstance(val, list):
        return val
    if val is None:
        return []
    return [val]


def build_user_context(user_input: dict) -> str:
    """Build context string from user intake data for RAG queries."""
    symptoms = ensure_list(user_input.get('symptoms'))
    symptoms_note = user_input.get('symptoms_note', '')
    goals = ensure_list(user_input.get('goals'))
    goals_note = user_input.get('goals_note', '')
    preferences = ensure_list(user_input.get('dietaryRestrictions')) or ensure_list(user_input.get('preferences'))
    dietary_note = user_input.get('dietaryRestrictions_note', '')
    cycle = user_input.get('cycle', '')
    reason = user_input.get('reason', '')
    whatWorks = user_input.get('whatWorks', '')
    extraThoughts = user_input.get('extraThoughts', '')

    context = (
        f"User Profile:\n"
        f"- Symptoms: {', '.join(symptoms)}\n"
        + (f"- Symptom notes: {symptoms_note}\n" if symptoms_note else "")
        + f"- Goals: {', '.join(goals)}\n"
        + (f"- Goals notes: {goals_note}\n" if goals_note else "")
        + f"- Dietary restrictions: {', '.join(preferences)}\n"
        + (f"- Dietary notes: {dietary_note}\n" if dietary_note else "")
        + f"- Cycle phase: {cycle}\n"
        + (f"- Reason for using app: {reason}\n" if reason else "")
        + (f"- What already works: {whatWorks}\n" if whatWorks else "")
        + (f"- Additional thoughts: {extraThoughts}\n" if extraThoughts else "")
    )
    
    return context

def build_question(user_input: dict) -> str:
    """Build a question from user input for the chatbot, using all intakeData fields and optional notes.
    DEPRECATED: Use build_user_context() + user's actual question instead."""
    symptoms = ensure_list(user_input.get('symptoms'))
    symptoms_note = user_input.get('symptoms_note', '')
    goals = ensure_list(user_input.get('goals'))
    goals_note = user_input.get('goals_note', '')
    preferences = ensure_list(user_input.get('dietaryRestrictions')) or ensure_list(user_input.get('preferences'))
    dietary_note = user_input.get('dietaryRestrictions_note', '')
    cycle = user_input.get('cycle', '')
    reason = user_input.get('reason', '')
    whatWorks = user_input.get('whatWorks', '')
    extraThoughts = user_input.get('extraThoughts', '')

    question = (
        f"My symptoms are: {', '.join(symptoms)}. "
        + (f"Symptom notes: {symptoms_note}. " if symptoms_note else "")
        + f"My goals are: {', '.join(goals)}. "
        + (f"Goals notes: {goals_note}. " if goals_note else "")
        + f"My dietary restrictions are: {', '.join(preferences)}. "
        + (f"Dietary notes: {dietary_note}. " if dietary_note else "")
        + f"I'm currently in the {cycle} phase of my cycle. "
        + (f"My reason for using this app: {reason}. " if reason else "")
        + (f"What already works for me: {whatWorks}. " if whatWorks else "")
        + (f"Extra thoughts: {extraThoughts}. " if extraThoughts else "")
        + "What should I eat?"
    )

    return question


def generate_advice(user_question: str, user_context: str = None) -> dict:
    """Generate advice using the chatbot approach with user's actual question and context."""
    print(f"RAG Debug: strategy_retriever is {strategy_retriever}")
    print(f"RAG Debug: user_question: {user_question}")
    print(f"RAG Debug: user_context: {user_context}")
    
    if not strategy_retriever:
        print("RAG Error: strategy_retriever is None - vector store not loaded")
        return {"answer": "I'm sorry, but I'm having trouble accessing my knowledge base right now. Please try again later."}
    
    if not os.getenv("OPENAI_API_KEY"):
        print("RAG Error: OPENAI_API_KEY not set")
        return {"answer": "I'm sorry, but I'm having trouble accessing my knowledge base right now. Please try again later."}
    
    # Combine user's actual question with their context
    if user_context:
        full_question = f"{user_context}\n\nUser Question: {user_question}"
    else:
        full_question = user_question
    
    # Create a conversational chain with memory
    from langchain.chains import ConversationalRetrievalChain
    from langchain.memory import ConversationBufferMemory
    
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )
    
    # Create the chain
    qa_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=strategy_retriever,
        memory=memory,
        return_source_documents=True,
        output_key="answer",
        verbose=False
    )
    
    try:
        # Invoke the chain with the user's actual question
        result = qa_chain.invoke({"question": full_question})
        return {"answer": result["answer"]}
    except Exception as e:
        print(f"RAG Error: {str(e)}")
        # Provide a fallback response based on common questions
        if "eat" in user_question.lower() or "food" in user_question.lower():
            return {"answer": "For PCOS management, focus on anti-inflammatory foods like leafy greens, berries, fatty fish, and whole grains. Avoid processed foods and refined sugars. Consider working with a nutritionist for personalized meal planning."}
        elif "exercise" in user_question.lower() or "workout" in user_question.lower():
            return {"answer": "Regular exercise is crucial for PCOS management. Aim for 150 minutes of moderate activity per week, including both cardio and strength training. Start slowly and gradually increase intensity."}
        elif "stress" in user_question.lower() or "cortisol" in user_question.lower():
            return {"answer": "Stress management is important for PCOS. Try meditation, deep breathing, yoga, or other relaxation techniques. Consider speaking with a healthcare provider about stress management strategies."}
        else:
            return {"answer": "I'm sorry, but I encountered an error while processing your request. Please try again later or contact support if the issue persists."}

def generate_advice_legacy(user_input: dict) -> dict:
    """Legacy function for backward compatibility. DEPRECATED: Use generate_advice() with actual user questions."""
    if not strategy_retriever:
        return {"answer": "I'm sorry, but I'm having trouble accessing my knowledge base right now. Please try again later."}
    
    # Build the question from user input (legacy method)
    question = build_question(user_input)
    
    # Create a conversational chain with memory
    from langchain.chains import ConversationalRetrievalChain
    from langchain.memory import ConversationBufferMemory
    
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )
    
    # Create the chain
    qa_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=strategy_retriever,
        memory=memory,
        return_source_documents=True,
        output_key="answer",
        verbose=False
    )
    
    try:
        # Invoke the chain with the question
        result = qa_chain.invoke({"question": question})
        return {"answer": result["answer"]}
    except Exception as e:
        return {"answer": "I'm sorry, but I encountered an error while processing your request. Please try again."}


# RAG Chain for Simple Advice (no conversation memory)
RAG_PROMPT_TEMPLATE = """
### CONTEXT
{context}

### QUESTION
{question}
"""
rag_prompt = ChatPromptTemplate.from_template(RAG_PROMPT_TEMPLATE)

# Initialize rag_chain only if main_retriever exists
rag_chain = None
if main_retriever is not None:
    rag_chain = (
        {"context": main_retriever | format_docs, "question": RunnablePassthrough()}
        | rag_prompt
        | llm
        | StrOutputParser()
    )

def get_advice(question: str) -> str:
    """Get simple advice for a question."""
    if not strategy_retriever:
        return "I'm sorry, but I'm having trouble accessing my knowledge base right now. Please try again later."
    
    try:
        docs = strategy_retriever.invoke(question)
        if not docs:
            return "I don't have specific information about that. Please try asking about symptoms, cycle phases, or dietary strategies."
        
        # Use the first document for a simple response
        doc = docs[0]
        return doc.page_content
    except Exception as e:
        return "I'm sorry, but I encountered an error while processing your request. Please try again."

def get_strategies(user_input: dict) -> list:
    """Get strategy recommendations based on user input."""
    if not strategy_retriever:
        return []
    
    # Build query from user input
    symptoms = ensure_list(user_input.get('symptoms'))
    symptoms_note = user_input.get('symptoms_note', '')
    goals = ensure_list(user_input.get('goals'))
    goals_note = user_input.get('goals_note', '')
    preferences = ensure_list(user_input.get('dietaryRestrictions')) or ensure_list(user_input.get('preferences'))
    dietary_note = user_input.get('dietaryRestrictions_note', '')
    cycle = user_input.get('cycle', '')
    reason = user_input.get('reason', '')
    whatWorks = user_input.get('whatWorks', '')
    extraThoughts = user_input.get('extraThoughts', '')

    query = (
        f"Symptoms: {', '.join(symptoms)}. "
        + (f"Symptom notes: {symptoms_note}. " if symptoms_note else "")
        + f"Goals: {', '.join(goals)}. "
        + (f"Goals notes: {goals_note}. " if goals_note else "")
        + f"Dietary restrictions: {', '.join(preferences)}. "
        + (f"Dietary notes: {dietary_note}. " if dietary_note else "")
        + f"Cycle phase: {cycle}. "
        + (f"Reason for using the app: {reason}. " if reason else "")
        + (f"What already works: {whatWorks}. " if whatWorks else "")
        + (f"Extra thoughts: {extraThoughts}. " if extraThoughts else "")
        + "Looking for strategies that match this profile."
    )

    try:
        docs = strategy_retriever.invoke(query)
        strategies = [doc.metadata for doc in docs]
        return strategies
    except Exception as e:
        return []


def get_recommendations(intake_data, df, top_k=3):
    # Build the query string from the intake data dictionary
    user_data_dict = intake_data.dict()
    symptoms = ", ".join(user_data_dict.get('symptoms', []))
    goals = ", ".join(user_data_dict.get('goals', []))
    query_text = f"User is experiencing {symptoms} and has goals to {goals}."

    # Use the global embeddings instance instead of creating a new one
    query_embedding = embeddings.embed_query(query_text)

    # Prepare the strategy embeddings from the DataFrame
    strategy_embeddings = np.array(df['embedding'].apply(eval).tolist())

    # Calculate cosine similarity
    similarities = cosine_similarity([query_embedding], strategy_embeddings)[0]

    # Get top_k recommendations
    top_indices = similarities.argsort()[-top_k:][::-1]
    recommendations = df.iloc[top_indices]

    return recommendations.to_dict(orient='records')


if __name__ == '__main__':
    # This file is now used as a module, not for testing
    pass

