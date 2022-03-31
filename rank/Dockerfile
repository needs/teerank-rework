#
# Rank service.
#

FROM python:3 AS production

WORKDIR /usr/src/app
ENV PYTHONPATH "${PYTHONPATH}:/usr/src/app/rank/sources"

# Install dependencies.
COPY rank/sources/requirements.txt rank/sources/requirements.txt
RUN pip install --no-cache-dir -r rank/sources/requirements.txt

# Copy sources.
COPY rank/sources rank/sources

# Generate proto files.
COPY rank/rank.proto rank.proto
RUN python -m grpc_tools.protoc \
	--proto_path=. \
	--python_out=rank/sources \
	--grpc_python_out=rank/sources \
	*.proto \
	&& \
	rm *.proto

CMD [ "python", "rank/sources/main.py" ]
