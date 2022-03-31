#
# Update service.
#

FROM python:3 AS production

WORKDIR /usr/src/app
ENV PYTHONPATH "${PYTHONPATH}:/usr/src/app/update/sources"

# Install dependencies.
COPY update/sources/requirements.txt update/sources/requirements.txt
RUN pip install --no-cache-dir -r update/sources/requirements.txt

# Copy sources.
COPY update/sources update/sources

# Generate proto files.
COPY update/update.proto update/update.proto
RUN python -m grpc_tools.protoc \
	--proto_path=update \
	--python_out=update/sources \
	--grpc_python_out=update/sources \
	update/update.proto \
	&& \
	rm update/update.proto

CMD [ "python", "update/sources/main.py" ]
