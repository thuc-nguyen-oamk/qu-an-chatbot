import argparse
from transformers import pipeline
from evaluate import load

# Function to execute the question-answering task
def question_answering(context, question):
    # Initialize the question-answering pipeline
    qa_pipeline = pipeline("question-answering", model="deepset/minilm-uncased-squad2")
    # Get the answer from the pipeline
    response = qa_pipeline(question=question, context=context)
    return response

# Function to evaluate the answers
def evaluate_answers(expected_answer, predicted_answers):
    # Load the SQuAD evaluation metric
    squad_evaluator = load("squad_v2")
    cumulative_predictions = []
    cumulative_references = []

    for index, predicted_answer in enumerate(predicted_answers):
        # Format predictions
        formatted_prediction = [{
            'prediction_text': predicted_answer,
            'id': str(index),
            'no_answer_probability': 0.0
        }]
        cumulative_predictions.append(formatted_prediction[0])

        # Format references
        formatted_reference = [{
            'answers': {
                'answer_start': [1],
                'text': [expected_answer]
            },
            'id': str(index)
        }]
        cumulative_references.append(formatted_reference[0])

    # Compute cumulative results
    overall_results = squad_evaluator.compute(
        predictions=cumulative_predictions,
        references=cumulative_references
    )
    return overall_results

if __name__ == "__main__":
    # Parse arguments
    parser = argparse.ArgumentParser(description="Run a question-answering task using Hugging Face.")
    parser.add_argument("--context", type=str, required=True, help="The context text file for the QA task.")
    parser.add_argument("--question", type=str, required=True, help="The question to be answered.")
    parser.add_argument("--evaluate", action="store_true", help="Evaluate predictions using SQuAD metric.")
    parser.add_argument("--expected_answer", type=str, help="The expected answer for evaluation.")
    parser.add_argument("--predicted_answers", type=str, nargs="+", help="A list of predicted answers for evaluation.")

    args = parser.parse_args()

    # Read the context from the file
    with open(args.context, 'r') as file:
        context_text = file.read()

    # Execute the question-answering task
    qa_response = question_answering(context_text, args.question)
    print("\nAnswer to the question:")
    print(qa_response)

    # Evaluate if specified
    if args.evaluate:
        if not args.expected_answer or not args.predicted_answers:
            raise ValueError("Both --expected_answer and --predicted_answers are required for evaluation.")
        
        evaluation_results = evaluate_answers(args.expected_answer, args.predicted_answers)
        print("\nEvaluation Results:")
        print(evaluation_results)
