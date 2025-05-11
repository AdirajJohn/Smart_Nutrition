from backend.logic.smart_logic import Smart_Logic
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import openai
import json
from pydantic import BaseModel
from fastapi import Request
import re

data_path = "data/golden_dataset_mh.csv"

client = openai.OpenAI(
    api_key="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",
    base_url="https://api.openai.com/v1"
)
app = FastAPI()

# Optional: Enable CORS so frontend can call the API from a browser
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Change to your frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class InputData(BaseModel):
    input_json : dict[str,int]

class PromptInput(BaseModel):
    user_input: str

@app.post("/data")
def smart_data(input_data: InputData):
    input_dict = input_data.input_json
    df = Smart_Logic.smart_fetch(sample_input=input_dict,data_path=data_path)
    return df.to_dict(orient='records')

@app.post("/generate-data")
def generate_data(prompt_input: PromptInput, request: Request):
    user_prompt = prompt_input.user_input
    #Get the ingredients list
    ingredients_list = Smart_Logic.get_ingredient_str(data_path=data_path,col_name = "name")
# JSON Extraction Prompt
    prompt_extraction = (
        "You are a food ingredient extractor. "
        "Extract all food ingredients and their quantities in grams from the sentence below. "
        "Return ONLY a valid JSON object — no explanation or extra text — where the keys are ingredient names and the values are their quantities in grams as integers. "
        "Only include ingredients that are explicitly mentioned with a quantity.\n\n"
        f"Input: \"{user_prompt}\"\n"
        "Output:"
    )
    # Send prompt to OpenAI API
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini-2025-04-14",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that extracts structured data."},
                {"role": "user", "content": prompt_extraction}
            ],
            temperature=0.2
        )

        res1 = response.choices[0].message.content.strip()
        #Remove unwanted marker from the response
        json_extracted = re.sub(r"```json|```", "", res1).strip()
        # Step 2: Ingredient Validation Prompt
        prompt_validation = (
                "You are a food ingredient validator. "
                "From the extracted JSON, check if each ingredient key matches one of the known ingredients from the list below. "
                "If an ingredient in the JSON is sufficiently similar (at least 75% similarity) to an ingredient in the list, replace the key with the correct ingredient name from the list. "
                "Ensure the output is a valid JSON object where the keys match the known ingredient names from the list exactly.\n\n"
                f"List of known ingredients:\n- " + "\n- ".join(ingredients_list) + "\n\n"
                f"Input JSON: {json_extracted}\n"
                "Output:"
            )
        response_validate = client.chat.completions.create(
                model="gpt-4.1-mini-2025-04-14",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that corrects and validates extracted data."},
                    {"role": "user", "content": prompt_validation}
                ],
                temperature=0.2
            )
            
        validated_json_str = response_validate.choices[0].message.content.strip()
        validated_json = json.loads(validated_json_str)
        #Secondary validation with the ingredients name in the data
        final_items = Smart_Logic.filter_json_by_list(input_json=validated_json,comparison_list=ingredients_list)
        return final_items

    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)