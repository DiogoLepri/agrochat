from django.shortcuts import render, redirect
from django.http import JsonResponse
import openai
import requests
from django.contrib import auth
from django.contrib.auth.models import User
from .models import Chat
import json
import re
from django.utils import timezone
from datetime import datetime, timedelta, time
import unicodedata
from dotenv import load_dotenv
import os

load_dotenv()



openai.api_key = os.getenv("OPENAI_API_KEY")
OPEN_WEATHER_ENDPOINT = "http://api.openweathermap.org/data/2.5/weather"
OPEN_WEATHER_API_KEY = os.getenv("OPEN_WEATHER_API_KEY")


def obter_previsao_por_data_e_hora(cidade, data_solicitada, hora_solicitada=None):
    PREVISAO_ENDPOINT = "http://api.openweathermap.org/data/2.5/forecast"

    params = {
        'q': cidade,
        'appid': OPEN_WEATHER_API_KEY,
        'units': 'metric',
        'lang': 'pt'
    }

    response = requests.get(PREVISAO_ENDPOINT, params=params)

    if response.status_code != 200:
        response.raise_for_status()

    data = response.json()

    hoje = datetime.today().date()
    delta = (data_solicitada - hoje).days

    if delta < 0 or delta > 4:
        return "Data solicitada fora do intervalo da previsão disponível."

    previsoes_dia = [p for p in data['list'] if data_solicitada.strftime('%Y-%m-%d') in p['dt_txt']]

    if hora_solicitada:
        if isinstance(hora_solicitada, str):
            try:
                hora_solicitada = datetime.strptime(hora_solicitada, '%H:%M').time()
            except ValueError:
                return f"Formato de hora inválido: {hora_solicitada}. Por favor, use o formato HH:MM."

        if not isinstance(hora_solicitada, time):
            return f"Tipo de hora inválido: {hora_solicitada}. Por favor, forneça um objeto datetime.time ou uma string no formato HH:MM."

        previsoes_dia = sorted(previsoes_dia, key=lambda p: abs(
            datetime.strptime(p['dt_txt'], '%Y-%m-%d %H:%M:%S').time().hour - hora_solicitada.hour))

    if not previsoes_dia:
        return f"Não foi possível encontrar uma previsão para {data_solicitada} às {hora_solicitada}"

    previsao = previsoes_dia[0]

    dt_parsed = datetime.strptime(previsao['dt_txt'], '%Y-%m-%d %H:%M:%S')

    result = {
        'data': dt_parsed.date().strftime('%Y-%m-%d'),
        'hora': dt_parsed.time().strftime('%H:%M'),
        'clima': previsao['weather'][0]['description'],
        'temperatura': previsao['main']['temp'],
        'umidade': previsao['main']['humidity']
    }

    return result


def obter_clima_em_tempo_real(cidade):
    params = {
        'q': cidade,
        'appid': OPEN_WEATHER_API_KEY,
        'units': 'metric',
        'lang': 'pt'
    }

    response = requests.get(OPEN_WEATHER_ENDPOINT, params=params)

    if response.status_code != 200:
        response.raise_for_status()

    data = response.json()
    return {
        'clima': data['weather'][0]['description'],
        'temperatura': data['main']['temp'],
        'umidade': data['main']['humidity']
    }


def format_payload_for_openai(weather_data):
    # Mensagem modelo com um espaço reservado para os dados do clima.
    # Esta é apenas uma sugestão. Você pode criar sua própria mensagem baseada no que quer perguntar ao GPT-3.
    message_template = "Com base nos seguintes dados meteorológicos WEATHER_JSON, você pode fornecer um resumo?"

    stringJson = json.dumps(weather_data)

    # Substitui o espaço reservado pelos dados do clima.
    final_message = message_template.replace("__WEATHER_JSON__", stringJson)

    return final_message


def ask_open_weather_and_openai(city):
    weather_data = obter_clima_em_tempo_real(city)
    system_message = "Voce é um assitente climatico para agronegocio"
    user_message = (f"Em {city}, o clima é descrito como {weather_data['clima']}. "
                    f"A temperatura atual é de {weather_data['temperatura']}°C "
                    f"e a umidade é de {weather_data['umidade']}%.")

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
    )

    return response.choices[0].message['content'].strip()


def ask_open_weather_forecast_and_openai(city, date_solicited, hora_solicitada):
    forecast_data = obter_previsao_por_data_e_hora(city, date_solicited, hora_solicitada)

    if isinstance(forecast_data, str):  # Se for uma string, retorne-a diretamente
        return forecast_data

    # Aqui, vou considerar apenas a primeira entrada da previsão para simplificar, mas você pode adaptar conforme necessário.
    first_forecast = forecast_data

    system_message = "Você é um assistente climático para agronegócio"
    user_message = (f"A previsão para {city} é: "
                    f"Clima - {first_forecast['clima']}, "
                    f"Temperatura - {first_forecast['temperatura']}°C, "
                    f"Umidade - {first_forecast['umidade']}%.")

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
    )

    return response.choices[0].message['content'].strip()


def ask_gpt(message):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system",
             "content": """
            Você é o AgroChat, um assistente virtual especializado em agronegócio, criado pela AgroWise.
             Oferece suporte em decisões para cooperados da Integrada Cooperativa Agroindustrial e tem acesso a dados climáticos em tempo real.
              Por exemplo, um usuário pode perguntar: "AgroChat, qual é o clima em Londrina?" ou 
              "AgroChat, qual o melhor período para colheita da soja em Londrina?" ou 
              "AgroChat, para amanha, qual é a previsão do tempo em Maringá?"
             """},
            {"role": "user", "content": message},
        ]
    )

    answer = response.choices[0].message.content.strip()
    return answer


def extract_city_from_message(message):
      # Certifique-se de importar o módulo re

    # Procura por várias possibilidades de padrões que mencionam o clima e a cidade
    patterns = [
        r'(clima|tempo) em (\w+(?: \w+){0,3})',
        r'como está o clima em (\w+(?: \w+){0,3})',
        r'qual é o tempo em (\w+(?: \w+){0,3})',
        r'qual é o clima em (\w+(?: \w+){0,3})',
        r'(\w+(?: \w+){0,3}) está frio',
        r'está chovendo em (\w+(?: \w+){0,3})',
        r'previsão do tempo para (\w+(?: \w+){0,3})',
        r'previsão do tempo em (\w+(?: \w+){0,3})',
        r'previsão do tempo na cidade de (\w+(?: \w+){0,3})'
    ]

    for pattern in patterns:
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            # Retorna o último grupo capturado
            return match.groups()[-1]

    return None






def normalize(string):
    return ''.join(c for c in unicodedata.normalize('NFD', string) if unicodedata.category(c) != 'Mn').lower()

def detectar_data(mensagem):
    mensagem = normalize(mensagem)

    if "depois de amanha" in mensagem:
        return (datetime.now() + timedelta(days=2)).date()
    elif "amanha" in mensagem:
        return (datetime.now() + timedelta(days=1)).date()
    elif "hoje" in mensagem:
        return datetime.now().date()

    # Mapeamento dos nomes dos meses
    meses = {
        'janeiro': 1, 'fevereiro': 2, 'marco': 3, 'abril': 4,
        'maio': 5, 'junho': 6, 'julho': 7, 'agosto': 8,
        'setembro': 9, 'outubro': 10, 'novembro': 11, 'dezembro': 12
    }

    date_pattern = re.compile(r'(\d{1,2})\s*de\s*([a-zç]+)')
    match = date_pattern.search(mensagem)

    if match:
        dia = int(match.group(1))
        mes = meses.get(match.group(2))

        if mes:
            ano_atual = datetime.now().year
            try:
                return datetime(ano_atual, mes, dia).date()
            except ValueError:
                # Exceção para capturar datas inválidas como 30 de fevereiro
                pass

    return None


def extrair_horario(message):
    """
    Extrai um horário no formato HH:MM da mensagem.
    Retorna o horário se encontrado, caso contrário, retorna None.
    """
    # Padronização do formato HH:MM
    pattern = re.compile(r'(?:(?:[01]\d|2[0-3]):[0-5]\d)')
    match = pattern.search(message)
    if match:
        return match.group(0)
    return None




def format_response(response):
    """ Breaks the response into lines for better readability. """
    lines = re.split('[:]', response)  # Vai dividir o texto em ":" e "-"
    formatted_response = ":\n".join([line.strip() for line in lines if line])
    return formatted_response


def chatbot(request):
    if not request.user.is_authenticated:
        return JsonResponse({
            'error': 'Você necessita estar logado para usar o AgroChat!'
        }, status=401)  # 401 Unauthorized

    user_id = request.user.id

    chats = Chat.objects.filter(user=request.user)
    default_response = ("Desculpe, não consegui entender sua solicitação. "
                        "Por favor, especifique uma cidade para obter informações climáticas. "
                        "Por exemplo: 'Qual é o clima em São Paulo?'")

    if request.method == 'POST':
        message = request.POST.get('message')

        # Detecção de cidade e data
        city = extract_city_from_message(message)
        date_solicited = detectar_data(message)
        hora_solicitada = extrair_horario(message)

        if city and date_solicited:  # Se cidade e data foram detectadas, obter previsão.
            final_response = ask_open_weather_forecast_and_openai(city, date_solicited, hora_solicitada)
        elif city:  # Se apenas cidade foi detectada, obter clima atual.
            final_response = ask_open_weather_and_openai(city)
        else:  # Caso contrário, utilize o GPT para responder.
            final_response = ask_gpt(message)  # Você deve implementar a função ask_gpt de acordo com suas necessidades.

        # Formatação da resposta
        final_response = format_response(final_response)

        chat = Chat(user=request.user, message=message, response=final_response, created_at=timezone.now())
        chat.save()
        return JsonResponse({'message': message, 'response': final_response})

    return render(request, 'chatbot/chatbot.html', {'chats': chats})


# As funções de autenticação (login, register, logout) permanecem as mesmas e não foram incluídas aqui para economizar espaço.

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('chatbot')
        else:
            error_message = 'Usuário ou senha inválidos'
            return render(request, 'chatbot/login.html', {'error_message': error_message})
    else:
        return render(request, 'chatbot/login.html')


def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 == password2:
            try:
                user = User.objects.create_user(username, email, password1)
                user.save()
                auth.login(request, user)
                return redirect('chatbot')
            except:
                error_message = 'Erro criando a conta'
                return render(request, 'chatbot/register.html', {'error_message': error_message})
        else:
            error_message = 'Senha não compatível'
            return render(request, 'chabot/register.html', {'error_message': error_message})
    return render(request, 'chatbot/register.html')


def logout(request):
    auth.logout(request)
    return redirect('home')


def home(request):
    return render(request, 'chatbot/home.html')


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('chatbot')
        else:
            error_message = 'Usuário ou senha inválidos'
            return render(request, 'chatbot/login.html', {'error_message': error_message})
    else:
        return render(request, 'chatbot/login.html')
