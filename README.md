# ssh-connection-notify-py

Простой python скрипт для отправки уведомлений об успешных попытках аутентификации на SSH. Отправляет уведомление на email, а так-же на терминал пользователей. (man wall). Можно настроить исключения, при которых не будет происходить уведомлений при попытке подключения с определённых айпи-адресов или сетевых масок.

Для работы: Установить модули python-ipaddr, python-yaml.
```shell
cp .ssh-connection-notify.yaml /etc/ssh/.ssh-connection-notify.yaml
vi/nano /etc/ssh/.ssh-connection-notify.yaml
cp ssh-connection-notify.py /usr/local/bin/ssh-connection-notify.py
chmod +x /usr/local/bin/ssh-connection-notify.py
echo "/usr/local/bin/ssh-connection-notify.py" >> /etc/ssh/sshrc
```
