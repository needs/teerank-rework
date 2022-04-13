#
# Production target.
#

FROM python:3 AS production

ARG project

WORKDIR /usr/src/app
ENV PYTHONPATH "${PYTHONPATH}:/usr/src/app/sources:/usr/src/app/protos"

# Install dependencies.
COPY config/python/sources/requirements.txt sources/requirements-config.txt
COPY $project/sources/requirements.txt sources/requirements.txt
RUN pip install --no-cache-dir \
	-r sources/requirements-config.txt \
	-r sources/requirements.txt

# Copy sources.
COPY $project/sources sources

# Copy gql_client package.
COPY gql_client/sources gql_client

# Generate proto files.
COPY config/protos protos
RUN python -m grpc_tools.protoc -Iprotos --python_out=protos --grpc_python_out=protos protos/*.proto

# Run service.
CMD [ "python", "-u", "sources/main.py" ]

#
# Test target.
#

FROM production AS test

# Install tests dependencies.
COPY config/python/tests/requirements.txt tests/requirements-config.txt
COPY $project/tests/requirements.txt tests/requirements.txt
RUN pip install --no-cache-dir \
	-r tests/requirements-config.txt \
	-r tests/requirements.txt

# Generate mypy stub files.
RUN python -m grpc_tools.protoc -Iprotos --mypy_out=protos protos/*.proto

# Copy tests.
COPY $project/tests tests
COPY config/python/tests/setup.cfg setup.cfg

COPY config/schema.graphql config/schema.graphql

# Run service.
CMD [ "pytest" ]
