# paddu_food_chatbot

# create the virtual environment along with python version
conda create -n venv python=3.12

# install the required libraries
!pip install -r requirements.txt

# to run the flask api
uvicorn main:app --reload
