FROM pwn.red/jail

COPY --from=ubuntu@sha256:7a57c69fe1e9d5b97c5fe649849e79f2cfc3bf11d10bbd5218b4eb61716aebe6 / /srv

COPY main /srv/app/run

COPY flag.txt /srv/app/

EXPOSE 1337
