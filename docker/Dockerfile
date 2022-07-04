FROM python:3.10.5-bullseye

COPY dataloop-0.0.1-py3-none-any.whl /tmp
RUN python -m pip install /tmp/dataloop-0.0.1-py3-none-any.whl
ENTRYPOINT ["python","-m","dataloop"]