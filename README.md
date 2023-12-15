## AgroChat 

<p align="center">
  <img src="https://github.com/raphaelgpalma/agrochat/blob/main/static/output.png" alt="Descrição da Imagem">
</p>


AgroChat is an innovative Django project that leverages real-time weather data to provide specific and efficient recommendations for each user. It integrates with the real-time weather data API to offer accurate information about current and future weather conditions. Moreover, it is enhanced with the ChatGPT generative text API, transforming it into an intelligent virtual assistant for agriculture.

## Prerequisites

Make sure to have the following requirements installed before getting started:

- **Python**: 
  - [Download Python](https://www.python.org/downloads/)

## Usage

1. Clone this repository:

```bash
git clone https://github.com/raphaelgpalma/agrochat.git
```

2. Virtual Environment Setup:

I recommend using a virtual environment to isolate project dependencies. Execute the following commands to create and activate a virtual environment:

```bash
# On Windows, use venv\Scripts\activate
# On Unix or MacOS, use source venv/bin/activate
python -m venv venv
source venv/bin/activate
```
3. Install Project Dependencies:

```bash
pip install -r requirements.txt
```

4. Create a .env file at the root of your project:

  ```bash
  touch .env
  ```

  Add on your .env file:

  ```bash
  OPENAI_API_KEY=<YOUR OPENAI API KEY>
  OPEN_WEATHER_API_KEY=<YOUR OPEN WEATHER API KEY>
  ```

5. Run the Project's Server:

```bash
python manage.py runserver
```
If you want to stop running the server press CTRL+C on Terminal



   
