import requests
import random
import time

# Загрузка списка кошельков из файла
def load_wallets(filename):
    with open(filename, 'r') as file:
        return [line.strip() for line in file if line.strip()]

# Загрузка списка прокси из файла
def load_proxies(filename):
    with open(filename, 'r') as file:
        return [line.strip() for line in file if line.strip()]

# Проверка баланса кошелька с использованием API
def check_wallet(wallet, proxy):
    url = f"https://api.odos.xyz/loyalty/users/{wallet}/balances"
    retries = 3  # Количество попыток
    for attempt in range(retries):
        try:
            response = requests.get(url, proxies={"http": proxy, "https": proxy}, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get("data", {}).get("claimableTokenBalance", None)
            else:
                print(f"[{wallet}] Ошибка: {response.status_code}")
                return None
        except requests.RequestException as e:
            print(f"[{wallet}] Прокси не работает или ошибка соединения: {proxy}. Попытка {attempt + 1} из {retries}.")
            if attempt < retries - 1:  # Ждать только если есть ещё попытки
                time.sleep(10)  # Задержка между попытками
    return None  # Возврат None, если все попытки не удались

# Основная функция
def main():
    wallets = load_wallets('wallets.txt')  # Список кошельков
    proxies = load_proxies('proxies.txt')  # Список прокси

    if not wallets or not proxies:
        print("Убедитесь, что списки кошельков и прокси заполнены.")
        return

    proxy_index = 0
    results = {}

    for wallet in wallets:
        # Если прокси закончились, начать с первого
        if proxy_index >= len(proxies):
            proxy_index = 0

        proxy = proxies[proxy_index]
        print(f"Проверяем кошелек: {wallet} через прокси: {proxy}")

        # Попытка проверки баланса
        claimable_balance = check_wallet(wallet, proxy)

        # Если данные получены и баланс > 0, сохраняем результат
        if claimable_balance is not None:
            claimable_balance = int(claimable_balance)  # Преобразуем в число
            if claimable_balance > 0:
                results[wallet] = claimable_balance
                print(f"[{wallet}] claimableTokenBalance: {claimable_balance}")
        else:
            # Если прокси не сработал, переход к следующему
            proxy_index += 1

        # Небольшая задержка между запросами
        time.sleep(random.uniform(1, 1))

    # Сохранение результатов в файл (только кошельки с балансом > 0)
    with open('results.txt', 'w') as file:
        for wallet, balance in results.items():
            file.write(f"{wallet}: {balance}\n")

    print("Проверка завершена. Результаты сохранены в results.txt (только кошельки с балансом > 0).")

if __name__ == "__main__":
    main()
