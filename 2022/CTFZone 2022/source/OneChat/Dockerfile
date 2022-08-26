FROM archlinux:base-20220529.0.58327

RUN pacman -Syy --noconfirm
RUN pacman -S socat --noconfirm

COPY ./chat ./chat
COPY ./flag.txt /flag.txt

RUN chmod +x ./chat

CMD ["socat", "tcp-l:1337,reuseaddr,fork", "EXEC:\"/chat\",stderr"] 