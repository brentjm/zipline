FROM brentjm/jupyter:1.0

USER root
RUN pip3 install zipline scikit-learn tensorflow

USER brent
#CMD ["/bin/bash", "-c", "sleep 10000"]
CMD ["jupyter", "notebook", "--port=8888", "--no-browser", "--ip=0.0.0.0"]
