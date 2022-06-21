from datetime import datetime
import json

def logs(function):
    def wrapper_log(*args, **kwargs):
        args_repr = [repr(a) for a in args]
        kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
        signature = ", ".join(args_repr + kwargs_repr)
        value = function(*args, **kwargs)

        try:
            with open('log.txt', 'r', encoding='utf8') as myFile:
                txt = myFile.read()
                if 'Log file for API testing https://petfriends1.herokuapp.com/' not in txt:
                    txt = 96 * '*' + '\n' + 'Log file for API testing https://petfriends1.herokuapp.com/' + '\n' + 96 * '*'

        except:
            txt = 96 * '*' + '\n' + 'Log file for API testing https://petfriends1.herokuapp.com/' + '\n' + 96 * '*'
        try:
            with open('log.txt', 'w', encoding='utf8') as myFile:
                date = '\n' + '\n' + str(datetime.now()) + '\n'
             #в текст файла с логами добавляем дату и время выполнения запроса, название функции, параметры запроса (аргументы), код ответа и тело ответа
                txt += date + f"Function: {function.__name__}\n" \   
                          f"Request params:\n{signature}\n" \
                          f"Status:\n{value[0]}\n" \
                          f"Response:\n{value[1]}\n\n"
                myFile.write(txt)
        finally:
            return value
    return wrapper_log



