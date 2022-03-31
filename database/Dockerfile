#
# Database service.
#

FROM python:3 AS production

WORKDIR /usr/src/app
ENV PYTHONPATH "${PYTHONPATH}:/usr/src/app/sources:/usr/src/app/protos"

# Install dependencies.
COPY database/sources/requirements.txt sources/requirements.txt
RUN pip install --no-cache-dir -r sources/requirements.txt

# Copy sources.
COPY database/sources sources

# Generate proto files.
COPY database/protos protos
RUN python -m grpc_tools.protoc -Iprotos --python_out=protos --grpc_python_out=protos protos/*.proto

# Run service.
CMD [ "python", "-u", "sources/main.py" ]

#
# Database service tests.
#

FROM production AS test

ENV MYPYPATH "${MYPYPATH}:/usr/src/app/sources:/usr/src/app/protos"

# Install tests dependencies.
COPY database/tests/requirements.txt tests/requirements.txt
RUN pip install --no-cache-dir -r tests/requirements.txt

# Generate mypy stub files.
RUN python -m grpc_tools.protoc -Iprotos --mypy_out=protos protos/*.proto

# Copy tests.
COPY database/tests tests
RUN mv \
	tests/pytest.ini \
	tests/.coveragerc \
	tests/.pylintrc \
	.

# Run service.
CMD [ "pytest" ]
