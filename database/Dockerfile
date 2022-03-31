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

CMD [ "python", "database/sources/main.py" ]
