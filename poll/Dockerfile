#
# Poll service.
#

FROM python:3 AS production

WORKDIR /usr/src/app
ENV PYTHONPATH "${PYTHONPATH}:/usr/src/app/poll/sources"

# Install dependencies.
COPY poll/sources/requirements.txt poll/sources/requirements.txt
RUN pip install --no-cache-dir -r poll/sources/requirements.txt

# Copy sources.
COPY poll/sources poll/sources

# Generate proto files.
COPY update/update.proto update.proto
COPY rank/rank.proto rank.proto
COPY database/database.proto database.proto
RUN python -m grpc_tools.protoc \
	--proto_path=. \
	--python_out=poll/sources \
	--grpc_python_out=poll/sources \
	*.proto \
	&& \
	rm *.proto

CMD [ "python", "poll/sources/main.py" ]
