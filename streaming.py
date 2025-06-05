from google.cloud import bigquery_storage_v1
from google.cloud.bigquery_storage_v1 import types
from google.cloud.bigquery_storage_v1 import writer
from google.protobuf import descriptor_pb2
import logging
import json

import sample_data_pb2

# The list of columns from the table's schema to search in the given data to write to BigQuery.
TABLE_COLUMNS_TO_CHECK = [
    "name",
    "age"
    ]

# Function to create a batch of row data to be serialized.
def create_row_data(data):
    row = sample_data_pb2.SampleData()
    for field in TABLE_COLUMNS_TO_CHECK:
      # Optional fields will be passed as null if not provided
      if field in data:
        setattr(row, field, data[field])
    return row.SerializeToString()

class BigQueryStorageWriteAppend(object):

    # The stream name is: projects/{project}/datasets/{dataset}/tables/{table}/_default
    def append_rows_proto2(
        project_id: str, dataset_id: str, table_id: str, data: dict
    ):

        write_client = bigquery_storage_v1.BigQueryWriteClient()
        parent = write_client.table_path(project_id, dataset_id, table_id)
        stream_name = f'{parent}/_default'
        write_stream = types.WriteStream()

        # Create a template with fields needed for the first request.
        request_template = types.AppendRowsRequest()

        # The request must contain the stream name.
        request_template.write_stream = stream_name

        # Generating the protocol buffer representation of the message descriptor.
        proto_schema = types.ProtoSchema()
        proto_descriptor = descriptor_pb2.DescriptorProto()
        sample_data_pb2.SampleData.DESCRIPTOR.CopyToProto(proto_descriptor)
        proto_schema.proto_descriptor = proto_descriptor
        proto_data = types.AppendRowsRequest.ProtoData()
        proto_data.writer_schema = proto_schema
        request_template.proto_rows = proto_data

        # Construct an AppendRowsStream to send an arbitrary number of requests to a stream.
        append_rows_stream = writer.AppendRowsStream(write_client, request_template)

        # Append proto2 serialized bytes to the serialized_rows repeated field using create_row_data.
        proto_rows = types.ProtoRows()
        for row in data:
            proto_rows.serialized_rows.append(create_row_data(row))

        # Appends data to the given stream.
        request = types.AppendRowsRequest()
        proto_data = types.AppendRowsRequest.ProtoData()
        proto_data.rows = proto_rows
        request.proto_rows = proto_data

        append_rows_stream.send(request)

        print(f"Rows to table: '{parent}' have been written.")

if __name__ == "__main__":

    ###### Uncomment the below block to provide additional logging capabilities ######
    #logging.basicConfig(
    #    level=logging.DEBUG,
    #    format="%(asctime)s [%(levelname)s] %(message)s",
    #    handlers=[
    #        logging.StreamHandler()
    #    ]
    #)
    ###### Uncomment the above block to provide additional logging capabilities ######

    with open('entries.json', 'r') as json_file:
        data = json.load(json_file)
    # Change this to your specific BigQuery project, dataset, table details
    BigQueryStorageWriteAppend.append_rows_proto2("jagan-461105","terraform_dataset", "terraform_table",data=data)