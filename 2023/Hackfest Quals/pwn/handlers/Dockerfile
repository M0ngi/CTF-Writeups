FROM pwn.red/jail

COPY --from=ubuntu@sha256:5ed6262a1edb954cae006b966ca70468e982285aa57419b4d2b221a5e11dd881 / /srv

COPY main /srv/app/run

COPY flag.txt /srv/app/

EXPOSE 1337
