from stream_event_consumer_service import MessageConsumer
from stream_event_consumer_service import PacketReplicaMetadata
from .utils.utilities import generate_gs_gateway_connection_stats_message, generate_gs_down_send_message, \
    generate_gs_status_receive_message
from unittest.mock import Mock


def test_parse_sub_bands():
    # Define input sub_bands data
    sub_bands = [
        {
            "min_frequency": 100,
            "max_frequency": 200,
            "downlink_utilization_limit": 50,
            "downlink_utilization": 40
        },
        {
            "min_frequency": 300,
            "max_frequency": 400,
            "downlink_utilization_limit": 80,
            "downlink_utilization": 70
        }
    ]

    # Call the parse_sub_bands method
    result = MessageConsumer.parse_sub_bands(sub_bands)

    # Assert the parsed sub_band_info dictionary
    assert result == {
        "min_freq_band_0": 100,
        "max_freq_band_0": 200,
        "dl_utilization_limit_band_0": 50,
        "dl_utilization_band_0": 40,
        "min_freq_band_1": 300,
        "max_freq_band_1": 400,
        "dl_utilization_limit_band_1": 80,
        "dl_utilization_band_1": 70
    }


def test_parse_metrics():
    # Define input metrics data
    metrics = {
        "txin": 100,
        "txok": 90,
        "lpps": 80,
        "rxin": 70,
        "rxok": 60,
        "rxfw": 50,
        "ackr": 40
    }

    # Call the parse_metrics method
    result = MessageConsumer.parse_metrics(metrics)

    # Assert the parsed metrics dictionary
    assert result == {
        "txin": 100,
        "txok": 90,
        "lpps": 80,
        "rxin": 70,
        "rxok": 60,
        "rxfw": 50,
        "ackr": 40
    }


def test_parse_round_trip_times():
    # Define input data with round trip times
    data = {
        "round_trip_times": {
            "min": 10,
            "max": 100,
            "median": 50,
            "count": 1000
        }
    }

    # Call the parse_round_trip_times method
    result = MessageConsumer.parse_round_trip_times(data)

    # Assert the parsed round trip times dictionary
    assert result == {
        "min_round_trip_times": 10,
        "max_round_trip_times": 100,
        "median_round_trip_times": 50,
        "count_round_trip_times": 1000
    }


def test_get_common_features():
    # Define sample input data for the rx_event_message
    rx_event_message = {
        "result": {
            "name": "Sample Event",
            "time": "2023-06-07T10:00:00",
            "identifiers": [
                {
                    "gateway_ids": {
                        "gateway_id": "123456",
                        "eui": "ABCDEF"
                    }
                }
            ],
            "context": {
                "tenant-id": "my-tenant"
            },
            "visibility": {
                "rights": ["read", "write"]
            },
            "unique_id": "abcdef123456"
        }
    }

    # Call the get_common_features method
    result = MessageConsumer.get_common_features(rx_event_message)

    # Assert the parsed common features dictionary
    assert result == {
        "name": "Sample Event",
        "time": "2023-06-07T10:00:00",
        "gateway_id": "123456",
        "gateway_eui": "ABCDEF",
        "tenant-id": "my-tenant",
        "rights": "read",
        "unique_id": "abcdef123456"
    }


def test_decode_gs_gateway_connection_stats():
    # Create a random gateway connection stats message
    message = generate_gs_gateway_connection_stats_message()

    # Create a logger object
    logger = Mock()

    # Set up test parameters
    rabbit_username = "guest"
    rabbit_password = "guest"
    rabbit_host = "localhost"
    queue_name = "test_queue"
    db_engine = Mock()
    max_threads = 5

    # Create a MessageConsumer instance
    consumer = MessageConsumer(logger, rabbit_username, rabbit_password, rabbit_host, queue_name, db_engine,
                               max_threads)
    decoded_data = consumer.decode_gs_gateway_connection_stats(message)

    # Add assertions to verify the decoded data against the expected output

    assert decoded_data["event_name"] == "gs.gateway.connection.stats"
    assert decoded_data["event_time"] == message["result"]["time"]
    assert decoded_data["gateway_id"] == message["result"]["identifiers"][0]["gateway_ids"]["gateway_id"]
    assert decoded_data["gateway_eui"] == message["result"]["identifiers"][0]["gateway_ids"]["eui"]
    assert decoded_data["connected_at"] == message["result"]["data"]["connected_at"]
    assert decoded_data["protocol"] == message["result"]["data"]["protocol"]
    assert decoded_data["last_status_received_at"] == message["result"]["data"]["last_status_received_at"]
    assert decoded_data["last_status_time"] == message["result"]["data"]["last_status"]["time"]
    assert decoded_data["last_uplink_received_at"] == message["result"]["data"]["last_uplink_received_at"]
    assert decoded_data["last_downlink_received_at"] == message["result"]["data"]["last_downlink_received_at"]
    assert decoded_data["boot_time"] == message["result"]["data"]["last_status"]["boot_time"]
    assert decoded_data["ttn_lw_gateway_server"] == message["result"]["data"]["last_status"]["versions"][
        "ttn-lw-gateway-server"]
    assert decoded_data["fpga"] == message["result"]["data"]["last_status"]["versions"].get("fpga")
    assert decoded_data["hal"] == message["result"]["data"]["last_status"]["versions"].get("hal")
    assert decoded_data["latitude"] == message["result"]["data"]["last_status"]["antenna_locations"][0].get("latitude")
    assert decoded_data["longitude"] == message["result"]["data"]["last_status"]["antenna_locations"][0].get(
        "longitude")
    assert decoded_data["altitude"] == message["result"]["data"]["last_status"]["antenna_locations"][0].get("altitude")
    assert decoded_data["source"] == message["result"]["data"]["last_status"]["antenna_locations"][0].get("source")
    assert decoded_data["ip"] == message["result"]["data"]["last_status"].get("ip", [None])[0]
    assert decoded_data["rxin"] == message["result"]["data"]["last_status"]["metrics"].get("rxin")
    assert decoded_data["rxok"] == message["result"]["data"]["last_status"]["metrics"].get("rxok")
    assert decoded_data["rxfw"] == message["result"]["data"]["last_status"]["metrics"].get("rxfw")
    assert decoded_data["ackr"] == message["result"]["data"]["last_status"]["metrics"].get("ackr")
    assert decoded_data["txin"] == message["result"]["data"]["last_status"]["metrics"].get("txin")
    assert decoded_data["txok"] == message["result"]["data"]["last_status"]["metrics"].get("txok")
    assert decoded_data["uplink_count"] == message["result"]["data"]["uplink_count"]
    assert decoded_data["downlink_count"] == message["result"]["data"]["downlink_count"]


def test_parse_gs_up_message():
    # Create a sample message for testing
    message = {
        "payload": {
            "mac_payload": {
                "f_hdr": {
                    "f_ctrl": {"adr": True},
                    "f_cnt": 123,
                    "dev_addr": "ABC123"
                },
                "f_port": 1,
                "frm_payload": "Hello"
            },
            "join_request_payload": {
                "join_eui": "ABCDEF",
                "dev_eui": "123456",
                "dev_nonce": "789"
            }
        },
        "raw_payload": "..."
    }

    # Create a logger object
    logger = Mock()

    # Set up test parameters
    rabbit_username = "guest"
    rabbit_password = "guest"
    rabbit_host = "localhost"
    queue_name = "test_queue"
    db_engine = Mock()
    max_threads = 5

    # Create a MessageConsumer instance
    consumer = MessageConsumer(logger, rabbit_username, rabbit_password, rabbit_host, queue_name, db_engine,
                               max_threads)
    parsed_message = consumer.parse_gs_up_message(message)

    # Assert the expected values
    assert parsed_message["raw_payload"] == message["raw_payload"]
    assert parsed_message["frm_payload"] == message["payload"]["mac_payload"]["frm_payload"]
    assert parsed_message["f_ctrl_adr"] == message["payload"]["mac_payload"]["f_hdr"]["f_ctrl"]["adr"]
    assert parsed_message["f_cnt"] == message["payload"]["mac_payload"]["f_hdr"]["f_cnt"]
    assert parsed_message["dev_addr"] == message["payload"]["mac_payload"]["f_hdr"]["dev_addr"]
    assert parsed_message["f_port"] == message["payload"]["mac_payload"]["f_port"]
    assert parsed_message["join_eui"] == message["payload"]["join_request_payload"]["join_eui"]
    assert parsed_message["dev_eui"] == message["payload"]["join_request_payload"]["dev_eui"]
    assert parsed_message["dev_nonce"] == message["payload"]["join_request_payload"]["dev_nonce"]


def test_decode_gs_down_send():
    # Create a random gateway connection stats message
    message = generate_gs_down_send_message()

    # Create a logger object
    logger = Mock()

    # Set up test parameters
    rabbit_username = "guest"
    rabbit_password = "guest"
    rabbit_host = "localhost"
    queue_name = "test_queue"
    db_engine = Mock()
    max_threads = 5

    # Create a MessageConsumer instance
    consumer = MessageConsumer(logger, rabbit_username, rabbit_password, rabbit_host, queue_name, db_engine,
                               max_threads)
    decoded_message = consumer.decode_gs_down_send(message)

    # Perform assertions to validate the decoding
    assert decoded_message["event_time"] == message["result"]["time"]
    assert decoded_message["gateway_id"] == message["result"]["identifiers"][0]["gateway_ids"]["gateway_id"]
    assert decoded_message["gateway_eui"] == message["result"]["identifiers"][0]["gateway_ids"]["eui"]
    assert decoded_message["raw_payload"] == message["result"]["data"]["raw_payload"]
    assert decoded_message["bandwidth"] == message["result"]["data"]["scheduled"]["data_rate"]["lora"]["bandwidth"]
    assert decoded_message["spreading_factor"] == message["result"]["data"]["scheduled"]["data_rate"]["lora"][
        "spreading_factor"]
    assert decoded_message["coding_rate"] == message["result"]["data"]["scheduled"]["data_rate"]["lora"]["coding_rate"]
    assert decoded_message["frequency"] == message["result"]["data"]["scheduled"]["frequency"]
    assert decoded_message["timestamp"] == message["result"]["data"]["scheduled"]["timestamp"]
    assert decoded_message["concentrator_timestamp"] == message["result"]["data"]["scheduled"]["concentrator_timestamp"]
    assert decoded_message["tx_power"] == float(message["result"]["data"]["scheduled"]["downlink"]["tx_power"])
    assert decoded_message["invert_polarization"] == message["result"]["data"]["scheduled"]["downlink"][
        "invert_polarization"]


def test_decode_gs_status_receive():
    # Generate a sample message
    message = generate_gs_status_receive_message()
    print(message)

    # Create a logger object
    logger = Mock()

    # Set up test parameters
    rabbit_username = "guest"
    rabbit_password = "guest"
    rabbit_host = "localhost"
    queue_name = "test_queue"
    db_engine = Mock()
    max_threads = 5

    # Create a MessageConsumer instance
    consumer = MessageConsumer(logger, rabbit_username, rabbit_password, rabbit_host, queue_name, db_engine,
                               max_threads)
    decoded_message = consumer.decode_gs_status_receive(message)

    # Verify the decoded message
    assert decoded_message["name"] == "gs.status.receive"
    assert decoded_message["event_time"] == message["result"]["time"]
    assert decoded_message["gateway_id"] == message["result"]["identifiers"][0]["gateway_ids"]["gateway_id"]
    assert decoded_message["gateway_eui"] == message["result"]["identifiers"][0]["gateway_ids"]["eui"]
    assert decoded_message["time"] == message["result"]["data"]["time"]
    assert decoded_message["boot_time"] == message["result"]["data"]["boot_time"]
    assert decoded_message["ttn_lw_gateway_server"] == message["result"]["data"]["versions"]["ttn-lw-gateway-server"]
    assert decoded_message["fpga"] == message["result"]["data"]["versions"].get("fpga")
    assert decoded_message["hal"] == message["result"]["data"]["versions"].get("hal")
    assert decoded_message["latitude"] == message["result"]["data"]["antenna_locations"][0].get("latitude", None)
    assert decoded_message["longitude"] == message["result"]["data"]["antenna_locations"][0].get("longitude", None)
    assert decoded_message["altitude"] == message["result"]["data"]["antenna_locations"][0].get("altitude", None)
    assert decoded_message["source"] == message["result"]["data"]["antenna_locations"][0].get("source", None)
    assert decoded_message["ip"] == message["result"]["data"]["ip"][0]
    assert decoded_message["txin"] == message["result"]["data"]["metrics"].get("txin", None)
    assert decoded_message["txok"] == message["result"]["data"]["metrics"].get("txok", None)
    assert decoded_message["lpps"] == message["result"]["data"]["metrics"].get("lpps", None)
    assert decoded_message["rxin"] == message["result"]["data"]["metrics"].get("rxin", None)
    assert decoded_message["rxok"] == message["result"]["data"]["metrics"].get("rxok", None)
    assert decoded_message["rxfw"] == message["result"]["data"]["metrics"].get("rxfw", None)
    assert decoded_message["ackr"] == message["result"]["data"]["metrics"].get("ackr", None)
