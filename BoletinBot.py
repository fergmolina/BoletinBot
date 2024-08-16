from tools.tweet import post_tweet
from tools.telegram import send_message_telegram
from openai import OpenAI
import requests
import io
from datetime import datetime
import holidays
import pytz
import time
from dotenv import load_dotenv
import os


def is_weekday_and_not_holiday(date):
    """Function that will return True if is a weekday and not a holiday in Argentina
    Args: 
        date: Date for comparison
    Returns: -
    """
    # Get the holidays for Argentina
    ar_holidays = holidays.AR(years=date.year)
    
    # Check if the date is a weekday (Monday to Friday) and not a holiday
    if date.weekday() < 5 and date not in ar_holidays:
        return True
    return False

def fetch_messages_with_retry(client, thread_id, run_id, retries=5, delay=30):
    """Function to retry if for some reason OpenAI API fails sending back a message
    Args: 
        client: OpenAI client
        thread_id: Id of the thread created previously
        run_id: 
        retries: amount of attempts - default 5
        delay: seconds in between each retry - default 30 seconds
    Returns: -
    """
    for attempt in range(retries):
        messages = list(client.beta.threads.messages.list(thread_id=thread_id, run_id=run_id))
        if messages:
            return messages
        else:
            print(f"No messages returned, retrying... ({attempt + 1}/{retries})")
            time.sleep(delay)  # Wait before retrying
    return None  # Return None if all retries fail

def main(data,context):
    load_dotenv()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    # Create the assistant with file_search enabled
    assistant = client.beta.assistants.create(
        name="Boletin Oficial de Argentina Bot",
        instructions="Sos un bot que lee el Boletin Oficial de Argentina y hace un resumen para que todo el mundo pueda leerlo",
        model="gpt-4o",
        tools=[{"type": "file_search"}],
    )

    # Current day
    timezone = pytz.timezone('America/Argentina/Buenos_Aires')
    current_date = datetime.now(timezone).date()
    # Check if it is a workable weekday
    if not is_weekday_and_not_holiday(current_date):
        exit()

    # Fetch the latest Boletin Oficial
    file_url = "https://s3.arsat.com.ar/cdn-bo-001/pdf-del-dia/primera.pdf"
    response = requests.get(file_url)
    file_like_object = io.BytesIO(response.content)
    file_like_object.name = "boletin.pdf"

    # Upload the file
    message_file = client.files.create(
        file=file_like_object, purpose="assistants"
    )

    # Create the vector store with adjusted chunk size and overlap
    vector_store = client.beta.vector_stores.create(
        name="Boletin Oficial Vector Store",
        chunking_strategy={
            "type": "static",
            "static": {
                "max_chunk_size_tokens": 4096,
                "chunk_overlap_tokens": 2048
            }
        },
        file_ids=[message_file.id]
    )

    # Poll the status of the file batch to ensure completion
    file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
        vector_store_id=vector_store.id,
        files=[file_like_object]
    )
    print(file_batch.status)
    print(file_batch.file_counts)

    # Update the assistant to use the new vector store
    assistant = client.beta.assistants.update(
        assistant_id=assistant.id,
        tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}}
    )

    # Create a thread and attach the file to the message
    thread = client.beta.threads.create(
        messages=[
            {
                "role": "user",
                "content": """Este es el boletin oficial de la Republica Argentina para el dia """ + str(current_date) + """. 
                            Hace un resumen con el contenido del documento CON MUCHOS DETALLES. 
                            Evita partes introductorias y de protocolo, enfocate solo en lo importante. 
                            Todos los puntos deben tener algun detalle, no dejar nada con comentarios genericos como 'resolucion administrativas varias'. 
                            La parte de los Decretos es la mas importante. Agregar el nombre de todas las designaciones a cargos. 
                            En las Disposiciones y Resoluciones resumir lo que se resuelve. Son dos secciones separadas.
                            No agregues Referencias. Empeza siempre con Boletin Oficial dd-mm-yyyy y termina con una frase 'Fin Boletin Oficial'""",
                "attachments": [
                    { "file_id": message_file.id, "tools": [{"type": "file_search"}] }
                ],
            }
        ],
    )

    # The thread now has a vector store with that file in its tool resources.
    print(thread.tool_resources.file_search)

    # Use the create and poll SDK helper to create a run and poll the status of
    # the run until it's in a terminal state.
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id, assistant_id=assistant.id
    )

    # Fetch messages with retry logic
    messages = fetch_messages_with_retry(client, thread.id, run.id)

    if messages:
        message_content = messages[0].content[0].text
        annotations = message_content.annotations
        citations = []
        for index, annotation in enumerate(annotations):
            message_content.value = message_content.value.replace(annotation.text, f"[{index}]")
            if file_citation := getattr(annotation, "file_citation", None):
                cited_file = client.files.retrieve(file_citation.file_id)
                citations.append(f"[{index}] {cited_file.filename}")

        print(message_content.value)
        link_tweet = post_tweet(message_content.value)
        send_message_telegram('Tweet sent', link_tweet, False)
    else:
        print("Failed to retrieve messages after multiple attempts.")
        send_message_telegram('Failed to retrieve messages after multiple attempts.', '', True)
        raise ValueError("Failed to retrieve messages after multiple attempts.") 
        

if __name__ == "__main__":
    main('','')