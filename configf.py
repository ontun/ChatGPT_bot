import configparser

# Создаем объект конфигурации
config = configparser.ConfigParser()

# Добавляем секцию и параметры
config.add_section('Settings')
config.set('Settings', 'API_key_bot', 'Bot_token')
config.set('Settings', 'API_key_gpt', 'GPT_token')

# Записываем конфигурацию в файл
with open('config.ini', 'w') as f:
    config.write(f)