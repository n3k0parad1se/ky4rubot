FROM n3k0parad1se/Ky4ruBot:debian

RUN set -ex \
    && git clone -b main https://github.com/n3k0parad1se/Ky4ruBot /root/userbot \
    && chmod 777 /root/userbot

WORKDIR /root/userbot/

CMD ["python3", "-m", "userbot"]
