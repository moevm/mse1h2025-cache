FROM ubuntu:22.04

ARG PYTHON_REQUIRED_LIBS
ARG UTIL_NAME

# Remove diverted man binary to prevent man-pages being replaced with "minimized" message.
RUN if  [ "$(dpkg-divert --truename /usr/bin/man)" = "/usr/bin/man.REAL" ]; then \
        rm -f /usr/bin/man; \
        dpkg-divert --quiet --remove --rename /usr/bin/man; \
    fi
RUN apt-get update
RUN apt-get install -y python3-pip
RUN pip3 install --upgrade setuptools
RUN apt-get install -y clang libncurses5
RUN apt-get install -y man
RUN apt-get install -y vim nano less

RUN pip3 install $PYTHON_REQUIRED_LIBS

VOLUME /usr/src/works
WORKDIR /usr/src/$UTIL_NAME
