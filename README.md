## Установка пакетов и программ
1. скачать adb `https://developer.android.com/tools/releases/platform-tools`
2. скачать pycham
3. скачать genymotion, подключить эмулятор с вертикальным экраном
4. запустить эмулятор и установить подключение по ftp/локальное
5. запустить через cmd - adb: `adb start-server`
6. проверить подлюченный  девайс: adb devices (здесь будут указаны подключенные эмуляторы с их `adb devices ip address` )
7. Установить uiautomator2:  `pip install -U uiautomator2 `
8. Установить UI Inspector:  `pip install uiautodev`


## Запуск скраппера
Добавить в код строки 
1. `u2.connect(`adb devices ip address`)`
2. `logger.log('u2 connect info {0}'.format(d.info) )`
3. запуск скрипта: `python domain.py regionId taskId --log`

## Запуск скраппера в тестовом режиме с использованем UI Inspector
запуск UI Inspector:  `uiauto.dev`

