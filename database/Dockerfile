#
# Database service.
#

FROM python:3 AS production

WORKDIR /usr/src/app
ENV PYTHONPATH "${PYTHONPATH}:/usr/src/app/database/sources"

# Install dependencies.
COPY database/sources/requirements.txt database/sources/requirements.txt
RUN pip install --no-cache-dir -r database/sources/requirements.txt

# Copy sources.
COPY database/sources database/sources

# Generate proto files.
COPY database/database.proto database.proto
RUN python -m grpc_tools.protoc \
	--proto_path=. \
	--python_out=database/sources \
	--grpc_python_out=database/sources \
	*.proto \
	&& \
	rm *.proto

CMD [ "python", "-u", "database/sources/main.py" ]

#
# Database service tests.
#

FROM production AS test

# Install dependencies.
COPY database/tests/requirements.txt database/tests/requirements.txt
RUN pip install --no-cache-dir -r database/tests/requirements.txt

# Copy tests.
COPY database/tests database/tests

CMD [ "pytest" ]
