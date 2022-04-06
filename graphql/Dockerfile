#
# Production target.
#

FROM mitmproxy/mitmproxy:latest AS production
COPY graphql/sources/graphql.py graphql.py
CMD [ "mitmdump", "-s", "graphql.py" ]

#
# Test target.
#

FROM python:3 AS test

COPY config/python/tests/requirements.txt tests/requirements-config.txt
COPY graphql/tests/requirements.txt tests/requirements.txt

RUN pip install --no-cache-dir \
	-r tests/requirements-config.txt \
	-r tests/requirements.txt

COPY graphql/tests tests
COPY config/python/tests/setup.cfg setup.cfg

CMD [ "pytest" ]
