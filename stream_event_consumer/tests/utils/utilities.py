import base64
import random
from datetime import datetime, timedelta


def generate_gs_up_receive_message():
    # Generate random values for the message
    gateway_id = random.randint(10000, 99999)
    gateway_eui = ''.join(random.choices('0123456789ABCDEF', k=16))
    timestamp = int(datetime.now().timestamp())
    rssi = random.randint(-130, -70)
    snr = random.uniform(-10, 10)
    f_port = random.randint(1, 255)
    f_cnt = random.randint(0, 65535)
    dev_addr = ''.join(random.choices('0123456789ABCDEF', k=8))
    payload = ''.join(random.choices('0123456789ABCDEF', k=32))

    # Create the message dictionary
    message = {
        "result": {
            "name": "gs.up.receive",
            "time": datetime.utcfromtimestamp(timestamp).isoformat() + "Z",
            "identifiers": [
                {
                    "gateway_ids": {
                        "gateway_id": f"21673-{gateway_id:08X}",
                        "eui": gateway_eui
                    }
                }
            ],
            "data": {
                "@type": "type.googleapis.com/ttn.lorawan.v3.GatewayUplinkMessage",
                "message": {
                    "raw_payload": base64.b64encode(payload.encode()).decode(),
                    "payload": {
                        "m_hdr": {
                            "m_type": "UNCONFIRMED_UP"
                        },
                        "mic": base64.b64encode(payload.encode()).decode(),
                        "mac_payload": {
                            "f_hdr": {
                                "dev_addr": dev_addr,
                                "f_ctrl": {
                                    "adr": True
                                },
                                "f_cnt": f_cnt
                            },
                            "f_port": f_port,
                            "frm_payload": payload
                        }
                    },
                    "settings": {
                        "data_rate": {
                            "lora": {
                                "bandwidth": 125000,
                                "spreading_factor": 7,
                                "coding_rate": "4/5"
                            }
                        },
                        "frequency": "867700000",
                        "timestamp": timestamp,
                        "time": datetime.utcfromtimestamp(timestamp).isoformat() + "Z"
                    },
                    "rx_metadata": [
                        {
                            "gateway_ids": {
                                "gateway_id": f"21673-{gateway_id:08X}",
                                "eui": gateway_eui
                            },
                            "time": datetime.utcfromtimestamp(timestamp).isoformat() + "Z",
                            "timestamp": timestamp,
                            "rssi": rssi,
                            "channel_rssi": rssi,
                            "snr": snr,
                            "uplink_token": base64.b64encode(payload.encode()).decode(),
                            "channel_index": random.randint(0, 7),
                            "received_at": datetime.utcfromtimestamp(
                                timestamp + random.randint(0, 10)).isoformat() + "Z"
                        }
                    ],
                    "received_at": datetime.utcfromtimestamp(timestamp + random.randint(0, 10)).isoformat() + "Z",
                    "correlation_ids": [
                        f"gs:conn:{random.getrandbits(128):032X}",
                        f"gs:uplink:{random.getrandbits(128):032X}"
                    ]
                },
                "band_id": "EU_863_870"
            },
            "correlation_ids": [
                f"gs:conn:{random.getrandbits(128):032X}",
                f"gs:uplink:{random.getrandbits(128):032X}"
            ],
            "origin": "ip-20-23-15-190.example.internal",
            "context": {
                "tenant-id": base64.b64encode("example".encode()).decode()
            },
            "visibility": {
                "rights": ["RIGHT_GATEWAY_TRAFFIC_READ"]
            },
            "unique_id": ''.join(random.choices('0123456789ABCDEF', k=16))
        }
    }

    return message


def generate_gs_gateway_connection_stats_message():
    # Generate random values for the message
    gateway_id = random.randint(10000, 99999)
    gateway_eui = ''.join(random.choices('0123456789ABCDEF', k=16))
    connected_at = datetime(2022, 12, 13, 14, 0, 17).isoformat() + "Z"
    last_status_received_at = datetime(2023, 1, 3, 15, 50, 3).isoformat() + "Z"
    last_uplink_received_at = datetime(2023, 1, 3, 15, 50, 3).isoformat() + "Z"
    last_downlink_received_at = datetime(2023, 1, 3, 14, 9, 15).isoformat() + "Z"
    uplink_count = str(random.randint(0, 999999))
    downlink_count = str(random.randint(0, 9999))
    min_round_trip_time = "4.265192138s"
    max_round_trip_time = "4.882918997s"
    median_round_trip_time = "4.536759571s"
    round_trip_count = 20

    # Create the message dictionary
    message = {
        "result": {
            "name": "gs.gateway.connection.stats",
            "time": datetime.utcnow().isoformat() + "Z",
            "identifiers": [
                {
                    "gateway_ids": {
                        "gateway_id": f"24713-{gateway_id:016X}",
                        "eui": gateway_eui
                    }
                }
            ],
            "data": {
                "@type": "type.googleapis.com/ttn.lorawan.v3.GatewayConnectionStats",
                "connected_at": connected_at,
                "protocol": "udp",
                "last_status_received_at": last_status_received_at,
                "last_status": {
                    "time": datetime.utcfromtimestamp(
                        datetime.strptime(last_status_received_at, "%Y-%m-%dT%H:%M:%SZ").timestamp() - random.randint(0,
                                                                                                                      10)).isoformat() + "Z",
                    "boot_time": datetime.utcfromtimestamp(
                        datetime.strptime(last_status_received_at, "%Y-%m-%dT%H:%M:%SZ").timestamp() - random.randint(0,
                                                                                                                      10)).isoformat() + "Z",
                    "versions": {
                        "hal": "5.0.1",
                        "ttn-lw-gateway-server": "3.23.1-rc0-SNAPSHOT-c7ea98ce9",
                        "fpga": "31"
                    },
                    "antenna_locations": [
                        {
                            "latitude": 51.56352996826172,
                            "longitude": -0.4188860058784485,
                            "altitude": 41,
                            "source": "SOURCE_GPS"
                        }
                    ],
                    "ip": ["95.140.30.30"],
                    "metrics": {
                        "txin": 0,
                        "txok": 0,
                        "lpps": 0,
                        "rxin": 2,
                        "rxok": 1,
                        "rxfw": 2,
                        "ackr": 100
                    }
                },
                "last_uplink_received_at": last_uplink_received_at,
                "uplink_count": uplink_count,
                "last_downlink_received_at": last_downlink_received_at,
                "downlink_count": downlink_count,
                "round_trip_times": {
                    "min": min_round_trip_time,
                    "max": max_round_trip_time,
                    "median": median_round_trip_time,
                    "count": round_trip_count
                },
                "sub_bands": [
                    {
                        "min_frequency": "863000000",
                        "max_frequency": "865000000",
                        "downlink_utilization_limit": 0.001
                    },
                    {
                        "min_frequency": "865000000",
                        "max_frequency": "868000000",
                        "downlink_utilization_limit": 0.01
                    },
                    {
                        "min_frequency": "868000000",
                        "max_frequency": "868600000",
                        "downlink_utilization_limit": 0.01,
                        "downlink_utilization": 0.00096028444
                    },
                    {
                        "min_frequency": "868700000",
                        "max_frequency": "869200000",
                        "downlink_utilization_limit": 0.001
                    },
                    {
                        "min_frequency": "869400000",
                        "max_frequency": "869650000",
                        "downlink_utilization_limit": 0.1
                    },
                    {
                        "min_frequency": "869700000",
                        "max_frequency": "870000000",
                        "downlink_utilization_limit": 0.01
                    }
                ],
                "gateway_remote_address": {
                    "ip": "95.140.30.30"
                }
            },
            "correlation_ids": [
                "gs:conn:01GMQMPGVWDWN692BGMPYDQHD0"
            ],
            "origin": "ip-20-23-15-190.example.internal",
            "context": {
                "tenant-id": "CgxleGFtcGxl"
            },
            "visibility": {
                "rights": ["RIGHT_GATEWAY_LINK", "RIGHT_GATEWAY_STATUS_READ"]
            },
            "unique_id": ''.join(random.choices('0123456789ABCDEF', k=16))
        }
    }

    return message


def generate_gs_down_send_message():
    # Generate random values for the message
    gateway_id = random.randint(10000, 99999)
    gateway_eui = ''.join(random.choices('0123456789ABCDEF', k=16))
    timestamp = datetime.now().isoformat() + "Z"
    raw_payload = "YPpNASeDSQECDgEA/v3R"
    frequency = "868500000"
    tx_power = 16.15

    # Create the message dictionary
    message = {
        "result": {
            "name": "gs.down.send",
            "time": timestamp,
            "identifiers": [
                {
                    "gateway_ids": {
                        "gateway_id": f"24713-{gateway_id:08X}",
                        "eui": gateway_eui
                    }
                }
            ],
            "data": {
                "@type": "type.googleapis.com/ttn.lorawan.v3.DownlinkMessage",
                "raw_payload": raw_payload,
                "scheduled": {
                    "data_rate": {
                        "lora": {
                            "bandwidth": 125000,
                            "spreading_factor": 7,
                            "coding_rate": "4/5"
                        }
                    },
                    "frequency": frequency,
                    "timestamp": 1745197475,
                    "downlink": {
                        "tx_power": tx_power,
                        "invert_polarization": True
                    },
                    "concentrator_timestamp": "87644543395000"
                },
                "correlation_ids": [
                    "gs:conn:01GMQMPGVWDWN692BGMPYDQHD0",
                    "gs:up:host:01GMQMPGVZE39N2FG05HC5NFHM",
                    "gs:uplink:01GMT88YA7WAK9GTWFRWA7PE3M",
                    "ns:downlink:01GMT88YQ8NAZJJ09Y5JJ2P7CG",
                    "ns:transmission:01GMT88YQ8CKCPBX7V34SNC71B",
                    "ns:uplink:01GMT88YA9NSA630XSC7WT2S99",
                    "rpc:/ttn.lorawan.v3.GsNs/HandleUplink:01GMT88YA90WDMVJCR84N2AEEJ",
                    "rpc:/ttn.lorawan.v3.NsGs/ScheduleDownlink:01GMT88YQ8KJT0A1E1PK9Q6NFZ"
                ]
            },
            "correlation_ids": [
                "gs:conn:01GMQMPGVWDWN692BGMPYDQHD0",
                "gs:up:host:01GMQMPGVZE39N2FG05HC5NFHM",
                "gs:uplink:01GMT88YA7WAK9GTWFRWA7PE3M",
                "ns:downlink:01GMT88YQ8NAZJJ09Y5JJ2P7CG",
                "ns:transmission:01GMT88YQ8CKCPBX7V34SNC71B",
                "ns:uplink:01GMT88YA9NSA630XSC7WT2S99",
                "rpc:/ttn.lorawan.v3.GsNs/HandleUplink:01GMT88YA90WDMVJCR84N2AEEJ",
                "rpc:/ttn.lorawan.v3.NsGs/ScheduleDownlink:01GMT88YQ8KJT0A1E1PK9Q6NFZ"
            ],
            "origin": "ip-20-23-15-190.example.internal",
            "context": {
                "tenant-id": "CgxleGFtcGxl"
            },
            "visibility": {
                "rights": ["RIGHT_GATEWAY_TRAFFIC_READ"]
            },
            "unique_id": "01GMT88YQ90176P4D6W7F1K3CN"
        }
    }
    return message


def generate_gs_status_receive_message():
    # Generate random values for the message
    gateway_id = random.randint(10000, 99999)
    gateway_eui = ''.join(random.choices('0123456789ABCDEF', k=16))
    timestamp = int(datetime.now().timestamp())
    latitude = round(random.uniform(-90, 90), 5)
    longitude = round(random.uniform(-180, 180), 5)
    altitude = random.randint(0, 1000)
    rxok = random.randint(0, 100)
    rxfw = random.randint(0, 100)
    ackr = random.randint(0, 100)
    txin = random.randint(0, 100)
    txok = random.randint(0, 100)
    rxin = random.randint(0, 100)

    # Create the message dictionary
    message = {
        "result": {
            "name": "gs.status.receive",
            "time": datetime.utcfromtimestamp(timestamp).isoformat() + "Z",
            "identifiers": [
                {
                    "gateway_ids": {
                        "gateway_id": f"24713-{gateway_id:08X}",
                        "eui": gateway_eui
                    }
                }
            ],
            "data": {
                "@type": "type.googleapis.com/ttn.lorawan.v3.GatewayStatus",
                "time": datetime.utcfromtimestamp(timestamp).isoformat() + "Z",
                "boot_time": (datetime.utcfromtimestamp(timestamp) - timedelta(hours=24)).isoformat() + "Z",
                "versions": {
                    "fpga": "31",
                    "hal": "5.0.1",
                    "ttn-lw-gateway-server": "3.23.1-rc0-SNAPSHOT-c7ea98ce9"
                },
                "antenna_locations": [
                    {
                        "latitude": latitude,
                        "longitude": longitude,
                        "altitude": altitude,
                        "source": "SOURCE_GPS"
                    }
                ],
                "ip": [f"192.168.0.{random.randint(1, 255)}"],
                "metrics": {
                    "rxfw": rxfw,
                    "ackr": ackr,
                    "txin": txin,
                    "txok": txok,
                    "lpps": 0,
                    "rxin": rxin,
                    "rxok": rxok
                }
            },
            "correlation_ids": [
                "gs:conn:01GMQMPGVWDWN692BGMPYDQHD0",
                "gs:status:01GMT7SN1Z8WSPK3N8M2DQEHK3"
            ],
            "origin": "ip-10-23-13-196.example.internal",
            "context": {
                "tenant-id": "CgxleGFtcGxl"
            },
            "visibility": {
                "rights": ["RIGHT_GATEWAY_STATUS_READ"]
            },
            "unique_id": "01GMT7SN1ZYJ55FKAE4N90M9AD"
        }
    }

    return message
