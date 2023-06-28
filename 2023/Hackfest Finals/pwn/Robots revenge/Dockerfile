FROM ubuntu@sha256:83f0c2a8d6f266d687d55b5cb1cb2201148eb7ac449e4202d9646b9083f1cee0 AS app

RUN apt update

RUN apt install gdb wget python3 -y
RUN bash -c "$(wget https://gef.blah.cat/sh -O -)"
RUN apt install binutils -y
RUN apt install file -y

FROM pwn.red/jail

COPY --from=app / /srv

COPY main_bkup /srv/app/run

COPY flag.txt /srv/app/
ENV JAIL_MEM=20M JAIL_POW=5000 JAIL_ENV_NUM=5 JAIL_TIME=0

#RUN mount /proc/ /srv/proc/

EXPOSE 1337
