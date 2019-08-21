FROM python:3.5-stretch
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libatlas-base-dev \
        python-dev \
        gfortran \
        pkg-config \
        libfreetype6-dev \
    && apt-get clean

ENV TINI_VERSION v0.6.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /usr/bin/tini
RUN chmod +x /usr/bin/tini
ENTRYPOINT ["/usr/bin/tini", "--"]

RUN adduser --home /home/brent --group --system --uid 1000 brent \
 && mkdir /home/brent/.jupyter

RUN pip3 install jupyter zipline scikit-learn tensorflow
RUN pip3 install matplotlib numpy pandas scipy


COPY jupyter-service/jupyter_notebook_config.py /home/brent/.jupyter/.
RUN chown -R brent:brent /home/brent

RUN mkdir /home/brent/temp \
    && cd /home/brent/temp \
    && curl http://interactivebrokers.github.io/downloads/twsapi_macunix.976.01.zip --output tws_api.zip \
    && unzip tws_api.zip \
    && cd IBJts/source/pythonclient \
    && python3 setup.py install

USER brent
#CMD ["/bin/bash", "-c", "sleep 10000"]
CMD ["jupyter", "notebook", "--port=8888", "--no-browser", "--ip=0.0.0.0"]
