#client.py
from utils.config import API_IP, API_PORT, API_PATH
from const.const_bot import API_JSON_PATH
from utils.json_fun import post_client_json_updater
from utils.gen_uuid import generate_id, generate_sub_id
from utils.timestamp import set_date, update_date, current_timestamp
import database.user
import const.const_api
import const.const_db
import utils.ports
from utils.logging_utils import setup_logger, retry_on_error, log_function_call

# Настраиваем логгер
logger = setup_logger('client', 'api.log')


@log_function_call(logger)
def add_client(tg_id, period, username):
    """Добавление нового клиента с обработкой ошибок"""
    try:
        url = f"https://{API_IP}:{API_PORT}/{API_PATH}/panel/api/inbounds" + "/addClient"

        try:
            # Генерация идентификаторов и установка даты
            user_id = generate_id()
            email = username
            date = set_date(period)
            sub_id = generate_sub_id()
            port = utils.ports.random_port()
        except Exception as e:
            logger.error(f"Error generating IDs or date: {str(e)}")
            raise

        # Компиляция профиля vless
        try:
            vless_profile = (f'vless://{user_id}@{API_IP}:{port}?'
                            f'type=tcp&'
                            f'security=reality&'
                            f'pbk=OTaHp-w6pfI6LSU30DKJp00o2L0VVDpiDkYVa_EVcDs&'
                            f'fp=chrome&'
                            f'sni=www.google.com&'
                            f'sid=7c1a8b90ee&spx=%2F&'
                            f'flow=xtls-rprx-vision'
                            f'#{email}')
            login_date = current_timestamp()
        except Exception as e:
            logger.error(f"Error creating vless profile: {str(e)}")
            raise

        # Вставка в базу данных
        try:
            database.user.insert_user(tg_id, user_id, email, date, sub_id, vless_profile, login_date)
        except Exception as e:
            logger.error(f"Database insertion error: {str(e)}")
            raise

        try:
            # Компиляция JSON и отправка запроса
            data = post_client_json_updater(tg_id, f"{API_JSON_PATH}json/request_post_client.json",
                                            user_id, email, date, sub_id)
            response = const.const_db.SESSION.post(url, headers=const.const_api.HEADERS,
                                                   json=data, verify=False)

            if not response.ok:
                logger.error(f"Failed to add client. Status code: {response.status_code}")
                raise Exception(f"Failed to add client. Status code: {response.status_code}")
        except Exception as e:
            logger.error(f"API request error: {str(e)}")
            raise

        logger.info(f"Successfully added client with tg_id: {tg_id}")
        return vless_profile

    except Exception as e:
        logger.error(f"Error while adding client: {str(e)}")
        raise


@log_function_call(logger)
def update_client(tg_id, period):
    """Обновление данных активного пользователя"""
    try:
        try:
            # Получение информации из базы данных
            user_data = database.user.select_user(tg_id)
            if not user_data:
                raise Exception(f"User with tg_id {tg_id} not found")
        except Exception as e:
            logger.error(f"Database selection error: {str(e)}")
            return False

        tg_id, user_id, email, old_date, sub_id, vless, login_date, trial_date = user_data
        url = f"https://{API_IP}:{API_PORT}/{API_PATH}/panel/api/inbounds" + "/updateClient" + f"/{user_id}"

        try:
            # Обновление даты
            date = update_date(old_date, period)
            database.user.update_user_date(date, tg_id)
        except Exception as e:
            logger.error(f"Error updating date: {str(e)}")
            return False

        try:
            # Компиляция JSON и отправка запроса
            data = post_client_json_updater(tg_id, f"{API_JSON_PATH}json/request_post_client.json",
                                            user_id, email, date, sub_id)
            response = const.const_db.SESSION.post(url, headers=const.const_api.HEADERS,
                                                   json=data, verify=False)

            if not response.ok:
                logger.error(f"Failed to update client. Status code: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"API request error: {str(e)}")
            return False

        logger.info(f"Successfully updated client with tg_id: {tg_id}")
        return True

    except Exception as e:
        logger.error(f"Error while updating client: {str(e)}")
        return False


