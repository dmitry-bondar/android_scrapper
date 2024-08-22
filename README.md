## Установка пакетов и программ

1. Скачать инструменты платформы SDK для Windows `https://developer.android.com/tools/releases/platform-tools`
2. Распаковать platform-tools на диск C:\
3. Создать папку C:\opt\android_scrapper
4. Скачать и установить python
5. Скачать Pycham Community Edition, установить интерпритатор python
6. Установить uiautomator2:  `pip install -U uiautomator2 `
7. Установить UI Inspector:  `pip install uiautodev`
8. Скачать genyMotion + virtualbox, подключить эмулятор с вертикальным экраном, установить подключение BRIDGE, назвать девайс под нужное приложение


## Запуск скраппера

1. запустить через cmd - adb: `adb start-server`
2. проверить подлюченный девайс: adb devices (здесь будут указаны подключенные эмуляторы с их `adb devices ip address` )

запуск скрипта:
`python domain.py regionId taskId --log`

## Запуск скраппера в тестовом режиме с использованем UI Inspector

запуск UI Inspector:  `uiauto.dev`
