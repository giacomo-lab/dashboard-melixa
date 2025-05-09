FROM public.registry.u-hopper.com/python:3.12 as builder

ARG PIP_CONF_DOCKER


RUN mkdir -p /root/.config/pip
RUN echo "${PIP_CONF_DOCKER}" > /root/.config/pip/pip.conf
ENV PIP_CONFIG_FILE /root/.config/pip/pip.conf


RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt


FROM public.registry.u-hopper.com/python:3.12

RUN mkdir /var/www


COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

RUN pip install coverage pytest-cov anybadge PyYAML

ADD  src/ /scripts/
ADD  documentation/ /documentation/

WORKDIR /scripts

COPY  run.sh .


ENV DOCUMENTATION_PATH /documentation

ADD  test/ /scripts/test/
COPY  run_tests.sh .
COPY  test.sh .

COPY  run_test_coverage.sh .
COPY  .coveragerc .




ENV PYTHONPATH /scripts

ARG GIT_REF

CMD ["./run.sh"]
