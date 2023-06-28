FROM ubuntu@sha256:554e40b15453c788ec799badf0f1ad05c3e5c735b53f940feb8f27cf2ec570c5 AS app

// Added these to debug
RUN apt update

RUN apt install gdb wget python3 -y
RUN bash -c "$(wget https://gef.blah.cat/sh -O -)"
RUN apt install binutils -y

FROM pwn.red/jail

COPY --from=app / /srv

COPY main_bkup /srv/app/run

COPY flag.txt /srv/app/
ENV JAIL_MEM=20M JAIL_POW=5000 JAIL_ENV_NUM=5 JAIL_TIME=0 // Changed to 0 to help in debugging

RUN mount /proc /srv/proc // Debugging, needed for gdb

EXPOSE 1337
