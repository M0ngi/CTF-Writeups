FROM pwn.red/jail

COPY --from=ubuntu@sha256:09f035f46361d193ded647342903b413d57d05cc06acff8285f9dda9f2d269d5  / /srv

COPY main /srv/app/run

COPY flag.txt /srv/app/
ENV JAIL_MEM=20M JAIL_POW=5000 JAIL_ENV_NUM=5 JAIL_TIME=200

EXPOSE 1340
